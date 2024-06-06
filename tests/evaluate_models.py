import argparse
import os
import glob
import pickle
from ast import literal_eval

import numpy as np

from rl_sandbox.examples.eval_tools.utils import load_model, get_aux_rew_aux_suc
from rl_sandbox.examples.eval_tools.evaluate import evaluate
from rl_sandbox.learning_utils import evaluate_policy
from rl_sandbox.utils import get_rng_state, set_rng_state
import rl_sandbox.constants as c
from rl_sandbox.algorithms.sac_x.schedulers import FixedScheduler


def safe_save_train_dict(train_dict, path):
    print("Saving train dict")
    os.rename(path, path + '.bak')
    pickle.dump(train_dict, open(path, 'wb'))
    os.remove(path + '.bak')


parser = argparse.ArgumentParser()
parser.add_argument('--env_name', type=str, required=True)
parser.add_argument('--exp_name', type=str, required=True, help="String corresponding to the experiment name")
parser.add_argument('--eval_seed', type=int, default=12)
parser.add_argument('--top_save_path', type=str, default=os.path.join(os.environ['VPACE_TOP_DIR'], 'results'),
                    help="Top path for loading saved results")
parser.add_argument('--model_seed', type=int, default=100)
parser.add_argument('--algo', type=str, default='multi-sqil')
parser.add_argument('--aux_task', type=int, default=0)
parser.add_argument('--forced_schedule', type=str, default="")
parser.add_argument('--model_min', type=int, default=0)
parser.add_argument('--model_max', type=int, default=100000)
parser.add_argument('--device', type=str, default='cuda:0')
parser.add_argument('--num_eval_eps', type=int, default=10)
parser.add_argument('--stochastic', action='store_true')
parser.add_argument('--max_ep_steps', type=int, default=60)
parser.add_argument('--no_save', action='store_true')
args = parser.parse_args()

# forced schedule example: "{0: 3, 25: 2, 50: 4, 75: 5, 100: 1, 125: 3, 150: 4, 175: 2, 200: 1}"
# for exploratory episodes, higher max steps, and explore "{0: 1, 20: 2, 40: 0, 60: 1, 80: 2, 100: 0}"

# overwrite the train.pkl file in the experiment directory with a dictionary that contains:
# - the values that are already in the train.pkl file (i.e. only append, don't delete)
# - evaluation_successes_all_tasks: a list for each eval checkpoint, with each entry containing a
#   (num_tasks, num_tasks * num_eval_eps) np array with 1s and 0s for success
# - specifically want to customize and not be forced to evaluate non main task
# - evaluation_returns: same, but for returns instead of success
# - when this script is run, immediately generate a list of length of number of saved models in this directory,
#   but initially populated with None so we know which are invalid
# - add valid_eval parameter to dict, dict corresponding to each model to determine what is valid


forced_schedule = None if args.forced_schedule == "" else literal_eval(args.forced_schedule)

if 'multi' in args.algo:
    config_file = 'lfgp_experiment_setting.pkl'
else:
    config_file = 'dac_experiment_setting.pkl'

exp_path = os.path.join(args.top_save_path, args.env_name, str(args.model_seed), args.algo, args.exp_name)
all_exps = glob.glob(os.path.join(exp_path, '*'))
if len(all_exps) == 0:
    raise ValueError(f"No folders found in {exp_path}")
main_model_path = sorted(all_exps)[-1]
if len(all_exps) > 1:
    print(f"Multiple folders found, using {main_model_path}")
config_path = os.path.join(main_model_path, config_file)

model_paths = sorted(glob.glob(os.path.join(main_model_path, '*0.pt')))
model_ints = [int(m.split('/')[-1].split('.pt')[0]) for m in model_paths]

# sort ints and paths in incremental order
sorted_ints = np.argsort(np.array(model_ints))
model_ints = [model_ints[i] for i in sorted_ints]
model_paths = [model_paths[i] for i in sorted_ints]

# get number of valid aux tasks from one ex model
config, _, _ = load_model(0, config_path, model_paths[0], args.aux_task,
                          include_env=False, device=args.device, include_disc=False, force_egl=False)
num_aux_tasks = config.get(c.NUM_TASKS, 1)

train_file_path = os.path.join(main_model_path, 'train.pkl')
train_file_dict = pickle.load(open(train_file_path, 'rb'))
if 'valid_eval' not in train_file_dict:
    train_file_dict['valid_eval'] = {}
if 'evaluation_successes_all_tasks' not in train_file_dict or train_file_dict['evaluation_successes_all_tasks'] == []:
    train_file_dict['evaluation_successes_all_tasks'] = [[]] * len(model_paths)
if 'evaluation_returns' not in train_file_dict or train_file_dict['evaluation_returns'] == []:
    train_file_dict['evaluation_returns'] = [[]] * len(model_paths)
for m_int_i, m_int in enumerate(model_ints):
    if m_int not in train_file_dict['valid_eval']:
        # eval is done in parallel, so don't ned num_aux_tasks * args.num_eval_eps in valid_eval
        train_file_dict['valid_eval'][m_int] = np.zeros([num_aux_tasks, args.num_eval_eps])
        train_file_dict['evaluation_successes_all_tasks'][m_int_i] = np.zeros([num_aux_tasks, num_aux_tasks * args.num_eval_eps])
        train_file_dict['evaluation_returns'][m_int_i] = np.zeros([num_aux_tasks, num_aux_tasks * args.num_eval_eps])

# add random state to dict as well so that we handle resets properly
if 'eval_np_rng_state' not in train_file_dict:
    rng_state_dict = get_rng_state()
    for rng_k, rng_v in rng_state_dict.items():
        train_file_dict[f"eval_{rng_k}"] = rng_v
else:
    set_rng_state(train_file_dict['eval_torch_rng_state'], train_file_dict['eval_np_rng_state'])

if not args.no_save:
    safe_save_train_dict(train_file_dict, train_file_path)

models_to_test = []
model_ints_to_test = []
model_int_i_to_test = []
for m_int_i, (m_path, m_int) in enumerate(zip(model_paths, model_ints)):
    if args.model_min < m_int < args.model_max:
        models_to_test.append(m_path)
        model_ints_to_test.append(m_int)
        model_int_i_to_test.append(m_int_i)

env = None

for m_int_i, m_path, m_int in zip(model_int_i_to_test, models_to_test, model_ints_to_test):
    if not args.no_save:
        # check where we are in testing
        valid_eval = train_file_dict['valid_eval'][m_int][args.aux_task]
        if np.all(valid_eval):
            print(f"All eval complete for {m_path}, moving on to next")
            continue
    else:
        valid_eval = [False]

    if env is None:
        config, env, buffer_preprocessing, agent = load_model(args.eval_seed, config_path, m_path, args.aux_task,
                                                            args.device, include_disc=False)
    else:
        config, buffer_preprocessing, agent = load_model(args.eval_seed, config_path, m_path, args.aux_task,
                                        args.device, include_env=False, include_disc=False)
    
    env.unwrapped._max_episode_steps = args.max_ep_steps

    aux_rew, aux_suc = get_aux_rew_aux_suc(config, env)

    if hasattr(agent, 'high_level_model'):
        agent.high_level_model = FixedScheduler(args.aux_task, num_aux_tasks)

    if not np.any(valid_eval):
        first_ep = 0
    else:
        first_ep = valid_eval.nonzero()[0][-1] + 1

    if first_ep == 0:
        env.seed(args.eval_seed)

    for ep_i in range(first_ep, args.num_eval_eps):
        print(f"Starting evaluation of aux task {args.aux_task}, model {m_int}, ep {ep_i}")
        rets, _, all_suc = evaluate_policy(agent=agent,
                                           env=env,
                                           buffer_preprocess=buffer_preprocessing,
                                           num_episodes=1,
                                           clip_action=config[c.CLIP_ACTION],
                                           min_action=config[c.MIN_ACTION],
                                           max_action=config[c.MAX_ACTION],
                                           render=False,
                                           auxiliary_reward=aux_rew,
                                           auxiliary_success=aux_suc,
                                           verbose=True,
                                           forced_schedule=forced_schedule,
                                           stochastic_policy=args.stochastic)

        if not args.no_save:
            train_file_dict['valid_eval'][m_int][args.aux_task][ep_i] = 1

            ep_i_in_full_array = args.aux_task * args.num_eval_eps + ep_i
            train_file_dict['evaluation_successes_all_tasks'][m_int_i][:, ep_i_in_full_array] = all_suc.flatten()
            train_file_dict['evaluation_returns'][m_int_i][:, ep_i_in_full_array] = rets.flatten()
        
            rng_state_dict = get_rng_state()
            for rng_k, rng_v in rng_state_dict.items():
                train_file_dict[f"eval_{rng_k}"] = rng_v

            safe_save_train_dict(train_file_dict, train_file_path)

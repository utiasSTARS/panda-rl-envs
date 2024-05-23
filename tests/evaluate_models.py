import argparse
import os
import glob
import pickle
from ast import literal_eval

import numpy as np

from rl_sandbox.examples.eval_tools.utils import load_model
from rl_sandbox.examples.eval_tools.evaluate import evaluate
from rl_sandbox.learning_utils import evaluate_policy
import rl_sandbox.constants as c
from rl_sandbox.algorithms.sac_x.schedulers import FixedScheduler


def safe_save_train_dict(train_dict, path):
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
args = parser.parse_args()


# overwrite the train.pkl file in the experiment directory with a dictionary that contains:
# - the values that are already in the train.pkl file (i.e. only append, don't delete)
# - evaluation_successes_all_tasks: a list for each eval checkpoint, with each entry containing a
#   (num_tasks, num_tasks * num_eval_eps) np array with 1s and 0s for success
# - evaluation_returns: same, but for returns instead of success
# - when this script is run, immediately generate a list of length of number of saved models in this directory,
#   but initially populated with None so we know which are invalid
# - add valid_eval parameter to dict, dict corresponding to each model to determine what is valid


# TODO multitask not handled here yet
forced_schedule = None if args.forced_schedule == "" else literal_eval(args.forced_schedule)

if 'multi' in args.algo:
    config_file = 'dac_experiment_setting.pkl'
else:
    config_file = 'lfgp_experiment_setting.pkl'
exp_path = os.path.join(args.top_save_path, args.env_name, args.model_seed, args.algo, args.exp_name)
all_exps = glob.glob(os.path.join(exp_path, '*'))
if len(all_exps) == 0:
    raise ValueError(f"No folders found in {exp_path}")
main_model_path = sorted(all_exps)[-1]
if len(all_exps) > 1:
    print(f"Multiple folders found, using {main_model_path}")
config_path = os.path.join(main_model_path, config_file)

model_paths = sorted(glob.glob(os.path.join(main_model_path, '*0.pt')))
model_ints = [int(m.split('/')[-1].split('.pt')[0]) for m in model_paths]

# get number of valid aux tasks from one ex model
config, _, _, _ = load_model(0, config_path, model_paths[0], args.aux_task,
                                                      args.device, include_disc=False, force_egl=False)
num_aux_tasks = config[c.NUM_TASKS]

train_file_path = os.path.join(main_model_path, 'train.pkl')
train_file_dict = pickle.load(open(train_file_path, 'rb'))
if 'valid_eval' not in train_file_dict:
    train_file_dict['valid_eval'] = {}
if 'evaluation_successes_all_tasks' not in train_file_dict:
    train_file_dict['evaluation_successes_all_tasks'] = [] * len(model_paths)
if 'evaluation_returns' not in train_file_dict:
    train_file_dict['evaluation_returns'] = [] * len(model_paths)
for m_int_i, m_int in enumerate(model_ints):
    if m_int not in train_file_dict['valid_eval']:
        train_file_dict['valid_eval'][m_int] = np.zeros(num_aux_tasks, num_aux_tasks * args.num_eval_eps)
        train_file_dict['evaluation_successes_all_tasks'][m_int_i] = np.zeros(num_aux_tasks, num_aux_tasks * args.num_eval_eps)
        train_file_dict['evaluation_returns'][m_int_i] = np.zeros(num_aux_tasks, num_aux_tasks * args.num_eval_eps)
safe_save_train_dict(train_file_dict, train_file_path)

models_to_test = []
for m_path, m_int in zip(model_paths, model_ints):
    if args.model_min < m_int < args.model_max:
        models_to_test.append(m_path)

for m_path in models_to_test:
    config, env, buffer_preprocessing, agent = load_model(args.eval_seed, config_path, m_path, args.intention,
                                                        args.device, include_disc=False, force_egl=args.force_egl)

    if hasattr(agent, 'high_level_model'):
        agent.high_level_model = FixedScheduler(args.aux_task, num_aux_tasks)




# python ../../../rl_sandbox/rl_sandbox/examples/eval_tools/evaluate.py \
# --seed="${SEED}" \
# --model_path="${MODEL_PATH}" \
# --config_path="${CONFIG_PATH}" \
# --num_episodes="${NUM_EPISODES}" \
# --intention="${INTENTION}" \
# --model_path="${MODEL_PATH}" \
# --forced_schedule="${FORCED_SCHEDULE}" \
# --force_egl \
# --render \
# --render_substeps
import argparse
import os

import numpy as np

from rl_sandbox.buffers.utils import get_default_buffer
import rl_sandbox.constants as c
from panda_rl_envs import *


parser = argparse.ArgumentParser()
parser.add_argument('--env', type=str, default='SimPandaReach')
parser.add_argument('--num_ex', type=int, default=1200)
parser.add_argument('--aux_tasks', type=str, default="")
parser.add_argument('--no_save', action='store_true')
args = parser.parse_args()


env = globals()[args.env]()
if hasattr(env, 'get_aux_suc_examples'):
    if args.aux_tasks != "":
        suc_ex_dict = env.get_aux_suc_examples(args.num_ex, tasks=args.aux_tasks.split(','))
    else:
        suc_ex_dict = env.get_aux_suc_examples(args.num_ex)
else:
    suc_ex_dict = {'main': env.get_suc_examples(args.num_ex)}

for t, suc_ex in suc_ex_dict.items():
    (memory_size, obs_dim) = suc_ex.shape
    action_dim = env.action_space.shape[0]

    buffer = get_default_buffer(memory_size, obs_dim, action_dim)

    for obs in suc_ex:
        info = {c.DISCOUNTING: 1}
        buffer.push(obs, np.zeros(1), np.zeros(action_dim), 0., True, info, next_obs=obs, next_h_state=np.zeros(1))

    if not args.no_save:
        os.makedirs('data', exist_ok=True)

        buf_str_post = "" if t == "main" else f"_{t}"
        buffer.save(f"data/{args.env}{buf_str_post}.gz", end_with_done=False)
import argparse
import os

import numpy as np

from rl_sandbox.buffers.utils import get_default_buffer
import rl_sandbox.constants as c
from panda_rl_envs import *


parser = argparse.ArgumentParser()
parser.add_argument('--env', type=str, default='SimPandaReach')
parser.add_argument('--num_ex', type=int, default=1200)
args = parser.parse_args()


env = globals()[args.env]()
suc_ex = env.get_suc_examples(args.num_ex)
(memory_size, obs_dim) = suc_ex.shape
action_dim = env.action_space.shape[0]

buffer = get_default_buffer(memory_size, obs_dim, action_dim)

for obs in suc_ex:
    info = {c.DISCOUNTING: 1}
    buffer.push(obs, np.zeros(1), np.zeros(action_dim), 0., True, info, next_obs=obs, next_h_state=np.zeros(1))

os.makedirs('data', exist_ok=True)
buffer.save(f"data/{args.env}.gz", end_with_done=False)
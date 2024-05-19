import time
import argparse

import numpy as np

# from panda_rl_envs.panda_env import PandaExploreEnv
from panda_rl_envs import *


parser = argparse.ArgumentParser()
parser.add_argument('--ep_len', type=float, default=10, help="Ep length in seconds")
parser.add_argument('--max_trans_vel', type=float, default=.2, help="m/s")
parser.add_argument('--max_rot_vel', type=float, default=.4, help="rad/s")
parser.add_argument('--sim', action='store_true')
args = parser.parse_args()


config_dict = {
    'max_trans_vel': args.max_trans_vel,
    'max_rot_vel': args.max_rot_vel,
}

if args.sim:
    env = SimPandaExploreEnv(config_dict=config_dict)
else:
    env = PandaExploreEnv(config_dict=config_dict)

num_steps = round(args.ep_len * env.cfg['control_hz'])

obs = env.reset()

start_time = time.time()

for i in range(num_steps):
    # action = np.random.uniform(low=-np.ones(3), high=np.ones(3), size=3)
    action = env.action_space.sample()
    obs, env.step(action)

    if (i + 1) % 10 == 0:
        print(f"Ep at {i + 1}/{num_steps}")
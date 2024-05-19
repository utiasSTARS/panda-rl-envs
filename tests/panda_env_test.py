import time
import argparse

import numpy as np
from gym.wrappers.time_limit import TimeLimit

# from panda_rl_envs.panda_env import PandaExploreEnv
from panda_rl_envs import *


parser = argparse.ArgumentParser()
parser.add_argument('--ep_len', type=float, default=10, help="Ep length in seconds")
parser.add_argument('--max_trans_vel', type=float, default=.2, help="m/s")
parser.add_argument('--max_rot_vel', type=float, default=.4, help="rad/s")
parser.add_argument('--sim', action='store_true')
args = parser.parse_args()


config_dict = {
    'max_real_time': args.ep_len,
    'max_trans_vel': args.max_trans_vel,
    'max_rot_vel': args.max_rot_vel,
}

if args.sim:
    env = SimPandaEnv(config_dict=config_dict)
else:
    env = PandaEnv(config_dict=config_dict)

done = False
obs = env.reset()
while not done:
    action = env.action_space.sample()
    obs, rew, done, info = env.step(action)

    if (env._elapsed_steps + 1) % 10 == 0:
        print(f"Ep at {env._elapsed_steps + 1}/{env._max_episode_steps}")
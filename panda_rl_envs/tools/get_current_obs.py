import argparse

import numpy as np

# from panda_rl_envs.panda_env import PandaExploreEnv
from panda_rl_envs import *


parser = argparse.ArgumentParser()
parser.add_argument('--env', type=str, default="SimPandaReach")
parser.add_argument('--precision', type=int, default=5)
args = parser.parse_args()

env = globals()[args.env]()
obs, obs_dict = env.prepare_obs()

np.set_printoptions(suppress=True, precision=args.precision)

print(f"obs_dict: {obs_dict}")
print(f"obs: {obs}")
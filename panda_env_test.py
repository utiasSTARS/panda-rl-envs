import time
import argparse

import numpy as np

from panda_env import PandaExploreEnv

parser = argparse.ArgumentParser()
parser.add_argument('--ep_len', type=float, default=10, help="Ep length in seconds")
parser.add_argument('--max_trans_vel', type=float, default=.1, help="m/s")
parser.add_argument('--max_rot_vel', type=float, default=.2, help="rad/s")
args = parser.parse_args()

env = PandaExploreEnv(config_dict=
                      {'max_trans_vel': args.max_trans_vel,
                       'max_rot_vel': args.max_rot_vel,
                       })

num_steps = round(args.ep_len * env.cfg['control_hz'])

obs = env.reset()

start_time = time.time()

for i in range(num_steps):
    action = np.random.uniform(low=-np.ones(3), high=np.ones(3), size=3)
    env.step(action)

    if (i + 1) % 10 == 0:
        print(f"Ep at {i + 1}/{num_steps}")
import time
import argparse
import copy

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
    env = SimPandaReach(config_dict=config_dict)
else:
    env = PandaReach(config_dict=config_dict)

done = False
rets = [0, 0]
obs = env.reset()
print("Environment reset complete, starting actions in 2s!")
init_pose = env.arm_client.EE_pose
suc_reach_pose = copy.deepcopy(init_pose)
suc_reach_pose.set_pos(np.array(env.cfg['reach_goal']))
# suc_reach_pose.set_pos(np.array(env.cfg['aux_reach_goal']))
time.sleep(2)
while not done:
    # action = env.action_space.sample()
    # obs, rew, done, info = env.step(action)

    if env._elapsed_steps == 2:
        print("Moving arm to correct reach position manually!")
        env.arm_client.move_EE_to(suc_reach_pose)
        env.arm_client.reset_target_pose(suc_reach_pose)
        env.arm_client.start_controller()

    obs, rew, done, info = env.step(np.zeros(env.action_space.shape))

    # ret += rew
    rews = env.get_aux_rew(info)
    for ret_i in range(len(rets)):
        rets[ret_i] += rews[ret_i]

    sucs = env.get_task_successes(info)

    # if (env._elapsed_steps) % 10 == 0:
    #     # print(f"Ep at {env._elapsed_steps}/{env._max_episode_steps}, ret: {ret}, suc: {info['suc']}")
    #     print(f"Ep at {env._elapsed_steps}/{env._max_episode_steps}, all ret: {rets}, all suc: {sucs}")
    print(f"Ep at {env._elapsed_steps}/{env._max_episode_steps}, all ret: {rets}, all suc: {sucs}")
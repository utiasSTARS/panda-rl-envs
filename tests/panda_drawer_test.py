import time
import argparse
import copy

import numpy as np
from gym.wrappers.time_limit import TimeLimit

# from panda_rl_envs.panda_env import PandaExploreEnv
from panda_rl_envs import *


parser = argparse.ArgumentParser()
parser.add_argument('--sim', action='store_true')
parser.add_argument('--task', type=str, default='reach')
args = parser.parse_args()

if args.sim:
    raise NotImplementedError()
else:
    env = PandaDrawer()

done = False
rets = [0, 0, 0]
obs = env.reset()
print("Environment reset complete, starting actions in 2s!")
init_pose = env.arm_client.EE_pose
suc_pose = copy.deepcopy(init_pose)
suc_pose.set_pos(np.array(
    [env.cfg[f'{args.task}_suc_pos'][0], init_pose.pose.position.y, env.cfg[f'{args.task}_suc_pos'][1]]))
time.sleep(2)
while not done:
    # action = env.action_space.sample()
    # obs, rew, done, info = env.step(action)

    if env._elapsed_steps == 2:
        print("Moving arm to correct reach position manually!")
        env.arm_client.move_EE_to(suc_pose)
        env.arm_client.reset_target_pose(suc_pose)
        env.arm_client.start_controller()
        if args.task == 'grasp':
            env.grip_client.close()

    act = np.zeros(env.action_space.shape)
    if args.task == 'grasp' and env._elapsed_steps >= 2:
        act[-1] = 1.0

    obs, rew, done, info = env.step(act)

    # ret += rew
    rews = env.get_aux_rew(info)
    for ret_i in range(len(rets)):
        rets[ret_i] += rews[ret_i]

    sucs = env.get_task_successes(info)

    # if (env._elapsed_steps) % 10 == 0:
    #     # print(f"Ep at {env._elapsed_steps}/{env._max_episode_steps}, ret: {ret}, suc: {info['suc']}")
    #     print(f"Ep at {env._elapsed_steps}/{env._max_episode_steps}, all ret: {rets}, all suc: {sucs}")
    print(f"Ep at {env._elapsed_steps}/{env._max_episode_steps}, all ret: {rets}, all suc: {sucs}")
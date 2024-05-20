import pathlib
import os

import numpy as np

from panda_rl_envs import PandaEnv, SimPandaEnv


class PandaReach(PandaEnv):
    def __init__(self, config_dict={}, config_file=None):
        super.__init__(config_dict, config_file)

        print("!!!!! CHANGE THIS REACH GOAL IF USING REAL ROBOT !!!!")
        self.reach_goal = np.array([.5, -.1, .3])  # TODO overwrite with one for real world

    def get_rew(self, obs_dict, prev_obs_dict, act):
        prev_dist = np.linalg.norm(prev_obs_dict['pose'][:3] - self.reach_goal)
        dist = np.linalg.norm(obs_dict['pose'][:3] - self.reach_goal)
        return prev_dist - dist

    def get_suc(self, obs_dict, prev_obs_dict, act):
        # TODO Continue here!!!

        return False


class SimPandaReach(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_panda_reach.yaml')
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)

        self.reach_goal = np.array([.5, -.1, .3])
import pathlib
import os

import numpy as np

from panda_rl_envs import PandaEnv, SimPandaEnv


class PandaReach(PandaEnv):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'panda_reach.yaml')
        super().__init__(config_dict, config_file)
        self.cfg['reach_goal'] = np.array(self.cfg['reach_goal'])
        self._reach_suc_ts_thresh = int(np.ceil(self.cfg['reach_suc_time_thresh'] / self._real_time_step))
        self._reached_ts = 0

    def get_rew(self, obs_dict, prev_obs_dict, act):
        prev_dist = np.linalg.norm(prev_obs_dict['pose'][:3] - self.cfg['reach_goal'])
        dist = np.linalg.norm(obs_dict['pose'][:3] - self.cfg['reach_goal'])
        return prev_dist - dist

    def get_suc(self, obs_dict, prev_obs_dict, act):
        reached = np.linalg.norm(obs_dict['pose'][:3] - self.cfg['reach_goal']) <= self.cfg['reach_suc_thresh']
        if reached:
            self._reached_ts += 1
        else:
            self._reached_ts = 0
        if self._reached_ts >= self._reach_suc_ts_thresh:
            self._suc_latch = True
        return self._suc_latch

    def get_suc_examples(self, num_ex):
        # assuming suc thresh of 1, max dist of suc ex will be sqrt(3) / 3 = 0.577 < 1
        max_dist = self.cfg['reach_suc_thresh'] / 3
        suc_ex = self.cfg['reach_goal'] + \
            np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, self.observation_space.shape[0]))
        return suc_ex


class SimPandaReach(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_panda_reach.yaml')
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
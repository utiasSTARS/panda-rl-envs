import pathlib
import os

import numpy as np

from panda_rl_envs import PandaEnv
import panda_rl_envs.reward_utils as reward_utils


class PandaReach(PandaEnv):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'panda_reach.yaml')
        super().__init__(config_dict, config_file)
        self.cfg['reach_goal'] = np.array(self.cfg['reach_goal'])
        self.cfg['aux_reach_goal'] = np.array(self.cfg['aux_reach_goal'])

    def get_rew(self, obs_dict, prev_obs_dict, act, goal_str='reach_goal'):
        if 'pose' in self.cfg['state_data']:
            return reward_utils.generic_reach_rew(obs_dict['pose'][:3], prev_obs_dict['pose'][:3], self.cfg[goal_str])
        elif 'pos_obj_diff' in self.cfg['state_data']:
            return reward_utils.diff_reach_rew(obs_dict[f'pos_{goal_str}_diff'], prev_obs_dict[f'pos_{goal_str}_diff'])
        else:
            raise NotImplementedError()

    def get_suc(self, obs_dict, prev_obs_dict, act, goal_str='reach_goal'):
        if 'pose' in self.cfg['state_data']:
            reached = np.linalg.norm(obs_dict['pose'][:3] - self.cfg[goal_str]) <= self.cfg['reach_suc_thresh']
        elif 'pos_obj_diff' in self.cfg['state_data']:
            reached = np.linalg.norm(obs_dict[f'pos_{goal_str}_diff']) <= self.cfg['reach_suc_thresh']
        else:
            raise NotImplementedError()
        return self._suc_timer.update_and_get_suc(reached, self._elapsed_steps)

    def get_suc_examples(self, num_ex):
        # assuming suc thresh of 1, max dist of suc ex will be sqrt(3) / 3 = 0.577 < 1
        max_dist = self.cfg['reach_suc_thresh'] / 3
        if self.cfg['state_data'] == ['pose']:
            return self.cfg['reach_goal'] + \
                np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, self.observation_space.shape[0]))
        elif self.cfg['state_data'] == ['pos_obj_diff'] and self.cfg['num_objs'] == 2:
            # now includes both regular and aux diff
            suc_reach_diff = np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, sum(self.cfg['valid_dof'][:3])))
            other_reach_diff = self.cfg['reach_goal'] - self.cfg['aux_reach_goal'] + \
                np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, sum(self.cfg['valid_dof'][:3])))
            return np.hstack([suc_reach_diff, other_reach_diff])
        else:
            raise NotImplementedError()

    def prepare_obs(self):
        # first need to get obj pose for _obj_poses dict
        self._obj_poses['reach_goal'] = self.cfg['reach_goal']
        self._obj_poses['aux_reach_goal'] = self.cfg['aux_reach_goal']

        return super().prepare_obs()

    def get_aux_rew(self, obs_dict, prev_obs_dict, act, tasks=('main', 'reach')):
        rews = []
        for t in tasks:
            if t == 'main':
                rews.append(self.get_rew(obs_dict, prev_obs_dict, act))
            elif t == 'reach':
                rews.append(self.get_rew(obs_dict, prev_obs_dict, goal_str='aux_reach_goal'))
            else:
                raise NotImplementedError(f"get_aux_rew not defined for task {t}")

        return rews

    def get_aux_suc(self, obs_dict, prev_obs_dict, act, tasks=('main', 'reach')):
        sucs = []

        if not hasattr(self, '_aux_suc_timers'):
            self._aux_suc_timers = dict()

        for t in tasks:
            if t == 'main':
                sucs.append(self.get_suc(obs_dict, prev_obs_dict, act))
            else:
                suc_bool = False
                if t == 'reach':
                    suc_bool = np.linalg.norm(obs_dict['pose'][:3] - self.cfg['aux_real_goal']) \
                        <= self.cfg['reach_suc_thresh']
                else:
                    raise NotImplementedError(f"get_aux_suc not defined for task {t}")

                if t not in self._aux_suc_timers:
                    self._aux_suc_timers[t] = reward_utils.HoldTimer(self._real_time_step, self.cfg['suc_time_thresh'])
                sucs.append(self._aux_suc_timers[t].update_and_get_suc(suc_bool, self._elapsed_steps))

        return sucs

    def get_aux_suc_examples(self, num_ex, tasks=('main', 'reach')):
        suc_ex_dict = dict()
        for t in tasks:
            if t == 'main':
                suc_ex_dict['main'] = self.get_suc_examples()
            elif t == 'reach':
                max_dist = self.cfg['reach_suc_thresh'] / 3
                suc_ex_dict['reach'] = self.cfg['aux_reach_goal'] + \
                    np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, self.observation_space.shape[0]))
        import ipdb; ipdb.set_trace()


class SimPandaReach(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_panda_reach.yaml')
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
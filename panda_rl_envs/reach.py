import pathlib
import os

import numpy as np

from panda_rl_envs import PandaEnv
import panda_rl_envs.reward_utils as reward_utils


class PandaReach(PandaEnv):
    VALID_AUX_TASKS=('main', 'reach')
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            raise NotImplementedError(f"Redo reach limits, poses, etc. for new cabinet position!")
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'reach.yaml')
        super().__init__(config_dict, config_file)
        self.cfg['reach_goal'] = np.array(self.cfg['reach_goal'])
        self.cfg['aux_reach_goal'] = np.array(self.cfg['aux_reach_goal'])

    def get_rew(self, obs_dict, prev_obs_dict, action, goal_str='reach_goal'):
        if 'pose' in self.cfg['state_data']:
            return reward_utils.generic_reach_rew(obs_dict['pose'][:3], prev_obs_dict['pose'][:3], self.cfg[goal_str])
        elif 'pos_obj_diff' in self.cfg['state_data']:
            return reward_utils.diff_reach_rew(obs_dict[f'pos_{goal_str}_diff'], prev_obs_dict[f'pos_{goal_str}_diff'])
        else:
            raise NotImplementedError()

    def get_suc(self, obs_dict, prev_obs_dict, action, goal_str='reach_goal', specific_timer=None):
        if specific_timer is None:
            specific_timer = self._suc_timer
        if 'pose' in self.cfg['state_data']:
            reached = np.linalg.norm(obs_dict['pose'][:3] - self.cfg[goal_str]) <= self.cfg['reach_suc_thresh']
        elif 'pos_obj_diff' in self.cfg['state_data']:
            reached = np.linalg.norm(obs_dict[f'pos_{goal_str}_diff']) <= self.cfg['reach_suc_thresh']
        else:
            raise NotImplementedError()
        return specific_timer.update_and_get_suc(reached, self._elapsed_steps)

    def get_suc_examples(self, num_ex, goal_str='reach_goal'):
        # assuming suc thresh of 1, max dist of suc ex will be sqrt(3) / 3 = 0.577 < 1
        max_dist = self.cfg['reach_suc_thresh'] / 3
        if self.cfg['state_data'] == ['pose']:
            return self.cfg[goal_str] + \
                np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, self.observation_space.shape[0]))
        elif self.cfg['state_data'] == ['pos_obj_diff'] and self.cfg['num_objs'] == 2:
            # now includes both regular and aux diff
            other_goal_str = 'aux_reach_goal' if goal_str =='reach_goal' else 'reach_goal'
            suc_reach_diff = np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, sum(self.cfg['valid_dof'][:3])))
            other_reach_diff = self.cfg[goal_str] - self.cfg[other_goal_str] + \
                np.random.uniform(low=-max_dist, high=max_dist, size=(num_ex, sum(self.cfg['valid_dof'][:3])))
            if goal_str == 'reach_goal':
                return np.hstack([suc_reach_diff, other_reach_diff])
            else:
                return np.hstack([other_reach_diff, suc_reach_diff])
        else:
            raise NotImplementedError()

    def prepare_obs(self):
        # first need to get obj pose for _obj_poses dict
        self._obj_poses['reach_goal'] = self.cfg['reach_goal']
        self._obj_poses['aux_reach_goal'] = self.cfg['aux_reach_goal']

        return super().prepare_obs()

    def get_aux_rew(self, info, tasks=VALID_AUX_TASKS, **kwargs):
        obs_dict = info['obs_dict']
        prev_obs_dict = info['prev_obs_dict']
        rews = []
        for t in tasks:
            if t == 'main':
                rews.append(self.get_rew(obs_dict, prev_obs_dict, None))
            elif t == 'reach':
                rews.append(self.get_rew(obs_dict, prev_obs_dict, None, goal_str='aux_reach_goal'))
            else:
                raise NotImplementedError(f"get_aux_rew not defined for task {t}")

        return rews if len(rews) > 1 else rews[0]

    def get_task_successes(self, env_info, tasks=VALID_AUX_TASKS, **kwargs):
        obs_dict = env_info['obs_dict']
        prev_obs_dict = env_info['prev_obs_dict']
        sucs = []

        if not hasattr(self, '_aux_suc_timers'):
            self._aux_suc_timers = dict()

        for t in tasks:
            if t == 'main':
                sucs.append(self.get_suc(obs_dict, prev_obs_dict, None))
            else:
                suc_bool = False
                if t not in self._aux_suc_timers:
                    self._aux_suc_timers[t] = reward_utils.HoldTimer(self._real_time_step, self.cfg['suc_time_thresh'])
                if t == 'reach':
                    suc_bool = self.get_suc(obs_dict, prev_obs_dict, None,
                                            goal_str='aux_reach_goal', specific_timer=self._aux_suc_timers[t])
                else:
                    raise NotImplementedError(f"get_aux_suc not defined for task {t}")

                sucs.append(suc_bool)

        return sucs

    def get_aux_suc_examples(self, num_ex, tasks=VALID_AUX_TASKS):
        suc_ex_dict = dict()
        for t in tasks:
            if t == 'main':
                suc_ex_dict['main'] = self.get_suc_examples(num_ex)
            elif t == 'reach':
                suc_ex_dict['reach'] = self.get_suc_examples(num_ex, goal_str='aux_reach_goal')
        return suc_ex_dict


class SimPandaReach(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_panda_reach.yaml')
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)


class SimPandaReachRandInit(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_panda_reach.yaml')
        config_dict['server_ip'] = 'localhost'

        # reset_pose: [0.5284425, -0.09963877, 0.436256, -3.075285, -0.006185998, 0.6868039]
        # pos_limits: [[0.6, 0.15, 0.5], [0.3, -0.15, 0.3]]
        config_dict['init_ee_high_lim'] = [0.55, -0.05, 0.45, -3.075285, -0.006185998, 0.6868039]
        config_dict['init_ee_low_lim'] = [0.45, -0.15, 0.35, -3.075285, -0.006185998, 0.6868039]
        # config_dict['init_ee_random_lim'] = [.05, .05, .05, 0.0, 0.0, 0.0]

        super().__init__(config_dict=config_dict, config_file=config_file)


class SimPandaReachAbs(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_reach.yaml')
        config_dict['server_ip'] = 'localhost'
        config_dict['state_data'] = ['pose']
        config_dict['num_objs'] = 0
        super().__init__(config_dict=config_dict, config_file=config_file)
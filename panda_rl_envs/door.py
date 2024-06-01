import pathlib
import os
import copy

import numpy as np

from panda_rl_envs import PandaEnv
import panda_rl_envs.reward_utils as reward_utils
from transform_utils.pose_transforms import PoseTransformer


class PandaDoor(PandaEnv):
    VALID_AUX_TASKS=('main', 'reach', 'grasp')
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'door.yaml')
        super().__init__(config_dict, config_file)

    def get_rew(self, obs_dict, prev_obs_dict, action, task='main'):
        if 'pos_obj_diff' in self.cfg['state_data']:
            reach_rew = reward_utils.diff_reach_rew(obs_dict['pos_handle_diff'], prev_obs_dict['pos_handle_diff'])
        else:
            if task in ['reach', 'grasp']:
                reach_rew = reward_utils.generic_reach_rew(obs_dict['pose'], prev_obs_dict['pose'], self.cfg['reach_suc_pos'])
            else:
                reach_rew = 0
        if task == 'reach':
            return reach_rew

        grasp_rew = reward_utils.generic_reach_rew(obs_dict['grip_pos'], prev_obs_dict['grip_pos'], self.cfg['grasp_grip_pos'])
        if task == 'grasp':
            return reach_rew + grasp_rew

        door_rew = reward_utils.generic_reach_rew(obs_dict['handle_pose'], prev_obs_dict['handle_pose'], self.cfg['open_pos'])

        return reach_rew + door_rew

    def get_suc(self, obs_dict, prev_obs_dict, action, task='main', specific_timer=None):
        if specific_timer is None:
            specific_timer = self._suc_timer

        if task == 'main':
            suc = np.linalg.norm(obs_dict['handle_pose'] - self.cfg['open_pos']) <= self.cfg['main_suc_thresh']
        elif task in ['reach', 'grasp']:
            if 'pos_obj_diff' in self.cfg['state_data']:
                suc = np.linalg.norm(obs_dict['pos_handle_diff']) <= self.cfg['reach_suc_thresh']
            else:
                suc = np.linalg.norm(obs_dict['pose'] - self.cfg['reach_suc_pos']) <= self.cfg['reach_suc_thresh']
            if task == 'grasp':
                suc = suc and np.linalg.norm(obs_dict['grip_pos'] - self.cfg['grasp_grip_pos']) \
                    <= self.cfg['grasp_reach_suc_thresh']
        else:
            raise NotImplementedError()

        return specific_timer.update_and_get_suc(suc, self._elapsed_steps)

    def get_suc_examples(self, num_ex, task='main', rand_act_scaler=0.5):
        print(f"Press enter to move robot directly to master position for {task}.")

        dof_coord_dict = {0: 'x', 1: 'y', 2: 'z'}
        valid_dof = self.cfg['valid_dof'][:3].nonzero()[0]
        assert len(valid_dof) == len(self.cfg[f'{task}_suc_pos'])
        assert len(valid_dof) == len(self.cfg[f'{task}_suc_rand'])

        input()
        self.grip_client.open(blocking=True, timeout=5.0)
        pose = copy.deepcopy(self._reset_base_tool_pose)
        for dof_i, dof in enumerate(valid_dof):
            setattr(pose.pose.position, dof_coord_dict[dof], self.cfg[f'{task}_suc_pos'][dof_i])
        # pose.pose.position.x = self.cfg[f'{task}_suc_pos'][0]
        # pose.pose.position.y = self.cfg[f'{task}_suc_pos'][1]

        self.arm_client.move_EE_to(pose)

        if task == 'grasp':
            self.grip_client.close()

        print(f"Press enter again to begin collecting samples.")
        if task == 'main':
            print(f"For main task, move drawer to open pos and consider slightly moving it during ep!")
        input()
        self.arm_client.start_controller()

        orig_pos_limits = copy.deepcopy(self.arm_client._pos_limits)

        for dof_i, dof in enumerate(valid_dof):
            # upper limit   
            self.arm_client._pos_limits[0][dof] = getattr(pose.pose.position, dof_coord_dict[dof]) + \
                self.cfg[f'{task}_suc_rand'][dof_i]
            # lower limit
            self.arm_client._pos_limits[1][dof] = getattr(pose.pose.position, dof_coord_dict[dof]) - \
                self.cfg[f'{task}_suc_rand'][dof_i]

        # self.arm_client._pos_limits[0, 0] = pose.pose.position.x + self.cfg[f'{task}_suc_rand'][0]
        # self.arm_client._pos_limits[1, 0] = pose.pose.position.x - self.cfg[f'{task}_suc_rand'][0]
        # self.arm_client._pos_limits[0, 1] = pose.pose.position.y + self.cfg[f'{task}_suc_rand'][1]
        # self.arm_client._pos_limits[1, 1] = pose.pose.position.y - self.cfg[f'{task}_suc_rand'][1]

        suc_obs = []
        for i in range(num_ex):
            rand_act = self.action_space.sample() * rand_act_scaler
            if task == 'grasp':
                rand_act[-1] = 1.0
            else:
                rand_act[-1] = -1.0
            obs, _, _, _ = self.step(rand_act)
            suc_obs.append(obs)
            if i % 5 == 0:
                print(f"Collected {i+1}/{num_ex} success examples.")

        self.arm_client._pos_limits = orig_pos_limits

        return np.stack(suc_obs)

    # def prepare_obs(self):
    #     # # first need to get obj pose for _obj_poses dict
    #     # self._obj_poses['reach_goal'] = self.cfg['reach_goal']
    #     # self._obj_poses['aux_reach_goal'] = self.cfg['aux_reach_goal']

    #     return super().prepare_obs()

    def get_aux_rew(self, info, tasks=VALID_AUX_TASKS, **kwargs):
        obs_dict = info['obs_dict']
        prev_obs_dict = info['prev_obs_dict']
        rews = []
        for t in tasks:
            rews.append(self.get_rew(obs_dict, prev_obs_dict, None, task=t))

        return rews if len(rews) > 1 else rews[0]

    def get_task_successes(self, env_info, tasks=VALID_AUX_TASKS, **kwargs):
        obs_dict = env_info['obs_dict']
        prev_obs_dict = env_info['prev_obs_dict']
        sucs = []

        if not hasattr(self, '_aux_suc_timers'):
            self._aux_suc_timers = dict()

        for t in tasks:
            if t not in self._aux_suc_timers:
                self._aux_suc_timers[t] = reward_utils.HoldTimer(self._real_time_step, self.cfg['suc_time_thresh'])
            sucs.append(self.get_suc(obs_dict, prev_obs_dict, None, task=t, specific_timer=self._aux_suc_timers[t]))

        return sucs

    def get_aux_suc_examples(self, num_ex, tasks=VALID_AUX_TASKS, rand_act_scaler=0.5):
        suc_ex_dict = dict()
        for t in tasks:
            suc_ex_dict[t] = self.get_suc_examples(num_ex, task=t, rand_act_scaler=rand_act_scaler)
        return suc_ex_dict


class SimPandaDoor(PandaDoor):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_door.yaml')
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
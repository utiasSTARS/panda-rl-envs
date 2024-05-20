import copy
import time
import os
import pathlib

import numpy as np
import yaml
import gym
from gym import spaces

import panda_polymetis
from panda_polymetis.utils.poses import geodesic_error
from panda_polymetis.utils.rate import Rate
from panda_polymetis.control.panda_client import PandaClient
from panda_polymetis.control.panda_gripper_client import PandaGripperClient
from transform_utils.pose_transforms import (
    PoseTransformer,
    pose2array,
    matrix2pose,
)

class PandaEnv(gym.Env):
    def __init__(self, config_dict={}, config_file=None):

        self.cfg = {}

        # load defaults from default file first
        def_config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'panda_env_defaults.yaml')
        with open(def_config_file) as f:
            self.cfg.update(yaml.load(f, Loader=yaml.FullLoader))

        # override by config file
        if config_file is not None:
            with open(config_file) as f:
                self.cfg.update(yaml.load(f, Loader=yaml.FullLoader))

        # override all with config_dict
        self.cfg.update(config_dict)

        self.arm_client = PandaClient(
            server_ip=self.cfg['server_ip'],
            delta_pos_limit=self.cfg['max_trans_vel'] / self.cfg['control_hz'],
            delta_rot_limit=self.cfg['max_rot_vel'] / self.cfg['control_hz'],
            home_joints=self.cfg['reset_joints'],
            only_positive_ee_quat=self.cfg['only_positive_ee_quat'],
            ee_config_json=self.cfg['ee_config_json'],
            sim=self.cfg['server_ip'] == 'localhost'
        )

        # task
        self._max_episode_steps = round(self.cfg['max_real_time'] * self.cfg['control_hz'])
        self._elapsed_steps = 0
        self._prev_obs = None  # for reward/suc calc
        self._prev_obs_dict = None  # for reward/suc calc
        self._real_time_step = 1 / self.cfg['control_hz']
        self._suc_latch = False

        # reset
        self.arm_client.get_and_update_state()
        self.cfg['reset_pose'] = self.cfg['reset_pose'] if self.cfg['reset_pose'] is not None else\
            self.arm_client.EE_pose.get_array_euler(axes='sxyz')
        self._reset_base_tool_tf_arr = np.array(self.cfg['reset_pose'])
        self._reset_base_tool_pose = PoseTransformer(self._reset_base_tool_tf_arr, 'euler', axes='sxyz')
        self._reset_base_tool_pose.header.frame_id = "panda_link0"

        # control
        self.rate = Rate(self.cfg['control_hz'])
        self._max_trans_vel_norm = np.linalg.norm(np.ones(3))
        self._max_rot_vel_norm = np.linalg.norm(np.ones(3))
        self.cfg['valid_dof'] = np.array(self.cfg['valid_dof'])

        # gripper
        if self.cfg['grip_client']:
            self.grip_client = PandaGripperClient(server_ip='localhost', fake=self.cfg['server_ip'] == 'localhost')

        # observation and action spaces
        self._rot_in_pose = sum(self.cfg['valid_dof'][3:]) > 0
        pose_dim = 0
        pose_dim += sum(self.cfg['valid_dof'][:3])
        if self._rot_in_pose: pose_dim += 4

        obs_dim = \
            pose_dim * int('pose' in self.cfg['state_data']) + \
            1 * int('grip_pos' in self.cfg['state_data'])
        self.observation_space = spaces.Box(-np.inf, np.inf, (obs_dim,), dtype=np.float32)

        action_dim = \
            sum(self.cfg['valid_dof']) + \
            1 * int(self.cfg['grip_in_action'])
        self.action_space = spaces.Box(-1, 1, (action_dim,), dtype=np.float32)

        print("Env initialized!")

    def reset(self):
        self._elapsed_steps = 0
        self._suc_latch = False
        if self.cfg['grip_client']:
            self.grip_client.open()
            time.sleep(0.2)
            attempts = 0
            while not self.grip_client.is_fully_open() and attempts < 5:
                attempts += 1
                print(f"Gripper not yet open..try {attempts}/{5}")

            if attempts >= 5:
                raise ValueError("Gripper is not open.")

        self.arm_client.get_and_update_state()
        reset_shift = np.random.uniform(
            low=-np.array(self.cfg['init_gripper_random_lim']) / 2,
            high=np.array(self.cfg['init_gripper_random_lim']) / 2,
            size=6)
        reset_pose_shift_mat = PoseTransformer(
            pose=reset_shift, rotation_representation="rvec").get_matrix()
        new_arm_pose = PoseTransformer(
                pose=matrix2pose(self._reset_base_tool_pose.get_matrix() @ reset_pose_shift_mat))

        self.arm_client.move_EE_to(new_arm_pose)  # blocks to move
        self.arm_client.reset(target_pose=new_arm_pose, init_pose=new_arm_pose)  # resets current desired poses

        self.arm_client.start_controller()
        attempts = 0
        while not self.arm_client.robot.is_running_policy() and attempts < 5:
            print("Controller not started or stopped, attempting to restart..")
            self.arm_client.start_controller()
            attempts += 1
            time.sleep(1)
        if attempts >= 5:
            raise ValueError("Polymetis controller wouldn't start.")

        obs, obs_dict = self.prepare_obs()
        self._prev_obs = copy.deepcopy(obs)
        self._prev_obs_dict = copy.deepcopy(obs_dict)
        return obs

    def prepare_obs(self):
        # overwrite with child classes
        state_list = []
        state_dict = {}
        self.arm_client.get_and_update_state()

        if 'pose' in self.cfg['state_data']:
            pose = self.arm_client.EE_pose.get_array_quat()
            valid_pos = pose[:3][self.cfg['valid_dof'][:3].nonzero()[0]]
            valid_rot = np.array([])
            if self._rot_in_pose:
                valid_rot = pose[3:]
            pose = np.concatenate([valid_pos, valid_rot])

            state_list.append(pose)
            state_dict['pose'] = pose

        if 'grip_pos' in self.cfg['state_data']:
            self.grip_client.get_and_update_state()
            raw_grip_pos = self.grip_client._pos
            # normalize to -1, 1, min grip pos is 0
            max_pos = .5 * self.grip_client.open_width
            grip_pos = (raw_grip_pos - max_pos) / max_pos
            state_list.append(np.array([grip_pos]))
            state_dict['grip_pos'] = grip_pos

        return np.concatenate(state_list), state_dict

    def get_rew(self, obs_dict, prev_obs_dict, act):
        # overwrite with child classes
        return 0

    def get_suc(self, obs_dict, prev_obs_dict, act):
        # overwrite with child classes
        return False

    def get_done(self, obs_dict, prev_obs_dict, act):
        return False

    def get_info(self, obs_dict):
        return {**obs_dict}

    def step(self, act):
        act = np.array(act)

        if act.shape != self.action_space.shape:
            raise ValueError(f"Env requires act shape {self.action_space.shape}, act supplied has shape {act.shape}")

        # actions are rescaled s.t. +1 in all dimensions gives a movement of corresponding max vel
        # also assuming that actions are clipped to +1,-1, but env will force that anyways
        delta_trans = act[:3]
        delta_trans = delta_trans / self._max_trans_vel_norm * self.arm_client._delta_pos_limit
        delta_rot = act[3:]
        delta_rot = delta_rot / self._max_rot_vel_norm * self.arm_client._delta_rot_limit

        self.arm_client.shift_EE_by(translation=delta_trans, base_frame=True, rot_base_frame=True)

        if self.cfg['grip_in_action']:
            self.grip_client.open() if act[-1] < 0 else self.grip_client.close()

        self.rate.sleep()

        self.arm_client.get_and_update_state()
        obs, obs_dict = self.prepare_obs()
        rew = self.get_rew(obs_dict, self._prev_obs_dict, act)
        suc = self.get_suc(obs_dict, self._prev_obs_dict, act)
        obs_dict['suc'] = suc
        done = self.get_done(obs_dict, self._prev_obs_dict, act)
        info = self.get_info(obs_dict)

        self._elapsed_steps += 1
        if self._elapsed_steps >= self._max_episode_steps:
            info['env_done'] = done
            done = True

        self._prev_obs = copy.deepcopy(obs)
        self._prev_obs_dict = copy.deepcopy(obs_dict)

        return obs, rew, done, info


class SimPandaEnv(PandaEnv):
    def __init__(self, config_dict={}, config_file=None) -> None:
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
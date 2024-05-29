import copy
import time
import os
import pathlib
import timeit
from collections import OrderedDict

import numpy as np
import yaml
import gym
from gym import spaces
import cv2

import panda_polymetis
from panda_polymetis.utils.poses import geodesic_error
from panda_polymetis.utils.rate import Rate
from panda_polymetis.control.panda_client import PandaClient
from panda_polymetis.control.panda_gripper_client import PandaGripperClient
from panda_polymetis.perception.realsense_client import RealsenseAPI
from panda_polymetis.perception.aruco_client import ArucoClient
from transform_utils.pose_transforms import (
    PoseTransformer,
    pose2array,
    matrix2pose,
)

import panda_rl_envs.reward_utils as reward_utils

def timer(): return timeit.default_timer()

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

        # make np arrays for lists of numbers
        for k in self.cfg.keys():
            if type(self.cfg[k]) == list and len(self.cfg[k]) > 0 and type(self.cfg[k][0]) in [int, float]:
                self.cfg[k] = np.array(self.cfg[k])

        self.arm_client = PandaClient(
            server_ip=self.cfg['server_ip'],
            delta_pos_limit=self.cfg['max_trans_vel'] / self.cfg['control_hz'],
            delta_rot_limit=self.cfg['max_rot_vel'] / self.cfg['control_hz'],
            home_joints=self.cfg['reset_joints'],
            only_positive_ee_quat=self.cfg['only_positive_ee_quat'],
            ee_config_json=self.cfg['ee_config_json'],
            pos_limits=self.cfg['pos_limits']
        )

        # task
        self._max_episode_steps = round(self.cfg['max_real_time'] * self.cfg['control_hz'])
        self._elapsed_steps = 0
        self._prev_obs = None  # for reward/suc calc
        self._prev_obs_dict = None  # for reward/suc calc
        self._real_time_step = 1 / self.cfg['control_hz']
        self._suc_timer = reward_utils.HoldTimer(self._real_time_step, self.cfg['suc_time_thresh'])

        # reset
        self.arm_client.get_and_update_state()
        self.cfg['reset_pose'] = np.array(self.cfg['reset_pose']) if self.cfg['reset_pose'] is not None else\
            self.arm_client.EE_pose.get_array_euler(axes='sxyz')
        self._reset_base_tool_tf_arr = np.array(self.cfg['reset_pose'])
        self._reset_base_tool_pose = PoseTransformer(self._reset_base_tool_tf_arr, 'euler', axes='sxyz')
        self._reset_base_tool_pose.header.frame_id = "panda_link0"
        self.cfg['reset_joints'] = np.array(self.cfg['reset_joints']) if self.cfg['reset_joints'] is not None else\
            np.array(self.arm_client.joint_position)

        # control
        self.rate = Rate(self.cfg['control_hz'])
        self._max_trans_vel_norm = np.linalg.norm(np.ones(3))
        self._max_rot_vel_norm = np.linalg.norm(np.ones(3))
        self.cfg['valid_dof'] = np.array(self.cfg['valid_dof'])

        # gripper
        if self.cfg['grip_client']:
            self.grip_client = PandaGripperClient(server_ip='localhost', fake=self.cfg['server_ip'] == 'localhost')

        # observations
        self._obj_poses = OrderedDict()
        if 'aruco' in self.cfg['obj_pose_type'] and not self.cfg['dummy_env']:
            if self.cfg['obj_pose_type'] != 'aruco_single':
                raise NotImplementedError()
            hw = self.cfg['aruco_height_width']
            self.aruco_client = ArucoClient(
                height=hw[0], width=hw[1], valid_marker_ids=self.cfg['aruco_valid_marker_ids'],
                marker_width=self.cfg['aruco_marker_width'], dictionary=self.cfg['aruco_dictionary'],
                max_marker_stale_time=self.cfg['aruco_max_marker_stale_time'],
                base_to_cam_tf=self.cfg['aruco_base_to_cam_tf'].tolist(),
                marker_to_obj_tf=self.cfg['aruco_marker_to_obj_tf'].tolist()
            )
            for k in self.cfg['obj_names']:
                self._obj_poses[k] = np.zeros(7)
            self._aruco_img = np.zeros([hw[0], hw[1], 3], dtype=np.uint8)

        # observation and action spaces
        self._rot_in_pose = sum(self.cfg['valid_dof'][3:]) > 0
        pose_dim = 0
        pos_dim = sum(self.cfg['valid_dof'][:3])
        pose_dim += pos_dim
        if self._rot_in_pose: pose_dim += 4
        obj_pose_dim = pos_dim
        if self.cfg['obj_rot_in_pose']: obj_pose_dim += 4

        obs_dim = \
            pose_dim * int('pose' in self.cfg['state_data']) + \
            obj_pose_dim * self.cfg['num_objs'] + \
            pos_dim * self.cfg['num_objs'] * int('pos_obj_diff' in self.cfg['state_data']) + \
            1 * int('grip_pos' in self.cfg['state_data'])
        self.observation_space = spaces.Box(-np.inf, np.inf, (obs_dim,), dtype=np.float32)

        action_dim = \
            sum(self.cfg['valid_dof']) + \
            1 * int(self.cfg['grip_in_action'])
        self.action_space = spaces.Box(-1, 1, (action_dim,), dtype=np.float32)

        # optional simultaneous training
        self._training_called = False
        self._updated_bool = None
        self._training_update_info = None

        # timing debugging
        self._obs_gen_time = None

        print("Env initialized!")

    def reset(self):
        self._elapsed_steps = 0
        self._suc_timer.reset()

        # aux task handling
        if hasattr(self, '_aux_suc_timers'):
            for t in self._aux_suc_timers:
                self._aux_suc_timers[t].reset()

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
        if self.cfg['init_ee_high_lim'] is not None and self.cfg['init_ee_low_lim'] is not None:
            new_arm_pos_rvec = np.random.uniform(
                low=np.array(self.cfg['init_ee_low_lim']),
                high=np.array(self.cfg['init_ee_high_lim']),
                size=6
            )
            new_arm_pose = PoseTransformer(pose=new_arm_pos_rvec, rotation_representation="euler", axes='sxyz')
        else:
            reset_shift = np.random.uniform(
                low=-np.array(self.cfg['init_ee_random_lim']) / 2,
                high=np.array(self.cfg['init_ee_random_lim']) / 2,
                size=6)
            reset_pose_shift_mat = PoseTransformer(
                pose=reset_shift, rotation_representation="rvec").get_matrix()
            new_arm_pose = PoseTransformer(
                    pose=matrix2pose(self._reset_base_tool_pose.get_matrix() @ reset_pose_shift_mat))

        if self.cfg['initial_reset_to_joints']:
            if self.arm_client.sim:
                self.arm_client.move_to_joint_positions(self.cfg['reset_joints'], allowable_error=0.5)
            else:
                self.arm_client.move_to_joint_positions(self.cfg['reset_joints'], allowable_error=0.1)

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
        pose = self.arm_client.EE_pose.get_array_quat()
        valid_pos = pose[:3][self.cfg['valid_dof'][:3].nonzero()[0]]
        valid_rot = np.array([])
        if self._rot_in_pose:
            valid_rot = pose[3:]

        if 'pose' in self.cfg['state_data']:
            pose = np.concatenate([valid_pos, valid_rot])

            state_list.append(pose)
            state_dict['pose'] = pose

        if 'obj_pose' in self.cfg['state_data'] or 'pos_obj_diff' in self.cfg['state_data']:
            if 'aruco' in self.cfg['obj_pose_type']:
                poses = self.aruco_client.get_latest_poses()
                self._aruco_img = self.aruco_client.get_latest_image()
                for k_i, k in enumerate(self._obj_poses.keys()):
                    self._obj_poses[k] = PoseTransformer(
                        pose=poses[k_i], rotation_representation='rvec').get_array_quat()

            # for obj_pose_k, obj_pose in self._obj_poses.items():
            #     valid_obj_pos = obj_pose[:3][self.cfg['valid_dof'][:3].nonzero()[0]]
            #     if self.cfg['obj_rot_in_pose']:
            #         valid_obj_rot = obj_pose[3:]

        if 'obj_pose' in self.cfg['state_data']:
            for obj_pose_k, obj_pose in self._obj_poses.items():
                valid_obj_pos = obj_pose[:3][self.cfg['valid_dof'][:3].nonzero()[0]]
                valid_obj_rot = np.array([])
                if self.cfg['obj_rot_in_pose']:
                    valid_obj_rot = obj_pose[4:]
                obj_pose = np.concatenate([valid_obj_pos, valid_obj_rot])
                state_list.append(obj_pose)
                state_dict[obj_pose_k + '_pose'] = obj_pose

        if 'pos_obj_diff' in self.cfg['state_data']:
            for obj_pose_k, obj_pose in self._obj_poses.items():
                valid_obj_pos = obj_pose[:3][self.cfg['valid_dof'][:3].nonzero()[0]]
                pos_obj_diff = valid_pos - valid_obj_pos
                state_list.append(pos_obj_diff)
                state_dict['pos_' + obj_pose_k + '_diff'] = pos_obj_diff

        if 'grip_pos' in self.cfg['state_data']:
            self.grip_client.get_and_update_state()
            raw_grip_pos = self.grip_client._pos
            # normalize to -1, 1, min grip pos is 0
            max_pos = .5 * self.grip_client.open_width
            grip_pos = (raw_grip_pos - max_pos) / max_pos
            state_list.append(np.array([grip_pos]))
            state_dict['grip_pos'] = grip_pos

        self._obs_gen_time = timer()

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

    def render(self):
        if hasattr(self, 'aruco_client'):
            cv2.imshow("Cam image w/ aruco", self._aruco_img)
            cv2.waitKey(1)

    def step(self, act, train_func=None):
        act = np.array(act)

        if act.shape != self.action_space.shape:
            raise ValueError(f"Env requires act shape {self.action_space.shape}, act supplied has shape {act.shape}")

        # actions are rescaled s.t. +1 in all dimensions gives a movement of corresponding max vel
        # also assuming that actions are clipped to +1,-1, but env will force that anyways
        delta_trans = act[:3]
        delta_trans = delta_trans / self._max_trans_vel_norm * self.arm_client._delta_pos_limit
        delta_rot = act[3:]
        delta_rot = delta_rot / self._max_rot_vel_norm * self.arm_client._delta_rot_limit

        # print(f"Obs to act delay: {timer() - self._obs_gen_time}")

        self.arm_client.shift_EE_by(translation=delta_trans, base_frame=True, rot_base_frame=True)

        if self.cfg['grip_in_action']:
            self.grip_client.open() if act[-1] < 0 else self.grip_client.close()

        # train during step/sleep
        if train_func:
            update_tic = timeit.default_timer()
            self._update_bool, self._training_update_info = train_func()
            self._training_update_info["agent_update_time"] = [timeit.default_timer() - update_tic]
            self._training_called = True

        sleep_time = self.rate.sleep()
        if self._elapsed_steps == 0:
            sleep_time = self.rate.sleep()  # otherwise first sleep is 0
        if self._elapsed_steps > 0:
            if sleep_time == 0:
                print(f"WARNING: env did not sleep at ts {self._elapsed_steps}, is control delayed?")

        # print(f"DEBUG: ts: {self._elapsed_steps}, sleep time: {sleep_time}")

        self._elapsed_steps += 1  # used for get_suc

        self.arm_client.get_and_update_state()
        obs, obs_dict = self.prepare_obs()
        if self._prev_obs_dict is None:
            rew = self.get_rew(obs_dict, obs_dict, act)
            suc = self.get_suc(obs_dict, obs_dict, act)
            obs_dict['done_success'] = suc
            done = self.get_done(obs_dict, obs_dict, act)
        else:
            rew = self.get_rew(obs_dict, self._prev_obs_dict, act)
            suc = self.get_suc(obs_dict, self._prev_obs_dict, act)
            obs_dict['done_success'] = suc
            done = self.get_done(obs_dict, self._prev_obs_dict, act)
        info = self.get_info(obs_dict)

        if self._elapsed_steps >= self._max_episode_steps:
            info['env_done'] = done
            done = True

        if self.cfg['done_on_success'] and suc:
            done = True

        info['obs_dict'] = obs_dict
        if self._prev_obs_dict is None:
            info['prev_obs_dict'] = obs_dict
        else:
            info['prev_obs_dict'] = self._prev_obs_dict

        self._prev_obs = copy.deepcopy(obs)
        self._prev_obs_dict = copy.deepcopy(obs_dict)

        return obs, rew, done, info

    def get_train_update(self):
        if not self._training_called:
            raise ValueError("get_train_update called without calling step with a train_func")
        self._training_updated = False
        return self._update_bool, self._training_update_info

    # def __del__(self):
    #     if hasattr(self, 'aruco_client'):
    #         self.aruco_client.close_shm()

class SimPandaEnv(PandaEnv):
    def __init__(self, config_dict={}, config_file=None) -> None:
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
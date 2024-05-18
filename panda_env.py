import numpy as np
import threading
import queue
import copy
import time
import os
import pathlib
import yaml

import panda_polymetis
from panda_polymetis.utils.poses import geodesic_error
from panda_polymetis.utils.rate import Rate
from panda_polymetis.control.panda_client import PandaClient
from transform_utils.pose_transforms import (
    PoseTransformer,
    pose2array,
    matrix2pose,
)

class PandaExploreEnv:
    def __init__(self,
                 config_dict={},
                 config_file=None
                 ):

        # self._config = config_opts
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'panda_env_defaults.yaml')
        with open(config_file) as f:
            self.cfg = yaml.load(f, Loader=yaml.FullLoader)
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

        # reset
        self.arm_client.get_and_update_state()
        self.cfg['reset_pose'] = self.cfg['reset_pose'] if self.cfg['reset_pose'] is not None else\
            self.arm_client.EE_pose.get_array_euler(axes='sxyz')
        self._reset_base_tool_tf_arr = np.array(self.cfg['reset_pose'])
        self._reset_base_tool_pose = PoseTransformer(self._reset_base_tool_tf_arr, 'euler', axes='sxyz')
        self._reset_base_tool_pose.header.frame_id = "panda_link0"

        # control
        self.rate = Rate(self.cfg['control_hz'])
        self._max_trans_vel_norm = np.linalg.norm(np.ones(3))  # TODO assuming 3-DOF for now

        print("Env initialized!")

    def reset(self):
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

        obs, _ = self.prepare_obs()
        return obs

    def prepare_obs(self):
        # overwrite with child classes
        self.arm_client.get_and_update_state()
        pose = self.arm_client.EE_pose.get_array_quat()
        return pose, {'pose': pose}

    def get_rew(self, obs, act):
        # overwrite with child classes
        return 0

    def get_done(self, obs, act):
        return False

    def get_info(self, obs_dict):
        return {**obs_dict}

    def step(self, act):
        act = np.array(act)

        # TODO hardcoding delta pos only for now
        # actions are rescaled s.t. +1 in all dimensions gives a movement of corresponding max vel
        # also assuming that actions are clipped to +1,-1, but env will force that anyways
        delta_trans = act[:3]
        delta_trans = delta_trans / self._max_trans_vel_norm * self.arm_client._delta_pos_limit
        # act[3:] = self.cfg['max_rot_vel'] * act[3:]  # TODO handle once delta rot added

        self.arm_client.shift_EE_by(translation=delta_trans, base_frame=True, rot_base_frame=True)

        self.rate.sleep()

        self.arm_client.get_and_update_state()
        obs, obs_dict = self.prepare_obs()
        rew = self.get_rew(obs, act)
        done = self.get_done(obs, act)
        info = self.get_info(obs_dict)

        return obs, rew, done, info


class SimPandaExploreEnv(PandaExploreEnv):
    def __init__(self, config_dict={}, config_file=None) -> None:
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
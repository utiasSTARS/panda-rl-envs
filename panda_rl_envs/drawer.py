import pathlib
import os
import copy

import numpy as np

from panda_rl_envs import PandaEnv
from panda_rl_envs.door import PandaDoor
import panda_rl_envs.reward_utils as reward_utils
from transform_utils.pose_transforms import PoseTransformer


class PandaDrawer(PandaDoor):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'drawer.yaml')
        super().__init__(config_dict=config_dict, config_file=config_file)
    
    def reset(self):
        # detect if drawer is open, if so, close it
        obs = super().reset()  # sets self._prev_obs_dict to reset obs_dict

        if self.cfg['auto_reset']:
            drawer_open_dist = np.linalg.norm(self._prev_obs_dict['handle_pose'] - self.cfg['closed_pos'])
            if drawer_open_dist > .005:
                print(f"Detected drawer open {drawer_open_dist}, auto closing.")
                for pose, ttg in zip(self.cfg['auto_reset_poses'], self.cfg['auto_reset_pose_times']):
                    pose_tf = PoseTransformer(pose=pose, rotation_representation='euler', axes='sxyz')
                    self.arm_client.move_EE_to(pose_tf, time_to_go=ttg)
            
                obs = super().reset()
        
        return obs
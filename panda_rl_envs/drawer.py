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
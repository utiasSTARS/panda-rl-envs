import pathlib
import os

import numpy as np

from panda_rl_envs import PandaEnv, SimPandaEnv


class PandaReach(PandaEnv):
    def __init__(self, config_dict={}, config_file=None):
        super.__init__(config_dict, config_file)




class SimPandaReach(PandaReach):
    def __init__(self, config_dict={}, config_file=None):
        if config_file is None:
            config_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'cfgs', 'sim_panda_reach.yaml')
        config_dict['server_ip'] = 'localhost'
        super().__init__(config_dict=config_dict, config_file=config_file)
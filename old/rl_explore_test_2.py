import numpy as np
import copy
import time

from xarm_env import XArmEnv

np.set_printoptions(suppress=True, precision=4)


env = XArmEnv()

new_des_pos = copy.deepcopy(env.des_pos)
new_des_pos[0] += 50

env.update_pos(new_des_pos)

time.sleep(.5)
new_des_pos[0] -= 50
env.update_pos(new_des_pos)

time.sleep(2)

env.close()
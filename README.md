# panda-rl-envs
<p float="middle">
   <img src="https://github.com/utiasSTARS/panda-rl-envs/blob/main/assets/door-30k-explore-timelapse.gif" width="49%" />
   <img src="https://github.com/utiasSTARS/panda-rl-envs/blob/main/assets/drawer-15k-explore-timelapse.gif" width="49%" />
</p>

Real Panda/FR3 (inverse) reinforcement learning tasks/environments.
Used experimentally with [VPACE](https://github.com/utiasSTARS/vpace).

## Installation
1. Install [panda-polymetis](https://github.com/utiasSTARS/panda-polymetis) (and [polymetis](https://facebookresearch.github.io/fairo/polymetis/installation.html), following instructions in `panda-polymetis` repo).
2. Activate `polymetis` conda env.
3. Install this repo (`pip install -e .`)

## Usage
1. Launch robot controller
   1. (real) `bash /path/to/panda-polymetis/launch/real_robot.bash`
   2. (sim) `bash /path/to/panda-polymetis/launch/sim_robot.bash`
2. Launch gripper controller
   1. (real) `launch_gripper.py gripper=robotiq_2f gripper.comport=/dev/ttyUSB0`
   2. (sim) (None, just a fake client)
3. Use as a regular gym environment, but without gym.make:
```python
from panda_rl_envs import *

env = PandaExploreEnv()
obs = env.reset()

for i in range(10):
    obs, rew, done, info = env.step(env.action_space.sample())
```

### Keyboard Control
To get quick access to teaching (without stopping the controller), keyboard control per-joint or in task space, and keyboard gripper control, run
```bash
python -m panda_polymetis.tools.keyboard_interface
```

## Citation
If you find this repository useful for your work, please consider citing [VPACE](https://github.com/utiasSTARS/vpace).

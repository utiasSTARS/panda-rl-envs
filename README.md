# panda-rl-envs
Real Panda RL tasks/environments.

## Installation
1. Install [transform-utils](https://github.com/utiasSTARS/transform-utils)
2. Install [polymetis](https://facebookresearch.github.io/fairo/polymetis/installation.html)
   1. Needs to be installed on learning/policy machine AND on real-time NUC
   2. NUC version must be built from scratch (see more details in [panda-polymetis](https://github.com/utiasSTARS/panda-polymetis) instructions)
3. Install [panda-polymetis](https://github.com/utiasSTARS/panda-polymetis)
4. Install this repo (`pip install -e .`)

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
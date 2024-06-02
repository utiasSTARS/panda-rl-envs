# Real robot setup

## HOME TODO
- [x] Add in success evaluation (including aux) during RL exploration
- [x] verify that reset pose randomization works properly
- [x] pick up laminated sheets from staples
- [x] pick up tape, brackets, washers from canadian tire
- [x] make door env
  - [x] add aruco marker client to observations
  - [x] decide on way to generate success data
- [x] make drawer env

## TODO
- [x] Verify rosetta works to control arm
- [x] need a clean way to recover if we hit a cartesian reflex/control error...right now this will immediately stop the whole episode
  - [x] we can just use `is_running_policy` in the env code
  - [x] implemented, need to test
  - [ ] works, but not tested at large scale yet
- [x] Test reach on real arm
  - [x] most likely need to decrease max move dist or stiffness
- [x] staples trip (See below)
  - [ ] https://fodi.github.io/arucosheetgen/ for printing full tag sheets!
- [x] (home) get tray
- [x] (home) get 2inch cubes
- [x] (home) test ar tags for door/drawer
- [ ] (home) test ar tags on cubes (can do this without 2inch cubes)

## June 2 new plan
1. 45 degree angle of gripper (new env name)
2. not 1000 steps, not 60 steps...maybe 200?
   1. actually going to go back to resetting first, doesn't seem like many steps is actually working
3. try higher tau again first
   1. ..possibly drop gradient steps

## June 1 to try
- [x] 500 stiffness + tvel .1 with new fixes
  - [x] in progress
  - [x] stuck in bad policy that goes to top corner for at least 20 minutes
  - [x] conclusion..this arrangement doesn't allow enough random exploration!
- [x] verify expert data isn't wrong
- [x] 1000 timestep episodes
  - [x] done on success
    - [x] calculation of drawer success needs to be fixed...drawer open plus gripper open plus gripper x pos lower than drawer x pos
    - [x] this is not wokring for some reason...debug this
      - [x] nvm this is working!
  - [x] alternating between WRS + 120120120, 20 timestep sched period is fine
  - [x] dropping stiffness back to 250
  - [x] need to verify this is actually workign properly...take away debug statements, check scheduler outputs
  - [ ] still a bug in scheduler update that makes it print at 360 steps for some reason?
- [x] 400 stiffness + tvel .15
  - [x] verify that tvel .15 doesn't hit the drawers in polykey
  - [ ] in progress
- [ ] call 000 only 25% of the time, instead of 50%
  - [ ] in progress on run above
- [x] 400 stiffness + tvel .2
  - [x] verify doesn't hit drawers in polykey
  - [x] verified, and bug fixed
  - [x] stiffness this high still fails quite often -- i think lower is better
  - [x] in progress
- [ ] 250 stiffness, tvel .2, tau 5e-3
- [ ] 250 stiffness, tvel .3, 1000 timestep eps
- [ ] 3Hz? 250 stiffness, tvel .2?
- [ ] no grasping, just hook and slightly different angle
- [ ] 500 stiffness, tvel .2, 10Hz?
- [ ] fewer gradient steps per step? and more random exploration?
  - [ ] yes more random exploration

### BIG BUG FOUND
- all pose adjustments, including enforcing limits, was happening AFTER the desired pose was already set
  - this is why we were crashing into the doors
  - this is also why force adjustments weren't happening right away

## DRAWER TODO
- [x] add randomization to initial pose
- [x] test reward/success functions with a panda_drawer_test.py file
- [x] test success example code to verify poses/limits are correct
- [x] collect and move success example data
- [x] test exploration with limits not allowing drawer interaction
- [ ] many steps with no action get added during automatic error recovery...would be preferable to just immediatley revert the controller upon error, instead of get 3 secs (15 frames) worth of bad data
- [ ] things to try for improvement
  - [ ] higher action mag
  - [ ] higher stiffness (maybe this first)
  - [ ] different arm position that would allow more accurate pose tracking
  - [ ] may31_first: 250 stiffness, tvel .2
    - [ ] turns out i messed the 2nd half of this run up entirely by dropping tvel to .1
  - [ ] also tried: 500 stiffness, tvel .1...too slow
  - [ ] trying: 500 stiffness, tvel .2...very aggressive, fixed bug where bad data was being added to buffer
  - [ ] now trying: 250 stiffness, tvel .2, bug fixed
- [x] depending on how successful, add in self-resetting via detection of drawer position, set of hardcoded poses to automatically close drawer
  - [x] works! all we need to figure out is the true close position (and open), since they appear to have changed...
- [x] alos we don't need the force-torque sensor to ensure that our impedance controller works the way we want, we can just cap the allowable differene between target pose and actual pose to specific values!!

## Door and Drawer todo
- [x] Save the ee config json to put in panda_polymetis/conf/franka-desk
- [ ] Choose shelf location/robot position boundaries and add to panda polymetis config
- [ ] L brackets *or* mounting tape to fix shelves into place
  - [ ] just marked location with tape for now
- [ ] Manually find z height (and x/y pos) for door and drawer
  - [ ] THIS is actually how we get the pos limits / reset pose
  - [ ] to go from this height to getting a reset pose, we need to activate freedrive with fewer degrees of freedom
    - [ ] reset_pose: [0.1653715, 0.4675048, 0.5384299, -1.623644, -0.8070195, 0.4270715]
          reset_joints: [1.7601, -1.219508, -0.7970036, -2.686295, 0.7965282, 2.621956, -1.57055]
    - [ ] new for drawer:
      - [ ] reset_pose: [0.6534886, 0.1962629, 0.6356113, 1.91674, -0.7635592, 1.304907]
            reset_joints: [0.9866469, -0.4365612, 0.007007468, -2.116341, -1.189016, 2.73617, -0.3003828]
- [x] Manually find pos limits for arm (separate for each)
  - [x] currenlty stored (with more freedom in z) as REAL_DEFAULT_POS_LIMITS in panda_client.py
- [ ] Manually choose reset position + reset randomization limits
  - [ ] remember that it's going to make the most sense to allow it randomly explore a lot without resetting (i.e. long episodes)
  - [x] if we do long episodes, we can add in done on main success
- [ ] attempt to "fix" camera in place with simple tripod for testing (until we get truly fixed option)
- [ ] INSTEAD OF CALIBRATING:
  - [ ] manually put arm at initial reach position, and use this position as offset for robot pose and door pose, and then don't include pos obj difference in observation...now robot pose will have a built in reach diff observation.
  - [ ] no need for calibration
  - [ ] no need for fixed offset
  - [ ] but any reward based on diff between handle pose and robot pose will not work
  - [ ] only if calibration seems to be a large hassle
- [ ] attempt arm/camera calibration with robostack + easy handeye
  - [ ] i've done this before with info here: https://github.com/utiasSTARS/thing/tree/feature/marker_calibration/thing_utils
  - [ ] for this also need to use ros packages and custom launch file
    - [ ] can verify some/most of these things at home and whether they work without a full ros install.
    - [ ] TODO: i don't think we need to run a controller necessarily, just need the description/tf tree?
      - [ ] if we do need to run with controller, we can easily run impedance with no stiffness or damping
    - [ ] aruco_ros: https://github.com/pal-robotics/aruco_ros/tree/noetic-devel
    - [ ] realsense-ros: robostack as ros-noetic-realsense2-camera (or https://github.com/IntelRealSense/realsense-ros/tree/ros1-legacy)
      - [ ] launch: `roslaunch realsense2_camera rs_camera.launch`
      - [ ] needed two fixes:
        - [ ] (udev rules) https://github.com/IntelRealSense/realsense-ros/issues/1408#issuecomment-698128999
        - [ ] and also manual install of libudev0 `sudo apt install libudev0`
    - [ ] franka_ros
      - [ ] why didn't conda install work? looks like it did
        - [ ] so just `conda install ros-noetic-franka-ros`
        - [ ] `conda install ros-noetic-moveit-ros`
        - [ ] `conda install ros-noetic-moveit-resources-panda-moveit-config`
        - [ ] `conda install ros-noetic-moveit-ros-move-group`
        - [ ] `conda install ros-noetic-geometric-shapes=0.7.3`
        - [ ] `conda install ros-noetic-moveit-planners`
        - [ ] `conda install ros-noetic-moveit-ros-control-interface`
      - [ ] also requires building libfranka
      - [ ] which required `sudo apt install libeigen3-dev libpoco-dev`
      - [ ] also required ros install `ros-noetic-combined-robot-hw` and `ros-noetic-boost-sml`
    - [ ] panda + moveit: robostack as ros-noetic-franka-ros
- [ ] (if calibration works) add calibration offset to aruco observation in panda_env
- [ ] (if calibration works) choose fixed offset from aruco tag as door handle pos, add to aruco observation in panda_env
  - [ ] we would have calibration_T * pose_in_cam_T * fixed_offset_T to get new pose
- [ ] Manually find (x,y) open positions of door (of aruco tag)
- [ ] manually find grasp positions of end effector when closed on handle
- [ ] verify that obj ee pos differences are okay-ish
- [ ] verify that aruco tag stays visible as door opens and closes
- [ ] verify that robot max forces don't destroy cabinets, and that this is over-force is handled reasonably within the env


## Env order:
- [ ] verify that closed gripper doesn't have excessive friction on handle..might need to add tape
- [ ] verify that door can be opened effectively without adding rotation about z
- [ ] get fixed z height + orientation with full freedrive (or x/y for drawer)
  - [ ] by moving to handle reach pos...this is also how we can get master reach position for suc examples
- [ ] freedrive robot to be close to desired reset pos
- [ ] manually move robot via client (move ee to) to same fixed z height but diff x y positions to get joint positions for reset
- [ ] move ee to for moving robot to master locations for each aux
- [ ] take random actions after manually overriding env.arm_client._pos_limits

## staples to buy
- 2 laminated sheets of tags 1-12, 4.5cm
- same, possibly more tags, 3.3cm
- 1 sheet, laminated tags 1-12, 5.5cm
- double sided tape (permanent)
- double sided tape (non-permanent)
- thin cardboard
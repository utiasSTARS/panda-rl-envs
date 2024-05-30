# Real robot setup

## HOME TODO
- [x] Add in success evaluation (including aux) during RL exploration
- [x] verify that reset pose randomization works properly
- [x] pick up laminated sheets from staples
- [x] pick up tape, brackets, washers from canadian tire
- [x] make door env
  - [x] add aruco marker client to observations
  - [x] decide on way to generate success data
- [ ] make drawer env

## TODO
- [x] Verify rosetta works to control arm
- [ ] need a clean way to recover if we hit a cartesian reflex/control error...right now this will immediately stop the whole episode
  - [ ] we can just use `is_running_policy` in the env code
  - [ ] implemented, need to test
- [ ] Test reach on real arm
  - [ ] most likely need to decrease max move dist or stiffness
- [ ] staples trip (See below)
  - [ ] https://fodi.github.io/arucosheetgen/ for printing full tag sheets!
- [x] (home) get tray
- [x] (home) get 2inch cubes
- [x] (home) test ar tags for door/drawer
- [ ] (home) test ar tags on cubes (can do this without 2inch cubes)

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
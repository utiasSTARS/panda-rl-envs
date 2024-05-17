# General notes
- There was no clean way to set an interruptable controller on the xArm without resorting to ROS (which *maybe* would have been okay)
- Instead, going to switch over to panda + polymetis (or at least attempt)
- if this turns out to be a hassle, might go ahead and do xarm + ROS + control similar to thing_control servo
- installation of polymetis on nuc: requires custom libfranka for FR3, which requires local build/install, which didn't work until i reinstall torch with:
  - `pip install --force-reinstall torch==1.13.1 --index-url https://download.pytorch.org/whl/cpu`

# Thinking again about Xarm
- the ros controller has a setup specifically for what i want to do:
  - https://github.com/xArm-Developer/xarm_ros/tree/master/examples#6-online-target-update
- let's try that in sim


# May 17 TODO
- [ ] Check.. does FR3 really have different joint limits? and if so, we should probably add that to polymetis?
- [ ] Set up basic panda class/tests to test RL exploration
  - [ ] if this looks good in polymetis sim, we'll test on real robot
  - [ ] if this looks good on real robot, doesn't cause significant errors, and allows gentle collisions with the world, we'll just move forward with this
    - [ ] doing all of this with xarm + force torque will require ~a day, minimum, to set up, so that is now lower priority than just using the robot we already have
- [ ] investigate camera/object pose tracking options
  - [ ] very well might be the case that it makes the most sense to just use AR tags, but would be nice to avoid
- [ ] assuming RL exploration works on real robot, we can get the entire interface with rl_sandbox (training between episodes, etc.) working exclusively in polymetis sim (for e.g. some basic reaching task to start)


## TODOS
- [ ] Get sim setup on local computer
- [ ] Get a basic "env" class setup to run in sim
- [ ] see how RL exploration looks in sim
- [ ] test RL exploration on real robot

# Xarm
**all lower priority until we test panda more**

## TODOS
- [ ] Get sim setup with xarm ros on local computer
- [ ] get a basic "env" class setup to run in gazebo
- [ ] see how rl exploration looks in sim
- [ ] test RL exploration on real robot
- [ ] test RL exploration + basic impedance control with force torque on real robot

## install notes
- needed to run `conda install ros-noetic-geometric-shapes==0.7.3`, version 0.7.5 was installed and caused moveit problems

## notes on how to setup
- on real robot, use https://github.com/xArm-Developer/xarm_ros?tab=readme-ov-file#robot-mode-7-firmware--v1110
- more info: https://github.com/xArm-Developer/xarm_ros/tree/master/examples#6-online-target-update
- can potentially use moveit servo as an alternative?
  - https://github.com/xArm-Developer/xarm_ros?tab=readme-ov-file#58-xarm_moveit_servo
  - this works in sim too, which is nice.
  - should try both on real robot


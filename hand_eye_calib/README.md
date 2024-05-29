# Hand eye calibration with Panda


## Instructions
1. Install noetic with robostack in python 3.9 (different conda env from polymetis)
2. Install realsense `conda install ros-noetic-realsense2-camera`
   1. Needed 2 fixes:
      1. `sudo apt install libudev0`
      2. Manual adding of [udev rules](https://github.com/IntelRealSense/realsense-ros/issues/1408#issuecomment-698128999)
3. Create ros1 workspace
   1. clone [aruco_ros](https://github.com/pal-robotics/aruco_ros/tree/noetic-devel)
   2. build, and should now be able to track a marker with `roslaunch realsense_marker_tracking.launch`
   3. clone [easy_handeye](https://github.com/IFL-CAMP/easy_handeye)
4. Install franka ros `conda install ros-noetic-franka-ros`

## Running
1. From RT computer, launch robot control with `roslaunch franka_control robot_ip:=192.168.2.2 robot:=fr3 load_gripper:=false`
2. To control, launch dynamic reconfigure for stiffness with `rqt`, and drop stiffness close to 0
   1. if this is slow, we can also install panda-ros-packages, but going to leave that out for now.
3. On main computer, `roslaunch hand_eye_calib.launch`
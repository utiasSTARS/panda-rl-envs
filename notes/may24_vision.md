# Computer vision setup

## Realsense testing
- [ ] re-investigate DOPE and similar packages and consider difficulty in setting up
- [ ] test AR tags at home (on cubes?)

## env setup
- [ ] Generate code for a play env with computer vision
- [ ] get a tray to recreate play env


## notes
- removed opencv-python, which was originally `opencv-python 4.9.0.80`
- installed opencv-contrib-python==4.9.0.80

## aruco notes
1. marker true size goes here (2nd argument):
   `rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients, distortion_coefficients)`
    - whatever this unit is the unit that the tvec will be, so picking something like e.g. meters probably makes sense
2. can resize markers to whatever you want after generating them inside document editor
3. markers should have some amount of white border around them, otherwise apparently they don't work as well

## common todo
- [x] run timing test on using opencv directly as we currently have it to detect markers
  - [x] if this is slow, test running a ros node to detect the markers (with robostack)
- [x] run timing test on pyrealsense2 method of acquiring images (i.e. what polymetis uses)
- [ ] print off larger (or correct size) markers for door/drawer
- [ ] test markers on door / drawer
  - [ ] attach markers to cardboard, and cardboard to door/drawer
  - [ ] next test...what about using a large array of markers for a single pose, rather than handling this manually?
- [x] get intrinsics from camera, might be built into pyrealsense2..otherwise should checkerboard calibrate to do this
- [ ] buy strong double-sided adhesive
- [ ] generate code for door and drawer envs
  - [ ] make it agnostic to whether we end up using charuco, single aruco, or multiple aruco
- [ ] (in lab) hand eye calibration
  - [ ] try to use easy_handeye, hopefully with robostack
  - [ ] use `freehand_robot_movement:=true to calibrate.launch`
  - [ ] if this takes >30 minutes to set up, drop it, not necessary.

## door/drawer env todo
- [ ] confirm whether real env allows you to specifically change force/torque max thresholds, and make them lower
  - [ ] then we don't need to use force-torque sensor for anything

## play env todo

## aruco todo

- [ ] reprint new (smaller) markers and add to cube for testing
- [ ] write function that takes detected cube markers and outputs cube pose
  - [ ] need to know fixed transformation of fixed cube frame to each marker
  - [ ] find largest detected marker, use fixed transform from above to get cube pose
  - [ ] use rotation logic from manipulator_learning to remove aliased rotations
- [ ] generate code for cube play environment
- [ ] generate code for door and drawer environments
- [ ] verify that laminated artags still work
- [ ] buy wooden cubes, print and laminate artags for wooden cubes and home cubes



## real sense notes
- original v4l2-ctl settings:
```
(polymetis) realsense_driver: v4l2-ctl -l -d 12

User Controls

                     brightness 0x00980900 (int)    : min=-64 max=64 step=1 default=0 value=0
                       contrast 0x00980901 (int)    : min=0 max=100 step=1 default=50 value=50
                     saturation 0x00980902 (int)    : min=0 max=100 step=1 default=64 value=64
                            hue 0x00980903 (int)    : min=-180 max=180 step=1 default=0 value=0
        white_balance_automatic 0x0098090c (bool)   : default=1 value=1
                          gamma 0x00980910 (int)    : min=100 max=500 step=1 default=300 value=300
                           gain 0x00980913 (int)    : min=0 max=128 step=1 default=64 value=64
           power_line_frequency 0x00980918 (menu)   : min=0 max=3 default=3 value=3 (Auto)
      white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=10 default=4600 value=4600 flags=inactive
                      sharpness 0x0098091b (int)    : min=0 max=100 step=1 default=50 value=50
         backlight_compensation 0x0098091c (int)    : min=0 max=1 step=1 default=0 value=0

Camera Controls

                  auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=3 (Aperture Priority Mode)
         exposure_time_absolute 0x009a0902 (int)    : min=1 max=10000 step=1 default=166 value=166 flags=inactive
     exposure_dynamic_framerate 0x009a0903 (bool)   : default=0 value=1
```
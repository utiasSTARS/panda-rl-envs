# Real Robot setup todos -- main

- [ ] Do some preliminary tests on Franka with polymetis to see if polymetis / RL dithering exploration is going to work
- [ ] See if xarm + force torque + simple impedance will work okay as well.
- [ ] Choose a visual sensor and possibly a library for converting data from the sensor to object poses
- [ ] an environment that plays nicely with existing code
- [ ] a way of alternating training and running in the env (or doing it in parallel)
- [ ] checkpoint saving and loading (mostly implemented, but maybe not fully there?)
- [ ] Determine options for bringing Franka home.


# Notes on Panda vs. Xarm, general hardware choices
- All robotiq hardware requires external power sources that may or may not be easy to come by
  - this makes both the force torque sensor and the robotiq gripper less desireable to use
- force torque + xarm might be a much cleaner way to get impedance control
  - xarm control rate? max 250Hz, suggested interpolate at 100Hz or 200Hz

# xarm tests
1. connect computer to xarm and try out some basic servo movement tests
   1. point to point movement
   2. random dithering exploration at 5Hz
   3. etc.

# force-torque tests
1. connect force torque sensor to

# camera tests
1. azure seems like installing alone would be a huge hassle
2. DOPE apparently can do pose tracking of known objects with RGB only...this should be good enough for me!
   1. unclear how you get this to work with new objects...need to look into more (can be done at home)
   2. could just use blocks and artags, of course

# things to buy
- USB extension cables for robotiq gripper + force-torque power box.


# Xarm testing notes
- set_tool_position seems to handle generating a path between current pose and desired pose, but unclear what sending higher frequency (i.e. 5Hz) commands will do to it
  - careful though, this appears to automatically set the new position based on the *current* position, which isn't what we actually want...so we'll have to store our own current desired position and feed it, in which case we should also probably specifically set relative to False
  - set_position seems like a better choice anyways, so that our rotation axes will be fixed.
- set_servo_cartesian_aa also allows setting motion relative to current pose, but seems to require/expect sending commands at a high frequency, and also attempts to move to a pose "as fast as possible?"
  - "Servo_cartesian motion: move to the given cartesian position with the fastest speed (1m/s) and acceleration (unit: mm)"
  - looks like set_tool_position might be more ideal since it will already generate smoother paths...unless the paths suck, and then we'll have to think more about it.

## set_position
- has a `radius` option that seems like it'll help interpolate when position changes
- also has a `motion_type` option that might help with pushing through singularities
  - 0, pure linear, is default, 1 is for linear but fallback to IK, 2 is for all IK
    - a bit unclear what these things actually mean though
- now is clear...doesn't actually update new position on the fly, has to make it to original position before a new position is set
  - `wait` simply makes it non-blocking, but doesn't stop it from executing the first command
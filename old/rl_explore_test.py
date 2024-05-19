import argparse
import time
import numpy as np

from xarm import XArmAPI

parser = argparse.ArgumentParser()
parser.add_argument('--hz', type=int, default=1)
parser.add_argument('--test_length', type=float, default=5.0, help="how long to run test for, seconds")
parser.add_argument('--arm_ip', type=str, default='192.168.2.229')
args = parser.parse_args()


arm = XArmAPI(port=args.arm_ip, is_radian=True, do_not_open=True)  # is_radian True here, so no need to set everywhere else

arm.connect()
arm.set_mode(0)  # position control mode
arm.motion_enable(True)  # disable brakes, no-op if they're already off
arm.set_state(0)  # necessary after motion_enable

# print(f"Running random actions at {args.hz}hz for {args.test_length}s")

start_time = time.time()
cur_time = start_time

# get current position to set as new desired pose
valid_pos, des_pos = arm.get_position_aa()
if valid_pos != 0:
    arm.disconnect()
    raise ValueError(f"Arm position invalid, code: {valid_pos}")
print(f"Des pos set to {des_pos}")
des_pos = np.array(des_pos)

# test setting pos to des pos @ 1cm/s to make sure it won't fly off
move_suc = arm.set_position_aa(des_pos, speed=10, wait=True)
if move_suc == 0:
    print(f"Arm successfully moved to des pos.")
else:
    arm.disconnect()
    raise ValueError(f"Arm did not move to des pos, error code {move_suc}")

# now do real tests..for now, move to different positions without finishing movement
# turns out set_arm_position isn't what we want...going to try with servo instead
# des_pos[0] += 100
# print("Sending first command..")
# move_suc = arm.set_position_aa(des_pos, speed=10, wait=False, radius=10)  # radius unit appears to be mm
# time.sleep(1)
# des_pos[0] -= 100
# print("Sending second command..")
# move_suc = arm.set_position_aa(des_pos, speed=10, wait=True, radius=10)

arm.set_mode(1)  # servo control mode
arm.set_state(0)  # necessary after motion_enable

# TODO should send true control at e.g. 100Hz, but going to send our changes at 50Hz
# for now going to just send at 100Hz
change = -100  # mm
freq = 100  # hz
speed = 10  # mm/s
expected_time = abs(change) / speed
expected_num_changes = round(expected_time * freq)
change_per_loop = -speed / freq

for i in range(expected_num_changes):
    des_pos[0] += change_per_loop
    arm.set_servo_cartesian_aa(des_pos)
    time.sleep(1 / freq)
    if i % 100 == 0:
        print(f"{i} / {expected_num_changes} complete")


arm.disconnect()

# arm.set_position()

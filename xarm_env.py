import numpy as np
import threading
import queue
import copy
import time

from xarm import XArmAPI

import utils

class XArmEnv:
    def __init__(self, hz=5, real_hz=100, arm_ip='192.168.2.229') -> None:
        # is_radian True here, so no need to set everywhere else
        self._arm_ip = arm_ip
        # self.arm = XArmAPI(port=arm_ip, is_radian=True, do_not_open=True)
        # self.arm.connect()

        self.hz = hz
        self._real_hz = real_hz

        # self.arm.set_mode(1)  # servo control mode
        # self.arm.motion_enable(True)
        # self.arm.set_state(0)  # necessary after motion_enable

        self._max_dist = 1  # safety, mm
        self._max_rot_dist = 0.1  # safety, rads

        self.des_pos = None
        self.cur_pos = None
        self.cur_vel = None

        # control thread
        self.des_pos_lock = threading.Lock()
        self.des_pos_q = queue.Queue()
        self._control_rate = utils.Rate(real_hz)
        self._control_thread = threading.Thread(target=self._control_loop, args=(self.des_pos_q,))
        self._control_thread.daemon = True
        self._control_thread.start()

        while self.des_pos is None and self.cur_pos is None:  # wait for arm to start in thread
            time.sleep(.01)

        print("Robot initialized, control loop started!")

    def get_pos_safe(self, arm):
        # valid_pos, pos = self.arm.get_position_aa()
        valid_pos, pos = arm.get_position_aa()
        if valid_pos != 0:
            arm.disconnect()
            raise ValueError(f"Arm position invalid, code: {valid_pos}")
        return np.array(pos)

    def get_pos(self):
        return copy.deepcopy(self.cur_pos)

    def close(self):
        # self.arm.disconnect()
        print("Disconnecting arm")
        self.des_pos_q.put("close")

    def _control_loop(self, q: queue.Queue):
        arm = XArmAPI(port=self._arm_ip, is_radian=True, do_not_open=True)

        arm.connect()
        arm.set_mode(1)  # servo control mode
        arm.motion_enable(True)
        arm.set_state(0)  # necessary after motion_enable

        # get current position to set as new desired pose
        self.des_pos = self.get_pos_safe(arm)
        self.cur_pos = copy.deepcopy(self.des_pos)
        print(f"Current robot pose: {self.des_pos}")

        last_control_pos = None

        while True:
            # only move when new traj of positions added to q
            control_pos = q.get(block=True)

            if control_pos == "close":
                break
            # print(f"control pos in thread: {control_pos}")
            arm.set_servo_cartesian_aa(control_pos)
            self.cur_pos = self.get_pos_safe(arm)

            if last_control_pos is None:
                last_control_pos = control_pos
            # self.cur_vel = (control_pos - last_control_pos) /

            last_control_pos = copy.deepcopy(control_pos)

            self._control_rate.sleep()

        arm.disconnect()

    def update_pos(self, new_pos, time_to_go=1):
        # interpolate between current pos and new desired pos, add all to q for control loop
        # this assumes that the xarm SDK handles smooth velocity/accel transitions, which may not be true
        # cur_pos = self.get_pos_safe()
        cur_des_pos = copy.deepcopy(self.des_pos)  # new actions change des pos only, not directly from current pos

        # clear the q
        with self.des_pos_q.mutex:
            self.des_pos_q.queue.clear()
            self.des_pos_q.all_tasks_done.notify_all()
            self.des_pos_q.unfinished_tasks = 0

        # TODO only testing with translation for now
        num_control_steps = round(time_to_go * self._real_hz)
        interp_des_pos = np.linspace(cur_des_pos, new_pos, num_control_steps)
        cur_pos = self.get_pos()

        # inputs: current pos interpolated desired pos from old desired pos to new desired pos
        # we want a trajectory that, at each timestep, moves towards the interpolated des pos for the timestep
        # assuming we are starting from the current pos...this is pretty suboptimal though
        # maybe, instead, we just set a max acceleration that limits how much the current "velocity" command can change

        for i in range(num_control_steps):
            self.des_pos_q.put(interp_pos[i])
            print(f"Adding pos to q: {interp_pos[i]}")

        self.des_pos = new_pos
import numpy as np


def generic_reach_rew(pos, prev_pos, goal_pos):
    prev_dist = np.linalg.norm(prev_pos - goal_pos)
    dist = np.linalg.norm(pos - goal_pos)
    return prev_dist - dist


def diff_reach_rew(diff, prev_diff):
    prev_dist = np.linalg.norm(prev_diff)
    dist = np.linalg.norm(diff)
    return prev_dist - dist


class HoldTimer:
    def __init__(self, real_t_per_ts, min_time, latch_suc=True):
        self._start_time = None
        self._min_time = min_time
        self._real_t_per_ts = real_t_per_ts
        self._latch_suc = latch_suc
        self._latch = False

    def update_and_get_suc(self, suc_bool, ep_ts):
        held_suc = False
        if suc_bool:
            if self._start_time is None:
                self._start_time = ep_ts
                held_suc = False
            else:
                held_suc = (ep_ts - self._start_time) * self._real_t_per_ts > self._min_time
        else:
            self._start_time = None
            held_suc = False

        if held_suc:
            self._latch = True

        if self._latch_suc:
            return self._latch
        else:
            return held_suc

    def reset(self):
        self._start_time = None
        self._latch = False
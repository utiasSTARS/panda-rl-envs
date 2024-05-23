#!/bin/bash

NUM_EPISODES="50"
INTENTION="0"
MODEL_NAME="32000.pt"
# CONFIG_NAME="lfgp_experiment_setting.pkl"
CONFIG_NAME="dac_experiment_setting.pkl"
SEED="12"

TOP="/media/ssd_2tb/data/lfebp/panda_rl_envs/results"

# may 23 testing in sim
MODEL_REST="SimPandaReach/100/sqil/pos_limits_fs2_fixenv/05-22-24_20_23_20"

# FORCED_SCHEDULE="{0: 3, 25: 2, 50: 4, 75: 5, 100: 1, 125: 3, 150: 4, 175: 2, 200: 1}"


COMMON_TOP="${TOP}/${MODEL_REST}"
MODEL_PATH="${COMMON_TOP}/${MODEL_NAME}"
CONFIG_PATH="${COMMON_TOP}/${CONFIG_NAME}"


python $HOME/projects/lfgp/rl_sandbox/rl_sandbox/examples/eval_tools/evaluate.py \
--seed="${SEED}" \
--model_path="${MODEL_PATH}" \
--config_path="${CONFIG_PATH}" \
--num_episodes="${NUM_EPISODES}" \
--intention="${INTENTION}" \
--model_path="${MODEL_PATH}" \
--forced_schedule="${FORCED_SCHEDULE}"
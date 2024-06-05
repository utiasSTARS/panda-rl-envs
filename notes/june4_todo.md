
## Videos
- short real time exploratory videos at each checkpoint (0, 5k, 10k, 15k, 20k, 25k)
- timelapse of 1000 steps at each checkpoint
- photos of success states
  - just take screenshots from high performing exploratory/success policies
  - instead, rerecording these manually...from approximately 10:45am June 5
- performance of main task at 25k (or 30k if we use that) (can use visualize model)

- performance in paper could show during training evaluation only, instead of final task eval
  - since this doesn't match anything else we did, we won't do this
- get main task success at each checkpoint, 10 eps per checkpoint...finish up evaluate_models.py script for this

## todo
- [x] Need code for loading model checkpoints and restarting training in a new folder.
  - [x] need to handle loading existing buffer up to a specific timestep
  - [x] need to handle loading data from one folder/checkpoint and generating a brand new folder (with a modified experiment name) for the new run -- this will be for the exploration videos
  - [x] i think lfgp code basically already handles this...need to confirm
  - [x] except that the train progress file is different...we need to load that
- [x] finish writing and test evaluate_models.py code
  - [x] needs to handle case where script stopped running...save data after every evaluated episode
- [x] run single task sqil on env and get same data as all of above
  - [x] run this while developing and testing the other code simultaneously
  - [x] getting DAC (both with no q over max penalty), and might get RCE as well if there's time
  - [ ] rce if there's time/justification

## instructions
### exploratory videos
args for run_vpace: --exp_name [original name] --load_model_name 5000 --load_buffer_start_index 5000

### performance videos
panda-rl-envs/tests/evaluate_models.py: --env_name [original name] --exp_name [original name] --algo [multi-sqil,sqil,disc,rce]
- going to start at 25k to make sure that 10 eps actually succeeds as often as we want
  - and worst case we just make our success metric more forgiving...
# RL Sandbox interface notes

## TODO
- [x] Install rl_sandbox requirements in polymetis env
- [x] make script to generate expert data for new env
- [x] start new branch from LfGP (public) and from VPACE for changes corresponding to this
- [x] allow training of single task reach env
- [x] add training between episodes instead of at steps
- [ ] add restarting training from checkpoint
  - [x] *probably* want to generate checkpoints after every episode, rather than at the save interval..save interval is just for models we keep long term
  - [x] test checkpoint on task that we know works to make sure training doesn't break
- [ ] allow training of multitask reach env
  - [ ] make a new sim task that has aux tasks as well
  - [ ] add aux rewards to rl_sandbox for aux tasks
    - [ ] maybe put them in the panda_rl_envs repo instead, and just import them from there
- [ ] decide on making frame stack 2 default
  - [ ] seems to be better
- [ ] verify that single task reach and multitask whatever are actually learnable
  - [ ] single task
  - [ ] multitask

## TODO Fixes
- [x] currently saving a buffer at every timestep AND checkpoint buffer AND termination buffer
  - [x] remove termination buffer for every ep checkpointing
  - [x] make checkpoint buffer only buffer for every ep checkpointing
  - [x] verify that termination buffer and timestep buffer won't both be saved (one or the other)
- [x] checkpointing doesn't actually work, possibly among other things, to be fixed:
  - [x] agent.learningalgoirthm.step isn't saved
  - [x] timestep_i from learning_utils
  - [x] cum_episode_lengths from learning_utils, also
    - [x] curr_episode
    - [x] num_updates
    - [x] returns
    - [x] all evaluation variables
  - [x] genrally all of the load utils are set up for *transfer learning*, but need to accomodate resuming a checkpoint
- [x] verify that frame stack is actually workingg

## frequent checkpointing notes
- [x] (before adding and naming option) verify how long checkpoint takes to generate...need to verify it's not excessively slow if we're going to do every episode.
  - [x] approx .03-.05s on a local save on my machine with a small obs space and small buffer..will need to track this
- [x] Need to verify whether we need to checkpoint anything else such as optimizers
- [x] sounds like yes, at least optimizer should be checkpointed as well (maybe it is? need to verify)

## training during step notes
- [x] add training between episodes instead of at steps
  - [x] at 5Hz, maybe this isn't necessary? need to verify forward pass + backward pass times
  - [x] we can at least improve this loop by training during the step:
    - [x] original: a = pi(o) --> o = env.step(a) --> var_sleep --> train(pi)
      - [x] creates a delay between pi choice and true o because of train delay
    - [x] new:      a = pi(o) --> env.step(a) --> train(pi) --> var_sleep --> o = env.get_o()
      - [x] only delay is forward pass (impossible to avoid)

before fix:
```
DEBUG: ts: 36, sleep time: 0.15924615859985353
Obs to act delay: 0.03142655798001215
```
after fix:
```
DEBUG: ts: 12, sleep time: 0.15385026931762696
Obs to act delay: 0.0037462409818544984

```

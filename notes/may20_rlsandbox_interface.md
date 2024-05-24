# RL Sandbox interface notes

## TODO
- [x] Install rl_sandbox requirements in polymetis env
- [x] make script to generate expert data for new env
- [x] start new branch from LfGP (public) and from VPACE for changes corresponding to this
- [x] allow training of single task reach env
- [x] add training between episodes instead of at steps
- [x] add restarting training from checkpoint
  - [x] *probably* want to generate checkpoints after every episode, rather than at the save interval..save interval is just for models we keep long term
  - [x] test checkpoint on task that we know works to make sure training doesn't break
- [ ] allow training of multitask reach env
  - [ ] make a new sim task that has aux tasks as well
  - [ ] add aux rewards to rl_sandbox for aux tasks
    - [ ] maybe put them in the panda_rl_envs repo instead, and just import them from there
  - [ ] still missing scheduler period
- [x] decide on making frame stack 2 default
  - [x] seems to be better
- [ ] verify that single task reach and multitask whatever are actually learnable
  - [x] single task
  - [ ] multitask
- [x] test increasing tau, since faster learning is very desireable
  - [x] in progress, may23_tau5e-3
  - [x] okay at best..not a *definite* improvement
- [ ] forward pass timing test on laptop
- [ ] gpu memory test with environment with higher dimensional space + multitask
  - [ ] on home desktop
- [x] make convenient script for testing trained policies
  - [x] should also produce a results file that matches the one generated during a regular training run
  - [x] also should allow stopping in the middle of collecting these results to restart (i.e. per-episode checkpoint)
  - [x] in progress at tests/evaluate_models, but may not be important so leaving alone for now
- [x] 5hz is a bit jerky for good policy..might need higher max movement, or lower stiffness
  - [x] not worth spending excessive time tuning in simulation..should just tune for real world
  - [x] confirmed that max vel in sim is 20 substeps + action mult of .002 is 2mm * 20 = 4cm/step, or 20cm/s
  - [x] dropped to lower stiffness (matching real), might slow down learning though
- [x] drop pos limits way down (comparable to sim env)
  - [x] panda play has 30cm in x, 30cm in y, and 13.5cm in z...we've been testing with much, much larger
  - [x] wayyyy faster learning now
- [x] try double grad updates
  - [ ] appears to learn faster, could rpobably even do 3 updates
- [ ] add option to have success eval added to training (in addition to returns)

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

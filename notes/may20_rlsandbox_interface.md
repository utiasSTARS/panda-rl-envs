# RL Sandbox interface notes

## TODO
- [x] Install rl_sandbox requirements in polymetis env
- [x] make script to generate expert data for new env
- [x] start new branch from LfGP (public) and from VPACE for changes corresponding to this
- [x] allow training of single task reach env
- [x] add training between episodes instead of at steps
- [ ] add restarting training from checkpoint
  - [ ] *probably* want to generate checkpoints after every episode, rather than at the save interval..save interval is just for models we keep long term
- [ ] allow training of multitask reach env
  - [ ] make a new sim task that has aux tasks as well
  - [ ] add aux rewards to rl_sandbox for aux tasks
    - [ ] maybe put them in the panda_rl_envs repo instead, and just import them from there
- [ ] decide on making frame stack 2 default


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

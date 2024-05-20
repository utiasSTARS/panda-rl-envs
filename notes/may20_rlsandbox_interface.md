# RL Sandbox interface notes

## TODO
- [x] Install rl_sandbox requirements in polymetis env
- [x] make script to generate expert data for new env
- [x] start new branch from LfGP (public) and from VPACE for changes corresponding to this

## Off the top of my head fixes
- [ ] add ability to restart training in rl_sandbox from a checkpoint
  - [ ] probably checkpoint frequently...maybe every episode? depends on save time
- [ ] add ability to train between episodes instead of every step
- [ ] *probably* going to make default for panda-rl-envs env_type frame stack 2
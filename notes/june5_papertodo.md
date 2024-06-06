## general todo
- [x] At 5:30, if robot hasn't learned to stop jamming, will change orientation
- [x] door baseline
- [x] door evaluation
  - [x] for evaluating door, use the 50000.pt model for final evaluation, but DO NOT use it for exploratory data! just load from the checkpoint and continue training instead!
- [x] door filming
  - [x] all todo list is now in june6_video_notes instead
- [ ] address Jon's/Bryan's notes

## adding drawer to video(s)
Note: current ratio for example images is: 1.512755715 (w / h)
    - e.g. 726 x 480
- [x] screenshots of expert examples (from video)
- [x] still need screenshots of initial state distribution
  - [x] still need these for door if we keep door
- [ ] get corresponding videos to what we have for other tasks
  - [ ] 5k, 15k, 25k exploration, multi-sqil + sqil
  - [ ] final performance, multi-sqil + sqil

## adding drawer to paper
### text
- [ ] mention in abstract
- [ ] mention in intro
- [ ] environment description in sec. 4.1
- [ ] (appendix, lower priority) corresponding more detailed description in appendix
  - [ ] talk about how approach to scheduling is different in real world
  - [ ] include a labelled screenshot (draw in inkscape)

### figures
- [ ] (matplotlib) add to average normalized results from fig 1
  - [ ] wait for final results from door
- [ ] (matplotlib) add panda rl envs to main performance plot
  - [ ] wait for final results from door
- [x] (inkscape) add examples to Fig. 3
  - [x] both? or just one task?
  - [x] going to try with both!
    - [x] and, therefore, no need for an average plot
- [ ] (matplotlib) add column to fig. 4
- [ ] (appendix, lower priority) (inkscape) add examples fo fig. 8
- [ ] (matplotlib) new figure in appendix with results from both environments
  - [ ] wait for final results from door
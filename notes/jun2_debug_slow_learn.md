# Debugging slow learning in real world
Although calling it slow learning is potentially not quite accurate, since even in sim most things took 50k or more to get to reasonable performance, and we're hoping to see the same in 10k-30k.

## Initial notes
- Both in sim and in reality the robot gets "stuck" in corners for a while before it starts learning
- unclear how much random exploration is needed before starting learning
  - 10k in sim, trying with 400/1000 in reality
- unclear if 4 gradient steps per step is causing overfitting to data

## to test
1. sim with default settings + render for reach, up to 20k
   1. original settings were 5k buffer warmup, 10k random explore
  - stuck in corners?
  - anything else to note?
2. sim with 1k exploration and 4 grad steps
3. higher tau, with or without changing the other settings
4. ...continue on depending on these results


## observations
in sim, home computer: roughly 1min/1000steps (compared to 5min/1000 on real)
- stack with original settings:
  - `debug/06-03-24_09_21_17`
  - gets stuck in corners for most policies from 10k to at least 13k
  - generally looks far less exploratory than random exploration
  - takes 10k steps to start exceeding reward from random exploration
    - after large drop before this, with much time hitting corners and not exploring
- 1k exploration, 1e-3 tau, 4 grad steps:
  - `jun3_1kexp_4grad/06-03-24_09_51_12`
  - `--buffer_warmup 500 --exploration_steps 1000 --num_gradient_updates 4`
  - also showing corner problem, but seems like to a lesser extent
  - learns considerably faster overall, but still takes 10k steps to do better than random exploration
  - is it due to less exploration, or more gradient steps?
- 1k exploration, 5e-3 tau:
  - `jun3_1kexp_5e-3tau/06-03-24_11_35_53`
  - definitely gets stuck in corners for several episodes
  - also takes 10k to beat random exploration
  - at 12k, has obviously learned to drive to corner for main task, takes long time to unlearn this
  - learns faster than original run, but unclear if it's because of 1k explore steps or because of higher tau
  - at 25k, performance starts to approach 4 gradient updates run
- 1k exploration, 1e-3 tau:
  - `jun3_1kexp/06-03-24_12_11_39`
  - need to verify that 4 grad updates/5e-3 tau actually gave the improvement, and not simply less exploration
  - exact same performance as 5e-3 tau (but much lower q loss)
  - actually, slightly better performance than 5e-3 tau
- 1k exploration, 5e-3 tau, 4 gradient updates
- 1k exploration, 5e-2 tau
  - nearly identical performance to others

## conclusions
- 5000 gradient updates while doing 5000 random exploration clearly causes a large drop in performance for the next 5-10k steps, but it's unclear whether this will be overly negative
- 500 buffer warmup, 1000 exploration seems to be totally fine
- 4 gradient updates seems to be strict (minor) improvement
- 5e-3 tau appears to give nearly the same performance boost as 4 gradient updates
- the initial drop betwen random exploration and good performance seems unavoidable
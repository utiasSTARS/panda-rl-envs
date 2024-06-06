## todo
- [x] eval for 5k-45k for door multi-sqil
- [x] sqil train from scratch door
- [x] sqil door timelapse exploration
  - [x] just manually run the camera at the correct-ish times
  - [x] 10k, 30k, 50k real time exploration, same, just run at correct times (for roughly 45s)
- [x] sqil door eval at 50k vid
- [x] sqil door eval for 5k-45k
- [x] 120120 explore vids of drawer

## eval
- good door eval vid roughly at 9:13am
- good door sqil eval vid at 1:21pm

## explore
- door 50k exploration 120120 vid at 9:25am
- door 30k exploration 120120 vid at 9:28am
- door 10k exploration 12012 vid at 9:29am (but none fully did 120120 without crashing)
- door sqil 10k exploration vid at 10:58am
- door sqil 30k exploration vid at 12:19pm
- door sqil 50k exploration vid at 1:08pm
- drawer 25k exploration 120120 vid at 2:02pm
- drawer 15k exploration 120120 vid at 2:04pm
- drawer 5k exploration 120120 vid at 2:05pm (or 2:06pm)

## timelapse explore
- door 50k rougly 9:33am
- door 30k 9:38am
- door 10k 9:43am
- door random exploration at 10:23am
- door 10k sqil timelapse 10:59am
- door 30k sqil timelapse 12:20pm
- door 50k sqil timelapse 1:09pm

## explore code for fixed scheduler
```bash
python evaluate_models.py --env_name PandaDoorNoJamAngleLongEp --exp_name june5_250stiff_p2tvel_5hz --algo multi-sqil --model_min 49000 --model_max 51000 --forced_schedule "{0: 1, 30: 2, 60: 0, 90: 1, 120: 2, 150: 0}" --no_save --max_ep_steps 180 --stochastic
```

```bash
python evaluate_models.py --env_name PandaDrawerLineLongEp --exp_name june3_250stiff_p2tvel_5hz --algo multi-sqil --model_min 24000 --model_max 26000 --forced_schedule "{0: 1, 20: 2, 40: 0, 60: 1, 80: 2, 100: 0}" --no_save --max_ep_steps 120 --stochastic
```
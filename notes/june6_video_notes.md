## todo
- [ ] eval for 5k-45k for door multi-sqil
- [ ] sqil train from scratch door
- [ ] sqil door timelapse exploration
  - [ ] just manually run the camera at the correct-ish times
- [ ] sqil door eval at 50k vid
- [ ] sqil door 120120 exploration
- [ ] sqil door eval for 5k-45k
- [ ] 120120 explore vids of drawer

## eval
- good door eval vid roughly at 9:13am

## explore
- door 50k exploration 120120 vid at 9:25am
- door 30k exploration 120120 vid at 9:28am
- door 10k exploration 12012 vid at 9:29am (but none fully did 120120 without crashing)

## timelapse explore
- door 50k rougly 9:33am
- door 30k 9:38am
- door 10k 9:43am


## explore code for fixed scheduler
```bash
python evaluate_models.py --env_name PandaDoorNoJamAngleLongEp --exp_name june5_250stiff_p2tvel_5hz --algo multi-sqil --model_min 49000 --model_max 51000 --forced_schedule "{0: 1, 30: 2, 60: 0, 90: 1, 120: 2, 150: 0}" --no_save --max_ep_steps 180 --stochastic
```
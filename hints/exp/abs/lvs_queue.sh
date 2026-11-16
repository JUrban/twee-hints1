#!/bin/bash
# (16 Nov 18:00) after LVZ: restore solve_new.sh (HEAD, with LOOPARGS), then run LVS and its curve.
cd /project/hintwork
until [ -f loops/LVZ.done ]; do sleep 20; done
git -C /project/twee checkout hints/solve_new.sh
ARM=LVS bash abs/lvs_test.sh &
until [ -f loops/LVS/config.json ]; do sleep 2; done
ARM=LVS bash abs/replaycurvec.sh

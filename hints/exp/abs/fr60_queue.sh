#!/bin/bash
# start FR60 when LVF is done (17 Nov)
cd /project/hintwork
until [ -f loops/LVF.done ]; do sleep 20; done
ARM=FR60 nohup abs/fr60_test.sh > /dev/null 2>&1 &

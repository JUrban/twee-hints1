#!/bin/bash
# start FO60 when MX60 is done (17 Nov)
cd /project/hintwork
until [ -f loops/MX60.done ]; do sleep 20; done
ARM=FO60 nohup abs/fo60_test.sh > /dev/null 2>&1 &

#!/bin/bash
# start round 3 of the full loop (ul3.sh) when round 2 (unleash.sh) has written loops/UL.done
until [ -s /project/hintwork/loops/UL.done ]; do sleep 60; done
bash /project/hintwork/abs/ul3.sh

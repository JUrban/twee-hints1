#!/bin/bash
# (19 Nov 23:11) exp37: the calibrated models' remaining paired arms, as CPU frees up. rm9gC when the control arm
# (MQ_rm4t_20) ends, rm9hC when rm9a's ends (rmshift.py: each model shifted to defer rm4t's share, 29.6%, at 0.1).
cd /project/hintwork
until [ -f loops/MQ_rm4t_20.done ]; do sleep 30; done
(M=rm9gC T=20 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
until [ -f loops/MQ_rm9a_20.done ]; do sleep 30; done
(M=rm9hC T=20 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)

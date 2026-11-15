#!/bin/bash
# copy-action hint generator (gencopy.py, 15 Nov 16:06): novel targets (--novel loops/UL/hints), encoder and the
# decoder parts of matching shape from gen2 at step 3000; compare with gen4 (novel targets, no copy)
cd /project/hintwork
exec venv/bin/python3 -u /project/twee/hints/gencopy.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
  --test-names sets/ultest --save models/gc1.pt --init-enc models/gen2_3000.pt --steps 6000 \
  --novel loops/UL/hints --eval-every 1000 --eval-n 30 --n 400 --temp 0.7 \
  --threads 4 --ctx 256 --batch 8 --targets 16 --lr 5e-4

#!/bin/bash
# hint generator, continued from gen1 at step 1000 (15 Nov 15:15): no attention dropout and per-sample cross-attention
# (step 2.4 s -> 0.5 s), batch 8 samples, cosine decay, 12000 more steps
cd /project/hintwork
exec venv/bin/python3 -u /project/twee/hints/gen.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
  --test-names sets/ultest --save models/gen2.pt --init-from models/gen1_1000.pt --step0 1000 --steps 12000 \
  --eval-every 2000 --eval-n 60 --n 200 --threads 4 --ctx 256 --batch 8 --targets 16 --lr 1e-3

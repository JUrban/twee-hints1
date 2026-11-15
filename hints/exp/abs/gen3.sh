#!/bin/bash
# hint generator, larger (15 Nov 15:18): d96, decoder 3 layers, from scratch, batch 8, 12000 steps (against gen2 = d64/2)
cd /project/hintwork
exec venv/bin/python3 -u /project/twee/hints/gen.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
  --test-names sets/ultest --save models/gen3.pt --steps 12000 --dim 96 --layers 6 --dlayers 3 \
  --eval-every 2000 --eval-n 60 --n 200 --threads 4 --ctx 256 --batch 8 --targets 16 --lr 1e-3

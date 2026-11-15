#!/bin/bash
# hint generator (gen.py), first real training: d64 L6 decoder 2 layers, ctx 256
cd /project/hintwork
exec venv/bin/python3 -u /project/twee/hints/gen.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
  --test-names sets/ultest --save models/gen1.pt --steps 6000 --eval-every 1000 --eval-n 40 --n 100 \
  --threads 4 --dim 64 --layers 6 --dlayers 2 --ctx 256 --batch 4 --targets 16

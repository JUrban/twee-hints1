#!/bin/bash
# hint generator on novel steps (15 Nov 15:55): gen2 at step 3000 recalled 24/2891 future proof steps (n=400, T 0.7)
# but only 2 of them are missing from the original's pool. Fine-tune gen2_3000 with targets (and cuts) only the
# proof rules no other goal of the original has as a hint (--novel loops/UL/hints).
cd /project/hintwork
exec venv/bin/python3 -u /project/twee/hints/gen.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
  --test-names sets/ultest --save models/gen4.pt --init-from models/gen2_3000.pt --step0 3000 --steps 6000 \
  --novel loops/UL/hints --pool-dir loops/UL/hints --eval-every 1000 --eval-n 30 --n 400 --temp 0.7 \
  --threads 4 --ctx 256 --batch 8 --targets 16 --lr 5e-4

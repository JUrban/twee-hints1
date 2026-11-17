#!/bin/bash
# (17 Nov 18:17) Pcat ENIGMA parental models (pg/pc1.sh: hashed keys of goal-constant-expanded rules, twee-e54) on the
# 200-goal testbed pg/tb at the threshold matching the sum filter's pruning (38% of overlaps): quality at a fixed
# abstract budget; the full forests cost ~30 us per judged pair (35 s CPU against 4.5 s on one run)
cd /project/hintwork/pg
python3 tm/var54.py /project/hintwork/pg/tb "base;--pg-threshold=0.269;--pg-enigma=1024,--pg-model=/project/hintwork/pg/pce_1024.bin,--pg-threshold=0.0052;--pg-enigma=1024,--pg-model=/project/hintwork/pg/pcd_1024.bin,--pg-threshold=0.0007" 5

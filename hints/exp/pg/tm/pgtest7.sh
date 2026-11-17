#!/bin/bash
# (17 Nov 18:21) additive Pcat ENIGMA parental models (pg/pc2.sh; twee-e55 PGEnigmaAdd: each rule scored once in both
# roles, a pair two lookups, CPU as the sum filter's) on the 200-goal testbed pg/tb: ENIGMA only (pca) and with the 10
# numbers per rule (pcad) at the sum filter's pruning (38% of overlaps), pcad stricter (25%); the sum as CPU reference.
# Starts when the half1 A/B (PGA/PGB solve_new.sh, PIDs 2204857 2204864) has ended.
cd /project/hintwork/pg
while kill -0 2204857 2>/dev/null || kill -0 2204864 2>/dev/null; do sleep 30; done
sed -e 's|/project/bin/twee-e54|/project/bin/twee-e55|' tm/var54.py > tm/var55.py
python3 tm/var55.py /project/hintwork/pg/tb "--pg-threshold=0.269;--pg-enigma=1024,--pg-model=/project/hintwork/pg/pca_1024.bin,--pg-threshold=0.0113;--pg-enigma=1024,--pg-model=/project/hintwork/pg/pcad_1024.bin,--pg-threshold=0.0018;--pg-enigma=1024,--pg-model=/project/hintwork/pg/pcad_1024.bin,--pg-threshold=0.005" 6

#!/bin/bash
# (17 Nov 18:00) the same 1,500 late-proved goals as d2, logged by twee-e54 (each rule's hashed ENIGMA keys,
# computed as the rule model's, on the goal-constant-expanded rule), 4 at a time
cd /project/hintwork
RELOG_TWEE=/project/bin/twee-e54 python3 pg/relog.py pg/cap1.log pg/cap1.late.tsv pg/d3 1500 4

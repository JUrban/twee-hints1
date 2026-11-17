#!/bin/bash
# (17 Nov 17:50) after the matched-pruning test: the same 1,500 late-proved goals as d2, logged by twee-e53
# (each rule's raw hashed ENIGMA keys, named and anonymous, in PGR lines), 4 at a time
cd /project/hintwork
until grep -q exited /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/b8wrb8qny.output 2>/dev/null; do sleep 20; done
RELOG_TWEE=/project/bin/twee-e53 python3 pg/relog.py pg/cap1.log pg/cap1.late.tsv pg/d3 1500 4

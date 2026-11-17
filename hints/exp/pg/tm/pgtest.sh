#!/bin/bash
# after the guidance test: e44 vs e46 equivalence (flags off), then parental-guidance thresholds
S=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/nfs
until [ -s /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/b6g2ndv8n.output ]; do sleep 20; done
python3 $S/tm/eq.py $S /project/bin/twee-e44,/project/bin/twee-e46 all.goals 4 2>&1 | tail -3
python3 $S/tm/var46.py $S "base;--pg-threshold=-3;--pg-threshold=-2;--pg-threshold=-1" 4

#!/bin/bash
S=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/nfs
python3 $S/tm/var48.py $S "base;--pg-threshold=0.4;--pg-threshold=0.6;--pg-threshold=0.8;--pg-threshold=0.95" 4

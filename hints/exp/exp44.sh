#!/bin/bash
# exp44 (20 Nov, written 18:44; runs after Z6): the failed-before goals as their own --mix class (loop.py
# --retry-class), from zero on half2, 2 hours, 6 workers: P2H = solve_new.sh's defaults + LOOPARGS=--retry-class,
# against P2E (exp41) and P2F (exp42), the same system without it. In Z6 the first runs of all goals ended at about
# 150 minutes, and then retries of goals with a new context proved 47%, the last first runs 3%.
# notes/2026-11-20-retry-class.md
cd /project/hintwork
LOOPARGS="--retry-class" SET=sets/half2 ARM=P2H bash abs/or_test2.sh
echo "exp44 done $(date +%T)" > loops/exp44.done

#!/bin/bash
# exp4 stage 1 (17 Nov): moves for the 47 exp3 goals (moves.py, Mace4 screen, 2 goals at a time, one file each),
# then the 5 s sketches of the kept moves (sketch.py -j 2). Run from /project/hintwork/exp4.
set -e
mkdir -p mv
xargs -P 2 -I{} sh -c '[ -s mv/{}.tsv ] || python3 moves.py {} --secs 5 --out mv/{}.tsv' < /project/hintwork/exp3/goals47
cat mv/*.tsv > moves47.tsv
python3 sketch.py moves47.tsv sketch47.tsv -j 2 --time 5
echo done

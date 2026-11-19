#!/bin/bash
# exp24/run.sh (19 Nov 03:55): production's 80 s chain level (L1) on 40 far goals that production only ever gives
# 5 s runs (sample.txt: far.py 24 40; far = more than 1 place and more than 80 proof lines after the nearest proven
# goal below, and no run over 30 CPU s). loop.py with ul56's flags, cascade 5,80 from level 0 (the 5 s run counts as
# tried in the current context), --frontier 1000000 so every goal may deepen, no variants, no scheduler, 2 workers.
set -e
cd /project/hintwork/exp24
[ -e F ] && { echo "F exists"; exit 1; }
mkdir -p F.ctx/hints
python3 - <<'PY'
import os, shutil
G = {l.strip() for l in open('sample.txt') if l.strip()}
n = 0
with open('F.ctx/solved.tsv', 'w') as f:
    for l in open('/project/hintwork/loops/UL/solved.tsv'):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 3 and w[0] not in G and os.path.exists('/project/hintwork/loops/UL/hints/' + w[0]):
            f.write(f'{w[0]}\t0\t{w[2]}\n'); n += 1
            shutil.copy2('/project/hintwork/loops/UL/hints/' + w[0], 'F.ctx/hints/' + w[0])
print('context:', n, 'proofs')
PY
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
LOOP_PRINT_CMD=1 python3 -u /project/twee/hints/loop.py sample.txt F --init F.ctx --start 5 --cascade 5,80 --cascade-start 0 \
  --retry-gap 3 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j 2 --reserve 0 \
  --pool original --wall-factor 15 --line-gaps 80,80 --frontier 1000000 --retry-hints 1.25 --fresh-first --retry-knn \
  --chain-level 1 --chain-records /project/hintwork/chain_records2.tsv --pass-every 1 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > F.log 2>&1
echo "$(date +%T) end" >> F.log

#!/bin/bash
# (23 Nov 19:50) exp67's control arm CC67 (notes/2026-11-23-climber-restart.md, "The control"): the 91 frozen heads
# (loops/EXP67.heads), exp67's frozen context (the t1854 trusted goals and their hints), one final run per head and no
# sketch runs (climb.py --runs 0, no fill), at arm A's (CLA67) mean CPU per finished target at the start, in abstract s
# (/1.07 CPU s per abstract s). The 14 Nov lesson: the climb's apparent gain was its long final run. Starts when exp65
# ends (loops/Q5A.done, Q5B.done), so its 8 CPUs are free; gives up at 24 Nov 02:00.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
END=$(date -d "2026-11-24 02:00" +%s)
until [ -e loops/Q5A.done -a -e loops/Q5B.done ] || [ $(date +%s) -gt $END ]; do sleep 60; done
[ -e loops/Q5A.done -a -e loops/Q5B.done ] || { echo "exp65 not done by the deadline" >> loops/EXP67.pids; exit 1; }
[ -e loops/CC67 ] && { echo "loops/CC67 exists" >> loops/EXP67.pids; exit 1; }
FT=$(python3 - <<'PY'
cpu = 0; fin = set()
for l in open('loops/CLA67/climb.tsv'):
    w = l.rstrip('\n').split('\t')
    try: cpu += float(w[5])
    except: pass
    if w[1] == 'final': fin.add(w[0])
own = {l.split('\t')[0] for l in open('loops/CLA67/solved.tsv') if l.split('\t')[1:2] == ['1']}
n = len(fin | own)
print(round(cpu / max(n, 1) / 1.07))
PY
)
echo "CC67 final time $FT abstract s (CLA67's CPU per finished target) $(date '+%d %T')" >> loops/EXP67.pids
python3 - loops/TRUSTNOW/t1854.trusted loops/CC67 <<'PY'
import os, sys, shutil
tr, d = sys.argv[1], sys.argv[2]
os.makedirs(f'{d}/hints')
T = [l.split()[0] for l in open(tr) if l.strip()]
open(f'{d}/solved.tsv', 'w').write(''.join(f'{g}\t0\t0.0\n' for g in T))
n = 0
for g in T:
    s = f'/project/hintwork/loops/UL/hints/{g}'
    if os.path.exists(s):
        shutil.copyfile(s, f'{d}/hints/{g}'); n += 1
print(d, len(T), 'solved', n, 'hints')
PY
CTX="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15"
nohup python3 -u /project/twee/hints/climb.py sets/all loops/CC67 --targets loops/EXP67.heads --m 8 --knn 8 --theories 4 \
  --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --min-sketch-steps 30 --runs 0 \
  --final-time $FT -j ${J:-4} -- $CTX --lemmas 6 --lemma-knn 30 --args="--abstract-time 2000 --no-eqhint-consider" > loops/CC67.log 2>&1 &
echo "CC67 $! $(date '+%d %T')" >> loops/EXP67.pids
wait
echo "CC67 done $(date '+%d %T')" >> loops/EXP67.pids

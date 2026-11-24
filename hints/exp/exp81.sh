#!/bin/bash
# (24 Nov, exp81, notes/2026-11-24-plain-time.md) Do longer plain runs pay on the local heads that fail at 60 s?
# HLW1 (exp72) proved 4 of its first 123 local heads at 60 s, all within 27 s; on the first heads, CC67D's long hinted
# runs proved 6 of their 9 after 150 CPU s. Set: 60 of HLW1's failed goals still unsolved at launch, random.seed(81)
# from the sorted list (cond/EXP81.set). Context: loops/UL/solved.tsv at launch (both arms the same). Arms, plain,
# H's lemma lists (100+30 siblings, 400 kNN), 2 threads each, at the same time:
#   P81A: 60 s, the control (the context moved since HLW1, so a proof here is the context's, not time's)
#   P81B: 300 s
#   P81C (after P81A, on its 2 threads): 60 s with every earlier sibling (--sibs 1000) and 100 later, 400 kNN: no plain
#   run at 60 s had more than 100+30 siblings (5 s: 200+60 with 1,000 kNN), and a long original's later goals miss
#   most of their proved earlier siblings, which are steps of the same Prover9 proof
# Waits for exp76's end (loops/EXP76.pids "exp76 done", its 4 threads), so the total stays near 20.
cd /project/hintwork
until grep -q "^exp76 done" loops/EXP76.pids 2>/dev/null; do sleep 60; done
cut -f1 loops/UL/solved.tsv | sort -u > cond/EXP81.trusted
python3 - <<'PY'
import random
T = {l.strip() for l in open('cond/EXP81.trusted') if l.strip()}
F = sorted({l.split('\t')[0] for l in open('cond/HLW1/results.tsv') if l.split('\t')[1] == 'NO'} - T)
random.seed(81)
open('cond/EXP81.set', 'w').writelines(g + '\n' for g in sorted(random.sample(F, 60)))
print(len(F), 'failed and unsolved; 60 sampled')
PY
echo "exp81 start $(date '+%d %T') context $(wc -l < cond/EXP81.trusted) set $(wc -l < cond/EXP81.set)" >> cond/EXP81.status
arm() {   # NAME TIME SIBS AFTER
  n=$1; tm=$2
  python3 -u /project/twee/hints/exp/condprove.py cond/$n --trusted cond/EXP81.trusted -j 2 --proved --time $tm \
    --sibs $3 --after $4 --knn 400 --only cond/EXP81.set > cond/$n.log 2>&1
  python3 /project/twee/hints/exp/condimport.py cond/$n loops/CI3 --trusted cond/EXP81.trusted --time $tm > cond/$n.import 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/$n.merge 2>&1
  echo "$n done $(date '+%d %T') ran $(grep -c . cond/$n/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$n/results.tsv) | $(tail -1 cond/$n.import) | $(tail -1 cond/$n.merge)" >> cond/EXP81.status
}
( arm P81A 60 100 30; arm P81C 60 1000 100 ) &
arm P81B 300 100 30 &
wait
echo "exp81 done $(date '+%d %T')" >> cond/EXP81.status

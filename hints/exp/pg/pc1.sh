#!/bin/bash
# (17 Nov 18:12) Pcat parental models on hashed ENIGMA keys of the goal-constant-expanded rules (twee-e54 logs
# pg/d3), as FroCoS 2021: P_proof labels, negatives sampled to 8 per positive in each training run, bases 1k/4k/8k;
# 60 held-out runs with all negatives for the offline check and the threshold matching the sum filter's pruning.
# Models: pce_B (the two ENIGMA vectors only, as the paper), pcd_B (+ both rules' 10 features and the id gap).
cd /project/hintwork/pg
ls d3/*.err | python3 -c "import sys,random; f=sorted(sys.stdin.read().split()); random.Random(1).shuffle(f); open('e3.test','w').write('\n'.join(f[:60])+'\n'); open('e3.train','w').write('\n'.join(f[60:])+'\n')"
P=/project/hintwork/venv/bin/python3; H=/project/twee/hints
for B in 1024 4096 8192; do
  ( $P $H/pgdata_enigma.py $B e3tr_$B $(cat e3.train) --neg 8 && $P $H/pgdata_enigma.py $B e3te_$B $(cat e3.test) ) > e3data_$B.log 2>&1 &
done
wait
for B in 1024 4096 8192; do
  $P $H/pgtrain_enigma.py e3tr_$B e3te_$B pce_$B --trees 100 --leaves 255 --enigma-only > pce_$B.log 2>&1
  $P $H/pgtrain_enigma.py e3tr_$B e3te_$B pcd_$B --trees 100 --leaves 255 > pcd_$B.log 2>&1
done
echo done > pc1.done

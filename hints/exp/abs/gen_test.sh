#!/bin/bash
# Online test of the hint generator (gen.py, 15 Nov; user: a GNN2Seq-style model proposing hints from the run's
# current situation). sets/gen200: 200 goals unsolved at 14:31 whose last production run was a failed fresh 5 s
# run; snapshot loops/ULsW (14:31). Round 1 = fresh 5 s (identical in all arms), round 2 = resume +15 s with the
# pool hints, + in the gen arms the --gen-n hints the generator samples from the goal and round 1's last 256 rules.
#   ARM=GC bash abs/gen_test.sh          (control)
#   ARM=GG M=models/gen1.pt REQ=--resume-requeue bash abs/gen_test.sh   (the saved queue re-scored against the new hints)
cd /project/hintwork
D=${ARM}
G=""; [ -n "$M" ] && G="--gen-model /project/hintwork/$M --gen-n ${N:-200} --gen-temp ${TEMP:-1.0} --gen-script ${GS:-gen.py}"
python3 -u /project/twee/hints/loop.py sets/${SET:-gen200} loops/$D --init loops/ULsW --start 1 --rounds 2 --timeout 0,5,15 \
  --resume --keep-out -j ${J:-2} --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee ${TWEE:-/project/bin/twee-e39} $G \
  --args="--abstract-time 2000 ${REQ:---no-resume-requeue} --no-eqhint-consider ${X}" > loops/$D.log 2>&1
echo "$D r1 $(grep -c THM loops/$D/r1/results.tsv) r2 $(grep -c THM loops/$D/r2/results.tsv)/$(wc -l < sets/${SET:-gen200}) $(date +%T)" | tee loops/$D.done

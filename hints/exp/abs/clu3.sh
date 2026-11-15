#!/bin/bash
# (15 Nov 23:46: + --theory-explore 2, two of the four theory slots random, theories.tsv logs the choice, for
# learning which stronger theory to assume.) Live up-down climber with the learned move policy as an A/B test (15 Nov 23:44; abs/clu.sh + --move-model
# MODEL --move-ab: targets of odd crc32 sample moves by the policy, the others take the fixed order; climb.tsv tells
# which is which by the name). Log appended. Earlier header (abs/clu.sh, 22:10): climb.py --live loops/UL takes UL's stalled goals (as abs/clive.sh)
# with the family test's full config (FUD, REPORT 2aj: 8 siblings + 8 kNN goals + 4 stronger theories with 10 of their
# lemmas each, up = theory unions / one more axiom / weaker goals, down, gap filling 3 s, --chain). It fills idle CPUs:
# climbs start only while fewer than --cpus twee processes run (others than its own). Real proofs go into loops/UL.
# Each sketch's proof is saved (loops/CLU/sketches) for learning the lattice moves.
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/all loops/CLU --live loops/UL \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 --min-sketch-steps 30 --move-model "${MODEL:-/project/hintwork/models/lattice1.json}" --move-ab \
  --runs 20 --sketch-time 5 --final-time 20 -j "${J:-6}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CLU.log 2>&1
echo "CLU $(tail -1 loops/CLU.log) $(date +%T)" | tee loops/CLU.done

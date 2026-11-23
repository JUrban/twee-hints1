#!/bin/bash
# Live head climber (16 Nov 06:40; --lemma-knn 30 from 07:47, as production, 2am): after abs/clh.sh (long climbs on the 111 heads: 12 of the first 65 proved,
# 1.4 per CPU hour), climb.py --live loops/UL --heads-only --reclimb-heads 3 climbs each original's first unsolved
# goal as it appears, and a climbed head again once its original has gained a proof, with clh.sh's config (160 s
# final run, 24 sketch runs). loops/CLHL starts from CLH's climb.tsv, so CLH's heads count as climbed.
cd /project/hintwork
mkdir -p loops/CLHL && [ -f loops/CLHL/climb.tsv ] || cp loops/CLH/climb.tsv loops/CLHL/climb.tsv
python3 /project/twee/hints/climb.py sets/all loops/CLHL --live loops/UL --heads-only --reclimb-heads 3 \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 160 -j "${J:-4}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CLHL.log 2>&1

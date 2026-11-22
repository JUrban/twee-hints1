#!/bin/bash
# (22 Nov 16:33) exp62 (notes/2026-11-22-o2-build.md): twee-e61 built with -O2 (tw61o2 worktree, commit 7e0c271)
# against the production binary (cabal's default -O1). abs/rd5.sh's command (sets/z8u300 in loops/Z8F.ctx, 5 abstract
# s, 1 worker) in two arms at once: loops/OB1 (twee-pg61) and loops/OB2 (twee-pg61o2). Identical searches expected.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
for a in OB1 OB2; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
echo "start $(date '+%d %T')" > loops/OB.pids
for arm in OB1:twee-pg61 OB2:twee-pg61o2; do
  A=${arm%%:*}; B=${arm#*:}
  python3 -u /project/twee/hints/loop.py sets/z8u300 loops/$A --init loops/Z8F.ctx --start 1 --rounds 1 --keep-out -j 1 \
    --pool original --wall-factor 15 \
    --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
    --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/$B --timeout 5 \
    --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/$A.log 2>&1 &
  echo "$A $! $B" >> loops/OB.pids
done
wait
echo "done $(date '+%d %T')" >> loops/OB.pids

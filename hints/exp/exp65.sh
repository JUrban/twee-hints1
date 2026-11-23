#!/bin/bash
# (23 Nov 13:15) exp65 (notes/2026-11-23-lemma-ranker.md, "exp65"): the learned lemma ranker for every run from zero.
# Two arms as exp64's (abs/or_test3.sh, sets/half2, 4 workers, 6 hours, the same CPU sets), started after exp64 ends
# (loops/EXP64.pids "exp64 done"):
#   Q5A: the control, DEEP_A (exp64's better arm, set at the launch);
#   Q5B: DEEP_A with --lemma-ranker models/lemmarank/lr2 --lemma-ranker-all: every run's kNN lemmas (all levels and
#        kN/pl variants; not kp, kd or cut candidates) re-ranked from the similarity list's top 1,000 once the
#        ranker is built (start_vix, rebuilt with each kNN refresh).
cd /project/hintwork
DEEP_A=${DEEP_A:?}
until grep -q "exp64 done" loops/EXP64.pids 2>/dev/null; do sleep 30; done
sleep 120
for a in Q5A Q5B; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
echo "DEEP $DEEP_A" > loops/EXP65.args
echo "Q5B LOOPARGS --lemma-ranker /project/hintwork/models/lemmarank/lr2 --lemma-ranker-all" >> loops/EXP65.args
DEEP="$DEEP_A" CPUSET="0-6,28-34" J=4 HOURS=6 SET=sets/half2 ARM=Q5A LOOPARGS="" nohup bash abs/or_test3.sh > /dev/null 2>&1 &
echo "Q5A $! $(date '+%d %T')" >> loops/EXP65.pids
DEEP="$DEEP_A" CPUSET="7-13,35-41" J=4 HOURS=6 SET=sets/half2 ARM=Q5B \
  LOOPARGS="--lemma-ranker /project/hintwork/models/lemmarank/lr2 --lemma-ranker-all" nohup bash abs/or_test3.sh > /dev/null 2>&1 &
echo "Q5B $! $(date '+%d %T')" >> loops/EXP65.pids
wait
echo "exp65 done $(date '+%d %T')" >> loops/EXP65.pids

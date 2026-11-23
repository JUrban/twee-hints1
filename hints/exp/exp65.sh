#!/bin/bash
# (23 Nov) exp65 (notes/2026-11-23-plain-sizes.md): larger kNN lists in the plain levels, from zero. The ranker design
# (every run's kNN lemmas from lr2h) was dropped before its start: on 235 held-out Z9 gap goals the ranked list lost to
# similarity at 30, 100 and 400 lemmas, and the list's size mattered more than its order (11/20/22/35/35 proofs at
# 30/100/200/400/800 similarity lemmas; notes/2026-11-23-lemma-ranker.md "Size, not order").
# Two arms as exp64's (abs/or_test3.sh, sets/half2, 4 workers, 6 hours), started after exp64 ends:
#   Q5A: the control, exp64's P4B (plain levels plk100s40@0 and plk400s130@0), on P4B's CPU set (so Q5A against P4B is
#        a cross-time replica of one configuration: the noise);
#   Q5B: the same with both plain levels' kNN lists four times as long: plk400s40@0 and plk1600s130@0 (the siblings as
#        P4B's; the pre-checks had no siblings: --set sets/z9gap500 left the sibling pool empty), on P4A's CPU set.
cd /project/hintwork
until grep -q "exp64 done" loops/EXP64.pids 2>/dev/null; do sleep 30; done
sleep 120
for a in Q5A Q5B; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
V="--chain-level 1 --variants unf@0,@P1@,@P2@,k60@0,k100@0,k200@0,k400@0,kd@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1,V@P1@=3,V@P2@=3 --ratio-order --explore 0.2 --explore-labels L1,Vk100@0,Vk200@0,Vk400@0,Vkd@0,V@P1@,V@P2@"
DA=$(echo "$V" | sed 's/@P1@/plk100s40@0/g; s/@P2@/plk400s130@0/g')
DB=$(echo "$V" | sed 's/@P1@/plk400s40@0/g; s/@P2@/plk1600s130@0/g')
echo "Q5A DEEP $DA" > loops/EXP65.args; echo "Q5B DEEP $DB" >> loops/EXP65.args
DEEP="$DA" CPUSET="7-13,35-41" J=4 HOURS=6 SET=sets/half2 ARM=Q5A LOOPARGS="" nohup bash abs/or_test3.sh > /dev/null 2>&1 &
echo "Q5A $! $(date '+%d %T')" >> loops/EXP65.pids
DEEP="$DB" CPUSET="0-6,28-34" J=4 HOURS=6 SET=sets/half2 ARM=Q5B LOOPARGS="" nohup bash abs/or_test3.sh > /dev/null 2>&1 &
echo "Q5B $! $(date '+%d %T')" >> loops/EXP65.pids
wait
echo "exp65 done $(date '+%d %T')" >> loops/EXP65.pids

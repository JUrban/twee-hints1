#!/bin/bash
# (20 Nov 10:50) Step joins as a live member (notes/2026-11-20-step-join.md): every EVERY seconds (default 1800),
# exp/joincheck.py over all of production's unsolved goals (unit goals in two shards, conditional goals with their
# hypothesis as a ground rule), then exp/stepjoin.py proves the joins with the steps as named lemma axioms into
# loops/UL. The bank is production's proofs; while the re-verification runs (loops/REVER2), only the trusted ones
# (its newest trust*.trusted).
# (20 Nov 11:25) stepjlive2: the re-verification dir is REV (default loops/REVER3), its driver PID in REV/pid.
#   stepjlive.sh [EVERY] [FIRST-DELAY]
EVERY=${1:-1800}
H=/project/twee/hints
cd /project/hintwork || exit 1
export OMP_NUM_THREADS=1
c=1
[ -n "$2" ] && sleep "$2"
while :; do
  D=loops/JOIN/c$c
  mkdir -p $D
  TR=
  REV=${REV:-loops/REVER3}
  t=$(ls -t $REV/trust*.trusted 2>/dev/null | head -1)
  if [ -n "$t" ] && kill -0 "$(cat $REV/pid 2>/dev/null)" 2>/dev/null; then TR="--trusted $t"; fi
  echo "cycle $c $(date +%T) bank ${t:-all}"
  python3 $H/exp/joincheck.py $D/u0.tsv -n 100000 $TR --shard 0/2 > $D/u0.log 2>&1 &
  p0=$!
  python3 $H/exp/joincheck.py $D/u1.tsv -n 100000 $TR --shard 1/2 > $D/u1.log 2>&1 &
  p1=$!
  python3 $H/exp/joincheck.py $D/c.tsv -n 100000 --cond $TR > $D/c.log 2>&1
  wait $p0 $p1
  tail -qn1 $D/u0.log $D/u1.log $D/c.log
  python3 $H/exp/stepjoin.py loops/STEPJ $D/u0.tsv $D/u1.tsv $D/c.tsv $TR -j 2 > $D/stepjoin.log 2>&1
  grep 'joined goals\|^transfer:' $D/stepjoin.log | tail -2
  awk -F'\t' '{n++; if($2=="THM")t++} END{print "STEPJ total: "n" runs, "t" THM"}' loops/STEPJ/transfer.tsv
  c=$((c + 1))
  sleep "$EVERY"
done

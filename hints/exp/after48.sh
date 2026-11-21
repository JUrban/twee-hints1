#!/bin/bash
# (21 Nov 05:00) exp49's launcher (notes/2026-11-21-quick-first.md). When exp48 ends (loops/P2N.done and
# loops/P2O.done): waits up to 20 minutes for loops/GO49 (written after reading exp48's 5-hour result), then starts
# two half2 arms from zero, 6 workers, 5 hours, on exp48's winner's base B:
#   P2Q: B + --quick 1
#   P2R: B (the control)
# B is P2O's options if P2O has at least P2N + 185 of sets/half2 solved at the end, else P2N's; a non-empty
# loops/<ARM>.args replaces an arm's options. Production stays paused. PIDs in loops/AFTER48.pids.
cd /project/hintwork
until [ -e loops/P2N.done ] && [ -e loops/P2O.done ]; do sleep 60; done
T=$(( $(date +%s) + 1200 ))
until [ -e loops/GO49 ] || [ $(date +%s) -ge $T ]; do sleep 20; done
BN="--retry-class --yield-discount 2000 --reexplore 12:0.25"
BO="$BN --knn-ctx 10 --head-class"
W=$(python3 - <<'EOF'
H = {l.strip() for l in open('sets/half2') if l.strip()}
sv = lambda d: len({l.split('\t')[0] for l in open(f'loops/{d}/solved.tsv') if l.strip()} & H)
n, o = sv('P2N'), sv('P2O')
print('O' if o >= n + 185 else 'N', n, o)
EOF
)
echo "exp48 at the end: $W $(date +%T)" >> loops/AFTER48.pids
case "$W" in O*) B="$BO" ;; *) B="$BN" ;; esac
for A in P2Q P2R; do
  if [ -e loops/$A ]; then echo "loops/$A exists, not started" >> loops/AFTER48.pids; continue; fi
  if [ $A = P2Q ]; then LA="$B --quick 1"; else LA="$B"; fi
  [ -s loops/$A.args ] && LA=$(cat loops/$A.args)
  HOURS=5 SET=sets/half2 ARM=$A LOOPARGS="$LA" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
  echo "$A $! $(date +%T) LOOPARGS=$LA" >> loops/AFTER48.pids
done

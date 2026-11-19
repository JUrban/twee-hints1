#!/bin/bash
# exp25/run.sh (19 Nov 05:22): does queue renormalisation change twee's search under the abstract clock? exp11's 80 s
# chain commands (s1.cmds) for 6 walls (3 that exp11 proved, 3 it did not), run with production's binary and flags
# (twee-pg61, TWEE_PG_ARGS) in three arms: base (as production), k008 (--queue-cost 0.008: renormalisation charged
# its real cost, so its 5% budget binds) and never (--cp-renormalise-threshold 1000: no renormalisation). Each output
# is kept whole (out/ARM.GOAL), with /usr/bin/time's CPU and peak RSS in err/. 2 workers.
cd /project/hintwork/exp25
mkdir -p out err
job() {
  g=$1; arm=$2
  c=$(grep "^$g	" /project/hintwork/exp11/s1.cmds | cut -f2 | sed 's#/project/bin/twee-e48#/project/bin/twee-pg61#')
  case $arm in base) x="";; k008) x="--queue-cost 0.008";; never) x="--cp-renormalise-threshold 1000";; esac
  TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100 $x" /usr/bin/time -f "TIME %U %S %M" $c > out/$arm.$g 2> err/$arm.$g
}
export -f job
for g in $(cat goals6); do for arm in base k008 never; do echo "$g $arm"; done; done | xargs -P 2 -n 2 bash -c 'job "$0" "$1"'
echo "$(date +%T) end" > done

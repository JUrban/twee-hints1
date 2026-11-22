#!/bin/bash
# (22 Nov; notes/2026-11-22-floor-ratio-until.md "120 minutes") abs/or_test2.sh with a CPU set per arm. In exp60 the
# kernel kept each arm's runs near its loop.py, and the control, alone on socket 0, ran about 10% faster per abstract
# second than the two arms that shared socket 1 with production. CPUSET (a taskset -c list; the whole tree inherits
# it) gives each arm whole cores on both sockets, e.g. "0-6,28-34" (socket 0: CPUs 0-27, siblings 56-83; socket 1:
# 28-55, siblings 84-111). Otherwise as or_test2.sh: ${SET:-sets/half1}, J workers, HOURS, SCHED= , transfer every 5
# minutes, solve_new.sh's defaults plus LOOPARGS.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
PIN=(); [ -n "${CPUSET:-}" ] && PIN=(taskset -c "$CPUSET")
SCHED= XEVERY=300 LOOPARGS="$LOOPARGS" "${PIN[@]}" bash loops/$ARM.solve_new.sh ${SET:-sets/half1} loops/EMPTY loops/$ARM ${J:-6} ${HOURS:-2} > loops/$ARM.out 2>&1
touch loops/$ARM.done

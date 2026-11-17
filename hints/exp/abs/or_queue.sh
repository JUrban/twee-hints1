#!/bin/bash
# (17 Nov 11:30) after ORC (5,20,80,320 s) and ORD (control repeat): ORE = twee-e43 + --lean-states (no state for
# proved goals, nor for fresh runs of goals that may not deepen), ORF = ORE + 5,20,80,320 s. sets/half1, 6 workers, 2 h.
cd /project/hintwork
until [ -f loops/ORC.done ] && [ -f loops/ORD.done ]; do sleep 30; done
ARM=ORE TWEE=/project/bin/twee-e43 LOOPARGS=--lean-states bash abs/or_test.sh &
sleep 2
ARM=ORF TWEE=/project/bin/twee-e43 CASCADE=5,20,80,320 LOOPARGS=--lean-states bash abs/or_test.sh &
wait

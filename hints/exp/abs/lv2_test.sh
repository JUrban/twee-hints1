#!/bin/bash
# From-scratch knobs (16 Nov 16:15), as abs/lv_test.sh (sets/rp3, clean context, 4 workers, 1 hour; control LVA 933):
# ARM=LVC KNN=60 (60 kNN lemmas), ARM=LVD XEVERY=120 (the transfer every 2 minutes instead of 10).
cd /project/hintwork
EXCLUDE=originals KNN=${KNN:-30} XEVERY=${XEVERY:-600} /project/twee/hints/solve_new.sh sets/rp3 loops/ALL loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done

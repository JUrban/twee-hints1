#!/bin/bash
# (23 Nov) After PLN2: import and merge its proofs (loops/CI2), then start abs/plainlive.sh (PREV=cond/PLN2).
cd /project/hintwork
until grep -q "PLN2 done" cond/PLN2.pids 2>/dev/null; do sleep 30; done
python3 /project/twee/hints/exp/condimport.py cond/PLN2 loops/CI2 --trusted loops/TRUSTNOW/t0641.trusted > cond/PLN2.import 2>&1
python3 /project/twee/hints/merge.py loops/UL loops/CI2 > cond/PLN2.merge 2>&1
echo "PLN2 imported $(date '+%d %T'): $(tail -1 cond/PLN2.import) | $(tail -1 cond/PLN2.merge)" >> cond/PLN2.pids
PREV=cond/PLN2 exec bash abs/plainlive.sh

#!/bin/bash
# (23 Nov) abs/lrab.sh's steps 3-4 without its wait for c${CYC}W's end (the context file is all PLL1 needs; the queue
# had already ended, its other sweeps held): PLL1 on cond/PLNL/c$CYC.trusted with lr1, then into loops/CI3 and UL.
cd /project/hintwork
CYC=${CYC:?}; PY=/project/hintwork/venv/bin/python3
[ -e cond/PLL1 ] && { echo "cond/PLL1 exists"; exit 1; }
echo "PLL1 start $(date '+%d %T') context cond/PLNL/c$CYC.trusted ($(wc -l < cond/PLNL/c$CYC.trusted))" > cond/PLL1.pids
$PY -u /project/twee/hints/exp/condprove.py cond/PLL1 --trusted cond/PLNL/c$CYC.trusted -j 3 --time 5 --sibs 100 --after 30 \
  --knn 400 --proved --index learned:models/lemmarank/lr1 > cond/PLL1.log 2>&1
echo "PLL1 done $(date '+%d %T') exit $?" >> cond/PLL1.pids
python3 /project/twee/hints/exp/condimport.py cond/PLL1 loops/CI3 --trusted cond/PLNL/c$CYC.trusted > cond/PLL1.import 2>&1
flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/PLL1.merge 2>&1
echo "PLL1 imported $(date '+%d %T'): $(tail -1 cond/PLL1.import) | $(tail -1 cond/PLL1.merge)" >> cond/PLL1.pids

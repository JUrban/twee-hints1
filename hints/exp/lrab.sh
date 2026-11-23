#!/bin/bash
# (23 Nov) The lemma ranker on the frontier (notes/2026-11-23-lemma-ranker.md, "Frontier test"):
# 1. after RKD1: data from RKD1 and the frontier sweeps, the grouped CV (cond/LR1.eval), model models/lemmarank/lr1;
# 2. the sweep queue paused after its current sweep (cond/SWEEPQ.stop);
# 3. PLL1: W's sizes (100+30 siblings, 400 kNN) ranked by lr1, on production's unsolved goals in the context of the
#    live loop's cycle c$CYC (cond/PLNL/c$CYC.trusted): that cycle's W run (c${CYC}W, the changed problems; the rest
#    failed under W with the same problem before) is the control in the same context;
# 4. PLL1's proofs into loops/CI3 and loops/UL; the queue restarted.
cd /project/hintwork
CYC=${CYC:?}; PY=/project/hintwork/venv/bin/python3; L=/project/twee/hints/exp/lemmarank.py
until grep -q "RKD1 done" cond/RKD1.pids 2>/dev/null; do sleep 30; done
$PY $L data cond/LR1.pkl cond/RKD1 cond/PLW1 cond/PLK1 cond/PLN1 cond/PLN2 cond/PLZ8 > cond/LR1.data 2>&1
$PY $L eval cond/LR1.pkl > cond/LR1.eval 2>&1
$PY $L train cond/LR1.pkl models/lemmarank/lr1 >> cond/LR1.data 2>&1
touch cond/SWEEPQ.stop
while kill -0 $(cat cond/SWEEPQ.pid) 2>/dev/null; do sleep 30; done
until [ -s cond/PLNL/c$CYC.trusted ] && grep -q "^c${CYC}W " cond/PLNL/log; do sleep 30; done
echo "PLL1 start $(date '+%d %T') context cond/PLNL/c$CYC.trusted ($(wc -l < cond/PLNL/c$CYC.trusted))" > cond/PLL1.pids
$PY -u /project/twee/hints/exp/condprove.py cond/PLL1 --trusted cond/PLNL/c$CYC.trusted -j 3 --time 5 --sibs 100 --after 30 \
  --knn 400 --proved --index learned:models/lemmarank/lr1 > cond/PLL1.log 2>&1
echo "PLL1 done $(date '+%d %T') exit $?" >> cond/PLL1.pids
python3 /project/twee/hints/exp/condimport.py cond/PLL1 loops/CI3 --trusted cond/PLNL/c$CYC.trusted > cond/PLL1.import 2>&1
flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/PLL1.merge 2>&1
echo "PLL1 imported $(date '+%d %T'): $(tail -1 cond/PLL1.import) | $(tail -1 cond/PLL1.merge)" >> cond/PLL1.pids
rm -f cond/SWEEPQ.stop
nohup bash abs/sweepq.sh > cond/sweepq.out 2>&1 &
echo $! > cond/SWEEPQ.pid
echo "queue restarted $(date '+%d %T') pid $(cat cond/SWEEPQ.pid)" >> cond/PLL1.pids

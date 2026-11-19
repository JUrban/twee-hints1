#!/bin/bash
# exp23/stage2.sh PID (19 Nov 02:46): after V5 (PID, its p9twee) ends, Veroff's settings at max_weight 40 and at the default
# 100, 1 worker each. V5 proved 0 of its first 46 walls at 37 CPU s a run (strict hint following needs hints from the
# goal's own earlier attempts, not siblings'); V100 isolates kbo, lex_order_vars, no back_demod, restrict_denials,
# para_from_small and no cac_redundancy from the weight limit.
cd /project/hintwork/exp23
while kill -0 $1 2>/dev/null; do sleep 30; done
P9=/project/twee/hints/p9twee.py; UL=/project/hintwork/loops/UL
V="assign(order, kbo). set(lex_order_vars). clear(back_demod). set(restrict_denials). set(para_from_small). clear(cac_redundancy)."
for W in 40 100; do
  echo "$(date +%T) start V$W" >> stage.log
  python3 $P9 walls107 $UL out_V$W --timeout 60 -j 1 --solved-rows 45414 --chain /project/hintwork/chain_records.tsv \
    --settings "$V assign(max_weight, $W)." > V$W.out 2>&1
done
echo "$(date +%T) end" >> stage.log

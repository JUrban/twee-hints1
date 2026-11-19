#!/bin/bash
# exp23/stage.sh: Prover9 with Veroff's AIM settings (AIM_REDONE .in files) and chain hints on exp16's 107 walls at
# 60 s, max_weight 5, 10, 20, 40 in turn, 1 worker each; hints, lemmas and proven state exactly as exp16's Q arm
# (UL's first 45,414 solved rows, chain_records.tsv), so the only change against Q is the settings.
cd /project/hintwork/exp23
P9=/project/twee/hints/p9twee.py; UL=/project/hintwork/loops/UL
V="assign(order, kbo). set(lex_order_vars). clear(back_demod). set(restrict_denials). set(para_from_small). clear(cac_redundancy)."
for W in 5 10 20 40; do
  echo "$(date +%T) start V$W" >> stage.log
  python3 $P9 walls107 $UL out_V$W --timeout 60 -j 1 --solved-rows 45414 --chain /project/hintwork/chain_records.tsv \
    --settings "$V assign(max_weight, $W)." > V$W.out 2>&1
done
echo "$(date +%T) end" >> stage.log

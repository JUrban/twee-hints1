#!/bin/bash
# exp23/stage3.sh (19 Nov 04:10): the rest of exp23 after its pause at 03:54. V40 on the 68 walls it had not run
# (walls_V40_rest; p9twee.py has no skip of done goals; its results append to out_V40), then V100 (Veroff's settings
# at the default weight) on all 107. 1 worker each, in turn.
cd /project/hintwork/exp23
P9=/project/twee/hints/p9twee.py; UL=/project/hintwork/loops/UL
V="assign(order, kbo). set(lex_order_vars). clear(back_demod). set(restrict_denials). set(para_from_small). clear(cac_redundancy)."
for x in "40 walls_V40_rest" "100 walls107"; do
  set -- $x
  echo "$(date +%T) start V$1 on $2" >> stage.log
  python3 $P9 $2 $UL out_V$1 --timeout 60 -j 1 --solved-rows 45414 --chain /project/hintwork/chain_records.tsv \
    --settings "$V assign(max_weight, $1)." >> V$1.out 2>&1
done
echo "$(date +%T) end" >> stage.log

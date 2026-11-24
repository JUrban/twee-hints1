#!/bin/bash
# (24 Nov 09:05) HLS2: HLW1's plain 60 s setting (100 earlier and 30 later siblings, 400 kNN lemmas) with the second slice of
# the kNN ranking, ranks 400-799 (condprove.py --knn-skip 400), on every unsolved local head and first head of cycle
# c39 (cond/PLNL/c39.lheads + c39.heads). exp81's arm P81D (notes/2026-11-24-plain-time.md) proved 2 of 60 of HLW1's
# failed heads with this slice, the 60 s control with ranks 0-399 0 of 60; HLW1's proofs used kNN ranks up to 397.
# 3 threads (exp81's finished 60 s chain and the climber's -j 8 left CPUs free). Proofs into loops/UL through loops/CI3
# every 30 minutes and at the end.
cd /project/hintwork
D=cond/HLS2
cut -f1 loops/UL/solved.tsv | sort -u > $D.trusted
cat cond/PLNL/c39.lheads cond/PLNL/c39.heads | sort -u | grep -v -x -F -f $D.trusted > $D.set
echo "HLS2 start $(date '+%d %T') context $(wc -l < $D.trusted) set $(wc -l < $D.set) -j ${J:-3}" >> $D.parts
imp() {
  python3 /project/twee/hints/exp/condimport.py $D loops/CI3 --trusted $D.trusted --time 60 > $D.import.part 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > $D.merge.part 2>&1
  echo "$(date '+%d %T') ran $(grep -c . $D/results.tsv) THM $(grep -c -P '\tTHM\t' $D/results.tsv) | $(tail -1 $D.import.part) | $(tail -1 $D.merge.part)" >> $D.parts
}
python3 -u /project/twee/hints/exp/condprove.py $D --trusted $D.trusted -j ${J:-3} --proved --time 60 --sibs 100 --after 30 \
  --knn 400 --knn-skip 400 --only $D.set > $D.log 2>&1 &
CP=$!
echo "condprove $CP" >> $D.parts
while kill -0 $CP 2>/dev/null; do
  E=$(( $(date +%s) + 1800 )); until [ $(date +%s) -ge $E ] || ! kill -0 $CP 2>/dev/null; do sleep 20; done
  kill -0 $CP 2>/dev/null && imp
done
imp
echo "HLS2 done $(date '+%d %T')" >> $D.parts

#!/bin/bash
# (24 Nov) Import the running HLW1 sweep's proofs every 30 minutes, not only at its end (abs/sweepq.sh imports
# then): HLW1's local heads unlock their next siblings, so production should get them as lemmas soon. Its first
# 27 runs proved 3 new goals (4.8 per CPU h). condimport.py skips goals already in loops/CI3 or in the sweep's
# context, so the sweep's final import adds only the rest. Exits when the sweep's condprove ($CP) has ended.
cd /project/hintwork
CP=${CP:?condprove PID}
while kill -0 $CP 2>/dev/null; do
  E=$(( $(date +%s) + 1800 )); until [ $(date +%s) -ge $E ] || ! kill -0 $CP 2>/dev/null; do sleep 20; done
  kill -0 $CP 2>/dev/null || break
  python3 /project/twee/hints/exp/condimport.py cond/HLW1 loops/CI3 --trusted cond/HLW1.trusted --time 60 > cond/HLW1.import.part 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/HLW1.merge.part 2>&1
  echo "$(date '+%d %T') ran $(grep -c . cond/HLW1/results.tsv) THM $(grep -c -P '\tTHM\t' cond/HLW1/results.tsv) | $(tail -1 cond/HLW1.import.part) | $(tail -1 cond/HLW1.merge.part)" >> cond/HLW1.parts
done
echo "$(date '+%d %T') hlwimport end" >> cond/HLW1.parts

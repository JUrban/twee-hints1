#!/bin/bash
# (24 Nov 09:34) exp82c: exp82's A/B again on 60 more unsolved local heads with at least 2 proved Horn siblings (seed 821, not
# in exp81's or exp82's sets; exp/exp82_set.py at the start), notes/2026-11-24-horn-lemmas.md. exp82 gave +1 -0 (aK2rev 444,
# whose proof uses the Horn lemma aK2rev 450), below its +2 rule; the rule applies to the 120. Starts when exp81 ends
# ("exp81 done" in cond/EXP81.status), on its two threads. H82G: TWEE_LEMMA_HORN=1 and --conditional-encoding fresh;
# H82D: the same problems without the Horn axioms (as H82C). Plain 60 s, 100+30 siblings, 400 kNN, one thread each.
cd /project/hintwork
END=$(date -d "2026-11-24 22:00" +%s)
until grep -q "^exp81 done" cond/EXP81.status 2>/dev/null || [ $(date +%s) -gt $END ]; do sleep 60; done
cut -f1 loops/UL/solved.tsv | sort -u > cond/EXP82C.trusted
python3 /project/twee/hints/exp/exp82_set.py --seed 821 --exclude cond/EXP81.set,cond/EXP82.set --out cond/EXP82C.set --write > cond/EXP82C.setlog 2>&1
echo "exp82c start $(date '+%d %T') context $(wc -l < cond/EXP82C.trusted) set $(wc -l < cond/EXP82C.set) | $(tail -1 cond/EXP82C.setlog)" >> cond/EXP82.status
arm() {   # NAME HORN [twee args]
  n=$1
  TWEE_LEMMA_HORN=$2 python3 -u /project/twee/hints/exp/condprove.py cond/$n --trusted cond/EXP82C.trusted -j 1 --proved --time 60 \
    --sibs 100 --after 30 --knn 400 --only cond/EXP82C.set ${3:+--args "$3"} > cond/$n.log 2>&1
  python3 /project/twee/hints/exp/condimport.py cond/$n loops/CI3 --trusted cond/EXP82C.trusted --time 60 ${3:+--args "$3"} > cond/$n.import 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/$n.merge 2>&1
  echo "$n done $(date '+%d %T') ran $(grep -c . cond/$n/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$n/results.tsv) | $(tail -1 cond/$n.import) | $(tail -1 cond/$n.merge)" >> cond/EXP82.status
}
arm H82G 1 "--conditional-encoding fresh" &
arm H82D 0 &
wait
echo "exp82c done $(date '+%d %T')" >> cond/EXP82.status

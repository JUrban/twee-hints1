#!/bin/bash
# Same statement proven in another theory (16 Nov 16:30; transfer.py find --same-other: 1,887 unsolved goals whose
# statement is a proven goal of an original with axioms not within theirs, 1,361 with one axiom missing).
# transfer.py run on SET (default sets/so60.tsv, 60 random of them), 20 s; context = the
# production snapshot ULs16 (UL at 16:30). ARM=SOP X=--src-pool (the source originals' whole pools as hints after the
# source proofs); ARM=SOC X= (control: the source proofs only, as XFR2). 16:35: SOP 0 of 25 (90% of source proofs
# use the missing axiom); SET=sof60 ARM=SOF X=: 60 of sets/so_free.tsv (323 whose source proof has no missing
# axiom as a step).
cd /project/hintwork
python3 /project/twee/hints/transfer.py run sets/${SET:-so60}.tsv loops/$ARM -j ${J:-2} --time 20 $X -- --init loops/ULs16 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e39 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/$ARM.log 2>&1
echo "$ARM $(grep -c THM loops/$ARM/transfer.tsv)/$(grep -c . sets/${SET:-so60}.tsv) $(date +%T)" | tee loops/$ARM.done

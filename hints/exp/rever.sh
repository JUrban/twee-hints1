#!/bin/bash
# (20 Nov 10:10) Re-prove the 1,130 quarantined goals (loops/UNSOUND/Q.txt): the 13 unsound Prover9 proofs (p9twee
# negation bug), the 132 proofs that used them as lemmas, and the proofs whose lemmas no record names (226 without a
# kept output since 15 Nov 08:56, 42 live-loop and 717 transfer proofs). Each goal: production's transfer options
# (rm4t, 6 sibling + 30 kNN lemmas from production's cleaned solved set, the original's pool), its own old proof as
# hints (hints do not affect soundness), 60 s; proofs into loops/UL. Passes until one proves nothing, each from
# production's solved set as it is then (re-proved goals become lemmas for the next pass); the last pass at 300 s.
# notes/2026-11-20-p9-negation-bug.md
cd /project/hintwork
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
D=/project/hintwork/loops/REVER
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
run_pass() {   # $1 pass, $2 seconds
  cp loops/UL/solved.tsv $D/solved.tsv
  S=$(cut -f1 loops/UL/solved.tsv | sort -u)
  comm -23 <(sort -u loops/UNSOUND/Q.txt) <(echo "$S") | awk '{print $1"\t/project/hintwork/loops/UNSOUND/qhints/"$1"\t0"}' > $D/goals_$1.tsv
  echo "pass $1 ($2 s): $(wc -l < $D/goals_$1.tsv) goals $(date +%T)"
  python3 /project/twee/hints/transfer.py run $D/goals_$1.tsv $D -j ${J:-4} --time $2 --src-lemmas 0 \
    --live-dst /project/hintwork/loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
    --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
    --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > $D/pass_$1.log 2>&1
  n=$(awk -F'\t' -v p=$1 '$2=="THM"' $D/transfer.tsv | cut -f1 | sort -u | wc -l)
  echo "pass $1 done $(date +%T): $n re-proved so far"
}
prev=-1; p=1
while [ $p -le 4 ]; do
  run_pass $p 60
  n=$(awk -F'\t' '$2=="THM"' $D/transfer.tsv | cut -f1 | sort -u | wc -l)
  [ "$n" = "$prev" ] && break
  prev=$n; p=$((p+1))
done
run_pass 9 300
echo "rever done $(date +%T)" > loops/rever.done

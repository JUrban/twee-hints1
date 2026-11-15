#!/bin/bash
# Summarize A/B arms (reflink copies of loops/UL): new proofs and runs per 10 minutes.
#   bash abs/ab_summary.sh K S ARM...   (K: UL r5 results rows at copy time, S: UL solved rows)
cd /project/hintwork
K=$1; S=$2; shift 2
for d in "$@"; do
  echo "$d: new $(tail -n +$((S+1)) loops/$d/solved.tsv | wc -l)"
  tail -n +$((K+1)) loops/$d/r5/results.tsv | awk -F'\t' '{t=substr($6,3)+0; b=int(t/600); r[b]++; s[b]+=($2=="THM"); if ($5!="L0") d[b]++; c[b]+=$3}
    END {for (b in r) printf "  %3d min: %3d runs (%2d resumes), %3d proved, %5.0f CPU s\n", b*10, r[b], d[b], s[b], c[b]}' | sort -n
done
echo "union: $(for d in "$@"; do tail -n +$((S+1)) loops/$d/solved.tsv | cut -f1; done | sort -u | wc -l)"

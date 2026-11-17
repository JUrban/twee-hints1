#!/bin/bash
# Run the hint loop on new problems, as on an unseen benchmark part (16 Nov; the setting of REPORT 2aq).
#
#   solve_new.sh NAMES CONTEXT OUT [J [HOURS]]
#
# NAMES    goal names (X__goal_N), one per line. The problem files X__goal_N.p are read from $AIM_PROB (default
#          the AIM60k tptp dir). For new problems, make a directory with links to the public and the new .p files:
#          the context's goals are read too.
# CONTEXT  a loop dir with solved.tsv and hints/ (for example loops/UL, or a snapshot of it). Its proofs are the
#          round-0 context: sibling and kNN lemma sources, hint pools, transfer sources. EXCLUDE=goals (default)
#          leaves out only proofs of the NAMES themselves, so goals moved out of a public original (1,156 of the
#          secret part, README) keep their public siblings as lemmas. EXCLUDE=originals leaves out every proof of
#          the NAMES' originals: a replay that simulates unseen originals (REPORT 2aq).
# OUT      the new loop dir (must not exist); OUT.ctx holds the context, OUT.xfer the transfer worker.
# J        cascade workers (default 4); the live proof-step transfer (transfer.py live) adds 2 at times.
# HOURS    no new cascade runs after this many hours (default 1).
#
# MODEL (default /project/hintwork/models/rm4t, with .bin and .vocab), TWEE (default /project/bin/twee-e22) and
# XTWEE (the transfer's, default /project/bin/twee-e39), CASCADE (the levels, default 5,80,320), KNN (kNN lemmas,
# default 30) and XEVERY (the transfer's cycle in seconds, default 120: 942 against 933 at 600, REPORT 2aq) can
# be set in the environment. ORDER (default --mix 0.1 --fail-order) orders the runs: each goal's first fresh run
# before any repeat, near before far, and a share of the workers for the deeper levels (REPORT 2at: on the whole
# benchmark from zero Z4 37,713 at 2 hours against Z1's 36,552 without it; the rp3 replay with today's context LVF
# 1,095 against LVU's 1,085 with the learned scheduler). SCHED (default empty) holds the learned scheduler's options,
# e.g. production's (abs/ul36.sh) "--sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain
# 200 --sched-pmin 0.011 --sched-pmin-auto 400 --sweep-first" (then --fail-order is idle; scheduler runs vary by
# about 25 in 1,320). PASS_EVERY (default 1 s; 0 = a full scheduling pass after every run, which on tens of
# thousands of goals leaves workers idle, REPORT 2as). LOOPARGS adds other loop.py options. Solved goals end up in
# OUT/solved.tsv, proofs in OUT/hints.
# (17 Nov 16:30) TWEE default twee-e44 (e43: no state dump for a proved goal; e44: incremental hint renormalisation,
# -11% CPU, same output), CASCADE 5,20,80,320 and STATES (default --no-fresh-states: a goal's first deeper level
# starts over with its full budget instead of resuming a fresh run's state; ORH 18,476 against ORG's 18,374 at
# 2 hours, 4,792 runs an hour against 4,268; REPORT 2au). STATES= keeps the fresh runs' states.
# (17 Nov 19:00) TWEE default twee-e48 and PG (default --pg-threshold 0.25): parental guidance, no critical pairs of
# two rules whose source pairs' rule-model scores sum below logit 0.25 (half1 from zero, 2 hours: PGA 18,987 against
# PGB's 18,410; REPORT 2av, notes/2026-11-17-pg-ab-half1.md). With PG= twee-e48 matches e44. The transfer keeps XTWEE.
set -e
H=/project/twee/hints
NAMES=$1; CTX=$2; OUT=$3; J=${4:-4}; HOURS=${5:-1}
M=${MODEL:-/project/hintwork/models/rm4t}
TWEE=${TWEE:-/project/bin/twee-e48}
PG=${PG---pg-threshold 0.25}
CASCADE=${CASCADE:-5,20,80,320}
STATES=${STATES---no-fresh-states}
KNN=${KNN:-30}
XEVERY=${XEVERY:-120}
XTWEE=${XTWEE:-/project/bin/twee-e39}   # the transfer worker's twee (as abs/rpx.sh)
PASS=${PASS_EVERY:-1}   # loop.py --pass-every: the full scheduling pass at most once a second (REPORT 2as)
SCHED=${SCHED:-}
ORDER=${ORDER---mix 0.1 --fail-order}
[ -n "$OUT" ] && [ -f "$NAMES" ] && [ -f "$CTX/solved.tsv" ] || { sed -n 2,20p "$0"; exit 1; }
[ -e "$OUT" ] && { echo "$OUT exists"; exit 1; }
mkdir -p "$OUT.ctx/hints"
python3 - "$NAMES" "$CTX" "$OUT.ctx" "${EXCLUDE:-goals}" <<'EOF'
import os, shutil, sys
names, ctx, snap, excl = sys.argv[1:]
assert excl in ('goals', 'originals'), excl
G = {l.strip() for l in open(names) if l.strip()}
O = {g.rsplit('__goal_', 1)[0] for g in G}
n = 0
with open(os.path.join(snap, 'solved.tsv'), 'w') as f:
    for l in open(os.path.join(ctx, 'solved.tsv')):
        w = l.rstrip('\n').split('\t')
        out = w[0] in G or (excl == 'originals' and w[0].rsplit('__goal_', 1)[0] in O)
        if len(w) >= 3 and not out and os.path.exists(os.path.join(ctx, 'hints', w[0])):
            f.write(f'{w[0]}\t0\t{w[2]}\n'); n += 1
            shutil.copy2(os.path.join(ctx, 'hints', w[0]), os.path.join(snap, 'hints', w[0]))
print(f'context: {n} proofs (EXCLUDE={excl}: {len(G)} new goals of {len(O)} originals)')
EOF
MOD="--model --model-fixed $M.bin,$M.vocab --model-theory --lemmas 6 --lemma-knn $KNN --lemma-subsets --lemma-after"
python3 -u "$H/loop.py" "$NAMES" "$OUT" --init "$OUT.ctx" --start 1 --cascade "$CASCADE" --cascade-start -1 --retry-gap 3 \
  $MOD --twee "$TWEE" --keep-out -j "$J" --reserve 0 --pool original --wall-factor 15 --line-gaps 80,80 \
  --retry-hints 1.25 --fresh-first --far-retry --retry-knn --sync 60 --cascade-hours "$HOURS" --pass-every "$PASS" $ORDER $SCHED $STATES $LOOPARGS \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider $PG" > "$OUT.log" 2>&1 &
LOOP=$!
until [ -f "$OUT/config.json" ] || ! kill -0 $LOOP 2>/dev/null; do sleep 2; done
python3 "$H/transfer.py" live "$OUT" "$OUT.xfer" -j 2 --time 20 --src-lemmas 6 --every "$XEVERY" --set "$(realpath "$NAMES")" -- \
  $MOD --pool original --twee "$XTWEE" --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" \
  > "$OUT.xfer.log" 2>&1 &
XFER=$!
wait $LOOP || true
kill $(ps -o pid= --ppid $XFER) $XFER 2>/dev/null || true
echo "$(awk -F'\t' 'NR==FNR {g[$1]=1; next} ($1 in g) {print $1}' "$NAMES" "$OUT/solved.tsv" | sort -u | wc -l) of $(grep -c . "$NAMES") solved ($OUT/solved.tsv)"

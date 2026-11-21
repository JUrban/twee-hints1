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
# (19 Nov) The deep portfolio of production, explored (exp27 PGC, exp29 PGD; REPORT 2az,
# notes/2026-11-19-from-zero-explore.md): TWEE default twee-pg61 (e61 with TWEE_PG_ARGS, default PG 0.25 and the
# ground-joining branch limit 100, which ends hangs), CASCADE 5,40,80,160,320 with chain hints from level 1, and DEEP
# (default below): 5 s members that change the problem (unfolded definitions; 60, 100, 200 and 400 kNN lemmas; proof-
# dependency lemmas), 80 s variants after the 160 s level, all ordered by live yield (--ratio-order) with --explore
# 0.2 for the new members and the 40 s level. DEEP= gives the 17 Nov system (with CASCADE=5,20,80,320 TWEE=twee-e48).
# (20 Nov) GIVEN (default 1): derived-rule transfer (exp38/exp40; notes/2026-11-20-given-transfer.md and
# notes/2026-11-20-from-zero-given.md). The loop scans every failed run's given rules against the unsolved goals
# (loop.py --given-scan OUT_GF: a rule that is an unsolved goal up to variables, the source's axioms within the
# goal's), and givenmatch.py live runs each hit once the loop has failed on its goal (the rule's ancestry at 20 s,
# then the log's prefix at 40 s; at most 60 goals per 300 s cycle; also the same statement proven in a theory with
# more axioms), proofs into OUT. half1 from zero, 2 hours: PGE 19,591 against PGD's 19,309 (identical runs differ by
# about 185); in the last 30 minutes the live loop proved 74 goals in about 0.85 CPU h, the loop 92 in 3. GIVEN=0
# gives the 19 Nov system. The live loop adds up to 2 workers at times. GIVENARGS (default "--every 300 -j 2 --cap 60
# --no-inst") holds its options, e.g. --same-cap N for the same-statement runs.
set -e
H=$(cd "$(dirname "$0")" && pwd)
NAMES=$1; CTX=$2; OUT=$3; J=${4:-4}; HOURS=${5:-1}
M=${MODEL:-/project/hintwork/models/rm4t}
TWEE=${TWEE:-/project/bin/twee-pg61}
export TWEE_PG_ARGS=${TWEE_PG_ARGS---pg-threshold 0.25 --ground-joining-branch-limit 100}   # (twee-pg61 appends them)
case "$TWEE" in *twee-pg6*) PG=${PG-} ;; *) PG=${PG---pg-threshold 0.25} ;; esac
CASCADE=${CASCADE:-5,40,80,160,320}
DEEP=${DEEP---chain-level 1 --variants unf@0,k60@0,k100@0,k200@0,k400@0,kd@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --ratio-order --explore 0.2 --explore-labels L1,Vk100@0,Vk200@0,Vk400@0,Vkd@0}
STATES=${STATES---no-fresh-states}
KNN=${KNN:-30}
XEVERY=${XEVERY:-120}
XTWEE=${XTWEE:-/project/bin/twee-e39}   # the transfer worker's twee (as abs/rpx.sh)
PASS=${PASS_EVERY:-1}   # loop.py --pass-every: the full scheduling pass at most once a second (REPORT 2as)
SCHED=${SCHED:-}
ORDER=${ORDER---mix 0.1 --fail-order}
# (21 Nov 12:19) LATE: the late-phase options of exp44/45 and exp48 (notes/2026-11-21-late-combo.md): retries of failed
# goals as their own mix class with live yield (--retry-class), past proofs discounted by 2000 abstract s and a 25%
# re-exploration every 12 minutes (--yield-discount 2000 --reexplore 12:0.25), a goal's context tracked through its
# 10 nearest kNN lemmas (--knn-ctx 10), and 40 s chain-level runs for the first unsolved goal after a proved one
# (--head-class). half2 from zero, 5 hours, side by side: P2O (all) 21,940 against P2N (without the last two) 21,702;
# at equal abstract work P2O ties exp44/45's best single option. LATE= gives the 20 Nov system.
# (21 Nov 23:51) + --floor-ratio 20 (exp52, notes/2026-11-21-floor-ratio.md): the retry and head classes keep their
# one-worker floor only while 20 times their yield reaches the best class's, so they do not hold workers while first
# runs prove at 100 times their rate. half2 from zero, 4 workers each, 3 hours: P2U 20,876 against P2T's 20,087.
LATE=${LATE---retry-class --yield-discount 2000 --reexplore 12:0.25 --knn-ctx 10 --head-class --floor-ratio 20}
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
GIVEN=${GIVEN:-1}
GIVENARGS=${GIVENARGS:---every 300 -j 2 --cap 60 --no-inst}   # (the live loop's own options)
ROUT=$(realpath -m "$OUT"); GSCAN=
[ "$GIVEN" = 1 ] && GSCAN="--given-scan ${ROUT}_GF"
python3 -u "$H/loop.py" "$NAMES" "$OUT" --init "$OUT.ctx" --start 1 --cascade "$CASCADE" --cascade-start -1 --retry-gap 3 \
  $MOD --twee "$TWEE" --keep-out -j "$J" --reserve 0 --pool original --wall-factor 15 --line-gaps 80,80 \
  --retry-hints 1.25 --fresh-first --far-retry --retry-knn --sync 60 --cascade-hours "$HOURS" --pass-every "$PASS" $ORDER $LATE $SCHED $STATES $DEEP $GSCAN $LOOPARGS \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider $PG" > "$OUT.log" 2>&1 &
LOOP=$!
until [ -f "$OUT/config.json" ] || ! kill -0 $LOOP 2>/dev/null; do sleep 2; done
python3 "$H/transfer.py" live "$OUT" "$OUT.xfer" -j 2 --time 20 --src-lemmas 6 --every "$XEVERY" --set "$(realpath "$NAMES")" -- \
  $MOD --pool original --twee "$XTWEE" --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" \
  > "$OUT.xfer.log" 2>&1 &
XFER=$!
GM=
if [ "$GIVEN" = 1 ]; then
  B=$(basename "$ROUT")
  python3 -u "$H/givenmatch.py" live "${ROUT}_GML" --loops "$(dirname "$ROUT")" --dst "$B" --dirs "$B,$B.xfer" \
    --gfail "${B}_GF" --set "$(realpath "$NAMES")" $GIVENARGS -- \
    $MOD --pool original --twee "$TWEE" --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" \
    > "$OUT.gml.log" 2>&1 &
  GM=$!
fi
wait $LOOP || true
desc() { for c in $(ps -o pid= --ppid $1); do desc $c; done; echo $1; }
kill $(desc $XFER) 2>/dev/null || true
[ -n "$GM" ] && { kill $(desc $GM) 2>/dev/null || true; }
echo "$(awk -F'\t' 'NR==FNR {g[$1]=1; next} ($1 in g) {print $1}' "$NAMES" "$OUT/solved.tsv" | sort -u | wc -l) of $(grep -c . "$NAMES") solved ($OUT/solved.tsv)"

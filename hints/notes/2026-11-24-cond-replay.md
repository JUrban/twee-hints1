# Replaying the climbers' conditional proofs (exp75, 24 Nov 00:03)

**Question.** A climber's sketch proof of an unsolved target uses assumptions (assume_*: unsolved goals stated as
axioms) and lemmas. climb.py records each proof's labels (used.tsv) and what each assumption stated (assume.tsv),
"so it can be replayed once they are proven", but nothing reran them. When production later proves the goals an
assumption stated, the sketch proof is a proof from proved goals. How many are ready, and does twee find them again?

**Set.** Every climber dir with used.tsv (loops/CC67B.v1, CC67C, CC67D, CC67.v1, CLA67, CLB67, CLHL2, CLHL3, CLHL4,
CLK69, CLS71, K70F, K70R, SMK3; CLU and older dirs have none). Context: loops/TRUSTNOW/t2352.trusted (trust.py at
23:52: 48,565 solved, 3 untrusted, 251 fill lemmas trusted).

**Method** (exp/condreplay.py). A proof is ready when each assumption label has a trusted candidate source goal
(kNN labels are written more than once; every trusted candidate is taken), every lemma_goal_J and lemma_knn_I_<goal>
is trusted, and a source from another original has a subset of the target's axioms. Theory conjectures ('-') are
never ready. The replay problem: the target's problem with those goals as lemma axioms, the sketch's steps as hints;
a proof that used a fill lemma (true_*) also gets all the original's trusted goals and the fill runs' hints, so the
fill is re-derived. twee-pg61 without PG, 60 abstract s, --no-proof. Proofs go through exp/condimport.py (rerun,
USEDAXIOMS resolved to trusted goals, printed proof) into loops/CRP75 and merge.py into loops/UL.

**Command.**
```
cd /project/hintwork
python3 -u /project/twee/hints/exp/condreplay.py cond/CRP75 loops/CC67B.v1 loops/CC67C loops/CC67D loops/CC67.v1 \
  loops/CLA67 loops/CLB67 loops/CLHL2 loops/CLHL3 loops/CLHL4 loops/CLK69 loops/CLS71 loops/K70F loops/K70R loops/SMK3 \
  --trusted loops/TRUSTNOW/t2352.trusted -j 2 --time 60 > cond/CRP75.log
python3 /project/twee/hints/exp/condimport.py cond/CRP75 loops/CRP75 --trusted loops/TRUSTNOW/t2352.trusted --time 60
python3 /project/twee/hints/merge.py loops/UL loops/CRP75
```

## Ready proofs

25 ready conditional proofs of 15 unsolved targets: dirs: CLHL2 (CLHL2: the 16-17 Nov head climber); 16 of the 25 used a fill
lemma.

The first scan (above) took every trusted candidate of a label and did not look at the sketch's goal. 12 of its
targets were replayed before I stopped it; 0 proved. Looking at why (aK2_eq_aK3_q 263, s2, one lemma axiom and the
sketch's 28 hint steps, no proof in 60 s): the sketch's header has `goal=` with X2 replaced by X0. climb.py's
`--weaken` runs prove an instance of the target (`goal=` set; used.tsv has their rows too), and an empty header is
the target itself. Of the 25, 4 are sketches of the target, and each of those rests on a kNN label with 2 candidate
goals, 1 untrusted.

| climber | sketch proofs with assumptions: of the target | of a weakened goal | rows without an assumption |
|---|---:|---:|---:|
| CLHL2 | 1,554 | 1,219 | 1,036 |
| CLB67 | 143 | 167 | 156 |
| CLS71 | 221 | 232 | 235 |

**Fixes.**
* exp/condreplay.py: only sketches of the target; a label written more than once is ready only when every goal it
  stood for is trusted. With that: 0 ready now.
* climb.py: used.tsv gets two more columns, each assume_* label's goal at that run (label=goal) and 1 for a weakened
  goal's proof, so later replays are exact. Readers use only the first three columns (trust.py, keylemmas.py,
  unsound.py, hintdata_build.py). The running climbers keep the old code until restarted.
* abs/crploop.sh (exp/prod/side/crploop.sh): the replay every hour, with the newest loops/TRUSTNOW trusted set and a
  tried list (cond/CRP75/tried.tsv); proofs through condimport.py into loops/CRP75 and merge.py into loops/UL. Status
  lines: cond/CRP75.status.

**exp69's key goals, rechecked.** exp/keylemmas.py also counted weakened-goal sketches as unlocking their target.
Without them (every candidate of an ambiguous label credited, so an upper bound) the 9 key goals still unlock
targets, but fewer for some:

| key goal | unsolved targets, all sketches | sketches of the target only |
|---|---:|---:|
| Kproperties_1__goal_332 | 10 | 4 |
| nil4_19K__goal_394 | 4 | 4 |
| Ka_eq_aK3__goal_420 | 14 | 9 |
| Ka_eq_aK3__goal_425 | 14 | 14 |
| TLRproperties_2__goal_386 | 7 | 7 |
| aK2_eq_aK3_1243b__goal_479 | 14 | 11 |
| aK2_eq_aK3_1243b__goal_522 | 10 | 3 |
| aK2_eq_aK3_1243b__goal_525 | 5 | 4 |
| nil3_2K__goal_383 | 8 | 6 |

(At 00:18, over every climber dir with used.tsv. keylemmas.py's own counts at 21:20 were smaller: it kept one candidate
per label.)

## exp76: CLS71's finals at 160 s, with and without the climb hints (00:24)

**Question.** CLS71 (the live stalled-goal climber) ends each climb with a 20 s final. By 00:40 it had made 1,174
sketch proofs and 0 real proofs in 119 finals. exp67's arm B made all 7 of its real proofs in 160 s finals
(CPU 7-380 s each; its 'direct' rows are re-proofs without fill lemmas). Do these targets fall to 160 s finals, and
do the climb hints matter at that length?

**Set.** 30 of CLS71's targets whose 20 s final failed, unsolved and not local heads (108 such at 00:40; seed 76;
sets/exp76, exp/sets/exp76; 22 originals).

**Arms** (abs/exp76.sh, exp/exp76.sh): final-only climbs (`--runs 0`, `--final-time 160`), CLS71's lemma lists
(30 siblings, 400 kNN) and model, the newest trusted set and production's hints at launch, -j 2 each:
* F76S: CLS71's sketches/ and fillhints/ copied at launch (reloaded as each original's climb hints);
* F76C: none (pool hints and lemmas only: a long production-like run).

It waits for exp67's arms to end (about 03:00) so the CPU stays near its level (bash 3766581). Reading: proofs per
arm, +/-, CPU h (exp/ccpair.py F76S F76C). If F76S > F76C, CLS71's finals get longer; if they tie, the stalled goals
need time, not climb hints.

## A term-size cap would not prune (00:31)

Veroff's Prover9 runs use weight limits (max_weight); twee has `--max-term-size` (rules whose left side is bigger
are discarded), tried only in a small speed test (exp/pg/tm/cap.py, twee-e44). Sizes, counting symbols and variables:
* Proofs near the frontier (production's hints of the 5 solved goals before and after each original's first
  unsolved goal, 846 proofs): the largest left side per proof has median 13, p90 22, p95 27, p99 39, max 58.
* A failing 60 s plain run on the cluster head nil3_2K 383 (exp74's problem, 400 kNN and 129 sibling lemmas):
  18,471 rules, 97.5% with a left side of size <= 10, 99.7% <= 15, the largest 26.

Twee's queue, ordered by size, already keeps its rules small, so a cap at 25-30 removes next to nothing, and one
below 15 would cut many real proofs. Not run. The proofs' few rules of size 13-27, which a run reaches late, are what
the hints are for.

## exp77: twee's CASC strategies on local heads (00:51)

**Question.** Production's runs, the climbers and the plain sweeps all use twee's default queue and ordering
(lhs-weight 4, depth-weight 2, no flip-ordering, kbo-weight0-unary only). Only Prover9-style loops and exp63 (another
KBO precedence: 0 of 120 for both at 20 s) varied anything. Twee's own parallel portfolio
(/project/twee/executable/ParallelMain.hs) runs 8 strategies for UEQ problems. Do they prove local heads the default
does not?

**Smoke test** (production's binary twee-pg61 without PG, 10 abstract s; an easy goal, aa1_12 20, and a cluster head
with 529 lemma axioms, nil3_2K 383, exp74's problem):
* S0 (default), S2, S8: the easy goal proved, the head gave up at about 12 s.
* S4 (lhs-weight 9, flip-ordering, complete-subsets, renormalising) did not prove the easy goal in 10 s.
* S1, S3, S4, S5, S7 (all with `--complete-subsets`) and S6 (`--depth-weight 60`) ran past 120 s on the head.
  One flag at a time, 60 s cap: `--complete-subsets` made 833 rules in 60 s and `--depth-weight 60` 3,617, against
  about 8,200 rules in 12 s for `--flip-ordering`, `--distributivity-heuristic`, `--lhs-weight 1` or 9 and
  `--ground-joining-limit 15`. Abstract time counts critical pairs (src/Twee.hs), so a strategy that spends more CPU
  per pair gets that much more CPU at the same abstract budget. These two are left out.

**Arms** (abs/exp77.sh, exp/exp77.sh, bash 3774081; starts when exp67's controls end, about 03:30): plain 60 s runs,
H's lemma lists (100+30 siblings, 400 kNN), condprove.py --proved, 2 threads, two arms at a time:
* A1: S1 without complete-subsets (`--lhs-weight 1 --flip-ordering --normalise-queue-percent 10
  --cp-renormalise-threshold 10 --ground-joining-incomplete-limit 15`);
* A2: S2 (`--no-flatten-goal --ground-joining-incomplete-limit 15 --ground-connectedness --normalise-queue-percent 10
  --cp-renormalise-threshold 10`);
* A4: S4 without complete-subsets (`--lhs-weight 9 --flip-ordering --normalise-queue-percent 10
  --cp-renormalise-threshold 10`);
* A8: S8 (`--no-kbo-weight0-unary --kbo-weight0 --no-flatten-goal`).

**Set.** 120 of the 937 unsolved local heads (sets/exp77, exp/sets/exp77; random.seed(77); 55 originals). The control
is HLW1 (the same setting with twee's defaults, on all local heads, from about 03:00). condimport.py now takes
`--args`, so a proof is re-checked under its own strategy; proofs go to loops/CI77 and loops/UL.

**Reading.** Per arm on the 120: proofs, +/- against HLW1, the union, CPU h (the results' seconds). A strategy with
3 or more proofs the default does not find at about the same CPU becomes a setting of the plain live loop.

## exp78: production retries climbed goals (ul79, 01:16)

**Why.** Production reloads the climb hints every 10 minutes but does not schedule a goal again because it was
climbed. Over production's rows since 23 Nov 21:14, only 22 of the 149 targets CLS71 had finished (with sketches)
had any production run after their climb (16 with an sk member; the first came a median 18 minutes after the climb).
The rest wait for a context change. 193 unsolved targets have sketches from the last 6 hours over the 14 climb dirs.

**Change** (loop.py `--retry-climb`, `--retry-climb-hours H`): at each climb-hint rescan (at most every 10
minutes, from the sync points), a goal whose newest sketch in any --climb-hints dir is newer than the last rescan's,
or than the cascade start minus H hours, counts as grown (like --retry-hints): the next pass gives it a fresh run,
after which the variants (sk@1:0, skk400s30@1:0 ...) follow by yield. The mark is dropped at that fresh run, and each
such retry is appended to DIR/climbretry.tsv (epoch, goal). Smoke test exp/retryclimb_smoke.sh (2 climbed targets,
rescans every 30 s via LOOP_CLIMB_RESCAN): both marked at the start with H = 24, retried once, and the one given a new
sketch at 90 s marked and retried again.

**ul79** (abs/ul79.sh, exp/prod/ul79.sh): ul78 plus `--retry-climb --retry-climb-hours 6`; loop.py PID 3780013 since
01:15 (ul78 stopped 01:15: 1,950 runs, 8 new proofs). The first rescan marked 212 goals (some already solved).

**Reading.** Proofs among the goals in loops/UL/climbretry.tsv (each goal's runs after its retry), proofs per CPU h of
those runs, against production's overall rate.

### exp78 result: negative, reverted (02:26)

ul79's 63 minutes (01:15-02:18, exp/climbretry.py at 02:18): 1,312 runs, 0 proofs, 5.96 CPU h. 1,304 of the runs
(5.94 CPU h) were on 287 climb-retried goals, a fresh run and then the variants (about 4.5 runs each), 0 proved. ul78
before it: 8 new proofs in 1,950 runs. At the stop, loops/UL/climbretry.tsv had 300 retries of 291 goals; 8 goals were
retried more than once (at most 3), so the re-marking of goals still being climbed was not the cost (ul80.sh's header
says it was; the running script is left as it is). The cost is the retry itself: climbed stalled goals do not fall
to production's cascade with their climb hints.

**ul80** (abs/ul80.sh, exp/prod/ul80.sh): ul79 without the flag, so ul78's setting (the scripts differ only in the
UL label). loop.py PID 3794779 since 02:19. loop.py keeps --retry-climb (off by default).

### exp77 stopped: it was tried before (03:53)

**Correction.** "Only Prover9-style loops and exp63 varied anything" above is wrong. I searched only REPORT and
JOURNAL for the flag names. notes/2026-11-22-cp-weights.md (exp57, 22 Nov) has twee's queue weights as portfolio
members: lhs-weight 2 and 8, depth-weight 0 and 5, var-weight 0.5 and 1.5, dup-factor 1, on 300 half2 heads at 20 s,
hinted. Every setting proved fewer heads than the defaults (98) at the same 20 s (76-95), and as a second member each
union stayed 12-18 below one 40 s default run (116). Before that, 15 Nov (abs/var_test.sh), --flip-ordering,
--kbo-weight0, --no-flatten-goal and --flatten-goal-lightly proved 0 on stalled goals at 5-20 s.

So exp77's prior was poor, and at about 19 CPU h it was stopped at 03:49 (cond/STR77.status) after A1 ran 14 goals
(0 proved) and A2 17 (1 proved: aK2_eq_aK3_gen 594). That proof was re-checked under A2's flags (condimport.py --args,
73 s) and merged into loops/UL through loops/CI77. The same problem with twee's defaults: proved in 11 s. It is the
setting (119 sibling and 400 kNN lemmas, plain), not the strategy; HLW1 would have found it. A4 and A8 never ran.

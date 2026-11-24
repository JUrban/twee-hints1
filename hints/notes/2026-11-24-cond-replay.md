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

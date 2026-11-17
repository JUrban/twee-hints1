# Expanding lemma-based proofs back to the axioms (Veroff style)

**Question.** The user, 17 Nov 18:57:
* Veroff expands simple lemma-based proofs back to the original axioms, to get many hints to learn from and reuse.
* This may flood us with hints that redo the same work, but that is what deduplication, tf-idf, premise selection
  and preference for rare or relevant hints are for.
* Veroff does the extra work because he thinks it pays off in the long run, like ML people generating synthetic
  data. It would also give training data for ENIGMA on really long runs.

So: how big are the expansions? Can a lemma-based proof's goal be re-proved from the axioms alone with the
expanded hints, where its own steps or the usual pool do not suffice? And what do the new axiom-level proofs give
as hints and as training data?

**Background.**
* Production's proofs are lemma-assisted. Only 0.3% of UL's recorded proofs use no lemma; 41% use a later
  sibling (2026-11-17-lemma-circularity.md).
* A lemma-based proof's hint file holds only the steps after the lemmas, so the derivation of each lemma is
  missing from it.
* For sibling lemmas, those derivations are in the original's pool anyway (each sibling's own hint file). For
  kNN lemmas from other originals (in 85% of UL's recorded proofs) they are not.
* Earlier tries in this direction:
  * 2ap added one level (the kNN lemmas' own proof steps) to runs that still had the lemmas as axioms. No gain,
    on a set where the control proved 6 of 150.
  * The step transfer (2026-11-16-step-transfer.md) showed that steps of proofs from the same or weaker axioms
    are very effective hints for goals that are such steps.

**Setup** (17 Nov, from 19:00).
* **hints/expand.py NAMES OUTDIR:**
  * Which lemmas a proof used comes from its kept output's USEDAXIOMS (depcheck.used_lemmas), over 16
    production-like loops: UL, Z0–Z4, PGA, PGB, ORA–ORH. 39,374 recorded proofs.
  * Records with lemma names that map to no goal (assumed or cut conjectures, old unnamed kNN lemmas) are skipped,
    so no sketch's steps enter.
  * The closure of G is found by BFS over the used lemmas. The expansion is the union of the closure's hint files
    (each holds its proof's steps and its statement), G's own steps first, then by depth, deduplicated by
    unordered (lhs, rhs).
  * Closure members without a record enter as leaves.
  * Mixing loops can make the graph cyclic. For hints that is harmless, since the re-proof from the axioms is the
    check.
* **Goals:** exp1/s200 (exp/sets/exp1_s200), 200 drawn with seed 1 from the 2,749 UL proofs with recorded, fully
  mapped lemmas. All are solved goals, so this measures re-proving, not new proofs.
* **Runs** (exp/exp1_run.sh): the original problem file with no lemma axioms. twee-e48, rm4t at 0.1 with penalty
  2, PG 0.25, `--no-eqhint-consider`, 20 abstract s, `--print-hints`, outputs kept. Arms by hints:
  * N: none;
  * O: G's own lemma-based proof steps (loops/UL/hints/G);
  * X: the expansion (exp1/xh);
  * P: the original's whole pool as production gives it (exp/exp1_mkpool.py: every solved goal's hint file in
    UL, most frequent first; G's own steps included).
* N, O, P on 4 workers from 19:02, X on 5 from 19:06 (after pgtest6).

**Expansion sizes** (200 goals):

| | lower quartile | median | upper quartile | max |
|---|---:|---:|---:|---:|
| proven goals in the closure | 506 | 817 | 1,040 | 2,174 |
| lemma-chain depth | 14 | 15 | 17 | 23 |
| distinct hints | 2,069 | 4,134 | 6,338 | 26,785 |

* The proof's own steps average 217. The whole original pool is 4,000–18,600 hints (nslm_to_aa1 18,638).
* 199 of 200 closures reach proofs without a record (about 40 per closure): proofs from before outputs were kept.
  Those enter as leaves, so the expansions are incomplete.

**Results so far** (19:11, partial):

| arm | proved / run |
|---|---|
| N, no hints | 2 / 55 |
| X, expanded | 4 / 55 |
| O, own steps | pending |
| P, whole pool | pending |

**Caveats to keep in mind.**
* The goals are solved, and the O and X arms contain G's own proof steps, which include G's statement. Matching
  the goal statement as a hint is not a proof: twee still has to derive it. But the own steps give a path from
  the lemmas to G, so O measures how much the lemmas' absence hurts.
* The expansions inherit the old pools' false generalised hypotheses (pre-HINTS-HYP). Under variant matching they
  are inert.
* 20 abstract s is short for proofs whose closures hold 800 goals. A longer budget for the failures is the
  natural next arm.

**exp2: expanded pools on the frontier** (exp/exp2_mkpools.py, exp/exp2_run.py; from about 19:25).

The question for the benchmark is whether expanded hints prove *new* goals in the production setting, where the
run still has its lemma axioms.

* **Goals:** the parental-guidance testbed pg/tb (exp/sets/exp2_goals200). 200 random goals that the 2-hour
  half1 run ORD never proved, whose 5 s first runs failed, and which production proved. The twee commands were
  captured in ORD's final context: sibling and kNN lemmas, the original's pool, rm4t, 5 abstract s.
* **Expansion within ORD only** (`expand.py exp2/ord_sibs exp2/xd --loops ORD`):
  * The 16,328 ORD-solved goals of the 49 originals are expanded through ORD's own 15,645 records.
  * Production's records are left out, because a closure through them could reach production's proofs of the
    test goals.
  * ORD's closures are small: median 4 goals, 14 hints (q3 17 and 55, max 917 and 4,140). Most ORD proofs are
    short, as in any run from zero.
* **Extras:** the hints in the siblings' expansions that the captured pool lacks, most frequent over siblings
  first.
  * The captured pool already holds every sibling's own steps (checked: 2,076 of 2,076 on aa1_12 345), so the
    extras are the derivations of kNN lemmas from other originals, and theirs in turn.
  * Per goal: median 1,509 extras against a median pool of 1,503 (min 479, max 4,470). So the pool doubles.
* **Arms,** all twee-e48 with `--pg-threshold 0.25` (production since 19:00):
  * base: the captured hints;
  * xa: + extras at the default factor 0.01;
  * xw: + extras at factor 0.1.
  * On the first two goals the extras roughly doubled the matched hints (548 to 1,057, and 640 to 999), and
    neither goal proved in any arm.
* For scale: the sum filter at 0.269 proved 52 of these 200 with twee-e51.

**Next.**
* At the end: compare N/O/X/P. If X beats P and O, the derivations of the lemmas carry information the pool
  lacks.
* Then use the new axiom-level proofs:
  * as hints, added to the pools;
  * as given logs of long runs for retraining the model (the user's synthetic-data point).
* Then test on unsolved goals: pools enriched with expanded proofs, against the plain pool, paired.

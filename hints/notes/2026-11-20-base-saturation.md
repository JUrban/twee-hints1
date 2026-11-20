# Base-theory runs as rule generators for the stronger theories (exp39)

Started 20 Nov 2026, 05:39 UTC.

## Question

13 originals share one axiom set, the 17 base axioms:
a_instances, Ka_eq_aK3, aK2_eq_aK3_1243b, Ka1_eq_Ka2, nil4_19K, aK2rev, nil3_2K, aKperms_1, TLRproperties_2,
aK1_eq_aK3, aa_instances_4, Kproperties_1 and axcom.
That set is within the axioms of almost every original. So a rule derived in a base-theory run holds for 3,001 of
the 3,133 unsolved unit goals, and so does every proven base goal (4,545 of them).

Since 04:15, production's failed runs are checked against the unsolved goals (loop.py `--given-scan`, exp38).
* Of the first 27 goals they derived, 19 came from runs of base originals, and 25 were in other originals.
* The base originals' runs had 1.18 of production's 14.7 CPU h (05:33). That is **about 16 goals per CPU h**,
  against 0.6 proofs per CPU h for production's own runs. The live loop proved most of them.

Do dedicated base-theory runs find such goals at the same rate, and for how long?

## Set and setting

* exp/gensat.py and abs/gsat1.sh write to loops/GSAT and loops/GSAT1.log.
* Each run takes an unsolved unit goal G0 of a base original, from 241 (seeded shuffle).
  * Its problem: the base axioms with G0 as conjecture.
  * Lemma axioms: the 6 proven goals just below G0 in its original, plus 30 random proven base goals (seed 1 and
    the run number).
  * Hints: the pool of G0's original, i.e. production's proof steps.
  * Production's twee, twee-pg61 with PG 0.25 and `--abstract-time 2000 --no-eqhint-consider`, at 30 s, with
    `--print-given-unsolved`.
  * No rule model.
* The scan is as loop.py's `--given-scan`: the canonical key of each given rule, in both orientations, against the
  unsolved unit goals' keys. The targets are refreshed every 10 minutes from production's solved.tsv.
* Hits go to loops/GSAT/hits.tsv. Since 05:40, givenmatch.py live reads them as it reads loops/GFAIL's, and runs
  each with the ancestry at 20 s, then the prefix at 40 s, with proofs going into production.
* A proof of G0 itself goes to loops/GSAT/direct.tsv, with its steps and the lemma axioms as a sketch.
* Pilot: 120 runs, 3 workers. That takes CPU from 21 to 24 until the time-matched control (2 workers) ends.
* Smoke test (loops/GSAT0, 2 runs at 10 s): 3,400 to 4,600 rules a run, of which 755 to 880 are some goal's
  statement (the check that the scan sees them), and no unsolved goal.

## Measures

* New goals hit per CPU h, and live-loop proofs from them per CPU h, against the 16 per CPU h from production's
  base runs and 0.6 for production's own.
* The decline over the runs: whether hits come from a few runs or from all of them.
* If it pays, the next step is a standing base-theory generator beside production, with more seeds, longer runs and
  rule models.

## exp39b: the stronger theories' goals without their extra axioms (05:46)

* Production's base hits came from short runs (6-8 s, L0 and the k60-k400 kNN members) of a_instances 440-459, not
  from base goals in general. So the question turns around: are many unsolved goals of the stronger theories base
  theorems, or theorems with the hypotheses' work already in proven sibling lemmas?
* Of the theories, 67 add 1 axiom to the base set, 28 add 2, 6 add 3, and 14 add 4-11.
* exp/naxrun.py (abs/nax1.sh, loops/NAX1): 60 of the 2,756 unsolved unit goals of such theories (seed 1), two arms at
  20 s with the same lemmas and hints:
  * full: the problem as it is;
  * nax: the extra axioms dropped.
* Lemma axioms: the 6 proven goals just below the goal in its original and 30 random proven base goals. All of them
  are theorems of the goal's theory, so either arm's proof is a proof in that theory.
* Measures: proofs per arm, the one-arm goals, and the hits of each arm's given rules.
* Interim (05:45, 13 runs of the base pilot): 2 new goals hit (aK2_eq_aK3_a 639 and aK2_eq_aK3_i 384), in 0.27 CPU h.

## Results

**exp39 pilot (05:39-06:33): 120 runs, 2.62 CPU h, 9 new goals hit and 1 direct proof.**
* The live loop proved 6 of the 9: aK2_eq_aK3_c 489, aK2_eq_aK3_i 384, aK2_eq_aK3_j 444, aK2_eq_aK3_o 450,
  nil3_23_32_to_26 476 and nslm_to_aa1 1196.
* It failed on aK2_eq_aK3_a 639 and nslm_to_aa1 1053 and 1099, in both passes.
* Direct proof: aK2rev 438, not in production before. It goes in through transfer.py run (abs/gsatd.sh).
* About 2.7 proofs per CPU h, against 0.6 for production's own runs. But that is a fifth of the hit rate of
  production's base runs (3.4 hits per CPU h here, against about 16).
* The hits come late in the runs: at rules 5,588 to 12,219 of runs with 6,828 to 14,339 rules. So at this setting,
  short runs would not reach them.
* Production's base runs that hit were short (6-8 s) with 36 to 406 lemmas nearest the goal. So the lemma choice
  (kNN, not random) is the first thing to vary.

**exp39b (05:46-06:33): nax 0, full 0 of 60**, in 2 × 60 runs of 20 s, and no goal hit by either arm. The 60 random
unsolved goals of the stronger theories are beyond a 20 s run with these lemmas and hints, with or without their
hypotheses. Dropping the hypotheses gains nothing here; stopped.

**exp39c (06:35-): production-like base runs.** abs/gsat2.sh: 8 s, 6 siblings + the 100 kNN lemmas of G0
(lemmas.LemmaIndex.select, as production's k100 member), 300 runs, 3 workers, run tag c in loops/GSAT/runs.tsv.

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

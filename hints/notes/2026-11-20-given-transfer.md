# Unsolved goals that other runs derived and did not use (exp38)

Written 20 Nov 2026, 02:21 UTC.

## Why

* Production's burst of 19-20 Nov (783 proofs from 22:20 to 02:13) came from the transfer loop
  (loops/XFL, transfer.py live; notes/2026-11-19-retrained-models.md). One L1 proof and its siblings had steps that
  were unsolved goals of 22 other originals. Proven at once, those started sibling chains of their own.
* transfer.py matches unsolved goals only against proof steps, the hints files: about 22 M positives in the logs.
* Every successful run's given log (loops/*/given/NAME: label, index, lhs, rhs, parents) also holds the rules
  it derived and did not use: 379 M over 643,782 logs (30 GB). A rule derived in a run on an unconditional unit
  goal is a consequence of that original's axioms and the run's lemmas, which are proven. So an unsolved goal of an
  original with the same or more axioms that is a variant of such a rule is a theorem. The rule's ancestry in that
  log (its parents, closed) is a proof sketch for it.

## Set and setting

* **Scan:** givenmatch.py over models/given_index.tsv. It skips climber loops (CL*, FUD*, SMK*: their runs may use
  unproven assumptions) and loops named *bad*.
  * Targets: production's 3,219 unsolved unconditional unit goals, both orientations.
  * Sources: logs of unconditional unit goals whose original's axioms are within the target's.
  * Twee prints each logged rule with its variables numbered in order of occurrence (66,797 of 66,797 checked). A
    variant is therefore a dict lookup of the raw (lhs, rhs).
  * 494,373 logs scanned with 3 workers. The first scan (02:20) split every line and read about 10 MB/s per
    worker; it was stopped at 02:25 for a scanner that splits each line at most 4 times and parses a log only on a
    hit, about 5 times faster. Output: loops/GM1/hits.tsv (goal, loop, source, rule index,
    label, ancestry size, at most 5 per goal, smallest ancestry first).
* **Proof:** each hit goal gets one run with the rule's ancestry first as hints, then the usual pool. That is
  transfer.py run with a sketch file as its source; since 02:21 an absolute source path is read as a file. Options
  are the transfer loop's, and proofs go into production's solved.tsv (`--live-dst loops/UL`), as XFL's do.
* Only variants for now. Instances, where the rule is more general than the goal, are left for later.

## Measures

* Hit goals, and how many the runs prove. Then production's proofs in the following hours from the chains these
  start.

## Scan result (02:59)

* **19 of the 3,218 unsolved unit goals are variants of a derived rule** (48 hits, 45 of them label 0, i.e. not a
  step of that run's proof). Sources: production 23 hits, exp30's P2D 5, the AB* loops 15, CA1 2, OR* 3.
* Ancestries are small: 1 to 27 rules for the first source of each goal.
* Of the scanned logs, 2 goals were proven outright by another loop and never merged into production:
  R1dist_to_aa1 643 and 645, by exp30's P2D (from zero on half2) at round 1. Their own P2D logs are among the
  sources.
* 243 goals have a given log outside production but are unsolved there. All but those 2 come from climber
  directories, whose logs include sketch runs with assumptions. F80 and F80b are climber directories (climb.tsv)
  that the name filter missed; none of the hits came from them, and givenmatch.py now skips every directory with a
  climb.tsv.
* **Instances** (`--instances`, the rule more general than the goal): across originals, AIM's few function symbols
  give root buckets of thousands of goals, 50 times the variant scan's time. So instance matching is restricted to
  the goal's own original's logs, at about 3 times the variant scan's time.
* Runs: abs/gm1run.sh from 03:00, 2 workers, 20 s each, into production (loops/GM1run/transfer.tsv).

## Runs (03:00-03:16): 13 of the 19 proved

| pass | sketch | time | proved | CPU |
|---|---|---:|---:|---:|
| gm1run.sh | the rule's ancestry | 20 s | 8 of 19 | 232 s × 2 |
| gm1b.sh | ancestry + the source run's axioms in it (.ax) | 40 s | 3 of 11 | 312 s × 2 |
| gm1c.sh | the log's whole prefix up to the rule (`sketch --prefix`) + its axioms | 40 s | 2 of 8 | 277 s × 2 |

* **13 proofs in 0.46 CPU h, about 28 per CPU h.** Production makes about 1 per CPU h at the moment.
* Proved: R1dist_to_aa1 643 and 645; mbol_to_aaxx 453; nil3_18 334; nil3_25 490; ns_to_aa1_b 661, 694, 702 and
  718; nslm_to_aa1 1028 and 1077; mbol_asqr 503 and 512.
* Still open: aa1_45_c 366, aa2_to_aa3 266, mbol_to_nil3 646, nil3_24 468, nil3_26 511, nil3_31 552.
* Why the ancestry is not enough: the given log's parents are a critical pair's, without the rewriting steps.
  E.g. mbol_asqr 512's rule 7723 records 1 parent, while its prefix holds 7,704 rules. The prefix sketch reproduces the
  source run's search; it proved that goal in 60 s.
* The proofs went into production's solved list. By 03:12 production had taken 14 synced proofs and proved
  nslm_to_aa1 1031 after 1028, so chains may follow.
* **Instance scan** (loops/GM2, `--instances`, own original's logs, 2 workers) from 03:17: 3,190 goals, 451,614 logs.

## exp38b: a sibling run's whole rule set as lemma axioms (from 03:18)

* Matching a single rule is the narrowest use of a log. More generally, a goal follows at once if a sibling run's
  rules join its two sides.
* Those rules are sound as axioms: they follow from that run's axioms and proven lemmas. This differs from
  production's pool@ members (the most frequent sibling proof steps as axioms) and from the transfer loop (proof
  steps only).
* exp/gm3prep.py, abs/gm3run.sh, loops/GM3run:
  * 40 unsolved goals, seed 1, out of 2,909 candidates;
  * each gets the newest production log of its original: all its rules (366 to 2,819, median 1,349) as lemma axioms
    and its proof steps as hints;
  * 20 s, 1 worker. Checked: the first run's input has 2,280 such axioms.
* Measure: proved of 40 per CPU h, against production's current ~1 per CPU h.
* **Result (03:40): 0 of 40** (0.38 CPU h). A sibling run's whole rule set does not join the unsolved goals, nor does
  it lead twee to a proof within 20 s. A genuine negative. The rule-level matches above (13 of 19) work because they
  pick the one run that derived the goal itself.
* Instance scan at 03:40: 1 goal hit in 300,000 logs, so instances add little beyond the variants.

## Live (from 03:42)

* `givenmatch.py live` (abs/gmlive.sh, loops/GML, every 20 min, 2 workers when there are hits). Each cycle:
  * scans the given logs of loops/UL and loops/XFL written since the last cycle against production's unsolved unit
    goals: variants, and instances within the own original;
  * runs the new hits as above, the ancestry at 20 s, then the log prefix with its axioms at 40 s. Proofs go into
    production.
  * Old logs need no rescan, as the targets only shrink.
* The full scan had used models/given_index.tsv, built on 19 Nov at 19:51, so it missed every log since: the burst's
  783. The first live cycle starts from that time.
* **Cycle 1 (03:42): 5 goals hit in 696 recent logs**, against 19 in 494,373 in the full scan. The frontier's logs are
  where the hits are.
* Cycle 1's runs: 2 of 5 by the ancestry pass (71 s × 2), 1 of the remaining 3 by the prefix pass (121 s × 2). So
  **3 of 5**, in about 0.11 CPU h.
* **Side check, transfer.py `find --instances`** (instances of unit-goal proof steps, last run 16 Nov; 3.5 min): only
  11 candidates now, 9 of them already tried by the transfer loop or exp38. The other 2 (own-original sources, abs/xi1run.sh)
  failed at 20 s. Not worth a live finder.
* **The instance scan (loops/GM2) ended at 03:49:** 2 goals hit in 451,614 logs (aa2_to_aa3 266, nil3_31 552).
  Both were already variant hits that failed all three passes. Instances add nothing here.
* **Fourth pass (abs/gm1d.sh, 03:51-04:05): 0 of 8.** The 8 hits still open (6 of exp38's 19 and 2 of cycle 1)
  were replayed as close to the source run as transfer.py run allows:
  * the source run's axioms up to the matched rule as the only lemma axioms;
  * the log's prefix as the only hints (`--max-hints 0`);
  * no target lemmas, no rule model, no PG, 80 s.
  Without the source's own rule-model scores and PG, the search does not retrace the source run. These 8 are known
  theorems without a printed proof; no more passes for them.
* Cycle 2 (04:02): 5 new logs, no hits.

## Ancestries fixed (04:08)

* The given log's parents are rule numbers; the rule at position k has number k+1 (given.py). givenmatch.py had
  read them as positions, so every ancestry so far followed the wrong rules.
* Check over 61,718 parents of proof steps in 200 production logs: read as numbers, 94% are proof steps or axioms;
  read as positions, 66%. Fixed in `ancestry()`. mbol_asqr 512's rule 7723 now has 14 ancestors, against 2.
* Pass 1 still proved 8 of 19, because the matched rule itself is always in the sketch.
* Fifth pass (abs/gm1e.sh, 04:10): the 8 open hits with the correct ancestries and their axioms, 40 s.

## Failed runs' given rules (loop.py --given-scan, ul74 from 04:15)

* Given logs exist only for successful runs. Most of production's CPU goes into failed runs on unsolved goals, the
  frontier, whose logs gave the hits in cycle 1 (5 in 696).
* loop.py `--given-scan DIR`:
  * Every failed run of an unconditional unit goal prints its given rules (twee `--print-given-unsolved`: about 6%
    more time on a 3 s run).
  * Those rules are checked against the unsolved unit goals' keys (both orientations, given.py's key, targets rebuilt
    every 10 minutes), with a prefilter on the rule without variables (0.04 s per run, against 0.17 s without).
  * A hit, for a goal of an original with the same or more axioms, writes the run's rule log to
    DIR/<stamp>/given/<name> and a row to DIR/hits.tsv in givenmatch.py's format.
  * givenmatch.py live reads the new rows each cycle and runs them like its own hits.
* Test (a planted target on a failed 3 s run of nil3_24 468): the hit rows and the log came out right; the run's
  success test is unchanged (an unsolved run prints no HINTS-END).
* ul74 = ul73 + `--given-scan /project/hintwork/loops/GFAIL` and member m10f@0 in place of m9f@0. Production rows from
  205,649.
* Measure: hits per hour and proofs from them, against the time cost (about 6% of production's twee time).

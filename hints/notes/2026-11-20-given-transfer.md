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

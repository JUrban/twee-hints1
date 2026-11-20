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

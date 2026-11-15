# Experiment scripts and goal sets

Copies of the launch scripts and goal lists behind the experiments in
`../REPORT.md`. They are kept in sync from the work directory
`/project/hintwork`, which is not under version control.

* `abs/*.sh` and `abs/*.py`: each script runs one experiment or one arm
  of one. The REPORT names the script in each section, for example
  2aj → `abs/cl6.sh`, `abs/fam.sh`, `abs/fam2.sh`.
* `sets/*`: lists of goal names (AIM60k problem names, one per line).
  For example, `sets/all` is the whole benchmark, `sets/gen48` the first
  48 of `sets/gen200`, and `sets/fam24` the family test set.

## How a run is set up

* The scripts `cd /project/hintwork` and call the tools in
  `/project/twee/hints` (`loop.py`, `climb.py`, …). They use twee
  binaries in `/project/bin` (`twee-eNN`, built from this branch) and
  problems in `/project/AIM60k/problems/tptp`.
* Each run writes to `loops/<ARM>/` (`results.tsv`, `solved.tsv`,
  `hints/`, `given/`, `climb.tsv`), its log to `loops/<ARM>.log` and a
  one-line summary to `loops/<ARM>.done`. These outputs are large and
  are not versioned; the REPORT gives the numbers.
* **Snapshots** (`--init loops/ULsX` etc.) are frozen copies of the
  production loop's state, so the arms of one test start from the same
  context. A snapshot holds `hints/` (the proofs' hint files) and
  `solved.tsv` with column 2 set to 0, because `--init` imports only
  those rows. To make one:

      mkdir loops/ULsX && cp -r loops/UL/hints loops/ULsX/hints
      awk -F'\t' 'BEGIN{OFS="\t"} {$2=0; print}' loops/UL/solved.tsv > loops/ULsX/solved.tsv

* Times are abstract (`--abstract-time 2000`: critical pairs, not CPU
  seconds), so runs are deterministic and comparable on a shared
  machine. `--wall-factor` and `--max-cpu` are only safety limits.
* Arms are paired: same snapshot, same goal set, same worker count. The
  control is the same tool with the tested feature off; the REPORT says
  which.

## Production

`abs/ul31.sh` is the current production loop: a cascade over `sets/all`
into `loops/UL`, with the restart history in its header comment. Its
output is `loops/UL31.log`.

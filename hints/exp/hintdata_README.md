# hintdata: proofs and records of the twee hint loop on AIM60k

This is the durable data of the twee hint-guidance project (code and reports: the twee repo, branch `hints`,
directory `hints/`). The first snapshot was taken on 19 Nov 2026 at about 15:30 UTC from the production loop
`loops/UL`: 47,229 solved goals. Every part is committed in small pieces (one original or one file per commit), so
the repo can be pushed in increments.

The goals are the AIM60k benchmark's problems (51,784 goals from about 150 originals, `problems/tptp/<goal>.p` in the
AIM60k repo). A goal is named `<original>__goal_<N>`.

## Layout

| path | what | format |
|---|---|---|
| `proofs/<original>/<goal>` | the proof steps of each proven goal, as twee's `--print-hints` writes them | one step per line: `lhs<TAB>rhs`, variables `X0, X1, ...` |
| `solved/UL_solved.tsv` | the production loop's solved goals | `goal<TAB>round<TAB>CPU seconds of the proving run` |
| `runs/UL_r<k>_results.tsv.gz` | every twee run of round k (round 5 is the long online round, 15-19 Nov) | `goal<TAB>THM/NO<TAB>CPU s<TAB>HINTSTATS ...<TAB>level label<TAB>t=<wall s since start>[<TAB>c=<context hash>]` |
| `chains/chain_records*.tsv.gz` | proof dependencies: the proven goals each proof used as lemmas (for chain hints, sibchain.py) | `goal<TAB>source<TAB>used goals, comma-separated` |
| `given/<original>.tar.xz` | rule logs: every rule twee added in a successful run, in order, labelled (training data of the rule models) | per goal: `label<TAB>index<TAB>lhs<TAB>rhs[<TAB>parent1<TAB>parent2]`; label 1 = in the proof, 0 = not, -1 = axiom |
| `models/` | rm*.bin + .vocab: LightGBM rule models in twee's binary forest format (`--rule-model M --rule-vocab V`); rm4t is production's. gc1.pt: the hint generator (copy model). gnn2.pt: GNN v2 (offline only) | |
| `sets/` | goal lists used by loops and experiments (`all` = all 51,784, `half1`/`half2` = the two random halves of the originals, ...) | one goal per line |
| `fromzero/<run>/` | 2-hour runs from zero on half1 (PGA, PGC, PGD, ORA, ORD) and half2 (P2A, P2D), 6 workers: solved list and run log | as above |

## What is not here

* Saved twee states (`loops/UL/states`, 101 GB). A rerun rebuilds them.
* Per-run problem files. Each run's lemmas are proven goals, built at dispatch: their statements come from AIM60k's
  problem files, chosen by the solved list.
* dp2.pt (67 MB).

## Restoring a loop directory

```
mkdir -p L/hints && cp proofs/*/* L/hints/
cp solved/UL_solved.tsv L/solved.tsv
mkdir -p L/given && for f in given/*.tar.xz; do tar -C L/given -xJf $f; done
```

## Updating

`hintdata_build.py` in the project's hints/exp directory (abs/ in hintwork) adds new proofs and the other files
in further small commits. Without `--given` it updates everything but the rule logs; with `--given` it writes only
the rule-log archives, one per original. Each part is re-committed only if it changed.

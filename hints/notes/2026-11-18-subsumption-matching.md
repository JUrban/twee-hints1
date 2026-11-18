# Hint matching by subsumption, as in Prover9 (exp7)

Started 18 Nov 2026, 06:14 UTC. Directory /project/hintwork/exp7; scripts in hints/exp/exp7_*.

## Why

The user (06:00): "in P9 the hint matchers subsume the hints, they dont have to be equivalent".

* Prover9 gives a clause a hint's weight when the clause subsumes the hint. The hint is then an instance of
  the clause, which is at least as strong as the hint.
* twee (since e1) boosts a critical pair only when it is a **variant** of some form of a hint, in either
  orientation (`eqHintScore`, `lookupEqHintG`). A pair more general than a hint got no boost. Its hint only
  dropped out later, as joinable, once the general rule was in.
* Earlier approximations:
  * `--eqhint-generalise` (2f) stores one-step generalisations of each hint (one subterm replaced by a variable):
    68 against 69 on the 345 at 8 s, neutral, off.
  * `--eqhint-instances` (2ah) is the other direction: a pair that is an instance of a hint. It floods the queue
    with false generalised hints and was dropped.
* Full subsumption matching was never tried. False hints cannot hurt it: a derived pair is true, so it cannot
  subsume a false hint.

## twee-e58 (`--eqhint-subsume`)

* **Index.** Every form of every hint, in both orientations (the keys of eh_map: each normal form a hint has
  had), is filed in a Map. The key is the first side's top symbol with each argument's top symbol or a wildcard
  (all 2^arity masks), plus the other side's top symbol or a wildcard. A variable side has its own key.
* **Lookup.** A critical pair's key is its first non-variable side's top symbol and argument tops (a variable
  gives the wildcard), plus the other side's top. One lookup gives the forms that agree with it to depth 1; then
  `match` / `matchIn` decide whether the hint is an instance of the pair.
* **Use.** It runs for pairs that variant matching missed, before `--eqhint-instances`, and also with the goal
  constants expanded. The boost is the variant boost (`hinted n`: weight plus the hint's factor).
* **Matched hints.** A new rule that subsumes a hint counts as matching it (`recordEqHintMatch`,
  `markResumedHints`), so HINTSTATS, HINTLOG and the stall counters see subsumption matches too.
* **Upkeep.** Forms that hint normalisation adds go into the index (`normaliseEqHints` collects them in its
  fold). The index is not saved with a state; on load it is rebuilt from the run's own hints, as eh_map is.
* With the flag off, e58 = e57. On 3 testbed goals the outputs match e57 at 7,402 / 22,020 / 40,000 pairs.
* **First look** (20 s, branch limit 100):

  | goal | hints matched, off → on | pairs, off → on | CPU s, off → on |
  |---|---|---|---|
  | Ka1_eq_Ka2 297 | 408 → 416 | 22,020 → 14,045 | 17.6 → 11.9 |
  | aK2_eq_aK3_i 233 | 362 → 393 | 7,402 → 8,259 | 3.5 → 4.8 |
  | nil3_30 370 (unproved) | 433 → 495 | 40,000 → 40,000 | 47.1 → 61.4 |

  Each pair costs about 30% more CPU on 370; candidate lists of general pairs are matched one by one.

## Test A: the 200 hard goals of the PG testbed

* Same commands as exp6's gb100 arm (pg/tb, production context, PG 0.25, 20 abstract s, CPU cap 200 s), so
  exp6's gb100 (e57, `--ground-joining-branch-limit 100`) is the control. The arm su100 adds `--eqhint-subsume`
  (e58). We compare proved, pairs to proof (abstract time) and CPU.

```
cd /project/hintwork/exp7
python3 run.py pg200_e58.cmds su100 2 --ground-joining-branch-limit 100 --eqhint-subsume
```

## Results

(pending)

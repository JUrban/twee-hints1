# The 80 s chain level on far goals (exp24)

Started 19 Nov 2026, 03:58 UTC. Directory /project/hintwork/exp24; scripts hints/exp/exp24_*. Part of the portfolio
task (notes/2026-11-18-portfolio-review.md).

## Why

* Production only lets a goal deepen near the frontier (`may_deepen`, `--frontier 1`, `--line-gaps 80,80`): at most
  1 place, or at most 80 proof lines, after the nearest proven goal below it. Far goals get the 5 s level and its
  5 s variants, nothing longer.
* At 03:55, of UL's 5,588 unsolved goals in sets/all, 4,176 were far. 3,683 of them had never had a run over
  30 CPU s. Of the 1,412 near goals, 341 had not had one either (queued).
* So the largest population has no measured yield for any deep member. The ratio rule cannot rank what it never
  ran, and the portfolio rule says to measure a member before leaving it out.
* If far goals pay even half the near goals' L1 rate (1.61 per CPU hour in ul56), they are the work for every
  worker once the frontier goals run dry. A far proof may also reopen its neighbours (the r class), as near proofs do.

## Set and setting

* **Sample:** 40 far goals with no run over 30 CPU s, drawn at random (far.py, seed 24) from the 3,683. By places
  after the nearest proven goal below: 2-5: 6, 6-12: 11, 13 or more: 23 (median of all far goals: 13).
  Originals: nil3_23_32_to_25 5, nil3_1K_e 3, nslm_to_aa1 3, then 2 or 1 each.
* **Member:** production's own L1, run by loop.py with ul56's flags: chain hints of the 10 nearest proven siblings
  (chain_records2.tsv), 6 lemmas, kNN 30, rule model rm4t, PG 0.25, twee-pg61, 80 abstract s. `--cascade 5,80
  --cascade-start 0` counts the 5 s run as tried in the current context. `--frontier 1000000` lets every goal
  deepen. No variants, no scheduler, 2 workers.
* **Context:** UL's 46,214 proofs at 03:57 (F.ctx). New proofs in the sample become context for their neighbours
  within the run, as in production; a neighbour then gets a fresh 5 s run first.

```
cd /project/hintwork/exp24; python3 far.py 24 40; bash run.sh
```

## A loop.py bug found on the way (fixed, 03:56)

* The first launch's 80 s runs got the original's pool, not the chain: 3,113 and 10,573 hints against chains of
  7,738 and 3,631.
* The chain records load in a background thread. The loop dispatched its first deep runs before they were in, and
  `deep_hints` then falls back to the pool. A production restart's first deep runs would get the pool in the same
  way; at a restart most early runs are 5 s fresh runs, so the damage there was small.
* Fix: a chain-hint level waits for the records, for up to 2 minutes, before dispatch. Skipping the level instead
  (my first version) ended exp24's loop at once, since nothing else was runnable. The relaunch waited 0.2 s, and its
  hint counts match the chains.

## Measures

* Proved, at what CPU, and new proofs per CPU hour, against ul56's L1 on near goals (1.61 at 03:50) and the
  deep variants after it (k60 0.82-1.19, p9 about 0.7).
* By distance (places, lines), to set a better far/near line than `--frontier 1`/80 lines, should that pay.
* Reopenings: fresh 5 s runs on the sample's neighbours after a proof, and what they prove.

## Results

**05:29: 0 of 40 proved, at 10,484 CPU s (2.9 CPU h; 262 s a run).** No goal ran twice; no sibling got a fresh
run, since nothing was proved.

* At the near goals' L1 rate (1.61 per CPU hour in ul56) about 4.7 proofs were due. Seeing none has a chance of about
  1%, so far goals are well below near ones. The sample cannot rule out a yield up to about 1 per CPU hour (95% upper
  bound, 3 proofs in 2.9 h).
* So far goals are not worth 80 s runs now. Their 5 s runs on each new context (the f class) and the frontier's
  advance are what reach them. A far goal becomes near when its neighbour below is proved.
* `--far-deep` stays off. With the measured prior it would score about 0.2 per CPU hour, level with the 320 s
  level (0.21), so the ratio rule would hardly ever pick it. It could serve as a last filler once every near option
  is used up.
* exp23's CPU went to exp25 instead (notes/2026-11-19-hint-cost.md), a cheaper and more promising question.

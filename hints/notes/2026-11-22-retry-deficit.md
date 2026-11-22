# The retry deficit: what Z8's final context proves in 5 s (exp61)

Written 22 Nov 2026, 15:40 UTC.

## Question

exp59 (notes/2026-11-22-hub-roots.md): 6 of 24 hub roots fell in under 10 s in Z8's final context, though Z8 had run
each only at about 5 s, hours earlier. How many of the 8,642 unit goals Z8 left unsolved at 6 hours would fall to a
single 5 s run in its final context? If many, better retry targeting (exp55's `--knn-drift`, a final sweep) has
much to gain; if few, the from-zero curve's end is set by goals that need more than a retry.

## Run

sets/z8u300 (exp/sets/z8u300): 300 of the 8,642, drawn with random.seed(60) from the sorted list. abs/rd5.sh
(exp/rd5.sh, waiter PID 2239989, 15:40): one fresh 5 s run each in loops/Z8F.ctx (Z8's 42,920 proofs), solve_new.sh's
model and lemma options, 1 worker, loops/RD5. It starts when the realproofs packer ends (about 1 CPU in all, 25 min).

## Measures

* Proved of 300, with a 95% interval; scaled to the 8,642.
* For the proved ones: Z8's runs on them (count, label, time of the last run) and the new kNN lemmas since.

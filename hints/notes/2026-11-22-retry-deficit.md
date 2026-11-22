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

## Result (22 Nov 16:29; RD5 ran 16:02:43-16:28:36, 0.42 CPU h)

* **9 of 300 proved** (3.0%; 95% interval 1.1-4.9%), median 1.5 CPU s. Scaled: about 260 of the 8,642 unit goals Z8
  left (92-426) fall to one 5 s run in its final context.
* So perfect late retries would add about 260 goals at 6 hours on all goals, about half that on half2. That bounds
  what exp55's `--knn-drift` can gain from 5 s retries alone; its +200 bar on half2 is likely out of reach, and a
  smaller gain can still be real (earlier retries also feed other goals).
* **Z8 never ran 4,475 of its 8,864 unsolved goals** (4,359 unit goals), most of them in nslm_to_aa1 (395),
  nsmr_to_aa1 (175) and the aK2_eq_aK3 originals. By design: the cascade runs a goal once it is near a proven
  sibling. In the final context those never-run goals proved 2 of 151 (1.3%), the others 7 of 149 (4.7%). Running all
  never-run goals at 5 s would cost about 6 CPU h for about 60 goals, below the late retry class's yield (19 per
  run-hour at Z8's end).
* Of the 7 proved goals Z8 had run, its last runs came at minutes 84 to 298.


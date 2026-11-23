# A learned lemma ranker for plain runs

Written 23 Nov 2026, 08:59 UTC, at the launch of its data sweep.

## Question

Plain frontier runs are proved by their lemma set (notes/2026-11-23-conditional.md: the hint bed; W's 400 kNN beat N's
100; most used kNN lemmas are goals of other originals). The kNN lemmas a proof used are spread almost evenly over
ranks 0-400 of the similarity list (idf-weighted Jaccard of goal features, lemmas.LemmaIndex): the ranking carries
little signal, and 1,000 kNN lemmas make twee slow (PLX1's smoke test). Can a model that ranks the candidates by
features of the goal and the candidate put the lemmas proofs need into the top 400 more often than similarity
does, and does that prove more frontier goals?

## Data (RKD1)

abs/rkd1.sh (exp/rkd1.sh): plain runs of 800 solved goals near the frontier (sets/rank800, copy exp/sets/rank800: the
later half of the trusted goals of the 40 originals with the most unsolved goals in PLN2, seed 65) with 200 earlier
and 60 later trusted siblings and 1,000 kNN lemmas (the goal itself excluded by LemmaIndex.select), 5 s, 2 threads,
the context t0641; cond/RKD1, never imported (the goals are solved). Each proof's Axiom lines give the used
lemmas (positives); the problem's other lemma axioms are the negatives. The sweeps' frontier proofs (PLZ8, PLN1,
PLN2, PLW1, PLK1, ...) are more data of the same kind; COND1/COND2 and the step bed only have 30 kNN.

## Plan

* Features per (goal, candidate): similarity and its rank, the candidate's original (same or not, sibling distance),
  axiom-set relation (equal or weaker), sizes, shared symbols, use counts (kp), dependency score (kd), the
  candidate's place in its original.
* LightGBM (n_jobs 2), grouped by original for validation; metric: recall at 100 and 400 of the used lemmas,
  re-ranking each problem's list, against the similarity order. A proof whose used lemma states the goal itself
  is left out.
* If recall rises clearly: condprove.py `--index learned:MODEL` (top 2,000 by similarity, re-ranked, top K) as a
  sweep against W on the frontier, as the queue's sweeps are read.

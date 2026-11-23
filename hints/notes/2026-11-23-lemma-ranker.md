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

## First test (read 09:04)

exp/lemmarank.py (features, grouped 5-fold CV by original, LightGBM; venv/bin/python3) on the frontier sweeps' proofs
so far (PLW1, PLK1, PLN1, PLZ8: 213 problems with a used kNN lemma, 32,986 candidate rows, 2,071 used):

| dir | K | problems | recall, similarity | recall, model | all used in top K, similarity | all used, model |
|---|---:|---:|---:|---:|---:|---:|
| cond/PLW1 | 50 | 23 | 0.183 | 0.436 | 0.043 | 0.043 |
| cond/PLW1 | 100 | 23 | 0.344 | 0.633 | 0.043 | 0.043 |
| cond/PLK1 | 50 | 16 | 0.176 | 0.448 | 0.000 | 0.000 |
| cond/PLK1 | 100 | 16 | 0.386 | 0.669 | 0.000 | 0.000 |
| cond/PLN1 | 50 | 24 | 0.584 | 0.728 | 0.083 | 0.208 |
| cond/PLZ8 | 50 | 150 | 0.665 | 0.816 | 0.273 | 0.400 |
gain: len_x 7710, simrel 7320, lhint 7209, uses 6921, len_ratio 6748, rank 6588, pos_x 6413, len_g 6154, sim 5518, sym_xonly 3199, dep50w 2763, sym_jac 2461, nvar_x 1871, dep50 1520, same_key 1369, lrank 1353, sib_dist 1191, sym_shared 1010, same_orig 74, eq_goal 0

Recall = the share of a proof's used kNN lemmas in the top K of its list (lists longer than K only). Even from 213
problems the model about doubles it at 50 and 100 within 400-lists. A caveat: the positives are what one proof used;
other candidates might have served as well.

## Frontier test (armed 09:04)

abs/lrab.sh (exp/lrab.sh, PID in cond/LRAB.pid): after RKD1, data from RKD1 and the frontier sweeps (cond/LR1.pkl),
the CV (cond/LR1.eval), model models/lemmarank/lr1; then the sweep queue is paused after PLS1, and PLL1 runs W's sizes
ranked by lr1 (condprove.py `--index learned:MODEL`: the similarity list's top 2,000 re-ranked) on production's
unsolved goals in the context of the live loop's cycle c5 (cond/PLNL/c5.trusted). The control is that cycle's W run
(c5W, the changed problems; the other goals failed under W with the same problem in an earlier cycle), in the same
context. Then PLL1's proofs into loops/CI3 and loops/UL, and the queue restarts.

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

## RKD1 and lr1 (read 09:59)

RKD1 (08:59-09:55): 743 of 800 solved goals proved with 1,000 kNN lemmas. cond/LR1.pkl: 770 problems with a used kNN lemma, 567,430
rows, 4,933 used (RKD1 and the frontier sweeps PLW1, PLK1, PLN1, PLN2, PLZ8). Grouped 5-fold CV (cond/LR1.eval):

| dir | K | problems | recall, similarity | recall, model | all used in top K, similarity | all used, model |
|---|---:|---:|---:|---:|---:|---:|
| cond/RKD1 | 50 | 552 | 0.446 | 0.651 | 0.246 | 0.375 |
| cond/RKD1 | 100 | 552 | 0.534 | 0.748 | 0.308 | 0.455 |
| cond/RKD1 | 400 | 536 | 0.784 | 0.935 | 0.517 | 0.743 |
| cond/PLW1 | 50 | 23 | 0.183 | 0.436 | 0.043 | 0.043 |
| cond/PLW1 | 100 | 23 | 0.344 | 0.637 | 0.043 | 0.087 |
| cond/PLK1 | 50 | 16 | 0.176 | 0.460 | 0.000 | 0.000 |
| cond/PLK1 | 100 | 16 | 0.386 | 0.671 | 0.000 | 0.062 |
| cond/PLN1 | 50 | 24 | 0.584 | 0.780 | 0.083 | 0.292 |
| cond/PLN2 | 50 | 5 | 0.533 | 0.883 | 0.200 | 0.600 |
| cond/PLZ8 | 50 | 150 | 0.665 | 0.843 | 0.273 | 0.440 |
gain: rank 40331, simrel 29873, uses 23670, len_x 23214, len_ratio 19349, len_g 16405, pos_x 15864, lhint 15364, sim 13993, lrank 12370, dep50w 6374, sym_xonly 6020, nvar_x 4516, sym_jac 4271, dep50 4068, sib_dist 4011, same_key 2528, sym_shared 2054, eq_goal 634, same_orig 260

On RKD1's 1,000-lists the model keeps 0.94 of the used lemmas in its top 400 (similarity 0.78), and all of a proof's used
lemmas in 0.74 of the problems (0.52): with the same 400 lemmas twee would see the whole lemma set of half again as
many proofs. The leading features are the similarity rank and score, the candidate's use count and its size.
lr1 (models/lemmarank/lr1) is trained on all rows.

PLL1 started 09:59 by abs/lrab2.sh (exp/lrab2.sh): lrab.sh's last steps without its wait for c5W's end (the context file
cond/PLNL/c5.trusted is all PLL1 needs; the queue had ended, its other sweeps held). The control c5W runs at the same
time in the same context.

## PLL1 result (09:59-10:54; read 10:55)

3 proofs of 3,282 goals, 2.61 CPU h, all merged into production (loops/CI3, 10:54). In this context every goal had
already failed under W at least once (PLW1, c4W), so W's own proofs here are only what c5W finds on changed problems
(the control; still running). The kNN lemmas the proofs used, by their similarity rank (LemmaIndex.select's top
2,000 in the context c5):

| goal | kNN lemmas used | ranked 400 or beyond by similarity | deepest similarity rank |
|---|---:|---:|---:|
| aKperms_1__goal_386 | 26 | 13 | 1617 |
| nil3_27__goal_533 | 8 | 4 | 1776 |
| nsmr_to_aa1__goal_891 | 24 | 5 | 586 |

Every proof needs lemmas W's list (similarity top 400) does not hold: the ranker brought them in.

exp/lemmarank.py now evaluates the model with numpy when lightgbm is missing (class Trees: the text model's trees,
numeric splits): the same raw scores as lightgbm (max difference 0.0 on 2,000 rows of cond/LR1.pkl), 0.1 s for 2,000
candidates, so condprove.py and loop.py run it under the system python3. Rerun of PLL1's 3 proofs that way
(cond/LRSYS, 11:06): all 3 proved; their kNN lists are the same but for 2 lemmas, in a slightly different order (the use counts and
proof steps come from production's current outputs, which grew since 09:59).

## In loop.py (11:13)

`--variants plr[kN][sM]` with `--lemma-ranker MODEL` (loop.py): a plain run whose kNN lemmas are re-ranked by the model,
in the loop's own context (its lemma index, the use counts of its kept outputs, the proof steps in its hints dir), built
in start_vix's background thread with kp/kd and rebuilt with them; a plr variant is eligible once its ranker is in.
Smoke test abs/plrsmoke.sh (exp/plrsmoke.sh; PLL1's 3 goals in loops/ULT.ctx, the context of 22 Nov 21:39, 1 worker):
the ranker was built in 24 s; the ranked level ran 3 times and proved 1 (nil3_27__goal_533).

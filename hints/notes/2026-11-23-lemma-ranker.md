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

## The control, and the live loop (read 11:24)

c5W (W in the same context, 09:46-11:23; 3,143 problems run, 139 SAME): **1 proof, 3.30 CPU h, 0.3 per CPU h**;
PLL1: **3, 2.61 CPU h, 1.2 per CPU h**, and W's 1 among them (+2 −0; exp/condcmp.py cond/PLNL/c5W cond/PLL1). Small
numbers, but every PLL1 proof needed lemmas beyond W's list, so the mechanism is the one the CV measures.

Live loop: abs/plainlive3.sh (exp/plainlive3.sh, PID in cond/PLNL3.pid) runs N and L (W's sizes ranked by lr1, numpy
under the system python) each cycle, from 11:24: plainlive2.sh was stopped in c6N (partial, 0 proofs, not imported);
PREV_N cond/PLNL/c5N, PREV_L cond/PLL1. The ranker's use counts and proof steps change with production's outputs,
so most L problems change each cycle: L cycles are full sweeps, as W's were.

## lr2's features, and a leak fixed (11:39)

* LambdaRank (lightgbm's LGBMRanker, the same features, cond/LR1.pkl, RKD1's problems): recall at 100 0.778 (binary
  0.748), all used in the top 100 0.493 (0.455); at 400 0.938 against 0.935, 0.746 against 0.743. The sweeps use 400:
  the binary model stays.
* New features (FEATS2): the goal's proved siblings within 20 goals whose proof steps (deps) or kept output's
  USEDAXIOMS hold the candidate, and the nearest such sibling's distance. A model's .json names its features and takes
  its columns (lr1 keeps FEATS; the same order for lr1 through the new code on 3 goals).
* **A leak in lr1's training rows:** for a solved goal (RKD1's), production's own kept output counted in the
  candidate's use count, so a lemma production's proof had used scored higher. Now the goal's own output is left out
  (unsolved goals have none, so lr1's frontier ranking is unchanged). PLZ8's goals are all production-solved, so its rows had it
  too; the rows of goals the plain sweeps proved first (PLW1, PLK1, PLN1: their records went into loops/UL/out by
  merge.py, which the use counts do not read) had none, and showed the same gains (0.18 to 0.44-0.46 at 50). cond/LR2.pkl is built with the fix; its CV compares lr1's
  features with FEATS2.

## lr2 (11:50)

cond/LR2.pkl (the leak fixed; with PLL1, PLS1 and the live loop's c4N, c4W, c5W): 783 problems, 570,530 rows, 5,138 used. CV
with lr1's features (cond/LR2.eval.v1) and with FEATS2 (cond/LR2.eval):

| dir | K | problems | recall, similarity | lr1's features | FEATS2 | all used, lr1's features | all used, FEATS2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| cond/RKD1 | 100 | 552 | 0.534 | 0.749 | 0.744 | 0.458 | 0.451 |
| cond/RKD1 | 400 | 536 | 0.784 | 0.933 | 0.941 | 0.741 | 0.752 |
| cond/PLW1 | 50 | 23 | 0.183 | 0.443 | 0.500 | 0.043 | 0.043 |
| cond/PLW1 | 100 | 23 | 0.344 | 0.643 | 0.653 | 0.087 | 0.087 |
| cond/PLK1 | 50 | 16 | 0.176 | 0.469 | 0.497 | 0.000 | 0.000 |

The fix changes little (RKD1 at 400: 0.933 against 0.935 with the leak), so lr1 was not riding it. The sibling features
add a little at 400 and on the frontier lists. lr2 (models/lemmarank/lr2, FEATS2, all of LR2) replaces lr1 in the live
loop after its current cycle (abs/plainlive3_lr2.sh, exp/plainlive3_lr2.sh: cond/PLNL.stop, then MODEL=lr2).

## exp65 (planned 11:56)

abs/exp65.sh (exp/exp65.sh): after exp64, the ranked plain level from zero: Q5A (DEEP_A, exp64's better arm) against
Q5B (DEEP_A with `plrk400s130@0`, `--lemma-ranker models/lemmarank/lr2`, prior 3, in `--explore-labels`); half2, 4 workers
each, 6 hours, exp64's CPU sets. Launched at exp64's end with DEEP_A chosen then. In a from-zero loop the ranker's
use counts and proof steps come from the loop's own outputs, smaller than production's; the A/B shows whether the
model trained on production's context still helps there.

## exp65 changed (13:05): the ranker for every run

exp64's plain levels proved few goals directly (6 of P4B's one-arm goals at 2 hours), so a ranked plain level is
unlikely to move a from-zero run. The larger lever is the 30 kNN lemmas of every run: exp59 found that most goals
production has and the from-zero runs lack fall at the 5 s first level once the right lemmas are in the problem
(notes/2026-11-22-hub-roots.md), and at K = 50 the model's recall of used lemmas is 0.65 against similarity's 0.45.

* loop.py `--lemma-ranker-all` (with `--lemma-ranker MODEL`): start_vix also builds 'plra', the same ranker with
  `--lemma-ranker-pool` (default 1,000, the training lists' length; 0.13 s per goal, 2,000: 0.27 s, similarity 0.02 s:
  scratchpad timing on 12 goals of sets/hintbed600), and every run's kNN lemmas come from it (all levels and the kN
  and pl variants; kp, kd and the cut candidates keep theirs). The retry signals (--retry-knn, --knn-ctx,
  --knn-drift) still watch the similarity picks: a new proof near the goal still counts as a new context.
* Smoke test (exp/rankallsmoke.sh, loops/PLA1: 6 goals in loops/ULT.ctx, 1 worker, 0.05 h): the ranker was built
  in 22 s; a run's problem held 30 kNN lemmas, 16 of them in the similarity top 30; no errors (no proofs: 2 rounds
  of 5 s runs on hint-bed goals).
* **exp65** (abs/exp65.sh, exp/exp65.sh): Q5A, DEEP_A (exp64's better arm), against Q5B, the same with
  `--lemma-ranker models/lemmarank/lr2 --lemma-ranker-all`; otherwise as planned. One change.

## Z9's gap: an offline pre-check for exp65 (started 13:06)

exp/z9gap.sh (abs/z9gap.sh): 500 goals production solved and Z9 (8 hours from zero, 6 workers) did not
(exp/sets/z9gap500, seed 66, of the 4,355 such goals at loops/TRUSTNOW/t1256), in Z9's final context (its 44,161
proofs). Plain 5 s twee (condprove.py `--proved`: only Z9-proved siblings, 4 earlier and 2 later, and 30 kNN lemmas,
about L0's lemma part without its hints and rule model), both arms at once on 1 thread each: cond/ZGS by similarity,
cond/ZGR by lr2 from the similarity list's top 1,000 with use counts, proof steps and sibling features from loops/Z9
(condprove.py `--rank-loop`, new), so no production proof enters. Measures: proved in each, +/−, union.

## lr2 has seen half2: lr2h (13:12)

350 of LR2.pkl's 783 problems are goals of sets/half2 (exp64 and exp65's set; half1 and half2 split by original).
lr2h (`lemmarank.py train cond/LR2.pkl models/lemmarank/lr2h --exclude sets/half2`) is trained on the other 433. On
RKD1's 250 half2 problems (exp/lemmarank_held.py, cond/LR2H.held):

| model | K | recall, similarity | recall, model | all used in top K, similarity | model |
|---|---:|---:|---:|---:|---:|
| lr2h | 30 | 0.355 | 0.539 | 0.188 | 0.264 |
| lr2h | 50 | 0.405 | 0.622 | 0.208 | 0.324 |
| lr2h | 100 | 0.512 | 0.737 | 0.284 | 0.428 |
| lr2 | 30 | 0.355 | 0.807 | 0.188 | 0.508 |
| lr2 | 50 | 0.405 | 0.856 | 0.208 | 0.568 |
| lr2 | 100 | 0.512 | 0.916 | 0.284 | 0.688 |

lr2's numbers there are in-sample; lr2h's are held out, and still well above similarity. exp65's Q5B now runs lr2h.
The Z9-gap pre-check had the same problem (25 of its 500 goals are lr2 training problems, 403 of their originals
have some): its lr2 arm was stopped at 44 goals; exp/z9gap2.sh runs lr2h on the 235 of the 500 in half2
(exp/sets/z9gap500h2, cond/ZGH), compared with cond/ZGS on those. The live loop keeps lr2: its goals are unsolved,
so none has a proof in the training data.

The other half (13:13): lr2h1 (`train ... --exclude sets/half1`, the 350 half2 problems) for the 265 goals of the 500 in
half1 (exp/sets/z9gap500h1, exp/z9gap3.sh, cond/ZGH1), started when cond/ZGS ends; with cond/ZGH every goal then has
a ranker that has not seen its original, against cond/ZGS's similarity lists.

## A hinted ranked member for production (13:20)

loop.py `--variants rkN[sM]` (with `--lemma-ranker`): a hinted run (pool hints, rule model) whose N kNN lemmas come
from the ranker (pool 2,000), a member of its own beside kN, so production's explore machinery measures it in proofs
per CPU hour instead of a switch for every run. Smoke test exp/rksmoke.sh (loops/PRK1, sets/rankall_smoke in
loops/ULT.ctx, 1 worker, 0.05 h, rk30@0 first): the ranker built in 24 s, 6 Vrk30@0 runs with hints, no errors.
For production (its goals are unsolved, so lr2 has seen no proof of them) after the pre-checks: rk30@0 and
plrk400s130@0 as explored members.

## Why the ranker's 30 can lose: clusters (13:22)

The first 127 paired goals of the pre-check: similarity 8 proofs, lr2h 4. In the 4 goals only similarity proved
(at the note's writing), its proofs used 3, 15, 18, 11 of their 30 kNN lemmas, and lr2h's 30 held 1, 6, 3, 6 of those: similarity gives twee a
cluster of near-identical lemmas that work together, while the model scores each lemma alone, trained on 1,000-lemma
problems where a proof takes a few of many substitutes. Recall of used lemmas there does not say a 30-lemma set
suffices.

A mixed list: the similarity list's top 15 first, then the model's best 15 of the rest (lemmarank.Ranker.MIX,
condprove.py `--rank-mix`, loop.py `--lemma-ranker-mix`; checked on 2 goals: the head is similarity's top 15, the tail
the model's order). Arm exp/z9gap4.sh: cond/ZGM2 (half2 goals, lr2h), then cond/ZGM1 (half1 goals, lr2h1), 1 thread.
exp65 waits for the pre-check: if the ranked or mixed lists lose to similarity on these goals, its Q5B changes (a mixed
list, or rk30@0 as a member after L0 instead of a switch for every run).

Proof sizes (13:23; kNN lemmas a proof used, condprove.py's column 6): RKD1 743 proofs, median 2, 80 with 10 or more; PLW1 23 proofs, median 12, 16 with 10 or more; PLL1 3 proofs, median 24, 2 with 10 or more; ZGS 19 proofs, median 3, 8 with 10 or more. The training data
are mostly small proofs. By proof size on RKD1's half2 problems (exp/lemmarank_bysize.py lr2h, cond/LR2H.bysize), the
share whose used lemmas are all in the list's top K, with the mixed list (similarity's top K/2, then the model's):

| used | problems | K | similarity | model | mixed |
|---|---:|---:|---:|---:|---:|
| 1-1 | 55 | 30 | 0.673 | 0.800 | 0.782 |
| 1-1 | 55 | 100 | 0.855 | 0.909 | 0.909 |
| 2-4 | 140 | 30 | 0.193 | 0.314 | 0.293 |
| 2-4 | 140 | 100 | 0.464 | 0.664 | 0.636 |
| 5-9 | 85 | 30 | 0.000 | 0.047 | 0.059 |
| 5-9 | 85 | 100 | 0.294 | 0.353 | 0.341 |
| 10-999 | 70 | 30 | 0.000 | 0.000 | 0.000 |
| 10-999 | 70 | 100 | 0.271 | 0.271 | 0.271 |

The model is at or above similarity at every size, but for proofs of 10 or more neither covers them at 30: a
1,000-lemma proof picks among substitutes, so its labels cannot say which 30 suffice. The runs decide.

## The pre-check at 30 lemmas: similarity wins (13:37)

On the 235 half2 goals (held-out lr2h; all 235 paired): similarity 11, ranker 6 (+0 −5, union 11), mixed
(similarity's top 15, then the ranker's) 9 (+1 −3, union 12). Similarity on all 500: 24. The ranker's 30 lose on these hard goals,
and the mixed list does not gain. So `--lemma-ranker-all` (every run's 30 from the ranker) would likely cost at L0;
**exp65 as designed is not run.** The ranker won with 400 lemmas on the frontier (PLL1), where whole clusters fit; the
from-zero loop's kN members (60-400 lemmas) are where a ranked list could pay. Next pre-check (exp/z9gap5.sh,
after the half1 arms): the same 235 goals at 100 lemmas, cond/ZKS similarity against cond/ZKH lr2h.

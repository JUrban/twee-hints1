# The whole public benchmark at 4 s per problem, long runs on hard holdout, and a Prover9 control

*Reconstructed on 17 Nov from REPORT 2h–2i and the session's commands (13 Nov 02:00–08:00). CPU-time limits.*

**Question.** At a fixed per-problem budget, on all 51,784 public problems, how much do the rule model, kNN
hints and lemmas give over plain twee? Is twee a good hint user compared with Prover9, the classic one?

**Setup.**
* **Plain:** one 4 s run per problem, 8 in parallel (28.1 CPU h).
* **The loop** (loops/ALL, twee-e12, rm4 at 0.1 with penalty 2, kNN 30:100):
  * round 0, 2 s, with hints from the start, from the training-split pools (hints/train_pool 8,562 proofs,
    hints/tr30_g1_pool 757);
  * round 1, 2 s on the unsolved, the pool extended by round 0's proofs, 12 in parallel.
* **The loop + lemmas** (loops/ALL_lem, `--init loops/ALL --start 1`): the same round 1 with 3 proven
  siblings below N as axioms (`--lemmas 3`). A third round (`--start 3`, -j 18) used lemmas and hints from
  rounds 0–1.
* **Long runs:** 300 random holdout problems that neither plain 4 s nor the loop solved, 60 s, with lemmas
  from everything proven so far. Then a final 60 s round on all 2,366 holdout problems unsolved by any 4–6 s
  run (rm4, 3 lemmas, kNN hints; 2 hours on 18 cores; runs/hou_r2_final_t60).
* **Prover9 control** (p9loop.py, Prover9-new master with default settings, -j 4):
  * sets/fam2: the families aa1_15 (198 goals) and aK2_eq_aK3_q (273), 471 problems, rounds of 2, 2, 2 and
    8 s.
  * Hints: the positive proof steps of all solved goals of the same original, skolems as variables
    (Veroff's practice), as `formulas(hints)`, about 14 per proof.
  * twee runs plain, without the model, with the same pool (`--pool original`).

**Results.**

| system | train | devel | holdout | all | CPU h |
|---|---:|---:|---:|---:|---:|
| E 2.6, 1 s (README) | | | | 18,369 | |
| Prover9, 1 s (README) | | | | 18,973 | |
| twee, plain, 4 s | 25,416 | 2,441 | 3,203 | 31,060 | 28.1 |
| loop, round 0 only (2 s) | 26,144 | 2,551 | 3,257 | 31,952 | 13.5 |
| loop, 2 + 2 s | 26,493 | 2,578 | 3,306 | 32,377 (+4.2%) | 24.8 |
| loop + lemmas, 2 + 2 s | 27,190 | 2,642 | 3,417 | 33,249 (+7.0%) | 24.5 |
| + third round (2 s) | | | 3,473 | 33,668 (+8.4%) | |

* Loop + lemmas against plain 4 s: +2,530 −341. Of the 341, plain solves 247 in 2–4 s. Holdout: +265 −51.
* Lemmas triple round 1's gain (1,297 against 425 new) at the same CPU.
* Holdout problems solved within a time:

  | within | plain | loop round 0 |
  |---|---:|---:|
  | 0.25 s | 2,309 | 2,697 |
  | 1 s | 2,776 | 3,067 |
  | 2 s | 3,005 | 3,248 |

On the 300 hard holdout problems at 60 s:

| setting | solved | vs plain |
|---|---:|---:|
| plain | 44 | |
| rm4 | 53 | +11 −2 |
| plain + 3 lemmas | 50 | +12 −6 |
| rm4 + 3 lemmas + kNN hints | **56** | +17 −5 |

* The union with plain is 61.
* No time-sliced portfolio beat the guided run alone: plain 15 s then guided 45 s gave 50; rm4 40 s then
  lemmas 20 s gave 56.
* The final 60 s round on 2,366 problems solved 399, bringing holdout to 3,913 of 5,880 (66.5%; 40 of these
  only by plain 4 s).

Prover9 against twee in the same loop (471 problems):

| | round 0, 2 s | +2 s, hints | +2 s, hints | +8 s, hints |
|---|---:|---:|---:|---:|
| Prover9 | 240 | 248 | 270 | **288** |
| twee | 347 | 361 | 362 | **376** |

Controls on the round-0 failures, 8 s:
* No hints: Prover9 +3 of 231, twee +20 of 124.
* Prover9 with the statements of all earlier goals as hints (solved or not): +11.

**Reading.**
* **Train and devel are optimistic.** rm4 and the pool hold proofs of these problems' siblings, and rm4 holds
  2 s proofs of many of the problems themselves. Holdout is clean in data (2026-11-12-holdout.md, with its
  design-level caveat).
* **The lemma totals are lemma-assisted proofs** (2026-11-17-lemma-circularity.md). That is sound in the
  batch, and a different measure from the README's per-problem baselines.
* **Prover9 is the better hint user:** +48 from hints against +3 from time alone. Twee's hints give +29
  against +20 from time. But twee without hints (367) beats Prover9 with the loop (288): Prover9's base
  search is its limit here. Prover9 ran with defaults; Veroff's tuned settings were not tried.
* The 300 are a random sample, so the 60 s numbers are clean of selection, but with ±3 noise.

**Decision and next.** The loop with lemmas becomes the benchmark loop; the full run continues in rounds
(2026-11-13-online-pools-cascade.md). REPORT 2h, 2i.

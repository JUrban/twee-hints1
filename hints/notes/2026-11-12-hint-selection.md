# Which hints to give: pools, kNN, and a learned ranking (transfer benchmark T1)

*Reconstructed on 17 Nov from REPORT 2, commit 6f1947c and the session's commands. CPU-time limits (before
abstract time); noise as in 2026-11-12-hints-dev10.md.*

**Question.** L1's pool (all proofs of the original, about 1,000 hints) gained little. Is the pool too large,
and does a smaller, targeted selection do better?

**Setup.**
* **T1** (sets/T1, 12 Nov 20:09): 276 dev10 problems:
  * the 176 that L1's round 0 solved in 0.8–2 s;
  * 100 drawn from L1's round-3 failures (`shuf -n 100 --random-source=<(yes)`, a fixed stream).
* **Leave-one-out:** hints/transfer.py runs each problem with hints from the other solved problems' proofs
  (loops/L1/hints), 4 s, twee-h5.
* **Strategies:**
  * none;
  * all of the same original;
  * near:10 (the 10 nearest goals by line in the original proof);
  * before:10;
  * kNN 30:100 (hintsel.py): the 30 solved goals most similar by goal statement, from any original. The
    similarity is idf-weighted Jaccard over subterm shapes of depth ≤ 3, variables as `*`. A hint scores
    the sum of the similarities of the neighbours whose proofs contain it; the top 100 are taken.
* **Offline:** over 200 solved problems, the recall of each pool (the share of the problem's own proof
  lemmas it contains) and its precision.
* **Learned reranking** (lgbsel.py, learnsel.py): LightGBM on pair features (kNN score, frequency) plus
  ENIGMA-style features of hint and goal. Training and testing are on different originals.

**Results.**

PAR2 is the mean time over the 176 slow-solved problems, a failure counting 8 s (twice the limit). The
output was printed by the analysis snippet at 12 Nov 20:20 and 20:26 (xfer/T1_*):

| hint selection | slow-solved (176) | PAR2 | unsolved (100) |
|---|---:|---:|---:|
| none | 176 | 1.51 | 6 |
| all of the same original (~1,000 hints) | 164 | 1.84 | 11 |
| all, factor 0.3 | 164 | 1.80 | 10 |
| all, requeue 0.1 | 156 | 2.30 | 9 |
| 3 nearest by proof line | 171 | 1.27 | 9 |
| 10 nearest by proof line | 171 | 1.14 | 8 |
| 10 nearest, factor 0.3 / 0.6 | 171 / 172 | 1.15 / 1.13 | 8 / 8 |
| 10 nearest, requeue 0.1 | 170 | 1.33 | 10 |
| 3 before | 171 | 1.37 | 7 |
| 10 before | 172 | 1.26 | 9 |
| 10 before, requeue 0.1 | 172 | 1.45 | 10 |
| kNN 30 neighbours, top 100 | 175 | **0.71** | 10 |
| kNN 30:100, requeue 0.1 | 174 | 0.77 | 10 |
| kNN 30:200, requeue 0.1 | 173 | 0.70 | 10 |
| kNN 100:400, requeue 0.1 | 172 | 0.71 | 10 |

* Requeue, which made the self-replay 8 times faster, made transfer slightly worse in every pool. With
  other problems' hints, re-simplifying the queue also brings forward the pairs that match wrong hints.
* All of these use 20 workers at CPU-time limits, so a difference of 1–2 problems is noise.

Offline recall and precision:

| hint pool | size | recall | precision |
|---|---:|---:|---:|
| all solved goals of the same original | ~1,100 | 0.71 | 0.024 |
| 10 nearest by proof line | 168 | 0.60 | 0.14 |
| kNN across originals, top 100 | 100 | 0.74 | 0.26 |
| kNN, same original only, top 100 | 100 | 0.66 | |
| kNN, 400 hints | 400 | 0.81 | |

Learned reranking: recall@100 0.849 against kNN's 0.838; precision 0.156 against 0.154. All 600 kNN
candidates hold 0.856.

**Reading.**
* Big pools hurt through search, not matching cost. Every matched hint goes to the front and pairs with
  every rule. In aa1_45_c__goal_224, 223 irrelevant hint rules came first; the real proof's lemmas arrived
  about 230 rules later (5.8 s against 3.4 s unguided).
* kNN halves the time on the slow-solved problems and solves 10 of 100 against 6 without hints. 4 extra
  of 100 is weak evidence at CPU-time limits.
* Recall and precision are measured against the one proof twee happened to find; other proofs may use other
  lemmas.
* Reranking cannot help much: the missing lemmas are in no neighbour's proof.
* This kNN later became the lemma selection (REPORT 2l: `lemma_knn 30`). For hints, production went back to
  the whole original's pool (`--pool original` in abs/ul41.sh). On 13–14 Nov, at 20 abstract s with online
  pools, the whole pool beat kNN 30:100 (60 against 55 of 189 goals, REPORT 2o): at 2 s a big pool hurts,
  at 20 s it does not (2026-11-13-online-pools-cascade.md).

**Decision and next.** kNN 30:100 for the loops of 12–13 Nov. REPORT 2.

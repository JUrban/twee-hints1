# Learned parental models on 10 numbers per rule

**Question.** Can a model trained on proof data beat the sum filter (52 of 200, 2026-11-17-pg-sum-filter.md)?
This follows the paper's labels (P_proof: a pair is positive when a proof step came from it) and its
negative sampling (8 negatives per positive in each run). As features, it uses ten cheap numbers per rule
instead of ENIGMA vectors (those follow in 2026-11-17-pg-pcat-enigma.md).

**Setup.**
* **Data capture** (pg/cap1*):
  * 20 minutes of the loop on half1 from zero, 8 workers, every twee command logged (`LOOP_PRINT_CMD=1`,
    pg/solve_new.cap.sh). It proved 15,577 goals.
  * pg/relog.py re-ran captured commands of proved goals with `--pg-log` (twee-e48):
    * d1: easy goals;
    * d2: 1,500 random goals among those proved late (row ≥ 10,000 in cap1's solved.tsv, cap1.late.tsv).
  * Re-running a captured command is deterministic, so the logged run is the run that proved the goal.
* **Rows** (hints/pgdata.py): one row per (new rule, partner) pair where both rules have a score. The
  features are each rule's 10 pgRuleFeatures, fixed when the rule is added:
  * raw score q;
  * lhs size, rhs size, number of variables, depth;
  * hint-match code, orientation code;
  * id, the queue score of its pair, the number of actives.

  The id gap is added as feature 21.
  * Train: 1,300 d2 runs (2,963 positive pairs, 8 negatives each).
  * Test: 200 held-out d2 runs with all 3 million pairs (test2).
  * hard1: the 29 testbed runs that base proves.
* **Models** (hints/pgtrain.py, LightGBM, 100 trees):
  * pgm1: full forest on 21 features;
  * pga1: additive (interaction constraints: each tree on one rule's 10 features);
  * pga2: pga1 without the queue score (`--drop`);
  * pgq: q alone;
  * pgqh: q and hint match.
* **Online:** the 200-goal testbed with `--pg-model M --pg-threshold P`, at 4 workers:
  * pgtest4 (twee-e50): pga1 at 0.01, 0.02, 0.05 and 0.1;
  * pgtest5 (twee-e51, started after 17:28, ended about 18:00): every model at the threshold that keeps the same share of
    overlaps offline as the sum at 0.269 (35.5%).

**Results.**

Offline, share of overlaps kept at a given share of proof pairs kept (lower is better):

| filter | test2, 95 / 90 / 85% | hard1, 95 / 90 / 85% |
|---|---|---|
| full forest pgm1 | 22.0 / 10.8 / 7.4% | 46.5 / 26.1 / 15.4% |
| additive pga1 | 19.2 / 11.1 / 7.6% | 45.4 / 30.0 / 16.4% |
| sum of q | 50.7 / 36.1 / 30.0% | 62.8 / 48.6 / 39.5% |

Online, proved of 200:

| run | filter | proved | CPU s |
|---|---|---:|---:|
| pgtest4 | base | 29 | 880 |
| | sum 0.269 | 52 | 882 |
| | pga1 at 0.01 / 0.02 / 0.05 / 0.1 | 37 / 37 / 39 / 37 | 749 / 716 / 693 / 711 |
| pgtest5 (matched pruning) | base | 29 | 933 |
| | sum 0.269 | **52** | 993 |
| | pga1 0.0146 | 39 | 819 |
| | pga2 0.0153 | 39 | 795 |
| | pgq 0.0636 | 49 | 1,040 |
| | pgqh 0.0517 | 45 | 966 |

At matched pruning, the models keep this share of proof pairs offline: pga1 98.1%, pga2 97.8%, pgq 86.8%,
pgqh 90.0%; the sum 88.5%.

**Reading.**
* Offline ranking and online result run opposite: the models that keep the most proof pairs offline prove
  the fewest goals online. My reading is that the queue-score and size features teach the model the
  existing selection order (the rule model's choices, which made the proofs it learns from). Ranking pairs
  by that is close to what the queue does anyway, and gives no new diversity.
* Online, the sum's 52 against pgq's 49 (q alone, learned) is within this testbed's noise of about 5.
* **Cost.**
  * The full 21-feature forest made a 2.3 s run take 5.35 s (twee-e50). Moving the check after unification,
    as the paper does (e51), left it at 5.94 against 2.70 s.
  * I first explained the cost as "every new rule is scored against all candidate partners, roughly 840k
    evaluations". That number was an unmeasured estimate, and the placement was not the paper's. The user
    corrected both ("in the E version we only score the partners that actually can produce an offspring —
    did you read the paper?").
  * Measured: about 25 µs per evaluation of a 100-tree forest; the number of candidates was not the cause.
* REPORT 2av still says the check comes before the overlap is computed, and repeats the 840k figure. Both
  are stale since e51 and must be corrected there.

**Decision and next.** Keep the sum filter. Next: the paper's own features (hashed ENIGMA vectors, Pcat),
2026-11-17-pg-pcat-enigma.md. REPORT 2av.

# Pcat parental models on hashed ENIGMA features, as in the paper

**Question.** The user, 17 Nov 17:30: "try ENIGMA features in Pcat, as in the paper". Then:
* 17:40: hash to a small base, as ENIGMA does, not sparse features;
* 17:54: FNV-1a is fine if fast;
* 17:56: no anonymous features: "in aim, we have only a few symbols and they likely matter";
* "didn't we discuss all this before?" Yes: features are computed on the rule with the goal constants
  expanded, with real symbol names (JOURNAL 4.4).

**What the paper does** (FroCoS 2021, pg/paper/pg.txt, sections 3.3, 4.3, 5.3–5.4):
* the model judges each real inference, after the inference is found and before the child is simplified;
* the features are ENIGMA Anonymous vectors hashed to a fixed length;
* Pcat puts the two parents' vectors side by side;
* labels are P_proof; negatives are sampled to ρ = 8 per positive for Pcat;
* the best Pcat models have 100–200 trees and 1k–8k leaves, at thresholds 0.05–0.2.

Two differences here, by the user's choice: names instead of anonymous features, and twee's FNV-1a hash
instead of E's sdbm.

**Setup.**
* **Builds.**
  * twee-e52: Pcat on the rule model's vocabulary (3,063 named features); superseded.
  * twee-e53: hashed keys, named and anonymous.
  * **twee-e54:** keys from the rule with the goal constants expanded (`expandGoalConsts`), by name; the
    rule model's convention.
  * **twee-e55:** adds the additive form (below).
  * Flags: `--pg-model M --pg-enigma B --pg-threshold P`. The row is the new rule's B buckets, the
    partner's B buckets, both rules' 10 numbers, and the id gap. A key goes to bucket `key mod B`.
  * With the flags off, e54 and e55 match e44 on 24 testbed goals (exp/pg/eqchk54.sh, eqchk55.sh).
* **Data:** the same 1,500 late goals as d2, re-run with e54 `--pg-log` (pg/relog5.sh, 18:00–18:09) into
  pg/d3. That gives 1,482 proved runs and 551,947 scored rules, the same as d2.
  * Feature counts in one run: 794 distinct features, 37 per rule.
  * Collisions: 36.6% at B = 1k, 14.2% at 4k, 9.9% at 8k. Anonymous features had only 112 distinct.
* **Training** (hints/pgdata_enigma.py, pgtrain_enigma.py; pg/pc1.sh, pc2.sh):
  * runs shuffled with seed 1: 60 test, 1,440 train;
  * train with ρ = 8: 32,144 rows, 3,105 positive;
  * test with all negatives: 1,176,204 rows, 276 positive;
  * LightGBM with 100 trees and 255 leaves (the paper went to 1k–8k leaves; not tried);
  * models pce_B (ENIGMA vectors only, as the paper), pcd_B (plus the 20 numbers), B = 1k/4k/8k;
  * additive versions (`--additive`, interaction constraints: each tree on one rule's side): pca_1024
    (ENIGMA only), pcad_1024 (with the numbers).
* **Online:** the 200-goal testbed (pg/tb), 5 abstract s.
  * pg/tm/pgtest6.sh (twee-e54, from 18:17, 5 workers): base, the sum filter at 0.269, pce_1024 at 0.0052,
    pcd_1024 at 0.0007.
  * pg/tm/pgtest7.sh (twee-e55, after the half1 A/B, 6 workers): the sum, pca_1024 at 0.0113, pcad_1024 at
    0.0018 and at 0.005.
  * Thresholds are those that keep the same share of overlaps offline as the sum at 0.269 (38.1%); pcad
    at 0.005 keeps 25%.

**Results.**

Offline, share of proof-parent pairs kept when each model keeps 38.1% of overlaps (the sum filter's pruning):

| model | 1k | 4k | 8k |
|---|---:|---:|---:|
| full, ENIGMA only (pce) | 93.5% | 93.8% | 91.7% |
| full, ENIGMA + numbers (pcd) | 97.5% | 96.7% | 97.1% |
| additive, ENIGMA only (pca) | 87.0% | | |
| additive, ENIGMA + numbers (pcad) | 96.4% | | |
| sum filter | 84.1% | 84.1% | 84.1% |

CPU on one failing goal, 5 abstract s:

| filter | CPU s |
|---|---:|
| base | 4.46 |
| sum | 4.99–5.03 |
| pce_1024 (full) | 33.6–35.5 |
| pca_1024 (additive) | 5.65 |
| pcad_1024 (additive) | 4.87 |

The full forest costs about 30 µs per judged pair. In this run the filter kept 143k pairs; the judged
ones are more, and I did not count them.

Online, pgtest6 (twee-e54, 200 testbed goals, 5 abstract s; ended 19:06):

| filter | proved | gained / lost against base | CPU s |
|---|---:|---:|---:|
| base | 29 | | 904 |
| sum 0.269 | **52** | +23 −0 | 977 |
| pce_1024 (full, ENIGMA only) at 0.0052 | 36 | +8 −1 | 5,960 |
| pcd_1024 (full, ENIGMA + numbers) at 0.0007 | 39 | +11 −1 | 4,767 |

pgtest7 (twee-e55, 6 workers; ended about 19:12; compared with the sum):

| filter | proved | gained / lost against the sum | CPU s |
|---|---:|---:|---:|
| sum 0.269 | **52** | | 889 |
| pca_1024 (additive, ENIGMA only) at 0.0113 | 36 | +1 −17 | 848 |
| pcad_1024 (additive, + numbers) at 0.0018 | 38 | +2 −16 | 809 |
| pcad_1024 at 0.005 (25% of overlaps kept) | 37 | +2 −17 | 795 |

**Reading so far.**
* **The full Pcat models lose online at the same abstract budget** (36 and 39 against the sum's 52), even
  before their 5–6× CPU cost. This repeats the dense models' pattern (2026-11-17-pg-learned-dense.md): better
  offline (93.5–97.5% of proof pairs kept against 84.1%), worse online. So the offline test, which ranks the
  pairs of the old proofs, does not measure what the filter does online. The filter changes which pairs get
  selected, so the old proofs' pairs are not the ones that matter. On-policy data (pairs logged from runs
  with the filter on) is the next thing to try, if any.
* The base does not matter, so 1k buckets are enough for AIM's small signature.
* Offline, the ENIGMA vectors alone already beat the sum (93.5% against 84.1%). But offline gains have not
  carried over before (2026-11-17-pg-learned-dense.md), so only the online test counts.
* A full Pcat forest cannot pay in CPU in twee: a twee pair costs a few µs to make, while E's clause
  generation is far more expensive relative to the model. The additive form costs what the sum costs. It
  gives up the interactions between the two parents; pgtest6 against pgtest7 shows what those are worth in
  proofs.

* The additive forms cost what the sum costs but lose as much as the full ones (36–38). So the interactions
  between the two parents are not what is missing. Every learned parental model, dense or ENIGMA, full or
  additive, has lost to the untrained sum of the two parents' rule-model scores.

**Decision and next.** Keep the sum filter (solve_new.sh's default since 19:00). Not tried: on-policy data (pairs
logged from runs with the filter on), and the paper's larger forests (1k–8k leaves); I would only try those with a
new reason. Was: wait for pgtest6/7. If a model beats the sum online: its half1 A/B against the sum.
If only the full model does: a faster forest evaluator (flat unboxed arrays) or smaller forests. REPORT 2av.

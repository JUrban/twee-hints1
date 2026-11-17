# Retraining the rule model on hard proofs, a GNN, the oracle test, and Prover9 as a side worker

*Reconstructed on 17 Nov from REPORT 2ad (15 Nov 07:30–09:30). Abstract time.*

**Question.** The user, 15 Nov: is ENIGMA retrained? The later long proofs should be worth more for training
than the many easy ones. Would a GNN (Chvalovský, Korovin, Piepenbrock, Urban, LPAR 2023) do better? Later
(about 09:05): the signature is small, so the GNN should know symbols; mark the conjecture's terms; expand the
goal constants; collect data dynamically; train more on hard proofs.

**Setup.**
* **Offline test:** the 400 newest round-5 given logs (sets/ultest, given/ultest), hard proofs no model saw.
  `rulemodel.py --load M --test-only`.
* **Models:**
  * rm4t (production);
  * rm7t (base data + UL's given logs of rounds 1–3);
  * rm8h (abs/rm8h.sh: base data + the 2,875 other round 4–5 logs, negmax 150; 26 GB, 22 min);
  * oracle rmO, trained on the 400 goals' own logs.
* **GNN** (gnn.py, CPU torch):
  * graph: equation, term, variable and symbol nodes; d = 32, 8 layers;
  * dynamic samples: a problem cut at a random point, the last 512 rules as context, the next 128 to score;
  * version 1 types symbols by arity only;
  * version 2 has a learned embedding per symbol name, skolem nodes and goal-term types, goal-match edges,
    the query's index, and weighted sampling towards long proofs and late rules.
* **Online, paired** (abs/mab.sh): snapshot loops/ULsT = UL minus the 400 test goals, fresh 20 s, production
  L0 settings, no `--online`; abs/mabcmp.py compares.
* **Stalled goals** (sets/st79u, 73 goals, ULsM): pool and model variants. INVALID: see below.
* **Prover9** (p9twee.py): a LADR problem with the axioms, 6 proven siblings either side, the conjecture, and
  the whole twee pool as `formulas(hints)`. 60 s on the 72 stalled goals (loops/P9T). Then live from 08:56
  (abs/p9live.sh: 3 workers, stalled goals within 80 lines, proofs into UL).

**Results.**

| model, offline on the 400 | AUC |
|---|---:|
| rm4t | 0.846 |
| rm7t | **0.897** (better on 341 of 400) |
| rm8h | 0.894 |
| GNN v1, step 2,000 / 4,000 | 0.809 / 0.802 |
| GNN v2, step 2,000 / 4,000 / 6,000 / 8,000 | 0.864 / 0.879 / 0.876 / **0.887** |
| oracle rmO | 0.956–0.958 |

At threshold 0.1: rm4t keeps 93.2% of proof rules and defers 35.1% of the others; rm7t 97.7% and 24.5%; rm8h
98.8% and 15.4%.

| online, proved of 400 (fresh 20 s) | proved | only this arm | work on shared proofs |
|---|---:|---:|---:|
| rm4t, 0.1 (production) | 271 | 8 | 1 |
| rm7t, 0.1 | 273 | 10 | 0.98 |
| rm7t, 0.2 | 269 | 9 | 1.00 |
| rm4t, 0.2 | 261 | 4 | 1.04 |
| oracle rmO, 0.1 | 273 | 9 | 1.03 |

Prover9: aK2_eq_aK3_r__goal_241, which every twee variant failed, proved in 44 s (448 steps, 277 hint
matchers). On all 72 stalled goals at 60 s only that one (about 0.8 proofs per CPU-hour). Live: the first proof
after 3 minutes (nslm_to_aa1__goal_688, pool of 15,182 hints). One crash inside Prover9-new ("stack smashing
detected", im2_24_to_25__goal_382).

**Reading.**
* **Even a near-oracle model gains nothing through the defer-once filter** (273 against 271). Rule-model
  quality cannot pay off through this mechanism, ENIGMA or GNN: the searches are driven by pools and lemmas.
  The GNN's twee integration was therefore not built. Parental guidance (17 Nov) is a different hook; the
  queue's order is another (tested in REPORT 2ao: too slow).
* What helps offline is training on proofs of the same originals (rm7t). The long proofs add nothing over that
  (rm8h).
* The user's GNN changes add 0.07–0.08 AUC (v2 at 0.887, level with rm7t).
* The work ratio on shared proofs is a BliStr-style proxy (user's remark); proved counts stay the main measure.
* **The stalled-goal probes were invalid** (round-0 context only, 2026-11-15-learned-scheduler.md).
* Twee with the Prover9 proof as hints but without the sibling lemmas still failed goal_241: the proof leans
  on the lemmas. Veroff's own AIM settings (from the AIM_REDONE .in files) failed both goals Prover9 had
  proved; they depend on hint lists from earlier attempts at the same goal.

**Decision and next.** Production keeps rm4t. The Prover9 side worker runs live beside UL24 (17 workers).
REPORT 2ad.

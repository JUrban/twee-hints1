# The rule model ordering the queue; hints from the kNN lemmas' proofs

*Reconstructed on 17 Nov from REPORT 2ao–2ap (16 Nov 11:20–11:55). Abstract time.*

**Questions.**
* The defer-once filter could not use a better model (2ad). Would a stronger hook, ordering the queue by the
  model, do better?
* Do the proof steps of a run's kNN lemmas help as hints? Those are proofs of goals of the same or weaker axioms,
  mostly of other originals.

**Setup.**
* **Queue order:** twee-e42 `--cp-model-factor F` multiplies each new pair's score by F ** q, where q is rm4t's
  probability, with parent features as in the deferral. F = 1 is off and identical to e41. abs/cpm_test.sh on
  sets/kn30thm (the 6 goals KN30 proved), same context.
* **Lemma-proof hints:** `loop.py --hint-lemma-proofs F` (`--hint-lemma-proof-max 300`). After the own pool it
  adds the proof steps of each of the run's 30 kNN lemmas, with factor F: 200–600 extra hints per goal after
  duplicates. abs/hlp_test.sh on unsol150 from ULsZ, fresh 20 s, paired with KN30.

**Results.**

| queue order | proved of 6 | wall s, the 4 proved by both |
|---|---:|---:|
| F = 1 | 6 | 25.6 |
| F = 0.1 | 4 (2 hit the 200 s CPU limit) | 264.9 |

Work in abstract time is mixed: nil3_32 343 took 2,597 considered pairs against 4,623; a_instances 361 took 8,012
against 6,879; aK2_eq_aK3_o 439 was unproved within 40,000.

| lemma-proof hints | proved of 150 | against KN30 | wall s |
|---|---:|---|---:|
| KN30 (control) | 6 | – | 4,919 |
| F = 0.1 (KH01) | 5 | +1 −2 | 5,323 |
| F = 0.01 (KH001) | 5 | +1 −2 | 5,240 |

**Reading.**
* Scoring every new pair costs about 10× the wall time: twee makes millions of pairs, and each costs three
  featurisations and 200 trees. Deferring non-proof pairs 125× is close to boosting proof pairs, and the oracle
  with repeated deferral tied (2af). So there is no sign the order is worth the cost.
* The lemma-proof test is too small to say anything: the control proves 6 of 150. "No gain" here means "no
  sign of a gain", not a measured null.
* **This is a one-level version of the user's 17 Nov expansion idea.** It adds the direct proof steps of the kNN
  lemmas only, not of the lemmas they used in turn, and not of sibling lemmas. And it was tested where twee
  already had those lemmas as axioms, which makes their derivation steps least useful. The expansion experiment
  instead re-proves from the axioms alone (2026-11-17-expanded-proofs.md).

**Decision and next.** `--cp-model-factor` and `--hint-lemma-proofs` stay in, off by default. REPORT 2ao, 2ap.

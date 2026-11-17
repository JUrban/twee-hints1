# ENIGMA-style looping, a Deepire-style model, and retraining online

*Reconstructed on 17 Nov from REPORT 2u (14 Nov). Abstract time.*

**Question.** The user, 14 Nov: would ENIGMA-style looping (retrain on the loop's own proofs, rerun) or a
Deepire-style model (rule embeddings from the derivation) improve the guidance?

**Setup.**
* **Offline test:** the 298 proofs of nil3_31, aK2_eq_aK3_a and R1dist_to_aa1 goals that the full loop found
  in rounds 1–4. These are later goals of originals whose earlier goals are solved. Training gets every other
  given log, including other proofs of the same originals, as an ENIGMA loop would. Metric: the mean
  per-problem AUC on the proofs' rules.
* **Models:**
  * rm4t (base data: train_only + tr30_g1);
  * rm7t: LightGBM retrained with the loop's proofs (negmax 150; 34 GB and 24 min to train);
  * deepire.py: axiom equations as learned leaves, a rule's embedding from its two parents (d = 32,
    4 epochs);
  * hybrid (`deepire.py --feats --goal`): the embedding plus hashed ENIGMA bags of rule and goal, 2,500
    problems, 6 epochs.
* **Online loop** (abs/el.sh, `loop.py --rerun-solved`): sets/e3, all 1,934 goals of the 3 originals, at
  5 abstract s, without lemmas. Arms:
  * EL: the model retrained each round on base data + the loop's shortest proof per problem, every goal
    rerun;
  * HL: hints from the loop's proofs, no model;
  * EHL: both, every goal rerun;
  * FHL: hints + EHL's round-0 model kept fixed, only unsolved goals rerun (the production setting).

**Results.**

| model | AUC |
|---|---:|
| rm4t | 0.850 |
| **rm7t** | **0.882** |
| Deepire-style, derivation only | 0.765 |
| rank fusion rm4t + 0.5 × Deepire | 0.861 |
| hybrid neural (still rising) | 0.814, against rm7t's 0.885 on its test |

| loop on e3 (1,934 goals) | round 0 | +1 | +2 | +3 | CPU, rounds 0–2 |
|---|---:|---:|---:|---:|---:|
| EL | 920 | 941 | 943 | 947 | 6.1 h |
| HL | 905 | 944 | 951 | 953 | 7.9 h |
| EHL | 920 | 963 | 971 | | 6.5 h |
| FHL | 920 | 970 | **987** | | 6.2 h |

* After round 2: 19 goals only FHL proves, 3 only EHL.
* Only 6,746 training logs have parent columns (older logs predate them).

**Reading.**
* Retraining on the loop's own proofs helps offline (+0.03 AUC) on later goals of the same originals.
* Deepire-style embeddings are weaker than ENIGMA term features and only slightly complementary (+0.011 by
  fusion). The hybrid did not beat LightGBM at this data size.
* Online, the ENIGMA loop alone gains little after its first retraining (+21, then +2, +4). The hint loop
  gains more (+39, +7, +2). Together they are about as good as both separately.
* **"Retraining loses" has a confound.** FHL differs from EHL in two things: a fixed model, and rerunning
  only unsolved goals. EHL's reruns of solved goals replace proofs and so change the hint pool and the
  training set. So the 16-goal gap is not cleanly due to retraining. It agrees with rm6t (no gain from more
  loop proofs, 2026-11-14-ablation-lemma-count.md), which had no such confound, though rm6t held these
  originals out.
* 3 originals, at 5 s, without lemmas: far from production's setting (6 lemmas, cascade to 320 s).

**Decision and next.** Keep the fixed rm4t in the full loop. The model question came back on 15 Nov with
hard proofs (REPORT 2ad) and on 17 Nov with parental guidance. REPORT 2u.

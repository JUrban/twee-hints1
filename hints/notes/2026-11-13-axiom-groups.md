# Lemmas and hints across originals with the same or weaker axioms

*Reconstructed on 17 Nov from REPORT 2l and the session's commands (13 Nov 09:40–11:30). Abstract time from
here on, so runs are deterministic.*

**Question.** Lemma import used only siblings of the same original, because their axioms are equal. Many
originals share axioms, and many have axioms that are a subset of another's. Can proven goals of the same
or weaker theories serve as lemmas, chosen by similarity to the goal?

**Facts** (all 51,784 public problems, from the problem files):
* The 129 originals use 68 distinct axiom sets, constant within an original.
* The largest groups of identical axioms have 15 originals (7,116 and 7,200 goals), 13 (5,426) and 6
  (3,557).
* 66 of the 68 sets have strict subsets among the others (127 pairs). A theorem of a weaker theory holds
  in the stronger one. mbol_KK_a, for example, has 279 goals with its own axioms but 12,873 goals of weaker
  theories.
* 5,842 groups of identical axioms and goal across originals cover 16,048 problems; 41,578 problems are
  distinct. The loop already solves duplicates together: only 24 unsolved problems had a solved duplicate.
* Only 15% of the kNN hint neighbours (from train_pool) of the ho3u targets have the target's axioms
  (median 4 of 30).

**Setup.**
* **Tools.**
  * `lemmas.py --knn K [--subsets] --pool F` adds the K proven goals most similar to the target's goal
    (idf-weighted Jaccard on term shapes). They come from problems with the same axioms, or with subset
    axioms under `--subsets`, from any original.
  * `loop.py --lemma-knn K` does the same inside the loop; `hintsel.py knnfiles --subsets` restricts hint
    neighbours the same way.
* **ho3u:** the 345 hard goals of the 3 dev originals (as before), 16,000 critical pairs each (8 abstract s).
  Group lemmas only (no `--subsets`). The kNN pool is everything plain twee solves in 4 s on the full
  benchmark, plus the 473 solved ho3 siblings.
* **r1sim**, a simulated loop round (sets/r1sim, 13 Nov 10:05):
  * 1,000 problems drawn with seed 11 from those plain twee does not solve in 4 s (runs/ALL_plain_t4), from
    116 originals;
  * lemma pool: the 31,060 plain 4 s proofs (tmp/all_plain4_solved);
  * 8,000 critical pairs each (4 abstract s);
  * problem dirs probs/r1sim_lem3, _lem3k3s, _k6s, _lem3k10s.
* rm4t is rm4's data with the theory block (axiom features) added, from 2f's work.

**Results.**

ho3u (345):

| setting | solved |
|---|---:|
| plain | 70 |
| rm4 | 81 |
| rm4t (theory block) | 87 |
| rm4 + 3 nearest siblings (old lemma import) | 77 |
| rm4 + 6 nearest siblings | 78 |
| rm4t + 3 nearest siblings | 83 |
| rm4 + 3 nearest + 3 group-kNN lemmas | 83 |
| rm4 + 6 group-kNN lemmas | 85 |
| rm4 + 3 nearest + 10 group-kNN lemmas | **91** |

r1sim (1,000):

| setting | solved |
|---|---:|
| rm4 | 92 |
| rm4t | 94 |
| rm4 + 3 nearest siblings | 126 |
| rm4 + 6 kNN lemmas, subset theories | 150 |
| rm4 + 3 nearest + 3 kNN, subset theories | 166 |
| rm4 + 3 nearest + 10 kNN, subset theories | 176 |
| the same + kNN hints, pool of all solved | **194** |
| the same + kNN hints, pool of own and weaker theories | 191 |
| rm4t + 3 nearest + 10 kNN | 180 |

Noise floor: rm4 with `--abstract-time` 1990 and 2010 instead of 2000 (budget ±0.5%, task timing shifted)
solves 93 and 95. At most 3 problems flip. So differences of 10 or more on r1sim are real.

**Reading.**
* **The old lemma import did not help on ho3u in abstract time** (77 against rm4's 81: −7 +3). Its earlier
  gain there (2026-11-13-lemma-import.md: 63 → 68) was within the load noise. On r1sim it does help
  (92 → 126): on a broad set many targets have proven neighbours.
* Lemmas chosen by goal similarity from the same and weaker theories nearly double rm4 on r1sim (+91%). They
  add 40% over the old import.
* **Soundness rests on the subset check.** A lemma from a weaker theory is a theorem of the target's theory.
  The check reads each problem's axioms. Verified on recorded proofs on 17 Nov: 0 of 88,637 used lemmas
  from a non-weaker theory (2026-11-17-lemma-circularity.md).
* kNN hints add +18 on top of lemmas, a real difference on r1sim.
* r1sim's lemma pool is everything plain twee solves, so it simulates round 1 of a loop. In a real loop the
  pool grows during the round.

**Decision and next.** `--lemma-knn 10 --subsets` with 3 nearest siblings, plus kNN hints, in the benchmark
loop. Later tuned: 6 siblings on both sides, 30 kNN lemmas (REPORT 2r, 2am). REPORT 2l.

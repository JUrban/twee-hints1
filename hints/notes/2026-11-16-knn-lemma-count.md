# How many kNN lemmas, and which; where production's proofs come from; what a head is worth

*Reconstructed on 17 Nov from REPORT 2am–2an (16 Nov 06:50–17:20). Abstract time.*

**Question.** Production's kept outputs show which kNN lemmas each proof used. Use barely falls with rank, so are
10 too few? Can use counts or MaSh-style proof dependencies choose them better? Where do production's proofs
come from by level, and is a tail head worth more than its own proof?

**Setup.**
* **Use by rank:** USEDAXIOMS of 2,755 proved runs (names `lemma_knn_<rank>_<goal>`).
* **Paired tests** (abs/knn_test.sh): sets/unsol150 = 150 random unsolved goals of snapshot ULsZ, fresh 20
  abstract s, 2 workers per arm. Arms:
  * 10 (production), 20, 30, 60, 100 kNN lemmas;
  * use counts `--lemma-pop 0.3` (KP03): similarity × (1 + B log(1 + uses));
  * MaSh-style dependencies `--lemma-deps 1` (KD10): a proven goal depends on another when the other's
    equation is a step of its proof (lemmas.proof_deps, 20 s over 44k proofs).
* **Replication:** sets/unsol300b, 300 other unsolved goals, RN30 against RN60 (from 09:20).
* **Offline:** 288 round 4–5 proofs, target's own proof left out, recall at 30 of the step lemmas from other
  originals.
* **Levels:** production's round 5 (32,768 runs) and its last 450 runs at 17:15.
* **Heads:** sets/heads_stuck, the 111 stuck heads of 03:10, goals per original-hour before and after a head's
  proof.

**Results.**
* Use: 2,625 of 2,755 proofs use a kNN lemma, 2,016 a sibling lemma. Rank 0 is used in 1,686 proofs, rank 1 in
  1,320, rank 5 in 1,127, rank 9 in 1,053. 12,205 uses fall on 3,369 distinct goals; a proof uses 4.4 of its 10.

| kNN lemmas (unsol150) | proved | wall s |
|---|---:|---:|
| 10 | 3 | 4,981 |
| 20 | 3 (the same) | 4,953 |
| **30** | **6** (+3 −0) | 4,919 |
| 60 | 9 (+4 −1 against 30) | 5,466 |
| 100 | 5 (+1 −2 against 30) | 5,685 |

* The 3 extra proofs with 30 use lemmas of rank 11–27.
* Replication (unsol300b): 30 lemmas 10 of 300, 60 lemmas 8 (+1 −3). Together, 30 and 60 are even at 19 and 17
  of 450.
* Selection at 30: plain 6, use counts 7 (+3 −2), dependencies 5 (+1 −2). Offline recall 0.183 (plain) against
  0.189 (W = 1).
* Production with 30 lemmas (abs/ul33.sh, from 07:20): 152 new in 3 hours, 4.1 per worker-hour. 88 of them came
  from 4,325 fresh retries.

| round 5 by level | runs | proved | wall h | proofs per wall h |
|---|---:|---:|---:|---:|
| 5 s | 25,205 | 2,191 | 133.3 | 16.4 |
| 80 s | 6,962 | 1,064 | 282.4 | 3.8 |
| 320 s | 603 | 119 | 116.0 | 1.0 |

* At 17:15 the 320 s level made 0.3 proofs per CPU-hour, against 3 at 80 s and 4 at 5 s.
* Heads: after a head's proof its original made 0.53 goals an hour, against 0.43 before and 0.24 for originals
  whose head is still unproved.

**Reading.**
* **Small numbers.** 150–300 goals at 20 s resolve only differences of several proofs. The first 30-against-60
  result (+4 −1) did not replicate. Production changes only on effects that large.
* The 10 → 30 change is backed by 3 −0 on 150 goals and by the extra proofs using ranks 11–27. That is weak but
  consistent; 30 stayed. Production's higher rate right after the change is partly the restart (fresh runs in
  new contexts first).
* Use counts and dependencies are within noise. The offline measure favours plain similarity, because the test
  proofs were found with it.
* A proved head raises its original's later rate by about 0.1 goals an hour. Most of the gap to unproved heads is
  selection: active originals get their heads proved.
* **Proof steps as lemma axioms** (the open decision in 2al) is now worth little: only 39 unsolved goals are
  instances of a step of a unit-goal proof from the same or weaker axioms, and 34 failed with the steps as hints
  and source lemmas.

**Decision and next.** `--lemma-knn 30`. The live head climber stopped at 11:05 (0.47 per CPU-hour), production to
16 workers (abs/ul34.sh), then 8 at 17:20 (abs/ul36.sh) with side batches. REPORT 2am, 2an.

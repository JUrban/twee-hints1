# The ENIGMA loop (rm4, rm5, rm4b) and generalisation matching

*Reconstructed on 17 Nov from REPORT 2f and the session's commands. CPU-time limits.*

**Question.** Does training the rule model on proofs found under guidance make it better, as in ENIGMA's
looping? Separately: does matching critical pairs that generalise a hint help (Prover9-new's generalised
hint hash)?

**Setup.**
* **rm4:** rm3's data plus the given-rule logs of 757 proofs (given/tr30_g1). These came from guided runs
  (rm3, kNN hints, 4 s) on the 5,355 training problems of tr30 that plain twee leaves unsolved at 2 s.
* **rm5:** rm4's data plus 2,687 training-split problems that the full-benchmark loop solved with rm4 in
  0.3–2 s (2.7M rows, 290k positives).
* **rm4b:** rm4's data, 400 trees of 127 leaves (four times the model).
* **Tests:**
  * 600 random holdout problems still unsolved after H2, at 8 s;
  * the 345 (sets/ho3_unsolved: hard goals of aa1_45_c, mbol_com, nil3_15; 2026-11-12-rule-model.md), at
    8 s, model only, no hints.
* **Generalisation matching** (`--eqhint-generalise`, twee from dd06c83, 12 Nov 23:15): each hint is also
  stored with its one-step generalisations (one proper non-variable subterm of one side replaced by a fresh
  variable). Tested on the 345 with rm2 and kNN hints at 8 s.

**Results.**

| test | result |
|---|---|
| 600 holdout, 8 s | rm3 8, rm4 8 (4 different each) |
| 345, rm3 / rm4 | 60 / **63** (+4 −1) |
| 345, rm4 repeated | 61 (+0 −2 against 63) |
| 345, rm5 | 58 (+2 −7) |
| 345, rm4b | 65 (+9 −7); loads in 0.15 s against 0.07 s |
| 345, generalisation matching | 68 against 69 without |

**Reading.**
* **Noise:** twee's background tasks were time-based then, so the same run differs by ±3 on the 345. Every
  difference here is within or near that.
* **Not unseen originals:** rm3 and rm4 were trained on solved goals of the 345's three originals, though
  not on the 345 themselves. So this compares the models in a loop over one batch.
* **rm5:** more medium proofs made the model worse. A possible reason is capacity or the threshold for the
  larger data; not tested then. The data mix question came back on 15 Nov (REPORT 2ad).
* Generalisation matching is neutral.

**Decision and next.** rm4 from here on; generalisation matching off. REPORT 2f.

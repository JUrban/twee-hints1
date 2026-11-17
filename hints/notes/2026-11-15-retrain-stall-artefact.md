# The stall was partly an artefact; unit forms of conditional lemmas; repeated deferral; folding

*Reconstructed on 17 Nov from REPORT 2ae–2af (15 Nov 09:30–11:20). Abstract time.*

**Questions.**
* With a valid snapshot, do the stalled goals really resist fresh runs?
* Can a stronger filter (repeated deferral) let a better model matter?
* Why does Prover9's side worker prove goals that twee fails, some in one step?

**Setup.**
* **Valid control:** snapshot loops/ULsN, UL at 09:30 with every row imported (round set to 0). sets/st79u (71
  run), fresh 20 s (abs/unit_probe.sh): PU_0 without and PU_1 with unit forms of conditional lemmas.
* **Unit forms** (`lemmas.lemma_form`): a conditional goal `~ s = X | C = D` whose hypothesis binds a variable
  X not in s is equivalent to the unit `C = D` with X := s. That covers 6,235 of AIM60k's 9,052 conditional
  goals. `TWEE_LEMMA_UNITIZE=0` turns it off.
* **Fix for the cascade** (`--retry-knn`, 3f05146): the kNN index is rebuilt every 30 min or 300 proofs, each
  fresh run's kNN lemma set is recorded (DIR/knn_at.tsv), and a changed set makes a goal eligible.
* **Repeated deferral** (twee-e38 `--rule-defer-max K`, 239245f), abs/defer_test.sh on sets/ultest (400):
  rm4t defer-once against the oracle rmO with K = 3, penalty 5.
* **Folding:** unfold.py substitutes the definitions (a, k, l, r, t) away; `loop.py --unfold`; `--lemma-fold 8`
  adds folded instances of lemmas. Sets:
  * p9l9, the 9 goals Prover9 proved;
  * p9no40, the first 10 of 231 that Prover9 failed;
  * unf80, random frontier goals;
  * lf116 = p9no40 + unf80.

  Snapshots of UL at 10:24 and 10:44; the folded control is loops/LF_ctl.

**Results.**
* Valid control on st79u: fresh 20 s proves 7 of 71 without the unit forms and 10 with them (+3 −0), 18–25
  proofs per CPU-hour against production's 2.
  * All six proofs of the first 35 use kNN lemmas proven after the goal's last run.
  * nil3_24__goal_356 failed twice on 14 Nov (the last a 141 s resume) and now takes 1.7 s.
* UL26 with `--retry-knn` from 09:44: its first 100 fresh runs made 41 new proofs in 132 s.
* Unit forms change the sibling lemmas of 2,234 of the 8,270 unsolved goals. Prover9's proof of
  aK2_eq_aK3_d__goal_405 (failed 9 times by twee) used such a sibling.
* Repeated deferral: the oracle with K = 3 270, baseline 269 of 400 (+8 −7), 11% more work on shared proofs.
  With K = 1, e38 equals e22 on 20 of 20 runs.
* Of Prover9's 9 side-worker proofs, 4 are short (1, 3, 10 and 130 steps); folded twee at 20 s proves 2 of the 9.
  aK2_eq_aK3_r__goal_212 is a 1-step Prover9 proof from sibling 209, which twee had too; twee fails it with
  12,880 rules. Unfolded it takes 1.2 s.

| goals (fresh 20 s, production context) | folded | + lemma instances | all unfolded | only t unfolded |
|---|---:|---:|---:|---:|
| p9l9 (9) | 2 | 3 | **7** | 3 |
| p9no40, first 10 | 0 | 0 | **3** | |
| unf80, first 28 | 1 | 1 | 1 (0 of 25 without rm4t) | |
| lf116, 111 run | 4 | 4 | | |

Unfolded runs take about 4.5× the real time for the same abstract time.

**Reading.**
* **The stall was the cascade's, not the goals'.** The retry gate ignored changes in kNN lemmas, and the kNN
  index was built only at start. A 13× rate gain came from fixing the bookkeeping.
* The earlier "stalled goals resist everything" findings came from an invalid snapshot. The cascade's bookkeeping
  bug and the snapshot bug pointed the same wrong way.
* **A better model does not pay through a stronger filter either.**
* **Twee folds definitions, Prover9 unfolds them.** Twee's KBO orients `ld(X,m(Y,X)) -> t(Y,X)`, and no
  precedence or weight can flip that, since B occurs twice in the defining term. Unfolding is no better in
  general (random frontier: 1 against 1) but works on the goals Prover9's worker picks.
* The folded column is the control: without it "stalled" overstates the gains, because the 4 folded proofs on
  lf116 come from context that arrived since production's last try.
* Small sets (9, 10, 28): the folded/unfolded difference rests on 5–8 goals.

**Decision and next.** `--retry-knn` and unit forms in production. The Prover9 worker stopped at 10:24 (9 proofs
in 283 tries). An unfolded-twee side worker from 11:18 (uflive.py, abs/uflive.sh, 4 workers): 8 of 48 in its
first 27 minutes. REPORT 2ae, 2af.

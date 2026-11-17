# Tail heads, the cutoff between fresh runs and resumes, and a 5 s first level

*Reconstructed on 17 Nov from REPORT 2ag (15 Nov 11:57–19:05). Abstract time.*

**Questions.** Can anything prove the tail heads (the first unsolved goal after an original's last proof), behind
which most unsolved goals sit? When is a fresh run worth more than a resume? Should the first level be 5 s
rather than 10 s?

**Setup.**
* **Heads:** 92 in all, line gaps 13–68 (median 34).
  * sets/heads30: 30 random heads, snapshot ULsV (11:57), fresh 20 s, production context. Arms: folded control;
    `--pool tier:20:500:0.1`; unfolded; 20 sibling lemmas; `--hint-after 10` (the next 10 unsolved unit goals'
    statements as hints).
  * Long budgets (abs/heads_long.sh, 18:15–19:05): sets/heads_u (the 30 still unsolved), fresh 160 abstract s,
    snapshot ULsW: unfolded HLU against folded HLF.
* **Settings** (abs/var_test.sh, ULsV, 36 goals Prover9's worker failed): `--no-flatten-goal`,
  `--flatten-goal-lightly`, `--flip-ordering`, `--kbo-weight0`.
* **Fresh against resume:** the last 1,500 UL27 runs.
* **5 s against 10 s** (abs/lvl_ab.sh, from 12:48): reflink copies UA and UB of UL at 16,416 round-5 rows,
  6 workers each, levels 10,80,320 against 5,80,320.
* **Sibling lemmas, unfolded** (abs/ufl_lem.sh, sets/p9no_v, ULsV): 6 against 12.
* **Head value:** a replay of production's round 5 (21,784 runs, 2,751 new proofs).

**Results.**
* Heads at 20 s: 0 of 30 in every arm, and 0 for every twee setting on the 36.
* Heads at 160 s: unfolded 0 of 8 (every run hit the 800 s CPU cap before 160 abstract s); folded 1 of the same
  8, 3 at 12 of 30.

| last 1,500 UL27 runs | proved | runs | rate | CPU-hours | proofs per CPU-hour |
|---|---:|---:|---:|---:|---:|
| fresh (10 s) | 54 | 1,039 | 5.2% | 5 | 10.8 |
| resume to 80 s | 47 | 461 | 10.2% | 20 | 2.4 |

* A resume costs 9 fresh runs (156 against 17 wall s), not the 3 the 0.06 cutoff assumed. The scheduler
  overpredicts 2.3×. So a fresh run predicted at 0.025 or more pays better.
* Of the last 194 fresh proofs, 84% came within 10,000 critical pairs (5 abstract s), 69% within 5,000.
* 5 s against 10 s, after 62 minutes: 33 against 20 proofs (15 shared).

  | arm | fresh proved / runs | resumes proved / runs |
  |---|---:|---:|
  | UA, 10 s, cutoff 0.025 | 13 / 476 | 7 / 91 |
  | UB, 5 s, cutoff 0.011 from 13:08 | 19 / 1,254 | 14 / 77 |

* Unfolded with 6 lemmas 3 of 36, with 12 lemmas 4 of 36.

| proofs of the same original after a head proof | within 500 runs | 2,000 | 8,000 |
|---|---:|---:|---:|
| mean | 3.2 | 3.6 | 4.6 |
| median | 1 | 1 | 2 |
| none | 30 | 28 | 22 |

Other proofs are followed by 5.3 within 2,000 runs.

**Reading.**
* The heads resist every variant at 20 s. This retests the tier pool and the settings portfolio in a valid
  snapshot, and confirms the earlier negatives.
* Unfolding does not scale to long budgets: runs become CPU-bound.
* **A head proof does not unlock a chain.** The goals behind a head are each hard. Counting what follows, a head
  is worth about 2 proofs per CPU-hour, below production's 3.5 then.
* UB's first cutoff starved fresh runs after its scheduler retrained on 5 s outcomes. The break-even scales
  with a fresh run's cost (0.44 × 0.025), hence 0.011.
* The 5 s A/B ran 62 minutes on 6 workers each; 33 against 20 is clear, but on one copy of UL at one time.

**Decision and next.**
* UL28 (abs/ul28.sh) with `--sched-pmin 0.025`.
* UL29 (abs/ul29.sh, 13:55) with `--cascade 5,80,320 --sched-pmin 0.011 --sched-pmin-auto 400`. `--sched-pmin-auto
  W` sets the cutoff online.
* The unfolded side worker keeps 6 lemmas. REPORT 2ag.

# A discounted yield estimate for the deeper levels from zero (exp45, 20 Nov)

Written 20 Nov 2026, 19:38 UTC, before launch. Launched with exp44 by abs/exp4445.sh
([hints/exp/exp4445.sh](../exp/exp4445.sh)), automatically when Z6 ends (about 23:33).

## Why

* **Z6 after 4 hours (notes/2026-11-20-z6.md):** 42,920 at 4 hours, then 151 in the next half hour. Its deeper
  class ran only the unfolded 5 s variant and L0 retries:

  | Z6, whole run to 4 h | proofs/runs | CPU h |
  |---|---|---:|
  | L1 (40 s chain level, goals right after a proven one) | 9/16, all in the first hour | 0.2 |
  | Vunf@0 (unfolded, 5 s) | 256/3,550; 2 of its last 291 | 9.2 |
  | Vk100@0, Vk200@0, Vk400@0, Vkd@0 | 67/602 | 0.8 |

* **The cause:** `--ratio-order` ranks a goal's next attempts by each label's cumulative estimate,
  (proofs + 2 × prior) / (CPU h + 2). Vunf@0 stood at 23 per CPU hour, from runs made while nearly everything
  proved; L1 at 5.7 (9 proofs in its 0.2 explore hour, prior 1.73). So after its explore hour L1 never ran again.
  The half tests show the same: L1 ran 33 times in P2E and P2F, all in the first hour, 18 proofs.
* **Z6's heads at 19:56** (unsolved goals right after a proven sibling, the only goals `--frontier 1` lets deepen):
  1,423, and production proved 1,245 of them. Production's first proof was at L0 for 504 (with production's
  larger lemma context), **at L1 for 358**, at L2 for 58, by variants for 65 and by side loops for 260. Z6 ran L1
  on 3 of its heads: its head runs were 2,841 at L0, 934 of Vunf@0 and 189 of the lemma-count variants. A head's
  proof also gives the goal after it a new context.
* **Offline (hints/exp/estcmp.py, its split test).** It scores each window's split of proofs among the labels that
  ran in it, predicted from the rows before (multinomial log-likelihood; windows of 1,000 rows, flat priors):

  | rows | cumulative | discounted over 1,000 | over 3,000 | over 10,000 | time-normalised | flat |
  |---|---:|---:|---:|---:|---:|---:|
  | Z6 | −791 | **−557** | −580 | −636 | −670 | −616 |
  | Z4 | −622 | **−395** | −438 | −532 | −559 | −1,955 |
  | production, rows 47,531 on (production's priors) | **−2,040** | – | −2,338 | −2,235 | −2,293 | −2,560 |

  From zero the cumulative estimate ranks worse than no information (Z6). On production's rows it stays best,
  as on 19 Nov (notes/2026-11-18-portfolio-review.md): there the rates swing with a common factor.

## Change

* loop.py `--yield-discount N`: each label's proofs and CPU are discounted by exp(−1/N) per counted results row (all
  labels' rows), estcmp's 'disc'. The prior term is not discounted, so a label that stops running drifts back to
  its prior. The explore thresholds still use the raw CPU.
* With `--reexplore W:R` (production has 150:0.25) a label of `--explore-labels` (L1, Vk100@0, Vk200@0, Vk400@0,
  Vkd@0 in solve_new.sh) that got under R CPU h in the last W CPU h is ranked with the best label until it has R.
  Here 12:0.25: on 6 workers the window is 2 hours, so at most 5 × 0.25 / 12 ≈ 10% of the CPU.
* Every 500 runs the cascade's stderr line lists the six best estimates (`est ...`).
* Smoke tests (19:37-19:55, 487 goals of aa3_45 and nsmr_to_aa1, 2 workers): loops/YDT (`--yield-discount 2000`,
  6 min) and loops/YDT2 (with `--reexplore 1:0.02`, 12 min, past 500 runs): no errors; the estimate line read
  `est L0 156.8 Vunf@0 4.1 L1 1.7 Vk100@0 1.0 ...`. L1 did not run there: no label had its 0.2 explore hours yet, so
  nothing was re-explored.

## Set and setting

* **P2J:** sets/half2 from zero, abs/or_test2.sh, 6 workers, 5 hours,
  `LOOPARGS=--yield-discount 2000 --reexplore 12:0.25`.
* **Control P2K** (shared with exp44): the same without LOOPARGS.
* Two changes in one arm: the discount alone would let L1 drift back to its prior 1.73, which is still above the
  late Vunf@0 (about 3), but the re-exploration measures it now. If P2J wins, a second arm splits them.

## Measures

* `abs/setcurve.py sets/half2 P2K P2H P2J --at 30,60,120,180,240,300`; exp/windows.py P2J against P2K (which labels
  ran when, proofs per CPU hour).
* **Decision:** P2J ≥ P2K + 185 at 5 hours makes the pair solve_new.sh's default. Equal is a negative for from-zero
  runs (production keeps the cumulative estimate either way).

## Interim at 1 hour (21 Nov 00:36)

P2J 19,161 against the control P2K 19,009 (+152; P2E and P2F, the same system as P2K, 19,198 and 19,307). Table in
[notes/2026-11-20-retry-class.md](2026-11-20-retry-class.md). At 1 hour nearly every run is a first run at L0
in all three arms, so the label estimates have not yet decided much: P2J's line reads `est L0 381.9 Vk100@0 6.8
... Vunf@0 6.8` (the discount keeps L0's estimate near its recent rate), P2K's `est L0 2601.2 Vunf@0 17.7 ...`.

## Interim at 2 hours (21 Nov 01:36)

P2J 20,124 against P2K 20,004 (+120, noise; P2H +607, table in the retry-class note). The estimate lines: P2J
`est L0 91.4 Vk100@0 4.2 ... Vunf@0 4.2`, P2K `est L0 1525.9 Vunf@0 16.2 Vk100@0 7.7 L1 7.4 ...`. The late phase,
where the discount should matter, starts after the first runs end (about 2.5 hours on half2).

## Interim at 3 hours (21 Nov 02:36)

P2J 20,774 against P2K 20,227 (+547; P2H +1,128). Most of it in 150-180 minutes: retries 396 / 902 (P2K 111 / 638
at 150). L1 ran 5 + 7 times in 120-180 minutes (2 + 2 proved); P2K none. Estimates: P2J `est L0 100.1 Vk100@0 7.1
Vk200@0 7.1 Vkd@0 7.1 Vunf@0 7.1 L1 2.4`, P2K `est L0 1100.3 Vunf@0 12.8 Vk100@0 7.7 L1 7.4 ...`.

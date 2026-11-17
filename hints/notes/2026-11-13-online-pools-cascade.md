# Online pools, multi-goal search, the gap to the nearest proof, and the cascade

*Reconstructed on 17 Nov from REPORT 2o–2p and the session's commands (13 Nov 14:40 – 14 Nov 06:00). Abstract
time.*

**Question.** On the unsolved frontier, can proofs found during a round reach the goals still waiting (online
pools)? Which pool is best at 20 s? Can one search serve many goals? And how should runs be scheduled: in
rounds by goal order, or right after new proofs?

**Setup.**
* **sets/u3** (13 Nov 14:41): all 996 goals of R1dist_to_aa1, aK2_eq_aK3_a and nil3_31 left unsolved after
  the full benchmark loop (loops/V2base: ALL_lem round 2 + G1). Why these three originals is not recorded.
* abs/u3.sh, u3c.sh: 20 abstract s, rm4t, 3 sibling lemmas + 10 subset-kNN lemmas, twee-e19, 5 workers per
  variant, `--init loops/V2base`.
* Variants:
  * kNN 30:100 hints, fixed for the round;
  * kNN online (`loop.py --online`: each proof joins the pool and the lemma source at once; goals in
    goal order, only -j runs queued);
  * the whole original's pool, online;
  * tiered (`--pool tier:30:100:0.3`): kNN hints at the full boost, the rest of the pool at 0.3.
* **Multi-goal search** (twee-e21 `--multi-goal`, `loop.py --multi W`): W consecutive unsolved goals as one
  problem, with the union of their lemmas and W times the budget.
* **Lemmas from both sides** (`--lemma-after`): 222 u3 goals the online whole-pool run left unsolved that
  have a proven sibling at most 10 above.
* **Cascade** (`loop.py --cascade 20,80,320`): a goal is retried at the first level as soon as a sibling at
  most `--retry-gap` below it is proved. Otherwise the goal right after a proof is deepened to the next
  level, resuming its saved state. The test: the 724 u3 goals left after the online 20 s run, from its
  proofs (loops/U3poI). Cascade against one online 80 s round with give-up 30, 5 workers, 2 h wall each.
* **Full benchmark, Veroff style** (abs/unleash.sh): every goal the 4 s loop left (18,064 of 51,784), from its
  33,720 proofs. Online whole-original pools, give-up 30, rounds of 5 then 20 abstract s, 14 cores
  (twee-e20, kill at 15× the limit, CPU cap 400 s).

**Results.**

On the first 189 aK2_eq_aK3_a goals (all later goals failed in every variant):

| variant | solved | wall s |
|---|---:|---:|
| kNN hints, fixed pool | 44 | 10,744 |
| kNN hints, online | 55 | 9,422 |
| whole-original pool, online | 60 | 9,866 |
| tiered pool, online | 61 | 10,209 |

* Whole pool, online, all three originals: 272 of the first 695 goals, against 0 for the 4 s loop.
* Give-up: the longest run of failures before a later success was 27 (R1dist_to_aa1). Giving up an original
  after 30 consecutive failures keeps every proof and saves 15–50% of the time; after 20 it loses 14 of 272.
* Frequency-weighted boosts (`--freq-factors 1:0.2,4:0.05`): 60 of 189, the same as uniform (+5 −5), in 19%
  more run time.
* Hint signals at 5 s did not predict which runs need 20 s: 18–20% of runs unsolved at 5 s were solved by
  20 s, whatever their last match or pool size.
* Multi-goal: 21 against 28 for separate runs on the first 33 aK2_eq_aK3_a goals; 4 against 5 on one window
  of 10 nil3_31 goals at 200 s.
* By gap in goal numbers to the nearest sibling proven before the run (full-benchmark round 2, 20 s):

  | gap | runs | solved |
  |---|---:|---:|
  | 1 | 537 | 58% |
  | 2–3 | 176 | 42% |
  | 4–10 | 66 | 26% |
  | more than 10 | 5 | 0 |

* Lemmas from both sides: 67 of 222. On a random 74, 26 against 20 with lemmas from below only (+6 −0).
* Cascade against the 80 s round:

  | wall s | 600 | 1,800 | 3,600 | 5,400 | 7,200 |
  |---|---:|---:|---:|---:|---:|
  | cascade | 27 | 57 | 64 | 77 | 90 |
  | 80 s round | 10 | 18 | 40 | 58 | 69 |

  58 shared proofs; the cascade alone has 32, the round 11. Only 30 of the cascade's 336 runs reached 80 s
  (16 succeeded).
* Full benchmark: round 1 (5 s) +2,337 to 36,057 (82 min); round 2 (20 s) +2,951 to 39,008 (12 h, 152 h of
  run time on failures).

**Reading.**
* Online pools give +25% at the same cost. The whole pool adds about 10% more at 20 s.
* The loop advances along each original's proof, and a hard goal blocks those after it. That is why the
  sibling lemmas, and the lemma-assisted proofs the user asked about on 17 Nov, carry so much of the total.
* Multi-goal loses because, in a joint search, goal k is only joinable and never becomes a rule. A separate
  run for goal k+1 has goal k as an axiom from the start.
* Lemmas from above are proven before the run, so the chain stays well-founded
  (2026-11-17-lemma-circularity.md).
* All on 3 originals (u3), so the size of these gains is specific to them; the full-benchmark rounds are the
  broad check.

**Decision and next.** Online whole-original pools, give-up 30, lemmas from both sides, and the cascade
(round 3 of the full benchmark, abs/ul3.sh: 20, 80, 320, 960 s). REPORT 2o, 2p.

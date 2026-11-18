# The time-matched control for portfolios: exp11's chain at 160 s on the failed walls (exp20)

Prepared 18 Nov 2026, 17:03 UTC; it starts when exp17's stage (PID 2434820) ends. Directory /project/hintwork/exp20;
scripts in hints/exp/exp20_*. Part of the portfolio task (notes/2026-11-18-portfolio-review.md).

## Why

A second method that loses some of the best method's proofs but adds its own can be worth running for a share of
the time (the user, 17:00). The test: give the best method the same extra CPU and compare the new proofs.
* On the 107 walls, every 80 s variant (exp14, exp15, exp16, exp18, and exp17 and exp19 when they end) is a
  second method next to exp11's 80 s chain run.
* So the best method's alternative is exp11's command run for 160 s: twice the budget, about the CPU of two 80 s
  methods.

## Set and setting

* The 92 walls exp11 did not prove at 80 s, with exp11's commands at `--max-time 160 --max-cpu 1600` (twee-e48,
  chain hints, CPU cap 10 times the abstract budget as in exp11).
* A larger limit leaves the first 80 s unchanged: aK2_eq_aK3_1243b 372 is proved at 23,570 pairs with either
  limit (exp20/res_chk.tsv). So exp11's 15 count as proved at 160 s too.
* Compared:
  * **best method, 160 s:** 15 + the new proofs among the 92, at exp11's CPU plus this run's;
  * **portfolio, 80 s + 80 s:** exp11 plus each variant (union), at the two runs' CPU.
* 4 workers.

```
cd /project/hintwork/exp20
python3 mk.py
bash stage.sh 2434820     # then: python3 run.py C160.cmds C160 4
```

## Cost accounting (17:49)

* exp20 runs fresh 160 s runs, but in production the second 80 s would resume the 80 s state.
* So the yield of extending is counted on the **increment**: a goal's CPU at 160 s minus exp11's CPU on the same
  goal at 80 s.
* The full fresh cost is reported too.
* The variants are counted on their full cost: they start fresh.

## Results

**Complete at 20:13, all 92 failed walls** (exp20/res_C160.tsv, `python3 ana.py`).

* **12 new at 160 s.** On the increment over exp11's 80 s runs that is 6.79 CPU h, **1.77 new per CPU hour**. On
  the full fresh cost it is 11.2 CPU h, 1.07.
  * The new walls: aK1_nil3_b 161, aK2_eq_aK3_a 455, aK2_eq_aK3_d 435, aK2_eq_aK3_p 302, aK2_eq_aK3_t 367,
    aK2rev 375, im2_24_to_25 405, mbol_12lemmas 503, mbol_KK_b 161, mbol_lem2 508, mbol_to_nil3 572 and
    nil3_23_32_to_25 485. They were proved at 172,846-315,915 pairs.
* **Against the 80 s variants on the same 92** (each alone, on its full cost, then the overlap with the 160 s 12):

| member | new | per CPU h | also at 160 s |
|---|---:|---:|---:|
| chain to 160 s (increment) | **12** | **1.77** | |
| Prover9 + chain, 60 s | 3 | 1.98 | 0 |
| 60 kNN lemmas | 6 | 1.24 | 1 |
| two-sided chain | 4 | 0.76 | 2 |
| unfolded | 7 | 0.43 | 1 |
| subsumption | 3 | 0.42 | 2 |
| no PG | 2 | 0.43 | 1 |

* **So the time-matched answer has two parts.**
  * Giving the best method another 80 s, resumed, beats any second 80 s method per CPU: 12 new at 1.77 against
    6 at 1.24 for the best variant.
  * The variants are still complementary to it. In the order 160 s, k60, two, unf, sub, nopg, the union is 24
    of 92 at 37 CPU h, against 12 for the 160 s run alone.
* **Conditional yields in that order:**
  * 160 s: 1.77;
  * k60: 1.19;
  * two: 0.23;
  * unf: 0.47;
  * sub: 0 of 68 runs;
  * nopg: 0 of 68 runs.
  * After the longer run, subsumption and no-PG prove nothing the others don't. In this position they are real
    negatives. The two-sided chain is mostly covered.
* Production since 18:53 (ul49, ul50) has the 160 s resume level right after the 80 s chain. The next restart
  orders the variants k60, unf, two and drops sub and nopg (priors set 20:14).
* All 12 are in UL: 5 merged at 19:38, the others were already there or came from other runs.

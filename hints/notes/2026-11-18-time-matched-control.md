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

(pending)

# From scratch on unseen originals: the replays (rp3, ho8), contexts, the scheduler, and leaks

*Reconstructed on 17 Nov from REPORT 2aq (16 Nov 11:55 – 17 Nov 00:50). Abstract time; 4 workers + the transfer,
1 hour unless said.*

**Question.** What would the final system do on a new benchmark part, such as the secret 10,016 problems? Replay
whole holdout originals from scratch, with and without other originals' proofs as context.

**Setup.**
* **rp3:** 3 whole holdout originals, a_of_aa, lra2aa and nil3_23_32_to_26 (sets/rp3, 1,320 goals). **ho8:** the
  other 8 (sets/ho8, 3,400 goals). Together, the 11 unseen originals (4,720).
* **Contexts:**
  * full: loops/RPs, UL at 11:50 minus the 3 originals. Contaminated, since other proofs used these originals'
    goals as kNN lemmas.
  * clean: loops/ALL minus them, 31,605 proofs of the 13 Nov 2 + 2 s loop, from before kNN lemmas.
  * from zero: loops/EMPTY.
  * today's, filtered: loops/ULX (abs/freshctx.py), UL at 21:52 minus the 3 originals and minus 46 proofs whose
    kept output names an rp3 goal. loops/HOX likewise for ho8, minus 1,114 proofs.
* **Runs:**
  * abs/replay.sh, rpx.sh (full); replayc.sh, rpxc.sh (clean); ho8.sh, ho8b.sh, hou_test.sh;
  * level and knob tests lv_test.sh, lv2_test.sh; from zero lvz_test.sh; the scheduler lvs_test.sh (LVS, LV4,
    LVS2, LZ4);
  * curves from proof-file times (abs/totcurve.py) and cascade work (abs/workcurve.py);
  * abs/leakcheck.py.

**Results.**

| rp3 (1,320) | proved |
|---|---:|
| plain twee, 4 s | 731 |
| from zero (LVZ), 60 min | 890 |
| from zero with the scheduler (LZ4), 4 h | 977 |
| clean context (RPc), 60 min | 934 |
| full context (RPs), 60 min | 1,041 |
| today's, filtered (LVU), 60 min | 1,085 |
| production, 3.5 days | 1,111 |

| minutes | 1 | 4 | 10 | 25 | 40 | 60 |
|---|---:|---:|---:|---:|---:|---:|
| clean, transfer every 10 min (LVA) | 634 | 807 | 849 | 896 | 905 | 933 |
| clean, every 2 min (LVD) | 628 | 809 | 847 | 884 | 921 | 942 |
| from zero (LVZ) | 565 | 732 | 806 | 858 | 883 | 890 |
| clean, scheduler (LVS) | 431 | 830 | 868 | 917 | 943 | 972 |
| clean, scheduler + sweep-first (LVS2) | 580 | 799 | 856 | 875 | 903 | 940 |
| today's, filtered (LVU) | 416 | 969 | 1,036 | 1,065 | 1,075 | 1,085 |

* Knobs on rp3, clean, against LVA 933: a 20 s level (LVB) 925; 60 kNN lemmas (LVC) 920; transfer every 2 min
  (LVD) 942.
* The transfer's first scan with the full context proved 545 of 546 candidates in 91 s. A third of these goals are
  instances of proven goals of other originals with the same or weaker axioms.

| ho8 (3,400) | proved |
|---|---:|
| clean, no scheduler, 10 min transfer (HO8) | 2,451 |
| clean, today's defaults (HO8b) | 2,573 |
| today's, filtered (HO8U) | 3,021 (an upper bound: leaks) |
| production, 3.5 days | 3,092 |

| all 11 holdout originals (4,720) | proved | share |
|---|---:|---:|
| plain twee, 4 s | 2,887 | 61.2% |
| loops/ALL, 13 Nov (LVS2 + HO8b) | 3,513 | 74.4% |
| today's, filtered (LVU + HO8U; HO8U leaks) | 4,106 | 87.0% |
| production, 3.5 days | 4,203 | 89.0% |

**Reading.**
* **The loop alone does most of it:** from zero, 890 of 1,320 in an hour, 22% over plain twee. The 13 Nov context
  adds 5–6%, today's (filtered) 22%.
* **Noise without the scheduler is about 1 proof** (LVA 933, RPc 934), so effects of about 20 show. **With the
  scheduler it is about 50.** I first read LVS's +30 as real; LV4 with LVS's exact settings had 919. The mean of
  three scheduler arms (971, 919, 940) is 943, the same as LVD.
* **The scheduler starved originals from zero** (LZ4's first try: all 427 runs on a_of_aa). Fixed by
  `--sweep-first` (d8e36da).
* **Leaks:** the full context (RPs) was contaminated by design. Among the newer proofs with kept outputs, 1.6% used
  an rp3 goal, so LVU's 1,085 stands. For ho8 the rate was 37% (the 8 originals belong to the big aK and aa
  families), and about 9,000 newer proofs could not be checked. So HO8U is an upper bound, and the truth for
  today's-size clean context lies between 2,573 and 3,021.
* The replays level off near 950 with loops/ALL because the goals production has and they lack mostly need
  kNN lemmas from goals proven after 13 Nov (45 of 54). The method was measured under a 3-days-older context.
* HO8b against HO8 (+122) changed the scheduler and the transfer cycle together, so it does not say which helped.
* rm4t is fixed and trained on plain 2 s proofs of the training split, the kind a from-zero sweep makes.

**Decision and next.** solve_new.sh (from this day) with XEVERY=120, 60 lemmas no, a 20 s level no (it came back
on 17 Nov, REPORT 2au), and the scheduler optional. REPORT 2aq.

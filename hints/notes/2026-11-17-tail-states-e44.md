# The tail: which goals get longer runs; original rates; saved states; noise at scale; e43/e44

*Reconstructed on 17 Nov from REPORT 2au (17 Nov 08:40–15:50). Abstract time; counts by proof-file times.*

**Questions.** Z4 ended near 38k while production had 44.8k. Which goals need longer runs, and can we predict
them? What does a failing run's time go to? How noisy are 2-hour half-benchmark comparisons?

**Setup.**
* **`--fail-reset`** (FR60): a goal's failure count restarts when its nearest proven goal below changes. rp3 from
  zero, 4 workers, 1 hour, against FO60.
* **The gap:** production's 6,818 goals that Z4 lacks, by the time production needed.
* **Predictors** of an 80 s success: the failed 5 s run's hint statistics (hints, live, matched, lastmatch,
  maxgap, deferred, rules), and the original's recent proof rate (online, smoothed towards the overall rate with
  weight 5, optionally weighted 0.9 per newer run).
* **`--orig-rate`:** goals of originals whose recent runs proved most go first, within failure counts, in bins of
  0.1.
* **half1** (abs/or_test.sh, 2 h, 6 workers, from zero, transfer every 5 min):
  * sets/half1, 64 of 129 originals chosen with seed 17, 25,937 goals; Z4 proved 18,887 of them and
    production 22,291;
  * arms ORA (control), ORB (`--orig-rate`), ORD (control repeat), ORC (5, 20, 80, 320 s), ORE (e43 +
    `--lean-states`), ORF (ORC + e43 + lean), ORG (as ORF), ORH (ORG with `--no-fresh-states`).
* **Twee changes:** twee-e43 writes no state for a solved problem (0903499). `--lean-states` keeps no state for a
  goal that may not deepen. twee-e44 renormalises hints incrementally (99dbf15).
* **Failing runs:** 30 of 200 re-failed goals with the loop's exact commands, 5 abstract s, 3 at a time. A
  cost-centre profile (ghc-prof, `-fprof-auto-top`) on three failing goals.

**Results.**
* FR60 886 against FO60 891: off.
* Z4 at 3 h 56 min: 38,044 (60 min 35,511, 2 h 37,713, 3 h 37,962). Only 545 goals had an 80 s run (112 proved).

| goals, by time production needed | ≤ 0.5 s | ≤ 2 s | ≤ 5 s | ≤ 20 s | ≤ 80 s | ≤ 320 s | more |
|---|---:|---:|---:|---:|---:|---:|---:|
| production only | 443 | 330 | 1,265 | 2,342 | 2,011 | 384 | 43 |
| both | 29,897 | 4,684 | 1,646 | 1,229 | 515 | 47 | 8 |

* Hint statistics predict nothing (AUC 0.42–0.58). The original's recent rate does: AUC 0.73 (production 5 s),
  0.66 (80 s), 0.84 (Z4 5 s), 0.85 with recency weighting.

| half1, 2 h | 10 min | 30 min | 60 min | 90 min | 120 min | never run |
|---|---:|---:|---:|---:|---:|---:|
| ORA, control | 9,412 | 15,349 | 17,381 | 18,074 | 18,319 | 3,923 |
| ORB, `--orig-rate` | 9,105 | 15,401 | 17,356 | 18,015 | 18,228 | 4,107 |
| ORD, control repeat | 9,303 | 15,330 | 17,422 | 18,254 | 18,504 | 3,902 |
| ORC, 5, 20, 80, 320 s | 9,575 | 15,216 | 17,502 | 18,277 | **18,552** | 4,031 |
| ORE, e43 + lean (died at 70 min) | **10,282** | 15,858 | 17,596 | | | |
| ORF, ORC + e43 + lean (died at 70 min) | 10,094 | 15,891 | **17,733** | | | |
| ORH, e43 + `--no-fresh-states` | | | | | 18,476 | |

* ORG and ORH finished at 2 h: 18,374 and 18,476 (REPORT 2au).
* Failing runs, mean CPU s: as in the loop without the dump 5.45–5.61; with the dump 6.66 (peak memory 93 →
  349 MB); without the model 4.87; hints at factor 1 4.34; without hints 3.29; startup 0.17.
* e44 on 203 captured runs: 186 byte-identical, 11 differ by 2–6 extra hint forms, 3 diverge slightly; the same 29
  prove; CPU −11%.
* Profile: 45–58% of a run goes to making each new rule's critical pairs, mostly normalising both sides.
  290,299 pairs were made in 5 abstract s; only 10,000 were ever taken from the queue.

**Reading.**
* **70% of the gap took production more than 5 s**, so the tail is about which goals get longer runs.
* **Noise at this scale:** two identical 2-hour half1 runs differ by up to 185 (1%). ORB's −91 and ORC's +48 are
  within it.
* `--orig-rate` predicts well alone but loses inside the existing order. I measured the AUC outside the key the
  loop uses; it should be measured within it.
* The e43 gain is not `--lean-states`'s: a proved run no longer dumps, and median proof wall time fell by a third.
  Lean states hardly ever applied (1,790 of 1,815 failed first runs kept a state).
* **ORE and ORF died after 70 minutes from my bug** in `--lean-states`: `hs` was reused as a name for a finished
  run's hints (None when failed). Fixed as `hds` (7d376a2). ORA–ORD ran without the option.
* ORD never retried a failed goal fresh: of production's 3,785 half1 goals ORD missed, 3,074 had failed one 5 s
  run. A fresh retry of 200 of them in ORD's context proved 14.5%, against 18% for first runs at the end. So
  never-run goals first is about right.
* The profile is the reason the parental filter could pay (2026-11-17-pg-sum-filter.md): most pairs are made and
  normalised but never selected.

**Decision and next.** solve_new.sh defaults twee-e44, cascade 5,20,80,320 and `--no-fresh-states` (ORH 18,476
against ORG's 18,374, 4,792 runs an hour against 4,268; 55e4e67). REPORT 2au.

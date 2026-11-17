# Repeats cost most of the time: `--mix` and `--fail-order`

*Reconstructed on 17 Nov from REPORT 2at (17 Nov 03:10–08:30). Abstract time; counts by proof-file times.*

**Question.** Z1 ran only first-level runs, retried changed-context goals over and over, and never ran 12,998
goals (2026-11-16-from-zero-dispatcher.md). Would reserving workers per kind of run, or ordering by failures,
use the time better?

**Setup.**
* **`--mix M`** (f065848, 187832f): three kinds (near retries; far goals, including never-run ones; deeper
  levels). Each kind with goals waiting keeps M of the workers. The rest go to the kind with the most proofs per
  run second over its last 300 runs, counting running jobs' seconds as spent without a proof.
* **`--fail-order`** (3db0e8d): one list of every goal with a new context, near and far. Fewest failed fresh runs
  in the round first, then within the retry gaps, then nearest. Used with `--mix`.
* **Pass fix** (5b15fc9): with `--pass-every`, the full pass waits at least 8× its own last length (kNN index
  rebuilds left out).
* **Runs, whole benchmark from zero, 12 workers:** Z2 = Z1 + `--mix 0.1` (abs/z2_test.sh); Z3 = Z2 +
  `--fail-order` (z3_test.sh); Z4 = Z3 + the pass fix (z4_test.sh).
* **rp3, from zero, 4 workers:** MX1, MX3, MX60, FO60, against PE1 and LVZ.
* **rp3 with today's context** (loops/ULX): LVF `--mix 0.25 --fail-order` against LVU (scheduler).

**Results.**

| minutes | 5 | 10 | 20 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Z1 | 2,064 | 7,942 | 22,165 | 28,996 | 34,181 | 35,514 | 36,552 |
| Z2 (+mix 0.1) | | 5,724 | 18,540 | 25,967 | 33,539 | | |
| **Z4** (+mix, fail-order, pass fix) | **8,101** | **15,398** | 24,215 | 29,814 | 35,511 | 37,328 | **37,713** |

Z1's second hour, first-level runs by earlier failures in the round:

| earlier failures | runs | proved | proofs per run hour |
|---|---:|---:|---:|
| 0 | 3,516 | 51% | 365 |
| 1 | 1,270 | 6% | 29 |
| 2 | 882 | 4% | 19 |
| 3–8+ | 1,443 | 4% | 17–32 |

* Z2's far goals paid less than near retries for the whole first hour; Z2 was stopped at 65 minutes, 2% behind Z1.
* Z3 was +65% at 10 minutes and level at 22. Only 4.6–7.8 of 12 workers were busy (passes 0.2–0.35 s each).
* Z4: 1,161 more than Z1 at 2 hours. Its rate falls fast after 90 minutes (122 proofs in the last quarter-hour
  against Z1's 415). In the first 30 minutes 25,250 of its 25,527 runs proved, yet 21,646 goals had not run.

| rp3 from zero | 15 min | 30 min | 45 min | 60 min |
|---|---:|---:|---:|---:|
| LVZ | 830 | 871 | 885 | 890 |
| MX60 `--mix 0.25` | 828 | 872 | 887 | **914** |
| FO60 `--mix 0.25 --fail-order` | 828 | 872 | 888 | 891 |

| rp3, today's context | 1 min | 4 min | 10 min | 25 min | 40 min | 60 min |
|---|---:|---:|---:|---:|---:|---:|
| LVU, scheduler | 416 | 969 | 1,036 | 1,065 | 1,075 | 1,085 |
| **LVF**, mix 0.25 + fail-order | 455 | 1,004 | 1,041 | 1,068 | 1,085 | **1,095** |

**Reading.**
* **A goal's first run pays 12–20× as well as a repeat**, and repeats took 61% of the workers' time in Z1.
* On the whole benchmark, ordering by failures gives Z4 twice Z1's count at 10 minutes and +3% at 2 hours.
* One Python process is now the limit in the first phase: every run proves, and the chains (a goal becomes easy
  once the one below is proved) gate the rest.
* The rp3 comparisons are single runs. MX60 against FO60 (914 against 891) and LVF against LVU (+10) are leans,
  not proof; scheduler runs vary by about 25.
* Z4's totals are lemma-assisted: depcheck on Z4 (17 Nov) found 13.7% of its recorded proofs standalone, and
  4,465 goals proved twice through the 60 s sync window.

**Decision and next.** solve_new.sh defaults to `--mix 0.1 --fail-order` (ORDER, 2db27bf); SCHED turns the
scheduler back on. REPORT 2at.

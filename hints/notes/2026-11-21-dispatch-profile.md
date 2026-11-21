# Where a from-zero start spends its time: loop.py's threads (21 Nov 07:20)

**Question.** In Z6's first 30 minutes (all 51,784 goals, 12 workers) twee ran for 3.0 of the 6 worker hours, and
its curve at 2-6 minutes was only 1.2-1.4 times that of a 6-worker run. What holds the workers back, and what is
cheap to fix?

## Evidence before profiling

* Z6's progress lines: at 8,000 runs (216 s) the main thread had spent pass 41 s, submit 72 s, results 51 s and
  waited 53 s (76% busy, about 20 ms of main-thread time per run). At 28,000 runs (1,795 s): 285 / 671 / 249 s
  busy, 583 s waiting.
* At 6 workers on all goals (PRA below) the main thread waited 62% of the time, at about 16 ms per run.
* Runs per second at minutes 3-6: PRA (6 workers) 21, Z6 (12 workers) 26.

## Tool

exp/stacksample.py, a sampling profiler (py-spy is not installed, and ptrace_scope 1 allows only children): it runs
loop.py as `__main__` and samples every thread's Python stack every 5 ms. Output: per thread kind (main, worker),
exclusive and inclusive shares per function, and since 07:13 the chain of loop.py frames down to the leaf.
`sed 's|python3 -u "$H/loop.py"|python3 -u .../exp/stacksample.py OUT.txt "$H/loop.py"|'` on a copy of
solve_new.sh runs a loop under it.

## Profiles

* **PRF** (06:59, sets/half2 from zero, 6 workers, 4 minutes; loops/PRF.prof.txt; 5,246 solved):
  * main thread: 64% waiting; `train_model`, which wrote every goal's rule-model goal file, 18.5% (about 44 s, before
    the first run); kNN picks 4%; the rest under 4% each.
  * workers: 80% inside `subprocess.run` (twee), 6% idle, the rest Python per run (proof_job 3.2%, hint
    generalisation 2.2%, proof dependencies 1.3%, file checks).
* **PRA** (07:05, sets/all from zero, 6 workers, 6 minutes; loops/PRA.prof.txt; 9,036 solved, Z6 8,834 at 6 minutes
  with 12 workers): main thread 57% waiting, `train_model` 25% ("trained rule model 90s" in its log: no run in the
  first 1.5 minutes), kNN picks 5.6%, `given.axioms` 4.4%, the rest small.

So at 6 workers the workers are busy and twee-bound. The one fixed cost is the goal files, written for every
goal before the first run.

## Change (07:15): goal files at first use

loop.py's train_model no longer writes all the goal files. `goalfile(name)` writes a goal's file at its first use
(tmp, then rename), with the same content. Smoke test loops/GFT (smoke487, 2 workers, 3 minutes): "trained rule
model 0s", no errors, the 380 goal files it made identical to QKC's, no tmp files left. Saves about 90 s at a
from-zero start on all goals (45 s on half2). It does not change which runs are made, so it does not bias the A/B
arms, which both get it.

## Next

A profile at 12 workers on all goals, Z7's setting, in the gap between exp48's end (about 09:40) and exp49's start
(abs/after48.sh waits up to 20 minutes for loops/GO49). That shows whether the main thread (pass, submit, results)
or contention for the interpreter lock is the limit at 12 workers.

abs/prof12.sh (exp/prof12.sh; started 07:25, PID 251315) waits for loops/P2N.done and loops/P2O.done, runs loops/PRB
(sets/all from zero, 12 workers, 6 minutes, exp48's base options, under exp/stacksample.py into loops/PRB.prof.txt),
then writes loops/GO49, so exp49 and exp50 start about 8 minutes after exp48 ends.

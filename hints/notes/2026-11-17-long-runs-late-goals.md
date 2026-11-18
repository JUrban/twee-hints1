# Long runs on the late goals no deep run proved, and the hint-match signal (exp5)

**Question.** The user, 17 Nov, after exp1. Veroff's research question is whether hints can guide the search from
the axioms to very late, hard goals. His heuristic is whether the search still finds hint matchers reasonably
often: if not, he may stop it. This is a method for very long, deep proof searches. As we get into the hard part of
the benchmark, we may need such methods too, even starting from lemmas.

exp3 (notes/2026-11-17-deep-runs-expanded-chains.md) ran 47 late unsolved goals for 320 abstract s in four arms.
Its unproved runs were still finding new hint matches at the end (median last new match at 313–317 s). So the
signal says to go on. exp5 goes on:
* Do runs twice as long prove some of them?
* Does the number of new matches late in the 320 s run (240–320 s) predict which ones?

**Set.** exp3/goals47 (exp/sets/exp3_goals47), in its order. Each goal enters as soon as all four exp3 arms have it
and none proved it. The final set is therefore fixed: every exp3 goal that no arm proved at 320 s.

**Command.** exp3's arm C, production's context as captured in exp3/tb:
* twee-e48, PG 0.25, rm4t, sibling and kNN lemmas, the original's pool;
* 640 abstract s, CPU cap 6,400 s;
* `--print-hint-matchers` (output only);
* (first `--dump-state` as well, dropped at 01:10, see below).

Abstract time is deterministic, so the first 320 s repeat exp3's C run exactly, and a proof within 640 s costs
fewer than 1,280,000 pairs.

**Run.** `cd /project/hintwork/exp5; echo 3 > J; nohup python3 run.py C 640 8 > run_C640.out 2>&1 &`
* Launched 22:55 with 3 workers (exp3 holds 8 until it finishes, about 04:00); 4 from 23:09, back to 3 at 23:20 (load 22.6 with exp4's refinement), 2 at 23:47 (exp4's rung proofs). The J file goes up as exp3 frees
  CPUs, to at most 6 for memory: peak at 320 s is up to 3.7 GB.
* Output: res_C@640.tsv (goal, proved, CPU s, peak MB, considered pairs, matched hints, hints), out_C@640/,
  given_C@640/.

**Heap limit** (found 18 Nov 00:02).
* The first three runs (299, 320, 409) ended without WORK or RESULT lines. All three had a peak of 6.4 GB: the
  binaries are built with `-with-rtsopts=-M6g`, production's deliberate default. Production counts a heap
  exhaustion as a failure.
* At 320 s exp3's runs stay under it (peak at most 3.7 GB, every row has its pair count). At 640 s they do not.
* Stopped at 00:03. The rows, outputs and partial states are kept as res_C@640.heap6g.tsv, out_C@640.heap6g/ and
  states_C@640.heap6g/.
* Relaunched at 00:03 with `+RTS -M12g -RTS` (run.py's 4th argument, default 12g) and 2 workers (24 GB at
  most): `nohup python3 run.py C 640 8 12g > run_C640.out 2>&1 &`.

**Not the heap** (00:47).
* With -M12g, goal 299 again ended without WORK or RESULT: 1,326 CPU s, peak 7.3 GB, so well under the limit.
* Its output stops at the same HINTMATCHER line as the 6 GB run. The search is deterministic, so both runs died
  at the same point. stdout to a pipe is block-buffered, so whatever was printed after the last full block was
  lost.
* The state file was written (26 MB, at the run's end).
* A 20 s run with --dump-state ends normally.
* Stopped at 00:47. A run of mbol_lem1 387 in progress was lost.
* Reproduction: 299 at 640 s twice, with and without --dump-state, with stderr and the exit status kept
  (exp5/dbg/a.* and b.*; the command is in exp5/dbg/cmd).

**Cause found** (01:09): the state dump and memwatch.py.
* With --dump-state the run was killed by signal 9 during the dump: RSS rose from 2.4 GB to 7.5 GB.
* Without it, the same run ended normally: 1,280,000 pairs, unproved, 1,272 CPU s, peak 2.3 GB.
* The killer is my own watchdog, `abs/memwatch.py 7 45` (running since 14 Nov). It kills any twee over 7 GB to
  protect the loops. REPORT 2au had measured that a dump takes about 4 times a run's peak memory.
* So every exp5 run with --dump-state died after its search had ended, with its output cut at the last full stdout
  block. The heap limit was a wrong first diagnosis.
* **Fix:** no --dump-state, and the binaries' own heap limit (-M6g, as in production). The faulty runs' files are
  in exp5/broken/. Goal 299's row is the debugging run without the dump (exp5/dbg/b.*); its command is the same
  apart from the heap limit, which it never reached.
* Relaunched at 01:10 with 2 workers: `nohup python3 run.py C 640 8 > run_C640.out 2>&1 &`.

**Analysis planned.**
* Proved at 640 s against the late-match count of the C@320 run (HINTLOG first matches after 480,000 pairs).
* The stall replay of exp3 on the 640 s runs.

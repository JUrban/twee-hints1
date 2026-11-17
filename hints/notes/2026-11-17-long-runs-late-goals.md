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
* `--dump-state states_C@640/<g>.state`, written only when unproved, so a later run can resume it with
  --load-state.

Abstract time is deterministic, so the first 320 s repeat exp3's C run exactly, and a proof within 640 s costs
fewer than 1,280,000 pairs.

**Run.** `cd /project/hintwork/exp5; echo 3 > J; nohup python3 run.py C 640 8 > run_C640.out 2>&1 &`
* Launched 22:55 with 3 workers (exp3 holds 8 until it finishes, about 04:00); 4 from 23:08. The J file goes up as exp3 frees
  CPUs, to at most 6 for memory: peak at 320 s is up to 3.7 GB.
* Output: res_C@640.tsv (goal, proved, CPU s, peak MB, considered pairs, matched hints, hints), out_C@640/,
  given_C@640/.

**Analysis planned.**
* Proved at 640 s against the late-match count of the C@320 run (HINTLOG first matches after 480,000 pairs).
* The stall replay of exp3 on the 640 s runs.

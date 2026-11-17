# Deep runs on late unsolved goals, guided by expanded proof chains (Veroff's question)

**Question.** The user, 17 Nov 19:53:
* Veroff's research question is whether he can hint-guide the search from the axioms to the very late, hard
  goals.
* His heuristic is whether the search still finds hint matchers reasonably often. If not, he may stop it. This
  is a method for very long, deep searches on very nontrivial, late goals.
* As we get into the hard parts of the benchmark we may need such methods too, even starting from lemmas
  instead of axioms, along with other tricks (climbing the ladder up and down, conjecturing intermediate goals).

So, on production's unsolved late goals:
1. Do long runs guided by the expanded proofs of the goals just below prove more than production's own setting?
2. From the axioms alone, as Veroff does?
3. Does the hint-match timeline separate the runs that will prove from the lost ones, so lost runs can be
   stopped early? On 13 Nov it did not, with the hint sets of then (2026-11-13-long-runs-stall.md). Whole pools
   kept matching to the end, and kNN hints stopped matching after about 3 s in solved and failed runs alike.

**Why this differs from exp1 and exp2** (2026-11-17-expanded-proofs.md):
* Those measured re-proving solved goals, and hint volume in 5 and 20 s frontier runs.
* Here: unsolved goals, one long run each, and the chain of proofs right below the goal as the guide. That is
  Veroff's ladder: the proofs of goal k−1, k−2, … expanded to their foundations guide goal k.

**Setup** (17 Nov, launched 20:08). Work dir /project/hintwork/exp3. Scripts in hints/exp (exp3_*), sets in
hints/exp/sets.
* **Goals** (exp/sets/exp3_goals48):
  * Candidates: public goals unsolved in all 16 production-like loops (UL, Z0–Z4, PGA, PGB, ORA–ORH; 44,906
    solved in some loop, of 51,784), with a UL-proven goal among the 3 goals below them in their original:
    1,347 goals.
  * Shuffled with seed 7, then taken in order with at most 2 per original: 48 goals of 38 originals
    (exp/exp3_pick.py, run in exp3; it also writes sibs10.tsv).
  * **Redone at 20:10.** The first pick (19:54) built the candidate list by iterating a Python set, so its order
    depended on the per-process hash seed and the pick could not be regenerated. It is kept in
    exp3/old_hashpick, unused. The script now iterates sorted, and it gives the same set under another
    PYTHONHASHSEED. It shares no goal with the first pick.
  * They are late: their position in the original's goal list has quartiles 0.82, 0.87 and 0.93.
  * Production's history on them: 14 only ever ran at 5 s, 22 reached 80 s and 12 failed at 320 s (all
    production runs: 356 at 5 s, 118 at 80 s, 13 at 320 s).
* **Commands, captured in production's context** (exp/exp3_solve_cap.sh = solve_new.sh with H fixed):
  * `LOOP_PRINT_CMD=1 LOOP_KEEP_TMP=1 SCHED= XEVERY=100000 CASCADE=5 timeout 900 bash solve_cap.sh goals48
    /project/hintwork/loops/UL exp3/CAP 3 0.05`. The context was 44,907 UL proofs at 19:55.
  * The first command printed per goal was kept, with its problem file (sibling and kNN lemmas), hints file
    (the original's pool) and rule-goal file. All were copied to exp3/tb (cmds.all, tmp/, goals/) and the paths
    rewritten. The loop was stopped once all 48 were captured (20:01).
  * **One goal proved in its 5 s capture run:** aK2_eq_aK3_o 495, with 13,927 pool hints. It is new to the
    benchmark (UL lacks it) and will be merged. That leaves **47 goals** (exp/sets/exp3_goals47).
  * The commands are solve_new.sh's defaults: twee-e48, `--pg-threshold 0.25`, rm4t at 0.1 with penalty 2,
    `--abstract-time 2000 --no-resume-requeue --no-eqhint-consider`, `--print-hints --print-given`.
* **Chains** (exp/exp3_mkhints.py):
  * For each goal, its 10 nearest UL-proven siblings below (exp3/sibs10.tsv: 439 goals) were expanded:
    `expand.py exp3/sibs10 exp3/xd`, over all 16 loops' records (39,390). No loop has proved any of the 48, so no
    proof of a test goal can enter.
  * chain(g) = the siblings' expansions, nearest sibling first, each with its own steps first and then its
    lemmas' steps by depth, duplicates dropped.
  * Sizes per goal (47), minimum, quartiles and maximum:
    * pool: 2,474, 5,061, 6,271, 8,182, 18,648;
    * chain: 1,333, 4,602, 8,968, 15,881, 23,861;
    * chain hints the pool lacks: 285, 2,422, 6,033, 12,075, 19,410.
* **Arms** (exp/exp3_run.py), 320 abstract s each, CPU cap 3,200 s:
  * **C:** the captured command (production's setting).
  * **K:** the same lemmas, with the chain alone as hints (h_K).
  * **E:** the pool, then the chain's extras (h_E).
  * **V:** the original problem from the axioms alone (no lemmas), with the chain as hints. This is Veroff's
    setting.
  * Runs are queued goal by goal, C, K, E, V for each, so partial results compare.
  * Workers: at most 12, the current limit read from exp3/J: 6 at the start, while exp1 P and exp2's 20 s arms
    finish, then 12 (with production's 6 that keeps the machine near 20).
* **Recorded per run:** res_<arm>@320.tsv (goal, proved, CPU s, peak MB, considered pairs, matched hints,
  hints). out_<arm>@320/<g> holds the output without the given log, with HINTLOG (each hint's first match, in
  critical pairs) for stallsim.py. given_<arm>@320/<g> holds the given log of proved runs, as training data of
  long proofs (the user's synthetic-data point).
* **Output only:** every run adds `--print-hint-matchers` (a HINTMATCHER line per rule that matches a hint).
  HINTLOG's second number is the matching rule's id, not the hint's, so only the matchers show which chain
  hints (which sibling, own steps or lemma steps) the search reached.
* **Launch** (20:08): `cd /project/hintwork/exp3; echo 6 > J; nohup python3 run.py C,K,E,V 320 12 > run320.out
  2>&1 &` (goals47 is the default set).
  * A first launch at 20:02 without `--print-hint-matchers` was stopped after 3 minutes, before any run had
    finished, and its files were removed.

**Smoke test** (on a goal of the first pick, R1dist_to_aa1 473, 5 s): all four arms ran and printed HINTLOG.
Hints: C 9,333, E 9,398, K and V 1,916. Matched: C 1,157, E 1,154, K 530, V 396.

**Planned analysis.**
* Proved per arm; paired gains and losses against C; CPU and peak memory.
* stallsim.py on each arm's outputs: proofs and work by stall limit, compared with 13 Nov's flat curve.
* For K and V: which chain hints were matched, by sibling distance and by depth. That shows whether the search
  climbs the chain.

**Caveats.**
* 47 goals at 320 s: an arm that proves 2 more is not evidence alone. Any proof is new to the benchmark.
* C repeats a depth production already tried on 16 goals, in an older context. C's proofs therefore measure the
  context and the PG filter as much as the method.
* The chains include proofs found with kNN lemmas from other originals. In V the derivations of those lemmas are
  hints only, so V must re-derive whatever the chain's unrecorded leaves hide.

# A portfolio of symbol precedences (exp85)

Written 25 Nov 2026, 08:08 UTC.

## Why

* The user (25 Nov, after exp84): Veroff just tried all possible symbol precedences (120?); maybe that can be reduced
  to some of them after portfolio construction, keeping the most complementary ones. Do not keep m, ld, rd, e at
  their default; evaluate experimentally. And build it in randomized stages: first all orderings on a small random
  set of problems, then a reasonably big portfolio of complementary ones with some redundancy, then a bigger random
  set with that smaller number of orderings, and iterate.
* exp84 (notes/2026-11-25-precedences.md) tried four random precedences on unsolved targets: 0 gained. On goals
  nobody can prove, complementarity cannot be seen. Here the orderings run on goals that are provable but not easy,
  in a context without their own proofs, with identical inputs per ordering.
* The user also: Veroff reorders the hints by the current term ordering in each search. Twee already does the
  equivalent: hints are matched in an orientation-free canonical form, and rewritten to normal form with the run's
  own rules as they are learned (`--eqhint-normalise`, on by default), so each ordering sees the hints in its own
  normal forms.
* AIM's signature: m, ld, rd (binary), e (constant), and the defined a, l, r (ternary), k, t (binary); 5! = 120
  orders of a, k, l, r, t. Twee ranks listed symbols above unlisted ones, in list order; the rest by occurrence
  count in the problem (lemma axioms included), so twee's default changes with each run's lemmas.

## Stage 1 (exp85): all 121 orderings on a small random set

* Orderings (exp/sets/exp85.orders): 0 = twee's default (no `--precedence`); 1-120 = each order of a, k, l, r, t
  exactly once, with m, ld, rd, e at random places (a full list of all nine symbols; order i: random.Random(85000+i)
  shuffles the nine, then the five defined ones take the slots of the defined ones in permutation i).
* Candidates (sets/exp85.cand, exp/sets/exp85.cand, seed 85): 40 of ul84's 55 L1 proofs (since 24 Nov 11:23, proved
  at the 40 s level, not at 5 s) and 80 of the 343 other climber-proved targets (CLS71 since 08:59, CLQ83).
* Capture (abs/exp85.sh, exp/exp85.sh, bash 4082683 from 08:07:13; loops/P85C, loops/EXP85.pids): CLQ83's final
  (clq83.sh's options, set mode `--targets`, `--runs 0 --final-cpu 40`, -j 4) on the 120 candidates, in
  t0758.trusted's context without them (49,624 solved; their rows and hints left out), with CLQ83's true.tsv,
  fillhints/, sketches/. `--twee exp/twee_capture.py`: a wrapper that keeps each run's problem, hints and rule-goal
  files and its arguments (loops/P85C/cap/log.jsonl), then runs twee-pg61.
* Dev set (loops/P85C/dev.txt): the candidates whose captured final proved with at least 1 CPU s, or failed; at
  most 50 (seed 85).
* Replay (exp/prec_replay.py, loops/P85C/replay.tsv): each dev goal's captured final under the 121 orderings,
  `--max-cpu 10`, without the --print-given/--print-hints output flags, -j 5. At most 121 x 50 x 10 s = 16.8 CPU h.
* Checked at 08:08: the replay reproduces captured runs (goal 420: captured final 9.76 CPU s, replay at the default
  9.65; goal 495: 19.26 and 18.24), and finds THM.

## Measures and the next stages

* Per ordering: proved of the dev set within 10 s; the default's count; the union of all 121; how many goals only
  non-default orderings prove; pairwise overlap.
* Stage 2: a portfolio of about 20-30 orderings by greedy cover with redundancy (each dev goal covered at least twice
  where possible) plus the default, on a bigger fresh random set (about 200 candidates, captured the same way).
* Stage 3: prune to the most complementary few, a bigger set again; then the portfolio against the default at equal
  CPU on stalled unsolved goals (CLQ83's failures) before any production use.
* Caveat: the dev goals are proved goals made unsolved in the context (their siblings' lemmas and the climbers'
  sketch hints still there); the use is on goals nobody has proved.

## Capture and dev set (08:07-08:23)

* Capture: 120 finals in 16 minutes, 76 proved within 40 CPU s in this context (without their own proofs; 44 failed).
* Dev set (loops/P85C/dev.txt): 50 of the 120 (seed 85, from those proved with at least 1 CPU s or failed): 31 the
  captured default proved (16 under 10 CPU s, 15 in 10-40 s: 11.8 to 38.5), 19 it failed at 40 s. So at the replay's
  10 s cap the default proves about 16, and the other 34 are where other orderings can show what they add.
* Replay from 08:23:17: 6,050 runs (50 x 121), -j 5, --cpu 10.

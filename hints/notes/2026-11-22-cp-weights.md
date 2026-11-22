# Twee's critical-pair weights as portfolio members (exp57)

Written 22 Nov 2026, 11:13 UTC.

## Question

The user (11:08): "ad portfolios, have we played with different weights for the default twee weighting functions?"

No. The records (REPORT, JOURNAL, notes/) have no run with `--lhs-weight`, `--rhs-weight`, `--var-weight`,
`--depth-weight`, `--dup-cost`, `--dup-factor` or `--fun-weight`. The search-setting variants tried so far are:
* the rule-model variants (threshold 0.2, no rule model, other models);
* no parental guidance; subsumption matching; the two-sided chain;
* `--flip-ordering`, `--kbo-weight0`, `--no-flatten-goal`, `--flatten-goal-lightly` (15 Nov, abs/var_test.sh).

All of them proved 0 on stalled goals at 5-20 s (exp21: "changing the search does nothing at 5 s where the same
problem just failed"). Those tests were on goals the same search had just failed in the same context, at short
budgets. A weight change reorders the whole critical-pair queue, so it may pay on goals that have not been tried yet,
at longer budgets.

Twee's score of a critical pair l = r (src/Twee/CP.hs), with m and n the weighted sizes of the two sides:

    depth * depth-weight + (m + n) * rhs-weight + max(m, n) * (lhs-weight - rhs-weight)

The defaults are lhs 4, rhs 1, var 6/7, depth 2, dup-cost 1 (a repeated subterm costs 1, not its size) and
dup-factor 0. The hint score is applied on top of this (`s * eqhint-factor + eqhint-weight`); the factor is a
multiplier, so it does not depend on the weights' scale.

## Set

* sets/wheads300 (exp/sets/wheads300) is 300 heads of sets/late2, drawn with random.seed(57) from the sorted list.
  * sets/late2 is the 3,817 half2 goals Z7 left unsolved (notes/2026-11-22-late-ab.md).
  * A head here is a late2 goal whose previous goal in its original is proven in Z7's context. There are 692 such
    heads, from 63 originals; the sample covers 58 originals.
  * The heads are the right population. LAA ∪ LAB proved 239 of the 692 heads (35%) in their first 2.7 hours,
    against 107 of the other 3,125 late2 goals (3%).
* Context: loops/LAA.ctx, Z7's 43,769 proofs without the late2 goals (exp54's context).

## Arms

There is one fresh run per goal and arm. The search is loop.py `--start 1 --rounds 1`, abs/var_test.sh's form, with
solve_new.sh's model and lemma options:
* rm4t, 6 lemmas, 30 kNN lemmas, pool original;
* twee-pg61 with TWEE_PG_ARGS `--pg-threshold 0.25 --ground-joining-branch-limit 100`;
* `--abstract-time 2000 --no-resume-requeue --no-eqhint-consider`.

| arm | twee flag | budget | workers |
|---|---|---|---|
| CW0 | (control) | 20 s | 1 |
| CW1 | `--lhs-weight 2` | 20 s | 1 |
| CW2 | `--lhs-weight 8` | 20 s | 1 |
| CW3 | `--depth-weight 0` | 20 s | 1 |
| CW4 | `--depth-weight 5` | 20 s | 1 |
| CW5 | `--var-weight 0.5` | 20 s | 1 |
| CW6 | `--var-weight 1.5` | 20 s | 1 |
| CW7 | `--dup-factor 1` (a repeated subterm costs its size + 1) | 20 s | 1 |
| CW9 | (control) | 40 s | 2 |

CW9 is the time-matched control for "the control plus one weight variant". The union of CW0 and CWk costs two 20 s
runs a goal, and CW9 is one 40 s run.

Smoke test (abs/wsmoke.sh, 11:10): 3 goals at 5 s, control and `--lhs-weight 2`. Both proved 0. The outputs
differ (3,154 against 3,007 rules on nil3_1K_b 377), so the flag reaches twee.

## Schedule

* abs/after_exp54w.sh (PID 2026476, 11:12) waits for exp54 to end (about 11:57). Then:
  * it writes loops/EXP55.skip, so abs/after_exp54.sh exits without starting exp55;
  * it runs abs/exp57.sh, about 2 hours on 10 workers;
  * it then runs abs/exp55.sh, unless loops/EXP55B.skip exists 10 minutes after exp57 ends.
* exp54's replica pair (abs/exp54r.sh) is deferred. exp54's +12 is far below its +50 bar either way.

## Measures

* Proved of 300 per arm; for each CWk, the +/− against CW0 and the union with CW0.
* That union against CW9 (equal CPU), and the CPU of each arm from its rows.
* The union of all arms, and the goals only one arm proved.
* Proofs: keep_proofs is on by default, so each proved run's printed proof is kept for proofq (rerun with
  `exp/proofq.py` on the CW dirs afterwards).

Decision: a weight arm whose union with CW0 beats CW9 by 5 or more goals becomes a member candidate. It would then
be a 40 s variant on heads in production and get its exploration hour. loop.py's variants are named (unf, k60, r2
and so on), so this needs a new variant kind that passes a twee flag.

## loop.py support (22 Nov 11:23)

`--flag-variants NAME=FLAGS;...` (commit d825cae) defines variants that add twee flags; NAME is then usable in
`--variants` like the named variants. Twee takes no `--flag=value`, so loop.py splits such a token in two, and the
option can go through LOOPARGS without spaces. Smoke FVS (solve_new.sh, sets/wsm3, 1 worker, 5 minutes,
`--flag-variants lw2=--lhs-weight=2 --variants lw2@0,unf@0`): the cascade built level Vlw2@0 at 5 s, its twee command
carried `--lhs-weight 2` (LOOP_PRINT_CMD), it ran on all 3 goals, and there was no traceback.

## Started (22 Nov 11:57:42)

abs/after_exp54w.sh started abs/exp57.sh 6 seconds after exp54 ended. Arm loop.py PIDs: CW0 2044955, CW1 2044958, CW2
2044960, CW3 2044961, CW4 2044963, CW5 2044965, CW6 2044967, CW7 2044968, CW9 2044969. abs/after_exp54.sh saw
loops/EXP55.skip and exited.

At 12:08 the arms had run 14 to 24 goals each in 11 minutes, so about 30 s a goal: 300 goals take about 3.2 hours,
to about 15:10. exp55 then starts about 15:20 and ends about 21:20. Read it with `exp/cwana.py CW0 CW9 CW1 CW2 CW3
CW4 CW5 CW6 CW7`, which counts only the goals every arm has run.

## Interim, 78 goals (22 Nov 12:39)

exp/cwana.py on the 78 goals every arm has run:

| arm | proved | CPU h | +/− vs CW0 | union with CW0 | vs CW9 (18 in 1.29 h) |
|---|---:|---:|---|---:|---|
| CW0 control 20 s | 17 | 0.57 | | | |
| CW9 control 40 s | 18 | 1.29 | +1 −0 | | |
| CW1 lhs-weight 2 | 15 | 0.57 | +0 −2 | 17 in 1.14 h | −1 |
| CW2 lhs-weight 8 | 15 | 0.57 | +0 −2 | 17 | −1 |
| CW3 depth-weight 0 | 15 | 0.48 | +1 −3 | 18 | +0 |
| CW4 depth-weight 5 | 15 | 0.66 | +0 −2 | 17 | −1 |
| CW5 var-weight 0.5 | 17 | 0.68 | +1 −1 | 18 | +0 |
| CW6 var-weight 1.5 | 16 | 0.49 | +0 −1 | 17 | −1 |
| CW7 dup-factor 1 | 16 | 0.58 | +0 −1 | 17 | −1 |

The union of all nine arms is 19 goals in 5.89 CPU h. Only CW3 proved a goal no other arm proved. So far the weights
hardly change which heads fall at 20 s, and twice the time adds 1. The heads split into those any setting proves
within 20 s and those none proves within 40 s.


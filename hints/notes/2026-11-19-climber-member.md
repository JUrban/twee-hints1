# The live head climber measured again as a deep member (exp32)

Written 19 Nov 2026, 15:39 UTC. Part of the portfolio task (notes/2026-11-18-portfolio-review.md).

## Why

The user forwarded a message about the climber at 15:20. Checked against the record:
* The live up-down climber (climb.py --live, stronger theories, up-down and learned lattice moves) ran from 15 Nov
  22:07 to 16 Nov 04:42. It was stopped at about 0.5 proofs per CPU hour, and its CPUs went to proof-step transfer
  (then 43 per CPU hour) (2aj, 2ak).
* The long head climbs (abs/clh.sh) proved 17 of the 111 stuck tail heads in 14.7 CPU h (1.2 per CPU hour). The live
  head climber after them (abs/clhl.sh) proved 4 of about 60 in 8.5 CPU h (0.47 per CPU hour). It was stopped on
  16 Nov at 11:05, and its CPUs went to production (2an).
* exp4 (the lattice with small steps, 17-18 Nov; notes/2026-11-17-lattice-construction.md) was a one-off and is
  not part of this.
* **The climber was dropped before the portfolio rule existed (18 Nov 17:00) and never re-measured under it.** Its
  0.47-1.2 per CPU hour came on goals production also worked on. That is above members still in the portfolio:
  * the unfolded 80 s run, 0.40-0.47 after the earlier members;
  * the two-sided chain, 0.25;
  * no rule model, 0.23.
* The 15 Nov test also found climbs and long fresh runs proving different goals (3 each, 6 distinct).

## Setting

* **Climber:** abs/clhl2.sh = abs/clhl.sh's setting, live on production (loops/UL), with a fresh climb record
  (loops/CLHL2) and 2 climbs at a time. The current twee binary is twee-pg61 with PG 0.25 and the branch limit.
  * Heads only: each original's first unsolved goal, re-climbed up to 3 times when its original gains a proof.
  * Moves: up to 8 candidate assumptions, kNN 8, 4 stronger theories (2 explored, 10 of their lemmas), up-down with
    single additions, 4 weakenings, chain, fill 3.
  * Runs: 24 sketch runs at 5 s, then a final run at 160 s.
  * Production context: rm4t, 6 sibling and 30 kNN lemmas, the original's pool.
  * Real proofs go into loops/UL (hints, then a solved.tsv row). Production picks them up through --sync.
* **Production:** ul66 = ul65 on 17 workers, to keep the total near 20 CPUs: 17 + 2 + the transfer's 2 at times.
* The smoke test (15:35, on the scratch loop with short budgets) ran with today's loop.py, without errors.

## Measures

* Climber proofs per CPU hour (loops/CLHL2.log, climb.tsv). The CPU is the twee runs' CPU time.
* Conditional: every climbed goal is a head that production's members failed in the current context (the live
  mode climbs only stalled goals). Count the climber's proofs that production had not found by the climb's end.
* Against production's deep members over the same hours: `levyield.py loops/UL/r5/results.tsv ROW` from ul66's
  first row.
* Decision rule: at 0.25 per CPU hour or more (the two-sided chain's rate), the climber stays as a member, and is
  then built into loop.py as a variant, so the ratio order gives it CPU by its yield. Below that, with no unique
  proofs, it is a measured negative.
* Length: about 5 hours (10 CPU h): about 5 proofs if 0.47 holds.

## Results

(running)

* First 11 minutes: 2 real proofs, both in production's solved.tsv with hints:
  * nslm_to_aa1 845 (15:45): the climb's final run proved it, and so did its plain 160 s control run (`direct`
    row, 75 s);
  * aK2_eq_aK3_a 518 (15:48): the final run, in 31 s.
  * Production's last runs on both were 5 s members (Vkd@0, Vk60@0, Vs12@0), all failed.
* **So each proof is credited by which run proved it.** Final only is the climb's own gain. Direct (a plain 160 s
  run) is something production's own 80-320 s levels could also do. Both counts are reported at the end, with the
  per-CPU-hour rate of each.
* (17:05) The climber was restarted at 17:00:52 and 17:03:00 with climb.py's new records (true.tsv, fillhints/,
  assume.tsv, used.tsv; [notes/2026-11-19-climber-outputs.md](2026-11-19-climber-outputs.md)). Its fill lemmas from 15:40 to 17:00 were lost,
  and the 2 climbs in flight were cut. The rate is still read per CPU hour from climb.tsv.
* **(17:50) Correction: `direct` is not a control.** climb.py runs it only after a successful final run, by which
  point that run's own proof steps are already among the sketch hints: 1,573 hints in 845's direct run, against 51
  in its final. The "direct" credit above means nothing. All 5 proofs so far are the climb's own (final runs): 845,
  518, 434, 458 and lra2aa 291. Whether their sketch hints were needed is exp36
  ([notes/2026-11-19-climb-ablation.md](2026-11-19-climb-ablation.md)).
* 17:40 tally: 5 proofs in 3.50 CPU h (1.43 per CPU h, above the 0.25 threshold). In the same rows (from 156,424)
  production's members: L0 4.1, Vpool@1:0 2.7, Vs40@0 1.9, Vkd@0 0.6 per CPU h, and the rest 0.

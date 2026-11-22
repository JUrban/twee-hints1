# exp53: deep runs without queue renormalisation, from zero (`--cp-renormalise-threshold 1000`) (21 Nov 22:22)

**Question.** Twee renormalises its passive queue (rescoring the queued critical pairs) as rules are added. Under
`--abstract-time` that work is free in abstract time but real CPU: 27% of a hinted 10 s run's CPU in the profile.
Turned off, an 80 s run costs about 25% less CPU but searches differently. Does a loop whose runs never renormalise
prove more goals in the same wall-clock time, from zero?

## Why

* notes/2026-11-19-hint-cost.md (exp25): 6 walls at 80 s, production's binary and flags. Never renormalising cost
  613 CPU s against 823 (−25%), with no higher peak RSS; of the 3 proofs, 2 were kept (one byte-identical, one
  different), 1 lost (aa1_14 482). At 20 s the outputs were byte-identical and 16% cheaper.
* notes/2026-11-19-queue-renorm-ab.md (exp26): an A/B on production's deep runs (half the goals by crc32, rows ab=1).
  B cost about 20% less a run; 7 proofs of 209 against 5 of 186, too thin to tell.
* In Z7 the retry and deep classes take about half the CPU after 2 hours. A from-zero A/B covers every kind of run,
  including the 5 s first runs, where the saving turns into more runs per hour.
* Smoke (21 Nov 22:00): twee-e61 takes the option. A copied 5 s proof job (P2T's aa1_45_a__goal_45) printed
  byte-identical output with and without it (0.20 against 0.21 s user).

## Setup

* abs/exp53.sh (exp/exp53.sh): P2V, the control (solve_new.sh's defaults), and P2W, the same plus
  `PG="--cp-renormalise-threshold 1000"`. solve_new.sh passes `$PG` into the main loop's twee arguments (`--args`);
  the transfer and derived-rule loops are the same in both arms. half2 from zero (loops/EMPTY), 4 workers each,
  3 hours, transfer every 5 minutes, SCHED= (abs/or_test2.sh), like exp52.
* Started by abs/after_exp52.sh (exp/after_exp52.sh) when P2T and P2U are done. If exp52's option is installed as a
  solve_new.sh default first, both arms have it.
* Binaries: /project/bin/twee-pg61 (twee-e61 with TWEE_PG_ARGS `--pg-threshold 0.25 --ground-joining-branch-limit
  100`), loop.py and solve_new.sh at the commit current at the start.

## Measures

* Goals of half2 proved by 10, 30, 60, 120, 180 minutes (abs/setcurve.py sets/half2 P2V P2W).
* Runs, proofs and CPU hours per level and per kind (results.tsv, exp/quickstat.py): the CPU per run should be lower
  in P2W, more so at the deep levels.
* Portfolio: one-arm goals both ways and the union per worker-hour.
* Decision: identical half2 runs differ by about 185, so P2W ≥ P2V + 185 at 3 hours, or a curve clearly ahead
  throughout with no loss at 3 hours.

## Started (21 Nov 23:51)

exp52 was accepted at 23:51 (`--floor-ratio 20` in solve_new.sh's LATE, 0e6996b), and loops/EXP53.go made
abs/after_exp52.sh start abs/exp53.sh at 23:51:52: P2V loop.py 1400531, P2W loop.py 1400534, each with its transfer
and derived-rule loops. Both config.json files have floor_ratio 20.0, retry_class and head_class; P2W's args are
`--abstract-time 2000 --no-resume-requeue --no-eqhint-consider --cp-renormalise-threshold 1000`, P2V's the same
without the last option. They end at about 02:52.

## Interim at 30 minutes (22 Nov 00:22): even

| min | 5 | 10 | 20 | 30 |
|---|---|---|---|---|
| P2V (control) | 5,604 | 9,766 | 13,466 | 15,382 |
| P2W (`--cp-renormalise-threshold 1000`) | 5,583 | 9,744 | 13,408 | 15,305 |
| P2W − P2V | −21 | −22 | −58 | −77 |
| P2U (exp52, the same setup as P2V, 21 Nov) | 5,182 | 9,627 | 13,604 | 15,574 |

Runs by level (proofs / runs / CPU hours / CPU s a run): L0 P2V 13,202 / 13,404 / 1.41 / 0.38, P2W 13,141 / 13,347 /
1.40 / 0.38; Vunf@0 29 / 111 / 0.20 / 6.54 and 24 / 108 / 0.21 / 6.94; L2 one run each, 155 and 158 s. No CPU saving
yet: first runs are short, and the queue is renormalised only as it grows. The deep runs, where exp25 measured −25%,
come later. P2V is a replica of P2U's setup and sits 192 below it at 30 minutes, within the usual spread.

## Interim at 1 hour (22 Nov 00:52): even, and no CPU saving

| min | 10 | 30 | 45 | 60 |
|---|---|---|---|---|
| P2V (control) | 9,766 | 15,382 | 16,875 | 17,804 |
| P2W (`--cp-renormalise-threshold 1000`) | 9,744 | 15,305 | 16,774 | 17,728 |
| P2W − P2V | −22 | −77 | −101 | −76 |
| P2U (exp52, same setup as P2V) | 9,627 | 15,574 | 16,931 | 17,696 |

CPU s a run (results.tsv): L0 0.64 against 0.63 (15,772 and 15,777 runs); Vunf@0 7.16 and 7.42; Vk100@0 4.73 and
4.57; Vk200@0 5.23 and 5.28; Vk400@0 5.50 and 5.71. Not renormalising saves nothing at these levels: the runs are
5-10 s, and exp25's −25% was at 80 s. Deep runs are few (L1 3 and 2, L2 1 each). P2V replicates exp52's P2U: +108 at
1 hour.

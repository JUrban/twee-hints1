# exp66: the head climber back beside production (23 Nov)

## Question

The live head climber (climb.py --live, abs/clhl2.sh, loops/CLHL2) ran 19 Nov 15:39 to 20 Nov 10:04. It made 69 proofs
in 66 CPU h (1.04 per CPU h; 68 are still trusted), about as good as production's deep levels (L1 1.20 and k200 1.23
proofs per hour of runs since 19 Nov). It stopped 3 minutes before the 20 Nov quarantine and nobody restarted it, an
oversight found when the user asked (23 Nov) whether any climbing runs. The user then said: "you can start the climber
now, taking some more cpus for this limited time is ok; you should remember to use the climber and experiment with it
as it's veroff's main weapon for solving open problems".

* Does the climber still make about 1 proof per CPU h on today's heads? The 92 heads (each original's first unsolved
  goal) are harder than those of 19 Nov: production's own loop proves about 0.15 an hour on them.
* How does it compare per CPU h with the plain 60 s head runs (HDW1: 4 of 92 with 400 kNN lemmas, about 1.8 per CPU h;
  plainlive4's H setting from HDG1's end)?

## Setup

* abs/clhl3.sh (copy in exp/prod/side/): clhl2.sh's setting unchanged, a fresh record loops/CLHL3. CLHL2's fill lemmas
  and assumptions predate the quarantine, so they are not reused.
  * `--heads-only --reclimb-heads 3`: heads only, each climbed again after 3 new proofs in its original;
  * sketches: 8 moves (`--m 8`), 8 kNN, 4 theories (2 explored), 10 theory lemmas, up-down, weakening 4, chain, fill 3;
  * 24 sketch runs of 5 s, a 160 s final run, 2 climbs at a time (`-j 2`);
  * loop.py's run arguments as production's: rm4t, 6 sibling and 30 kNN lemmas, twee-pg61 with PG 0.25.
* Launched 23 Nov 18:44:54 with `CPUS=28` (a climb starts only while fewer than 28 twee processes run): 23 were running then,
  and the user allowed more CPUs for a limited time. exp65 frees 8 at about 22:55.
* Proofs go straight into loops/UL (`--live`); trust.py checks them like any other.

## Readings

* Every few hours: real proofs (final runs with no unproved assumption) per CPU h from loops/CLHL3/climb.tsv
  (column 6, seconds), and how many are still trusted.
* Against plainlive4's H cycles over the same hours, per CPU h. Both target the heads, so whichever proves a head first
  takes it; the union and each one's unique proofs are reported too.

## Next experiments with the climber

* Final runs with the large plain lemma sets that won today: 400 or 1,600 kNN lemmas, no rule model
  (notes/2026-11-23-plain-sizes.md).
* Climbs started from the plain sweeps' near misses.

## exp67: two climber settings, paired (started 19:02)

* **Question:** do the climber's runs gain from the large lemma sets that won in the plain sweeps?
  * In those sweeps, 400 kNN lemmas proved 35 of 235 gap goals at 5 s against 11 with 30.
  * On the heads at 60 s, 400 lemmas proved 4 of 92 and 1,600 proved 1 of 88.
* **Targets:** the 91 heads of loops/TRUSTNOW/t1854 (exp/heads.py; exp/sets/heads67), frozen.
* **Arms** (exp/exp67.sh): both are set-mode climbs (climb.py's new `--targets FILE`), from the same context:
  solved.tsv = the 48,537 trusted goals, and a copy of their production hints, so nothing writes into loops/UL.
  * CLA67: abs/clhl3.sh's setting, 6 sibling and 30 kNN lemmas;
  * CLB67: the same with 30 sibling and 400 kNN lemmas.
  * Both: 24 sketch runs of 5 s, a 160 s final run, 2 climbs at a time, rm4t, twee-pg61 with PG 0.25.
* **Smoke test:** 2 heads at 2 s sketch and 5 s final runs. Arm B's problems had 400 kNN and 30 sibling lemmas.
  No proofs.
* **Readings:**
  * real proofs per arm (final runs, no unproved assumption, also solved.tsv rows with 1);
  * CPU h per arm from climb.tsv column 6;
  * +/−, the union, and the unique proofs.
  * A target proved by the live climber or production meanwhile still counts here; the context is frozen at 18:54.
* CPU: about 8 more twees beside exp65, on the user's leave for more CPUs while climbing.

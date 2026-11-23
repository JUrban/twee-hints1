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

## Climb proofs under their own names (19:47)

* Every THM run inside a climb, sketch runs too, queued a proof rerun (loop.py's proof job, exp/proofq.py). Each one
  wrote DIR/proofs/<target> over the last. A sketch proof takes unproved goals as axioms (assume_*), so the file
  held whichever run was rerun last. A late sketch rerun could replace a final run's real proof; jobs run oldest first,
  so that is unlikely, but it can happen.
* Checked: no file in loops/UL/proofs has an assume_ axiom, and CLA67's real proof of aa1_14 533 is intact.
* Fix (twee repo d79c82e): climb.py names each run's proof <target>.<tag> (s0, s3.weak, final, ...) through loop.py's
  new proof_name. The sketch proofs are kept as data, and nothing overwrites anything. A 2-head smoke test queued
  jobs named aa1_45_c__goal_340.s0, .s1.weak, .s2.weak.
* The packer (exp/hintdata_build.py) packs climber dirs as family climbers. It takes every tagged file, and an
  untagged file only if it has no assume_ axiom.
* The live climber was restarted at 19:47 with the fix, losing 2 climbs in flight. exp67's arms keep the old naming to
  the end, so as not to disturb the pair; only their real (untagged, assume-free) files will be packed.

## The control: one long run per head (CC67)

* exp67 compares two climber settings, but neither arm says whether climbing helps. On 14 Nov the climber's apparent
  gain was its long final run, found only when the right control ran (notes/2026-11-14-sketch-climbing.md). The
  19 Nov test of the sketch hints found they caused 3 of 54 climber proofs (notes/2026-11-19-climb-ablation.md).
* **CC67** (exp/exp67c.sh): the same 91 frozen heads, the same frozen context (t1854) and arm A's lemma sets
  (6+30), one run per head with the pool hints and the rule model, no sketch runs (`climb.py --runs 0`), no fill.
  * Its length is CLA67's mean CPU per finished target when it starts, in abstract seconds (/1.07).
  * The context is frozen, so it need not run at the same time as the other arms. It starts when exp65 ends (about
    22:55), on exp65's CPUs, with 4 at a time.
* Reading: CLA67 against CC67 per head and per CPU h, +/− and union. The climbing pays only if CLA67 beats CC67 by
  more than single heads (the sets are small).

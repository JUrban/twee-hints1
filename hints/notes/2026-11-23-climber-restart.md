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

## Readings at 21:04

| climber | targets | finished | real proofs | CPU h | per CPU h | proved |
|---|---:|---:|---:|---:|---:|---|
| CLHL3 | 20 | 18 | 0 | 4.10 | 0.00 |  |
| CLA67 | 24 | 22 | 1 | 3.86 | 0.26 | aa1_14__goal_533 |
| CLB67 | 28 | 26 | 3 | 3.98 | 0.75 | aK1_to_aK2__goal_76, aK2_eq_aK3_e__goal_326, aK2_eq_aK3_h__goal_279 |

* CPU h is every run of the climbs (sketch, fill, final, direct). CLHL3's rows include its runs before the 19:47 restart.
* **CLB67 (400 kNN) leads CLA67 (30 kNN), 3 proofs to 1**, at about the same CPU. Climb by climb (climb.tsv; a
  ":weak" row is a sketch run on a weakened goal, an instance of the conjecture, --weaken 4):
  * aK2_eq_aK3_h 279 (CLB67): s0 proved it with one assumed kNN goal; s1-s8 proved weakened goals with no
    assumption; the final run, with their steps as hints, proved the target in 7.3 s.
  * aK1_to_aK2 76 (CLB67): s0-s16 failed; s17 and s21 proved weakened goals; the final proved the target in 380 s
    (wall). CLA67's climb of 76 had 18 conditional sketches in 24 runs and a failed final (643 s).
  * aK2_eq_aK3_e 326 (CLB67): s0-s2 conditional sketches (3, 3 and 1 assumptions), s3-s10 weakened goals; the final
    proved it with fill lemmas in 244 s, then 'direct' without them in 44 s (the real proof). CLA67's final failed
    (599 s).
  * aa1_14 533 (CLA67's proof, final 165 s): CLB67's climb had 4 conditional sketches in 6 runs and a failed final.
  * In three of the four, the hints came from weakened-goal proofs.
* **The plain 60 s head runs failed on all four**: HDW1 (400 kNN, 100+30 siblings) on 326, 279 and 533 (plainlive4's
  H cycle c19H did not rerun them: the same problem text, SAME rows), and c19H on 76 (154 s wall). Whether a plain
  run of the climb's length gets them is what CC67 and CC67B (below) answer.
* Merged into production (merge.py loops/UL loops/CLA67 loops/CLB67), 4 proofs: the arms' contexts are frozen at
  18:54, so the merge does not change exp67.

## trust.py read climber proofs wrong

* trust.py took a climber's record of a goal as the union of all its used.tsv rows: every sketch run's axioms,
  assume_* included. Any assume_* made the record unresolved, so no climber proof in one of the 43 exposed
  originals could be trusted. aa1_14 is exposed: its proof was untrusted.
* The real proof does not rest on the sketch runs: it takes their steps only as hints. Fix: for the climber's own real
  proofs (its solved.tsv rows of round 1), the record is the target's last used.tsv row, the run that made the real
  proof (climb.py ends a climb at an assumption-free sketch proof, else runs the final and then direct).
* The mtime rule (production's hints newer than used.tsv: the proof was replaced) now applies only to dirs whose hints
  are production's (a symlink, the live climbers). merge.py copies the hints file after the rows were written, so the
  rule dropped every merged set-mode proof.
* Old against new, same moment: 3 untrusted against 2 of 48,547; the difference is aa1_14 533. The 2 left use
  production's lemma_fill_N (climbers' fill lemmas from true.tsv), which trust.py does not resolve.

## A control for arm B (CC67B)

* CC67 matches arm A. With B ahead, B needs its own: **CC67B** (exp/exp67d.sh), like CC67 with B's lemmas
  (30 siblings, 400 kNN) at CLB67's mean CPU per finished target. Armed beside CC67; both start when exp65 ends, -j 4
  each, on the 8 workers exp65 frees.

## exp68: the live climber with arm B's lemmas and every weakening (21:07)

* CLHL3 (arm A's setting, live) stopped at 21:07 with 0 real proofs in 4.1 CPU h (2 climbs in flight lost).
* **CLHL4** (abs/clhl4.sh, loops/CLHL4, PID 3702559): clhl3's setting with arm B's lemmas (30 siblings, 400 kNN;
  a generated problem had 30 lemma_goal and 321 lemma_knn axioms, the subset filter trims the rest) and
  `--weaken 12` (every weakened goal, clhl3 took the first 4). Both from the readings above: B 3 against A 1, and the
  hints of three of the four proofs came from weakened-goal sketches.
* Two changes at once: it is the production climber, not an A/B. Read per CPU h against CLB67 (same lemmas, weaken 4,
  frozen context) and plainlive4's H runs. If it leads CLB67 on the heads both climb, a paired weaken test follows.
* Launched with CPUS=28 while exp65 runs.

## ul76: today's climbs' sketches reach production (21:14)

* Production's members by yield (exp/memberyield.py on loops/UL/r5/results.tsv, at the restart):

Last 6000 runs: 19 proofs in 33.8 CPU h (0.56 per CPU h).

| level or member | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| Vsk@1:0 | 775 | 8 | 16.1 | 0.50 |
| L1 | 82 | 1 | 2.0 | 0.50 |
| L4 | 9 | 0 | 1.5 | 0.00 |
| Vpool@1:0 | 59 | 0 | 1.3 | 0.00 |
| Vk200s12@0 | 487 | 0 | 1.0 | 0.00 |
| Vm4b@0 | 451 | 0 | 1.0 | 0.00 |
| Vkp@0 | 500 | 0 | 1.0 | 0.00 |
| Vunf@0 | 186 | 0 | 0.8 | 0.00 |
| the other 21 | 3451 | 10 | 9.2 | |
* Over ul75's whole run (22 Nov 07:13 to 23 Nov 21:14, about 58,500 runs):

Last 58500 runs: 135 proofs in 216.1 CPU h (0.62 per CPU h).

| level or member | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| L1 | 1696 | 58 | 38.3 | 1.51 |
| Vsk@1:0 | 1142 | 10 | 23.7 | 0.42 |
| Vunf@0 | 3895 | 2 | 20.1 | 0.10 |
| L0 | 4400 | 39 | 13.2 | 2.96 |
| Vk1000@0 | 3453 | 0 | 11.6 | 0.00 |
| Vk400@0 | 3647 | 1 | 8.8 | 0.11 |
| the other 33 | 40267 | 25 | 100.3 | |
* **sk@1:0** (a 40 s fresh run with the climb hints: the sketch and fill steps of the climb dirs in `--climb-hints`) made
  8 of the last 19 proofs, the most of any member. Its dirs were all from 15-20 Nov (CLH, CLHL, CLU, CLHL2, FUD2p, FUDs),
  so the sketches of today's climbs, all on the current heads, never reached it.
* **ul76** (abs/ul76.sh, exp/prod/ul76.sh): ul75 plus loops/CLHL3, CLHL4, CLA67 and CLB67 in `--climb-hints`. One change,
  6 workers. At start: 87,403 steps of 109 originals and 3,055 fill lemmas of 96 originals (ul75: 85,117 and 2,675).
  Sketch steps are hints only; the fill lemmas become axioms (lemma_fill_N). A fill run proves the step from the
  original's axioms, proven lemmas and earlier fill lemmas only (climb.py fill(): no assume_* axiom), so they are sound;
  trust.py cannot resolve the label, so a proof using one in an exposed original stays untrusted (2 now).
* Reading: sk@1:0's proofs per CPU h in ul76 against the table above, and whether its proofs fall in the originals of
  today's climbs.

## exp69: climb the assumptions (21:22)

* The conditional proofs say more than "not yet". Each target's smallest assumption set in a sketch proof
  (used.tsv, at 21:20): CLA67 25 of 27 targets with a single assumption, CLB67 21 of 24, CLHL3
  19 of 19. The single assumption is nearly always an unsolved goal of another original (assume_knn: 21, 18 and 13),
  else a later sibling or a theory axiom.
* So "head T follows from unsolved goal X in 5 s" is an edge between unsolved goals. exp/keylemmas.py collects the
  edges and ranks each X by the unsolved targets it unlocks:

| X (the assumption) | head? | unsolved targets it unlocks |
|---|---|---:|
| Kproperties_1__goal_332 | no | 4 |
| nil4_19K__goal_394 | yes | 4 |
| Ka_eq_aK3__goal_420 | no | 2 |
| Ka_eq_aK3__goal_425 | no | 2 |
| TLRproperties_2__goal_386 | no | 2 |
| aK2_eq_aK3_1243b__goal_479 | no | 2 |
| aK2_eq_aK3_1243b__goal_522 | no | 2 |
| aK2_eq_aK3_1243b__goal_525 | no | 2 |
| nil3_2K__goal_383 | yes | 2 |

* (Unlock counts against t2120's trusted goals at 21:20; the exp69 target list is the same 9.) 7 of the 9 are not
  heads, so no climber or plain head run tried them. They sit 1-9 goals behind their original's
  head (Kproperties_1 332: 1 unsolved earlier sibling, the head 326).
* **exp69** (exp/exp69.sh, loops/CLK69, PID 3709639): a set-mode climb of the 9 (exp/sets/key69) from t2120's trusted
  goals, CLHL4's setting (30 siblings, 400 kNN, `--weaken 12`), 1 climb at a time. Real proofs are merged into loops/UL
  every 10 minutes, so production and the climbers rerun the heads they unlock.
* The older climbs agree. Over every climb record with used.tsv and assume.tsv (CLA67, CLB67, CLHL2 of 19-20 Nov,
  CLHL3, CLHL4, CLK69, SMK3; unlock counts against t2120, any unsolved target, not only heads):

| X | head? | unsolved targets it unlocks | in exp69 |
|---|---|---:|---|
| Ka_eq_aK3__goal_420 | no | 13 | yes |
| Ka_eq_aK3__goal_425 | no | 12 | yes |
| aK2_eq_aK3_1243b__goal_479 | no | 11 | yes |
| Kproperties_1__goal_332 | no | 10 | yes |
| aK2_eq_aK3_1243b__goal_476 | yes | 9 | no |
| aK2_eq_aK3_1243b__goal_522 | no | 8 | yes |
| nil3_2K__goal_383 | yes | 8 | yes |
| aKperms_1__goal_368 | no | 7 | no |
| TLRproperties_2__goal_386 | no | 6 | yes |
| Ka1_eq_Ka2__goal_428 | yes | 5 | no |
| a_instances__goal_424 | no | 5 | no |
| Ka1_eq_Ka2__goal_444 | no | 4 | no |
| aK1_eq_aK3__goal_409 | no | 4 | no |
| aK2_eq_aK3_1243b__goal_491 | no | 4 | no |
| aK2_eq_aK3_1243b__goal_525 | no | 4 | yes |

  Ka_eq_aK3 420 and 425 sit right behind their head Ka_eq_aK3 419, which is itself one of nil4_19K 394's targets: a
  chain nil4_19K 394, Ka_eq_aK3 419, then 420 and 425 with 13 and 12 targets. The next batch after CLK69: the
  X in this table that are not in exp69 and not heads (aKperms_1 368, a_instances 424, Ka1_eq_Ka2 444, aK1_eq_aK3 409,
  aK2_eq_aK3_1243b 491).
* Why the finals fail (latticedata.py on CLA67, CLB67, CLHL3; realization = the share of a conditional sketch's steps,
  not axioms of the target, that the final run derived as given rules): per target, the best sketch's realization
  has median 0.74 for the 3 proved targets and 0.79 for the 62 not proved. The finals re-derive most of a sketch,
  failed or not; what they miss is the part that rests on the assumption. A better final cannot supply that: proving the
  assumption can. This is the case for exp69.
* Veroff's way with sketches: an assumption a proof needs becomes the next target. Reading: the X proved, then
  whether their targets follow (production's reruns with X as a kNN lemma, the climbers).

## Fill lemmas and trust (21:38)

* Production's member sk@1:0 adds the climbers' fill lemmas as axioms (lemma_fill_N, loop.py climb_hints: true.tsv of
  every --climb-hints dir). A fill run proves a sketch step from the original's axioms, proven lemmas and earlier
  fill lemmas, with no assumption (climb.py fill()), so the lemmas are sound; but their premises are not recorded and
  trust.py cannot resolve the label. In an exposed original such a proof stays untrusted: 3 at t2120
  (aK2_eq_aK3_s 489 and 515, nil3_23_32_to_28 572; 515 is sk@1:0's proof of 21:06).
* Re-proof without them (abs/revf.sh, one pass of rever2.py's recipe: trusted lemmas only, no climb hints, the goal's
  own proof steps as hints, 60 s; loops/REVF1): 0 of 3. These proofs need the fill lemmas.
* ul76 has more fill lemmas (3,055 against 2,675), so the count may grow. If it does, the fix is a record per fill
  lemma (a kept proof of each, so trust.py can resolve lemma_fill_N through loop.py's numbering); for 3 proofs it is
  not worth it yet. Each trust run's untrusted count goes in REPORT's summary rows.

## Not only heads (21:42)

* Production's proofs since ul75 started (22 Nov 07:13; 273 goals whose hints file was written since), by the
  unsolved earlier siblings of the goal when its solved.tsv row was written: 0 (a head): 20, 1: 19, 2: 17, 3: 22,
  4: 11, 5 or more: 184. Two thirds were deep behind an unsolved goal of their own original (later siblings, kNN
  lemmas of other originals and the sketches' hints get there without the earlier steps).
* Who proved the 184 deep ones: production's own runs 84 (L1 35, L0 26, sk@1:0 8, the other members 15), side loops
  100: the plain sweeps 43 (cond import dirs CI1 19, CI3 14, CI2 and CI2+CI3 9, CI3+PLR1 1), the given-rule retries 23
  (GMR, GMR2, GMR3, GML), and 34 with no round-1 row in any side dir's solved.tsv (likely the transfer loop XFL,
  not checked).
* So the heads are not the only frontier, and a head-only restriction of production's members would be wrong. The
  climbers climb heads (CLHL4 `--heads-only`) and exp69 the goals the heads' sketches assume. Without `--heads-only` and
  `--reclimb-heads`, climb.py --live climbs any stalled goal (a failed fresh run in the latest round), fewest proof
  lines from a proven goal below first: the mode for the deep goals, last used by clu4.sh (16 Nov, loops/CLU).

## exp69 ended: 0 of 9 (23:05)

| climber | targets | finished | real proofs | CPU h | per CPU h | proved |
|---|---:|---:|---:|---:|---:|---|
| CLK69 | 9 | 9 | 0 | 1.51 | 0.00 |  |

| key goal | fill runs | gaps tried | gaps proved | final CPU s |
|---|---:|---:|---:|---:|
| Ka_eq_aK3__goal_420 | 5 | 7 | 2 | 384 |
| Ka_eq_aK3__goal_425 | 7 | 25 | 9 | 498 |
| Kproperties_1__goal_332 | 3 | 8 | 1 | 439 |
| TLRproperties_2__goal_386 | 13 | 68 | 32 | 386 |
| aK2_eq_aK3_1243b__goal_479 | 7 | 25 | 11 | 475 |
| aK2_eq_aK3_1243b__goal_522 | 5 | 11 | 1 | 533 |
| aK2_eq_aK3_1243b__goal_525 | 9 | 13 | 7 | 494 |
| nil3_2K__goal_383 | 3 | 13 | 12 | 707 |
| nil4_19K__goal_394 | 7 | 49 | 18 | 711 |

Gaps proved 93 of 219 tried. The proofs (used.tsv rows) by their assumptions: 0 assumptions 44, 1 assumptions 73, 2 assumptions 19, 3 assumptions 7, 4 assumptions 3, 5 assumptions 2: the 44 without one proved weakened goals (instances; a run on the goal itself without an assumption would be a real proof).
The key goals' own single-assumption sketches assume other unsolved goals of the same cluster (exp/keylemmas.py CLK69):

* Ka_eq_aK3__goal_420 follows from TLRproperties_2__goal_369
* Ka_eq_aK3__goal_425 follows from TLRproperties_2__goal_376
* nil3_2K__goal_383 follows from aK2_eq_aK3_1243b__goal_479
* TLRproperties_2__goal_386 follows from aK2_eq_aK3_1243b__goal_522
* Kproperties_1__goal_332 follows from aKperms_1__goal_365
* aK2_eq_aK3_1243b__goal_525 follows from aKperms_1__goal_387
* aK2_eq_aK3_1243b__goal_522 follows from nil4_19K__goal_426

So the 9 and their assumptions are one cluster of goals of 7 originals (Ka_eq_aK3, Kproperties_1, TLRproperties_2,
aK2_eq_aK3_1243b, aKperms_1, nil3_2K, nil4_19K): each follows from another unsolved one in a 5 s sketch, and none
was proved without one. Veroff's way through such a cluster is the gaps: the sketch steps that depend on the
assumption, proved on their own until a final run needs no assumption. CLK69's fills, 3 s each, proved 93 of 219.

## exp70: a second round on the key goals, with longer gap filling (23:05)

Question: does gap filling 10 times longer (30 s per fill run instead of 3 s) get a key goal of the cluster proved
in a second round? A control arm repeats CLK69's setting from the same state.

* abs/exp70.sh (exp/exp70.sh), launched with TRUSTED=loops/TRUSTNOW/t2300.trusted (48,549 trusted). Targets
  loops/EXP69.targets (exp/sets/key69, the same 9).
* Both arms start from CLK69's sketches/ and fillhints/ (805 sketch hints of 6 originals, reloaded as hints),
  a fresh copy of the trusted solved set and production's hints, CLHL4's setting (30 siblings, 400 kNN, --weaken
  12, 24 sketch runs of 5 s, final 160 s), --true-max 200, -j 1 each:
  * K70F: `--fill 30` (at most 300 CPU s per fill run);
  * K70R: `--fill 3`, CLK69's.
* CLK69's true.tsv is not copied: its fill lemmas have no premise record (below), so each arm proves its own.
* Real proofs are merged into loops/UL every 10 minutes (loops/EXP70.merge).
* Reading: exp/climbread.py K70F K70R CLK69, real proofs and CPU h; gaps tried and proved per arm (fill.tsv).

### Fill lemmas get a premise record

climb.py now writes fillprem.tsv: for each lemma a fill run proved, the original, the true label, the formula, the
target, the tag, and the lemma names the run's proofs used (twee's USEDAXIOMS line; all the run's proved gaps
together, so a superset of each lemma's). Without that line, every lemma name in the fill problem. Before, no
fill premise was recorded: the 6 untrusted goals at t2300 (aK2_eq_aK3_s 489, 494, 515, nil3_23_32_to_27 549,
nil3_23_32_to_28 572, nil3_23_32_to_30 549) are production sk@1 proofs with lemma_fill_N axioms, every one from
CLHL2's true.tsv, or proofs that use those goals. Climbers started before the change (CLHL4, CLA67, CLB67, CC67,
CC67B) still write none; exp70's arms do.

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

### trust.py checks fill lemmas (23:17)

* trust.py: each fill lemma is a node FILL:<dir>:<original>:<true label>, trusted when every premise of its
  fillprem.tsv row is (true_k: the same dir's fill lemma k). A formula is trusted when any fill lemma with it is.
  A climber's real proof that names true_k gets a record through its dir's fill nodes. A production goal in an
  exposed original without a complete record gets one from its printed proof (loops/UL/proofs/<goal>): that proof's
  axiom list, lemma_fill_N matched by formula (loop.py renumbers the fill lemmas at each refresh).
* exp/fillcheck.py re-proves the fill lemmas behind the untrusted roots with their premises recorded: the formula as
  the conjecture, the original's axioms and all its trusted goals as lemma axioms, the goal's hints, 60 abstract s.
  On t2300's roots: 20 of 22 proved (aK2_eq_aK3_s 4, nil3_23_32_to_27 13, nil3_23_32_to_28 3), the
  proved ones in 1.1-2.7 s; not proved: aK2_eq_aK3_s `m(X, k(X2, X3)) = rd(X, k(X3, X2))`; aK2_eq_aK3_s `m(rd(e, X), k(m(Yc1, Yc2), Yc0)) = rd(e, ld(k(m(Yc1, Yc2), Yc0), X))`.
* loops/TRUSTNOW/t2314: 48558 solved: 43497 before T0, 5058 later with trusted records; 3 untrusted (0 without a record, 2 with an unresolved lemma name, 1 using an untrusted or unsolved lemma); 34 fill lemmas trusted
* Untrusted: aK2_eq_aK3_s__goal_489, aK2_eq_aK3_s__goal_494, aK2_eq_aK3_s__goal_515 (two fill lemmas of aK2_eq_aK3_s not re-proved at 60 s; 494 uses 515).

## The controls, corrected (23:29)

CC67 and CC67B (22:56) got the arm's CPU per finished head divided by 1.07, exp65's CPU per abstract second, as an
abstract budget (564 and 525 s). On these heads the ratio is far higher: the arms' failed 160 s finals ran at a
median 3.45 (CLA67) and 3.17 (CLB67) CPU s per abstract s, the controls' long runs at
about 2.3-2.5 (the start-up with 400 lemmas and the hints is spread over a longer run). So each head got about 2.3
times the arm's CPU, and the 91 heads would have taken until the evening of 24 Nov. Their rows before the stop:

| dir | goal | result | CPU s |
|---|---|---|---:|
| CC67.v1 | aa1_14__goal_533 | THM | 94 |
| CC67.v1 | aa3_12__goal_487 | THM | 1313 |
| CC67B.v1 | aa1_14__goal_533 | THM | 547 |
| CC67B.v1 | aa2_12__goal_355 | NO | 1409 |

Stopped at 23:27 (kept as loops/CC67.v1, CC67B.v1). climb.py has a new option `--final-cpu S`: the final run's CPU
cap (twee --max-cpu) in place of 10 x --final-time. The corrected controls (abs/exp67e.sh, exp/exp67e.sh; 23:28) run
each head once with `--final-time 3000 --final-cpu C`, C the arm's CPU per finished head at launch: CC67C (arm A's
lemmas) 608 s, CC67D (arm B's) 552 s; -j 4 each, about 4 hours. Reading: exp/ccpair.py CLA67 CC67C and CLB67 CC67D.

## exp71: the live climber on stalled goals again, and ul77 (23:29)

**Why.** Production's sk members take every climb dir's sketch and fill steps of the goal's original as hints (sk@1:0:
40 s fresh runs). Of the sk proofs in production's last 8,000 runs (10, 23 Nov 17:19-22:35), every one was in an
original with CLU's sketches (26-293 sketch files each; CLU: 16 Nov, the live climber on stalled goals) and with
CLHL2's; today's head climbers had 2-18 files for some of them. CLU's own record (exp/climbread.py): 986 targets, 22
real proofs in 27.9 CPU h (0.79 per CPU h), 7,302 sketch files over 108 originals. The head climbers today: CLHL3 0 in
4.1 CPU h, CLHL4 0 in 3.5, CLA67 2 and CLB67 4 in 7.5 each; sketches for 14-15 originals each.

And most of the unsolved are holes: of 3,229 unsolved goals (t2314), 2,700 have a later goal of the same original
proved (529 are in an original's unsolved suffix). A head proof seldom unlocks later goals: of exp67's five proved
heads, the next goals after aK1_to_aK2 76, aK2_eq_aK3_h 279 and aK2_eq_aK3_e 326 were already proved (one of
326's was proved after it), gbol_to_aK1 460 is its original's last goal, and aa1_14 533 had 2 unsolved after it. Stalled mode climbs
the holes too, nearest to a proved goal first.

* abs/cls71.sh (exp/prod/side/cls71.sh), loops/CLS71, climb.py PID 3750581 (bash 3750577), since 23 Nov 23:22.
  CLU's climb (20 sketch runs of 5 s, final 20 s, --weaken 4, fill 3 s) with twee-pg61, rm4t, and arm B's lemmas
  (30 siblings, 400 kNN); no move-model or theory-ts arms. -j 6 while fewer than 30 other twee processes run (that
  cap counts the others, not the total: it started 5 climbs at once, 32 twee processes in all; about 21 once exp67
  ends).
* abs/ul77.sh (exp/prod/ul77.sh): ul76 plus loops/CLS71, CLK69, K70F, K70R in --climb-hints, rescanned every 10
  minutes. loop.py PID 3751009 since 23:24 (ul76 stopped at 23:23).
* Reading: CLS71's real proofs per CPU h (exp/climbread.py CLS71); production's sk proofs in originals CLS71 climbed
  after its sketches, against ul76's sk rate (2 proofs in 7.0 CPU h of sk@1:0 in its 1,800 runs; exp/memberyield.py).

**A check that came to nothing:** is a hole's equation a step of a proved sibling's proof (its hints file)? 0 of
2,657 holes with a unit-equation form. (The key is rough: a sample of solved goals finds its own equation in its own
hints file 105 times in 283; the conjecture's unitized form and twee's proved form differ, e.g. a variable set to
e. Even so, the holes are not hiding in the siblings' proofs.)

### CLHL4 stopped (23:31)

CLHL4 (exp68, the live head climber with arm B's lemmas and --weaken 12) stopped at 23:30: 21 heads finished, 0 real
proofs in 4.7 CPU h. Its targets were the current heads, the same ones exp67's arms (CLA67 2, CLB67 4 real proofs in 7.5
CPU h each) and controls were climbing at the time, so it mostly repeated them. Heads are covered by exp67 until about
03:00 and by the plain live loop's H setting (60 s plain runs on the heads; HDW1: 4 of 92 at 1.78 per CPU h); CLS71
takes its CPU. Whether a head climber comes back depends on the controls (CC67C, CC67D).

## exp67 at 23:41: arm B ahead

| | CLA67 | CLB67 |
|---|---:|---:|
| targets both finished | 54 | 54 |
| proved | 2 | 7 |
| only this arm | 1 | 6 |
| CPU h on these targets | 9.05 | 8.22 |
| proofs per CPU h | 0.22 | 0.85 |

Union 8, both 1. Only CLA67: aa1_14__goal_533. Only CLB67: aK1_to_aK2__goal_76, aK2_eq_aK3_e__goal_326, aK2_eq_aK3_h__goal_279, mbol_com__goal_71, mbol_lem1__goal_391, mbol_to_nil3__goal_623.

On the heads both arms finished, arm B (30 siblings, 400 kNN lemmas) proved 6 that arm A (6 siblings, 30 kNN) did
not, and A 1 that B did not, at about the same CPU. The arms differ only in the lemma lists. With 7 discordant heads
the sign test gives p = 0.0625 one-sided (0.125 two-sided): suggestive, not settled; the plain head runs (400 kNN)
point the same way. exp73 builds on it as a production member, measured there by its own yield. CLB67's proofs of
23:00-23:08 (mbol_lem1 391, mbol_com 71, mbol_to_nil3 623) reached production at 23:40; exp/exp67merge.sh now merges
the arms and the controls every 10 minutes until they end.

## exp70 early, and exp74: long plain runs on the cluster's heads (23:49)

exp70 so far: gaps proved per gap tried, K70F (30 s fills) 21 of 54 (39%), K70R (3 s) 29 of 73 (40%), CLK69 (3 s) 93
of 219 (42%). Ten times the fill time proves no larger share: these gaps depend on the assumption, as the key goals do.

The cluster's way in is each of its 7 originals' first unsolved goal, all earlier goals proved
(sets/clusterheads74, exp/sets/clusterheads74):

| head | unsolved goals in its original | production runs | longest single run, s |
|---|---:|---:|---:|
| Ka_eq_aK3 419 | 32 | 128 | 60 |
| Kproperties_1 326 | 3 | 56 | 77 |
| TLRproperties_2 367 | 10 | 70 | 124 |
| aK2_eq_aK3_1243b 476 | 77 | 119 | 96 |
| aKperms_1 355 | 11 | 66 | 88 |
| nil3_2K 383 | 13 | 70 | 100 |
| nil4_19K 394 | 20 | 86 | 141 |

(production's results.tsv rows, round 5; a resumed run's row is its increment, and the cascade stops at 320 abstract
s.) exp74 (abs/exp74.sh, exp/exp74.sh, bash 3758318, 23:49): one plain run of 1200 abstract s per head, H's lemma
lists (100+30 siblings, 400 kNN), 2 threads, through condprove.py into cond/LCH74; proofs to loops/CI3 and loops/UL.
A problem (aK2_eq_aK3_1243b 476) has 129 lemma_goal and 400 lemma_knn axioms.

**exp74 rerun (00:20, 24 Nov).** The first run's 6 finished goals were all TIMEOUT at 600 s wall: condprove.py capped
every run at a flat 600 s, well short of 1200 abstract s on this machine. No other sweep had a TIMEOUT row (every
cond/*/results.tsv checked). condprove.py now caps at 10 x --time (at least 600 s); the first run is kept as
cond/LCH74.v1, the rerun (bash 3765398) writes cond/LCH74.

## exp70 ended (24 Nov 01:14): 0 of 9 in both arms (01:17)

| arm | key goals proved | CPU h | fill runs | gaps tried | gaps proved | fill CPU s |
|---|---:|---:|---:|---:|---:|---:|
| K70F | 0 of 9 | 1.55 | 57 | 211 | 92 (44%) | 2254 |
| K70R | 0 of 9 | 1.54 | 57 | 213 | 85 (40%) | 314 |
| CLK69 | 0 of 9 | 1.51 | 59 | 219 | 93 (42%) | 307 |

Ten times the fill time (K70F) proved 44% of its gaps against K70R's 40%, at 7 times the fill CPU, and neither arm
proved a key goal: the second Veroff round from CLK69's sketches added nothing. The key goals' gaps are not short of
time; their sketches rest on assumptions that do not follow. Closed. No climber returns to these 9; exp74 tries the
cluster's heads with long plain runs instead.

## exp67, arm B against its control: climbing adds nothing (24 Nov, 02:55)

CLB67 ended at 02:35 (8 of 91 heads), its control CC67D at 02:54 (9 of 91). exp/ccpair.py on the 91 heads both
finished:

| | CLB67 (climber: sketches, fills, 160 s finals) | CC67D (one run per head, the climber's CPU per head) |
|---|---:|---:|
| heads proved | 8 | 9 |
| only this one | 0 | 1 (mbol_to_aaxx 377) |
| CPU h | 14.90 | 13.58 |

Both have the same lemma lists (30 siblings, 400 kNN), production's hints, rule model and PG; the control has no
sketches, fill lemmas or climb hints, and each run is capped at 552 CPU s (climb.py --final-cpu: CLB67's CPU per
finished head at launch). Every head the climber proved, one long run with the same lemmas proved too, at about the
same CPU. On these heads the long lemma lists made arm B's lead over arm A (7 against 2 at 23:41), not the climbing.
Arm A's pair (CLA67, CC67C) is still running. What follows for the stalled goals is long runs with long lemma lists
(exp74, HLW1); exp76 asks the same of CLS71's climbs.

## exp79: CC67D's run as a production member (ul81, 03:03)

CC67D's run (one fresh run with 30 siblings and 400 kNN, production's hints, model and PG, 552 CPU s cap) proved 9
of 91 heads at 0.66 per CPU h; production's last 6,000 runs made 0.48 per CPU h (exp/memberyield.py 6000 at 02:56),
and ul80 ran dry (550 runs, 0 proofs; at times 1 of 6 workers busy). Production's runs with 400 kNN were 5 s (k400@0)
or 80 s (k400 after level 3) with 6 siblings, and skk400s30@1:0 (40 s) had 51 runs and 0 proofs.

* **ul81** (abs/ul81.sh, exp/prod/ul81.sh): ul80 plus member k400s30@3:0, a fresh run at level 3's budget (160
  abstract s) right after L0. loop.py PID 3804373 since 02:56 (ul80 stopped 02:56: 550 runs, 0 new).
* Checked: its first run (com_Ralt 254, 160 s, 309 s wall) is labelled Vk400s30@3:0; recent problems have 400
  lemma_knn, 30 lemma_goal and no lemma_fill axioms.
* Reading: exp/memberyield.py, its proofs per CPU h against the other members, and the goals only it proved.

## exp67's controls ended (24 Nov 03:23): arm A agrees (03:24)

CC67C (arm A's lemma lists, 6 siblings and 30 kNN, one run per head at CLA67's CPU per head) ended at 03:23 with 5 of
91 heads. exp/ccpair.py:

| pair | heads both finished | proved | +/− | union | CPU h |
|---|---:|---|---|---:|---|
| CLA67 (climber) vs CC67C (control) | 88 | 2 / 5 | +0 −3 | 5 | 15.85 / 14.80 |
| CLB67 (climber) vs CC67D (control) | 91 | 8 / 9 | +0 −1 | 9 | 14.90 / 13.58 |
| CC67C (6+30) vs CC67D (30+400) | 91 | 5 / 9 | +2 −6 | 11 | 15.32 / 13.58 |

* In both arms every head the climber proved, its control proved too: climbing (sketches with assumptions, fills,
  climb hints in 160 s finals) added nothing beyond one run of the same CPU with the same lemmas.
* The lemma lists matter: 30+400 beats 6+30 by +6 −2 at less CPU, and the two are complementary (union 11: CC67C's
  aa1_14 533 and mbol_aa1sqrd_to_aa1 559 only with the short lists).
* CLA67 has its last heads running; exp76, exp77 and HLW1 start when it ends.

**exp67 ended at 03:46** (CLA67's last heads; every dir finished all 91). Final, exp/ccpair.py on all 91:

| pair | proved | +/− | union | CPU h |
|---|---|---|---:|---|
| CLA67 vs CLB67 (the arms) | 2 / 8 | +1 −7 | 9 | 16.91 / 14.90 |
| CLA67 vs CC67C | 2 / 5 | +0 −3 | 5 | 16.91 / 15.32 |
| CLB67 vs CC67D | 8 / 9 | +0 −1 | 9 | 14.90 / 13.58 |
| CC67C vs CC67D | 5 / 9 | +2 −6 | 11 | 15.32 / 13.58 |

All four together proved 11 of the 91 heads, every one also proved by a control. Closed. Then (03:47) exp76 and the
HLW1 sweep started, and exp77 at 03:24 after the controls (03:48).

**exp74 ended (24 Nov 04:34, cond/LCH74.status): 1 of 7 proved, 6.77 CPU h (wall s summed).** The one proof is TLRproperties_2 367 (2,033 s), which
CLB67 and CC67D had proved meanwhile, so it adds nothing; condimport.py's rerun of it hit its wall cap, which loses
nothing either. The 6 others failed at 1,200 abstract s (2,909-4,393 wall s each). One long plain run on the key
cluster's first heads gives nothing new: closed.

**exp71 with 160 s finals (24 Nov 06:05).** After exp76 (notes/2026-11-24-cond-replay.md: 160 s finals proved 2 of 30
targets whose 20 s finals had failed, +1 −0 for the climb hints), CLS71 restarted as abs/cls71b.sh
(exp/prod/side/cls71b.sh): the same record dir, lemma lists, cap (CPUS=20) and climb, `--final-time 160`.
Reading: real proofs per CPU h from 06:05 on (exp/climbread.py CLS71 on the climbs started after the restart),
against the 20 s finals' 1 in 23 Nov 23:33-24 Nov 06:05.

**First reading with 160 s finals (24 Nov 07:33).** After the 06:05 restart, 54 targets finished, 5 proved (aK1_eq_aK3 457
and 460, aK2_eq_aK3_o 522, aK2rev 450, aa1_14 538), 7.36 CPU h (climb.tsv seconds of those targets), **0.68 per CPU h**.
Before it, with 20 s finals: 3 real proofs in about 35 CPU h (climbread.py CLS71: 8 in 42.63 CPU h in all). The targets
differ (each is climbed once, in order), so this is not an A/B; exp76 was one (the same 30 targets: 160 s finals 2 with
the climb hints, 1 without, 20 s finals 0). The climber is now the best use of CPU per proof: HLW1 0.63 and falling,
production ul82 0 in 2,501 runs (9.4 CPU h). Production goes to 2 workers so the climber (cap: fewer than 20 other
twee processes) gets their threads.

**Re-climbs (24 Nov 07:37).** CLS71's live targets are new stalled goals only, and with production on 2 workers (ul83)
few come. climb.py `--reclimb FILE` (21a6d73): the listed goals may be climbed again while they have fewer than 2
finals, after the new targets, nearest proven goal below first, with the r1 tag prefix (as --reclimb-heads). The list
sets/cls71re (exp/sets/cls71re): 841 unsolved targets whose 20 s final failed (exp76's 30 left out) and 17 climbs cut off
by the two restarts (rows in climb.tsv, no final). A full re-climb costs about what a bare 160 s re-final does (the
sketches are about 150 of 600 CPU s) and makes its sketches in today's context. abs/cls71c.sh (exp/prod/side/cls71c.sh),
PID 3864270. The 20 s-final climber also proved mbol_to_nil3 636 just before the stop (6 since 06:05).
Reading: real proofs per CPU h of the r1 climbs (their climb.tsv rows have the r1 prefix) against the new targets'.

**Reading at 24 Nov 08:47** (CLS71.log split at its "reloaded" lines; CPU = climb.tsv seconds of the targets finished in
each part; every proof is in loops/UL):

| climber | targets finished | proved | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| 20 s finals (23 Nov 23:33 - 24 Nov 06:05) | 878 | 3 | 34.66 | 0.09 |
| 160 s finals (06:05-07:37) | 57 | 6 | 7.63 | 0.79 |
| 160 s finals with --reclimb (07:37 on), new targets | 50 | 7 | 5.81 | 1.20 |
| the same, re-climbs | 0 | 0 | 0 | – |

New stalled goals still come (50 in 70 minutes), so no re-climb has run yet. HLW1 (plain 60 s sweep) for comparison:
20 proofs in 22.3 CPU h (0.90). **What is not known:** how much of this is the climb and how much the long final with
30+400 lemmas. exp76 gave the climb hints +1 −0 at equal 160 s finals (30 targets); exp67 found the climbing added
nothing beyond CPU-matched long runs. A climb costs about 600 CPU s, a bare final about 450. Next: an online A/B in the
live climber (alternate targets by crc32: full climb or final only), with `--conditional-encoding fresh`, at its next
restart.

**Final-only A/B (24 Nov 08:59).** climb.py `--final-only-ab` (8f54292): targets with bit 2 of crc32 of their name set
get no sketch runs, only the 160 s final (with the climb hints their original has, their siblings' climbs included);
the others the full climb. By target, not by original: 391 of the 864 re-climb targets and 1,540 of the 3,159 unsolved
goals are final-only. The question is what a target's own climb adds to its final, at about 150 of a climb's 600 CPU
s. abs/cls71d.sh (exp/prod/side/cls71d.sh), PID 3878982, also with twee `--conditional-encoding fresh` (Horn assumptions
cost 8x under the default encoding, exp82; no change without them) and -j 8 (HLW1 ended). Its first runs: five 160 s
finals, all final-only targets, and three 5 s sketch runs, all climbing ones. 6 climbs cut off by the restart went onto
sets/cls71re (864). Reading: real proofs per CPU h by arm (crc32 of the target), new targets and re-climbs apart; a
final-only rate at or above the climbing one means long finals without climbs.

**A/B reading at 24 Nov 10:18** (exp/climbab.py, the instance from 08:59): new climb: 50 finished, 15 proved, 5.15 CPU h, 2.91 per CPU h; new final-only: 54 finished, 18 proved, 4.85 CPU h, 3.71 per CPU h.
33 proofs in 79 minutes, all in loops/UL, mostly in tails: aK2_eq_aK3_gen 6, nil3_23_32_to_26 5, nil3_27 4,
nil3_23_32_to_30 3, nil3_23_32_to_28 3, aK2_eq_aK3_b 3. With --chain a proof becomes a sibling lemma (and hints) of the
original's later targets at once, so a tail falls in runs. No re-climb has started yet (new stalled goals keep coming).
So far the final-only targets do as well as the climbed ones per CPU h.

**Restart with -j 10 (24 Nov 13:00).** abs/cls71e.sh (exp/prod/side/cls71e.sh), PID 3926911: cls71d.sh with -j 10, after
exp82c's end freed two threads (the 20-process cap still holds). 6 cut-off climbs went onto sets/cls71re (870). A/B from
08:59 to 13:00 (exp/climbab.py --from 1047, the new targets; no re-climb started): climb: 37 of 144, 17.13 CPU h, 2.16 per CPU h; final-only: 44 of 149, 13.91 CPU h, 3.16 per CPU h.
The final-only targets stay ahead per CPU h (3.2 against 2.2) and in count. Read across restarts with --from 1047.

**What the final-only arm is (24 Nov 13:28).** Every final since 08:59 had sketch hints from the original's climbs
(loops/CLS71/realized/<t> headers, `sketch_hints=`): the 163 final-only finals a median 679 (45 proved), the 154
climbing ones a median 727 (37 proved); no final had none. So the A/B measures a target's **own** climb on top of its
siblings' sketch hints, not finals without climbs. The question of the sketch hints themselves was exp36's
([notes/2026-11-19-climb-ablation.md](2026-11-19-climb-ablation.md), loops/CA1): the same final with and without the
sketch steps, context as of the proof. Split by budget from loops/CA1/results.tsv: at 20 s 12 both, 7 neither,
3 sketch only, 0 pool only; **at 160 s 24 both, 9 neither, 0 sketch only, 0 pool only.** Together: at today's 160 s
finals neither the target's own climb nor the original's sketch steps add proofs; the climber's yield is the 160 s
final with production's pool and lemmas, on goals its stalled() order picks (nearest a proved goal first), chained.
By the rule set at 08:59 the final-only rate (2.95 against 2.17 at 13:18) points to finals without climbs. The A/B
keeps running for more targets; turning the climbs off is the user's call (climbing is the method asked for).

**User, 24 Nov 13:43:** "keep the climbs for now, let the A/B run". cls71e.sh stays as it is (climbs on the crc32
bit-2-clear targets, final-only on the others); the reading goes on with exp/climbab.py --from 1047.

## The untrusted aK2_eq_aK3_s roots re-proved (24 Nov 17:03)

trust.py's run at 16:52 (loops/TRUSTNOW/t1652) left 21 untrusted, all aK2_eq_aK3_s: the roots 489 and 515 (untrusted
since 23 Nov, see "trust.py checks fill lemmas") and 19 goals resting on them, 17 of them proved since 11:18 (the
climbers' chains in that original). The loop in the records: 515's printed proof uses the fill lemma
`m(X, k(X2, X3)) = rd(X, k(X3, X2))` (CLHL2's true_4 of 20 Nov, no premise record); the only premise record of that
formula is CLS71's true_40, proved from lemma_goal_494; 494's proof uses lemma_goal_515. fillcheck.py had failed on
the formula at 60 s and on a retry (770 s).
REVF2 (abs/revf2.sh = revf.sh with TIME, LEM, KNN settable; exp/revf2.sh; roots exp/sets/revf2.roots): the context
production's solved rows that t1652 trusts (so none of the 21), production's hints, 30 siblings and 400 kNN, 160 s,
-j 3. All three proved: 515 in 1.86 s, 494 in 2.36 s, 489 in 10.36 s (loops/REVF2/transfer.tsv, kept outputs in
r1/out). trust.py at 17:03 (t1703): 49,325 solved, **0 untrusted**, holdout 5,540. revf.sh's 6 siblings and 30 kNN
at 60 s had failed on 489 and 515 (REVF1, 23 Nov); the long lemma lists were enough.

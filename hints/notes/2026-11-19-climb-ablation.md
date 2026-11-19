# Do the climbs' sketch hints help the climber's own proofs? (exp36)

Started 19 Nov 2026, 17:46 UTC. User, 17:20: "are you saying the hints from the climbs never help outside the climbs?
that sounds strange - presumably they helped inside the climb (that's why we did the climb, right)?"

## What was known

* Every test of sketch steps as hints gave the target a plain run with them: 2g (28 against 28), chained sketches
  (29 against 28), exp4 (0 of 20, also at a tenfold boost). All of them ran outside a climb.
* **No climber proof was ever ablated.** climb.py's `direct` run is no control. It comes after a successful final
  run, by which point that run's own proof steps are already among the sketch hints (exp32: 1,573 hints in
  nslm_to_aa1 845's direct run, against 51 in its final). exp32's notes and REPORT 2az had called it a plain 160 s
  run; that is corrected there.
* Offline, at 17:30, over 55 climber proofs from the climbs that saved their sketches (CLH, CLHL, CLU, CLHL2, FUD2p,
  FUDs):
  * of 12,999 final-proof steps, 8,499 (65%) were in the pool of the time (the original's goals proven before);
  * 2,808 (22%) appear in a sketch saved before the proof, mostly also in the pool;
  * only 218 (1.7%) were in a sketch and not in the pool, in 15 proofs with 5 or more (up to 49).
  * A step that is a hint and ends up in the proof was boosted 100× when it came. But that does not show it was
    needed.

## Set and setting

* exp/climbablate.py, abs/climbablate.sh, loops/CA1. The 55 proofs in production's row order. Each target's two
  arms run at once, at its directory's final time (CLU 20 s, the others 160 s):
  * **P:** the pool only;
  * **S:** the sketch steps saved before the proof that are not in the pool, first, then the pool (climb.py's order).
* **Context, as of the proof:** production's solved rows before the target's row (loops/UL/solved.tsv is
  append-only) give the pool and the sibling lemmas. kNN lemmas come from the 44,071 goals before the earliest
  target's row. Rule model rm4t, 6 sibling and 30 kNN lemmas (abs/clhl2.sh's options).
* **Not reproduced:** the fill lemmas (never saved before today), the climb's assumptions, and the binary of the time
  (e39). Both arms run today's twee-pg61 with PG 0.25. Proofs that today's binary finds without any climb therefore
  show up as P = S = THM.
* **CPU:** production on 15 workers (ul69 restarted at 17:46, rows from 163,799; the earlier ul69 log is
  loops/UL69a.log). Then exp36's 2 + exp33/exp35's 2 + the climber's 2.
* **Smoke test** (loops/CA0, the first CLU target): both arms proved it in 2.9 s, so today's binary does not need
  the climb for that goal. The first try failed at once: loop.py writes rule-model goal files only for unsolved
  goals, so the script now writes them for the targets.

## Measures

* Paired over the targets: P proves, S proves, and the one-arm goals in each direction.
* If S proves clearly more (say 5+ one-arm goals for S, few for P), the sketch hints are a cause of climber proofs.
  Then they should go into production (a variant with the original's sketch steps) and into the lattice labels
  (credit by ablation).
* If P ≈ S, the climber's proofs come from elsewhere: the long final budget, the fill lemmas, or binary changes.

## Results

Ended about 20:05. 54 of the 55 targets have both arms (CPU: P 2.12 h, S 2.12 h).

| | targets |
|---|---:|
| both arms prove | 35 |
| neither | 16 |
| S only (sketch steps first) | 3: aip_to_aK1 185, mbol_nil3_a 494, ns_to_aa1_b 610, all CLU at 20 s |
| P only (pool) | 0 |

* On the 35 shared proofs, S takes the same time as P (median ratio 0.97).
* **The sketch hints are a cause of 3 of the 54 climber proofs (+3 −0).** That is fewer than the decision's 5, but
  all in one direction.
* **35 of the 54 need no climb today.** Today's binary (PG 0.25) and the production context of the time prove them
  from the pool alone. When the climber found them, the binary was older (e39) and had no PG.
* **16 are not reproduced by either arm.** They need what the arms lack: the fill lemmas (not saved before today),
  the climb's assumptions, or the old binary's search.
* Reading: inside the climb, the sketch steps help a little, as the user expected. The sk member carries them
  to production, and since 18:25 the fill lemmas too. It had 0 proofs in its first 2.7 CPU h, before the fill
  lemmas, and is re-explored periodically.

* **Interim (18:09, 26 of 55 targets):** both arms 16, neither 7, S only 3 (ns_to_aa1_b 610, aip_to_aK1 185,
  mbol_nil3_a 494, all CLU at 20 s), P only 0.

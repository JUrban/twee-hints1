# Sketch climbing, gap filling, and the control that undid it

*Reconstructed on 17 Nov from REPORT 2ab (14 Nov evening – 15 Nov 03:30). Abstract time.*

**Question.** The user, 14 Nov: make a hard goal easy with extra assumptions, then climb the lattice of
assumption sets down to the empty set, with hints from every solved sketch guiding the next. Later: "frequent
extra axioms like commutativity". Does this reach stalled goals that fresh or resumed runs do not?

**Setup.**
* **climb.py** (1e46a74), on loop.py's production context:
  * The candidate assumptions are the M nearest unproven siblings by proof line, either side. They are lines
    of the same Prover9 proof, so true.
  * A sketch run is the target with assumption set S as axioms. USEDAXIOMS gives the used set U. The proof's
    steps become sketch hints of the original, placed before the pool hints. The sets U − {u} are queued
    next, smallest first.
  * The climb ends with a real proof (one that uses no assumption), or with a real run with all the sketch
    hints. A failing full set gets double the time, capped at 4× after b_364 reached 547 s.
* **`--laws`:** Veroff-style laws over the signature, possibly false: commutativity of each binary operation,
  associativity of each one no axiom defines, each defined operation equal to a constant or its first
  argument. A law with which twee proves X = Y in 2 s is dropped (6 of 18 for AIM). `--freq K` adds the K most
  frequent equations of the original's unconditional proofs, which are true.
* **`--fill S`** (gap filling, Veroff 2001, b506481):
  * twee-e37 lists the lemmas that depend on `assume_*` axioms (HINTS-ASSUMED);
  * after each sketch proof one `--multi-goal` run of S s tries to prove them without the assumptions;
  * the proven ones become axioms `true_i` for later runs on the original's goals.
* **`--knn K`:** true assumptions from the K most similar unproven goals of other originals with subset axioms.
* **Sets:**
  * sg1: 32 gap-1 goals that failed L1 in round 5 (2026-11-14-line-gaps-stalled.md);
  * sg3: 64 goals that failed L1, snapshot loops/ULsK (41,996 proofs).
* **Live:** `climb.py --live loops/UL` (abs/clive.sh) on UL's failed-L1 goals, from 15 Nov 00:43, writing
  real proofs into UL; UL11 (abs/ul11.sh) runs only L0 and L1 with `--sync 60`.
* **Control FV:** the live climber's first 102 targets rerun fresh at 20 s from loops/ULsL, a UL snapshot
  without the climber's proofs.

**Results.**

sg1 (up to 12 sketch runs of 5 s, then 20 s real; CPU = sum of run times, fills included):

| arm | solved | CPU s | proofs per CPU-hour |
|---|---:|---:|---:|
| fresh 20 s (S20) | 4 | ~1,000 | 14 |
| fresh 80 s (SD, stopped at 23 goals) | 7 | 3,158 | 8.0 |
| fresh 80 s, ordering 1 (SO) | 8 | 5,898 | 4.9 |
| CL2: siblings + laws + freq, no fill | 4 | 1,458 | 9.9 |
| CL3: CL2 + fill 3 s | 5 | 3,013 | 6.0 |
| CL4: siblings + kNN + fill 3 s | 6 | 3,618 | 6.0 |

* CL1 (siblings only, 7 goals): 1 real proof, also found by S20. One sibling often proves the target in 2 s,
  but the real runs still fail: the hard part is the sibling itself.
* Laws make every sketch trivial (one law proves the target in 0.3 s) and give few, short hints.
* Gap filling found mbol_lem1_393, which no fresh run solved. 3 of CL4's 6 are chain proofs via true lemmas.
  The union of all arms is 9 of 32.
* sg3: CL5 10 of 64 in 6,817 CPU s (5.3 per CPU-hour); fresh 80 s 12 in 9,919 s (4.4). CL5's 10 are a subset
  of F3's 12.
* UL10's own deepening: L0 12 proofs per CPU-hour, L1 10, L2 (resume to 320 s) 2.5, with 78% of the CPU.
* Live climber against fresh 20 s on its own targets: CLV 29–31 in 7,657 CPU s (15 per hour), FV 36 in
  2,861 s (45 per hour). 27 both, 2 climber only, 9 FV only.

UL13's replay (fresh 20 s and resumes by line distance; wall-clock rate per run):

| level | proof lines | runs | proved | proofs per 1,000 s |
|---|---|---:|---:|---:|
| L0 fresh 20 s | 0–13 | 613 | 159 | 8.0 |
| L0 | 14–21 / 22–40 / 41–80 | 491 / 515 / 527 | 75 / 99 / 85 | 4.4 / 5.7 / 4.6 |
| L0 | 81+ | 157 | 6 | 1.0 |
| L1 resume to 80 s | 0–13 / 14–21 | 227 / 120 | 36 / 21 | 1.2 / 1.4 |

**Reading.**
* **The climb's apparent gains were the loop's mistake.** Round 5 had started with `--cascade-start 0`, which
  marks every goal as freshly tried. 63 of the 97 climber targets had had no fresh run in round 5, only
  resumes of states from older contexts. Fresh 20 s proved 28 of those 63. The climb's advantage was mostly
  its final fresh run. I had compared it with the wrong control (L2 resumes) before running the right one.
* Gap filling is the one part that reached goals nothing else did (mbol_lem1_393), at a cost.
* Fresh runs up to 80 lines from a proof are 3–4× as productive per second as resumes near one.
* The sets are small (sg1 32, sg3 64), so single goals decide the comparisons between climb variants.

**Decision and next.**
* `loop.py --fresh-first` (d2625d2): goals without a fresh run in the round get one first (8,634 qualified).
  UL12 (abs/ul12.sh, 16 workers); UL14 (abs/ul14.sh) with `--line-gaps 80,13`.
* The climber became a filler (`--cpus 20`, up to 8), taking only goals whose latest fresh run also failed.
* The climb returned on 15 Nov in stronger theories (2026-11-15-sketches-stronger.md). REPORT 2ab.

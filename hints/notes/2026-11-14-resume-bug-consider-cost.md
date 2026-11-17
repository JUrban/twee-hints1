# A resume bug that grew one run to 100 GB; consider-emulation costs a quarter of the CPU

*Reconstructed on 17 Nov from REPORT 2x–2y (14 Nov, afternoon and evening).*

**What happened.** A resumed run of the full loop grew to 100 GB before the user killed it. Separately, a
profile showed consider-emulation taking a large share of the CPU with today's big pools.

**The bug** (fixed in 17ffcd3):
* Twee numbers its symbols when it interns them, and numbers them afresh when it loads a saved state. The
  saved state holds the hint matcher's goal-constant tables, keyed by the old numbers.
* Resume added the new axioms (lemmas proven since the save) while those stale tables were in place, and only
  then put in the current run's tables. A goal constant could then look up a definition that contains
  itself, and scoring one critical pair never stopped.
* **Fix:** the current tables go in, normalised, before the new axioms. Goal-constant definitions whose
  expansion is cyclic or longer than 1,000 symbols are dropped from matching.
* **Guards:**
  * a default heap limit (`-with-rtsopts=-M6g`, 110d93a): a run past 6 GB stops with "Heap exhausted"
    (exit 251), and loop.py marks it HEAP and deletes its saved state;
  * abs/memwatch.py 7 45 kills any twee over 7 GB and, while all twee processes together use more than
    45 GB, the largest one.
* **Check:** the saved state plus one lemma used to exhaust any heap; it now proves its goal in 1.9 s at
  190 MB. Fresh and resumed hinted runs on six current goals do the same work in critical pairs.

**Consider-emulation.**
* Profile: twee-e32prof on one failing nil3_15 goal, 30 abstract s, production config (3,088 hints): 16.4M
  simplify calls and 202M index lookups. Without consider-emulation, 10.9M calls and 16% less time.
* With large pools many pairs share a hint's symbol fingerprint, and each goes through `allSteps`.

| consider-emulation | CPU (nil3_15 / lra2aa, 30 abstract s) | hints matched |
|---|---|---|
| on, all hints (default then) | 67.9 / 57.6 s | 973 / 1,608 |
| only for hints not yet matched (`--eqhint-consider-open`) | 48.0 / 50.7 s | 971 / 1,608 |
| off | 46.4 / 46.4 s | 981 / 1,602 |

With `--eqhint-debug` it adds 8 and 20 distinct hints over 8,811 and 26,697 plain matches.

| arm (sets/u3n150, 20 s, 6 lemmas, online) | solved | wall (sum over runs) |
|---|---:|---:|
| on (N3x6) | 77 | 4,405 s (another time, other load) |
| off (N3c) | 76 | 3,023 s |
| open hints only (N3o) | 74 | 3,504 s |

The three solve 79 between them. On the goals all three solve, median wall 6.1, 4.2 and 4.7 s.

**Reading.**
* The bug was in resume, which the loop had used only since that morning. The guards are what keep a single
  run from taking the machine again; they have fired since (HEAP rows in results).
* Consider-emulation earned its place on 12 Nov with small pools (2026-11-12-hints-dev10.md); with pools of
  thousands it costs about 30% of the runs per hour. Most differences between the arms come from sibling
  lemmas: N3c and N3o prove goal 341, whose lemma then gives goal 400 a 4 s proof. Only about three goals
  differ directly, within noise.
* The on-arm's wall time is from another time and load, so the wall column compares only roughly.
* Rewriting `simplifyOutermost` not to rebuild unchanged terms was 0–5% slower and was reverted.

**Decision and next.** `--no-eqhint-consider` in the full loop from 14 Nov 20:15, and in solve_new.sh since.
REPORT 2x, 2y.

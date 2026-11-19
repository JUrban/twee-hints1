# What the climber makes, what production uses, and what was lost (exp34)

Written 19 Nov 2026, 17:05 UTC. User, 16:55: "are we using the hints from the climber runs? and the additional axioms
and weakened conjectures the climber runs use? they might be useful, right? also the climber runs should probably
be kept somewhere and also in the data repo and we should keep their stats for the lattice up-down climbing
learning?"

## What production uses

* **Real proofs: yes, all of them.** Over the 29 climb.py directories in loops/, every goal a climber proved is in
  production's solved list with its hints: 0 missing.
* **Sketch steps: no.** These are the steps of proofs that used assumptions, or proved a weakened goal.
  * The saved ones, in sketches/<target>/<tag> (since climb.py 57a0b00), hold 64,564 distinct steps over 108
    originals.
  * 29,511 of them (46%) are not in the original's production pool. That is about 270 new steps per original,
    against a median pool of 6,138 (about 4%).
  * Those 108 originals hold 4,551 of the 4,554 goals still unsolved.
  * As hints for the sketched target itself, they were tested three times, all without gain:
    * 2g: 28 against 28;
    * chained sketches: 29 against 28;
    * exp4: 0 of 20 at the pool's factor, and 0 of 20 at a tenfold boost.
  * They were never tried as part of the pool for the original's other goals.
* **Weakened conjectures:** the proofs of their instances are real proofs of true statements. Their steps are among
  the sketch steps above; the files record the instance as `# goal=`.
* **Assumptions:** an unproven goal cannot be an axiom of a real proof. But a sketch proof that used only sibling
  assumptions U is a conditional proof: once U is proven, T should follow with U as lemmas. Production never
  did this. Each run gets only its 6 nearest proven siblings as lemmas.
* **Fill lemmas:** these are the assumption-dependent steps that `--fill` proved without the assumptions. They are
  true lemmas of the original, used by the climber's later runs (REPORT: goal 441's final proof used 17).
  **Their statements were never written to disk**: fill.tsv has counts only. They and the fill runs' proof steps
  were lost whenever a climber stopped.

## exp34: replaying the conditional proofs

* exp/condtest.py, abs/condtest.sh, 16:53, 2 workers, results in loops/CT1/results.tsv.
* Every climb.tsv row in loops/: 12,607 sketch proofs used an assumption. 966 of them used only siblings, giving
  310 targets.
  * 85 of those targets are still unsolved.
  * 11 have every assumption proven now. Only 4 of them have such a proof that used no fill lemma; the fill
    lemmas of the other 7 are lost.
* Arms at 20 s, in the climber's production context: A plain, B + the siblings as lemmas, C = B + the sketch
  proof's steps first in the hints.
* **Result: 0 of 4 in every arm** (aK2_eq_aK3_o 425, aK2_eq_aK3_t 380, ns_to_aa1_b 617 and 658), at 4 times the
  sketch's budget.
* Likely reason: a sketch proof also uses the run's lemmas, the proven siblings and kNN goals of that day's
  context, which change as goals get proven. climb.tsv records only the assumptions used, so "T from U" was
  really "T from U plus unrecorded lemmas".

## Changes (climb.py, 17:00 and 17:03; the exp32 climber restarted both times)

* `true.tsv`: one row per fill lemma: original, label, formula, canonical pair, target, tag.
* `fillhints/<target>/<tag>`: the fill runs' real proof steps.
* `assume.tsv`: per climb, each assumption label with its source goal and formula. kNN labels are positions in a
  list that changes as goals get proved.
* `used.tsv`: every proof's full set of used axioms, `lemma_goal_J`, `lemma_knn_I_<goal>`, `assume_*` and
  `true_*`. That is a conditional proof's full premises.
* On start, climb.py reloads the fill lemmas and the sketch and fill hints, so a restart loses nothing.
* Smoke test on loops/SMK3 (a copy of SMK2's records, 3 s sketches): the first run wrote 2 fill lemmas, their
  steps and 70 assumption names. The second run reloaded them and added 5 more lemmas without duplicates.
* The exp32 climber was restarted at 17:00:52 and 17:03:00. Its fill lemmas from 15:40 to 17:00 were lost, and
  the climbs in flight were cut. Its rate is still read per CPU hour from climb.tsv.

## Data repo

* hintdata_build.py `--climbs` writes climbs/<dir>/ for every climb directory (not SMK*, *.old):
  * the small records, gzipped (climb, theories, fill, true, assume, used);
  * the climber's own real proofs, as hints.tar.xz (latticedata.py reads DIR/hints/<target>);
  * sketches.tar.xz and fillhints.tar.xz;
  * realized/ and given/ rule logs, one .tar.xz per original, committed in chunks of at most 10 MB.
* The archives are deterministic, so a rerun re-commits only what changed (the live CLHL2).

## Next

* A conditional-proof replayer: when every premise in used.tsv is proven, rerun T with exactly those premises
  as lemmas. That needs a few days of used.tsv rows first.
* A production variant with the original's fill lemmas as extra lemmas, and its sketch steps in the pool. It
  would be measured by the ratio order like the other members, once true.tsv has rows.

## The climbs' hints as production members (ul70, 17:58)

* User, 17:55: "why not collect the climb hints anyway? we do collect all hints from all standard runs already,
  right?" Production collects the proofs of the goals it proves, one hints file per goal. An original's pool is
  all of them. Failed runs leave nothing, and until now the climbs' other proofs reached no pool.
* loop.py `--variants sk`: the pool plus the original's climb steps, read from the `--climb-hints` directories
  (sketches/ and fillhints/ of CLH, CLHL, CLU, CLHL2, FUD2p and FUDs; re-scanned every 10 minutes). They go after
  the pool, at the default boost: 65,021 steps of 108 originals at 17:58.
* ul70 = ul69 + `sk@0` (5 s) + `sk@1:0` (40 s fresh after L0), J 15 while exp36 runs. Both are explored like
  every member, then get CPU by their measured yield. If they pay, the climb steps move into the base pool.
* The first launch at 17:58:23 died: loop.py's variant-name whitelist lacked 'sk'. Production was down about 30 s.
* Check (18:01): the first 24 sk@0 runs went to com_Ralt goals with 4,254 hints each: the pool's 3,804 (as in that
  original's L0 runs) plus 450 of its 833 climb steps that the pool lacks.

## Fill lemmas kept constants (found 18:18, fixed in climb.py 18:22)

* By 18:18 the climber had saved 154 fill lemmas, and 69 of its 132 proofs had used at least one.
* **120 of the 154 (78%) contained the goal's Skolem constants** (x0, x1_2, ...): the gap steps of a sketch proof
  are about the goal's constants. As axioms they say something about fresh constants named x0 and can match
  nothing. Only 3 of them were ever used, against 22 of the 34 with variables only. (They are sound: the fill
  problem leaves out the conjecture, so the constants are arbitrary there.)
* Fix: before a gap step is tried, every constant that occurs nowhere in the fill problem (axioms, lemmas, earlier
  fill lemmas) becomes a variable (Yc0, Yc1, ...). Trivial steps (t = t) are skipped. Hints were already
  generalised the same way (canon_key), so the sk member's fill steps were fine.
* New record `fillattempts.tsv`: every gap tried, proved or not (which steps are fillable). It is in the data repo.
* Smoke test on loops/SMK3: the attempts come out with Yc variables. The climber was restarted at 18:22:27 and
  reloaded all 154 lemmas.

## Fill lemmas into production, and CPU to the climber (18:25)

* loop.py: `sk` runs also get the original's fill lemmas from the climb directories' true.tsv as lemma axioms
  (`lemma_fill_K`). Lemmas that kept goal constants are left out. They are sound for every goal of the original:
  they were proved from its axioms and proven lemmas, with the conjecture left out.
* CPU: production 15 → 13 workers, the climber 2 → 4 (restarted at 18:25:19; production's rows from 165,394, its
  earlier log in loops/UL70a.log).
  * Reason: from 15:40 to 18:10 the climber made 1.34 proofs per CPU h, production 0.61 on average, and production's
    members at 80 s and above 0 in 13.9 CPU h.
  * Total: 13 + 4 + exp35's 2 + exp36's 2 = 21, plus the transfer's 1-2 at times. Once exp35 and exp36 end, their
    CPUs go back.


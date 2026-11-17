# Goals that are steps of existing proofs: transfer, source lemmas, and a kNN filter bug

*Reconstructed on 17 Nov from REPORT 2al (16 Nov 04:20–10:30). Abstract time.*

**Question.** 2,905 of the 7,543 unsolved goals were, up to variable names, a step of a proof found earlier. Would
those proofs' steps, as hints, prove them?

**Setup.**
* `transfer.py find LOOPDIR --out GOALS.tsv [--any-theory] [--instances] [--goals]` lists unsolved unit goals
  whose canonical equation is a step of some hints file:
  * `--any-theory`: the source may have more axioms;
  * `--instances`: the goal is σ(step), one-way matching over all hints files;
  * `--goals`: instances of proven goals of other originals.
* `transfer.py run GOALS.tsv DIR -- LOOP-OPTIONS`: one fresh run per goal, with the source proofs' steps first (up
  to 3 sources), then the pool and lemmas. Proofs go to DIR for merge.py.
* `--src-lemmas K` (05:05): the source goal and its K−1 nearest proven goals below become lemma axioms of the
  target run. Same trust level as `--lemma-knn --lemma-subsets`.
* Sets, from snapshot ULsY (04:15), fresh 20 abstract s:
  * transfer1.tsv, 101 goals with a source of the same or weaker axioms (abs/xfr.sh, 3 workers);
  * transfer2b.tsv, the 2,804 from other theories (abs/xfr2.sh);
  * transfer3b and transfer3c, instances;
  * transfer6, after the merges.
* Live from 05:37 (`transfer.py live`, abs/xfrlive.sh, 2 workers, every 20 minutes).

**Results.**
* Same or weaker axioms: **32 of 101**, about 43 proofs per CPU-hour, more than 20× production's average.
  Sources only in other originals 29 of 89; in the goal's own original 3 of 12 (already in its pool).
* Other theories: 1 of 28 (a stronger theory's step is mostly not derivable in the weaker one).
* Instances: own original first 1 of 61; other originals only 3 of the first 45.
  * Every one of the 2,581 candidates had a conditional goal among its sources, whose steps use hypotheses and
    are false once generalised.
  * Restricted to unit-goal sources, 132 candidates (28 new).
* With source lemmas, on the 69 transfer1 goals that failed: **63 proved** in 338 run s. 30 are one step, and 12
  goals are identical to a source goal.
* Live by 10:28: 21 of 25 new candidates. Totals 32 + 63 + 6 + 7; 101 merged into UL (44,240 at 04:12 → 44,398 at
  05:35).
* Long climbs on the 111 first unsolved goals (abs/clh.sh, 160 s final run): 2 of 8 (1.7 per CPU-hour).

**Reading.**
* **The kNN lemmas had a bug since 13 Nov** (d6b6bf9). `LemmaIndex._select` started with
  `seen = {target's formula}`, so it dropped every proven goal stating exactly the target, from any original. 46
  of the 63 source-lemma proofs were of this kind. Fixed 16 Nov 06:00: the identical proven goal now comes first.
* Production's pool offers only the goal's own original's proofs, and kNN lemmas are proven goals, not steps. So
  steps of other originals' proofs never reached these goals, until this transfer.
* **This is close to the user's 17 Nov expansion idea.** Steps of proofs, when the source's axioms are the same
  or weaker, are worth far more than similar proofs' steps chosen by similarity (2ap: no gain). Expansion adds
  exactly the steps of the lemmas' proofs, from other originals included (2026-11-17-expanded-proofs.md).
* **A decision for the user, still open.** A step of a proof from the same or weaker axioms (without hypotheses)
  is a proven theorem, like the sibling goals used as lemmas. As a lemma axiom it would prove its instances at
  once. The runs here gave steps as hints, so each proof stays at the current trust level.

**Decision and next.** The live transfer worker in production (later XEVERY in solve_new.sh); the kNN filter fixed.
REPORT 2al.

# The same statement proven in another theory

*Reconstructed on 17 Nov from REPORT 2ar (16 Nov 16:20–17:50). Abstract time.*

**Question.** `transfer.py find --same-other` lists unsolved goals whose statement, up to renaming, is a proven goal
of an original whose axioms are not within theirs: 1,887 of 7,025 on 16 Nov, 1,361 of them with one axiom missing.
Such a proof holds for the goal if neither it nor its lemmas use the missing axioms. Does it?

**Setup.**
* Count: in how many of 400 source proofs the missing axiom is itself a step.
* Pilot: `transfer.py run --src-pool`, the source original's whole pool as hints, sets/so60.tsv.
* sets/so_free.tsv: the 323 whose source proof has no missing axiom as a step. Source proof steps as hints, 20 s:
  sets/sof60.tsv (60), then sets/sof_rest.tsv (263, run SOR, 4 workers, to 17:47).

**Results.**
* In 359 of 400 source proofs (90%) the missing axiom is a step of the proof.
* Pilot: 0 of 25, stopped.
* so_free: 3 of 60 (0.6 CPU h, 5 per CPU-hour), then 10 of 263 (2.4 CPU h, 4.2 an hour; 9 new to production).

**Reading.**
* The shared statements hold in the source theory because of the hypothesis that differs. Even when the final
  proof does not show the missing axiom, its lemma chain carries the dependence.
* Exact reuse works within the same or weaker axioms (2026-11-16-step-transfer.md) and rarely across them.
* At 4–5 proofs per CPU-hour it still beat production's marginal rate then (about 1 per worker-hour), so the
  finite list was run to the end.
* The same point applies to the 17 Nov expansion: a lemma from another original is only used when its axioms are
  a subset of the target's (checked by depcheck), so expanded steps from those proofs are theorems of the
  target's theory.

**Decision and next.** All 323 tried; the proofs merged. REPORT 2ar.

## Redone on production, 20 Nov 04:18 (exp/sofree.py, abs/so2run.sh)

* `find --same-other` on production now: 627 candidates (1,887 on 16 Nov). 343 of them were tried on 16 Nov (SOF,
  SOP, SOR).
* 46 of the rest have a first source proof with none of the missing axioms as a step (canonical keys, both
  orientations). They run as SOF/SOR did: source proof steps first as hints, 20 s, 2 workers, proofs into production.
* **Result (04:29): 9 of 46 in 0.34 CPU h, about 26 per CPU h** (16 Nov: 13 of 323 at 4-5 per CPU h). Proved:
  aK2_eq_aK3_g 388 and 400, aK2_eq_aK3_o 451, aK3instance 402, nil3_1K_b 410, nil3_1K 471, ns_to_aK1 564, 584 and 585.
* The source side has grown: production's newest proofs give new same-statement sources. The finder takes 6 s, so it
  joins the live loop.

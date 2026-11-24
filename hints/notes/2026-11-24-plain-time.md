# Longer plain runs on the local heads (exp81)

Written 24 Nov 2026, 04:55 UTC, at launch (abs/exp81.sh, bash 3829770; exp/exp81.sh).

## Question

Do plain runs longer than 60 s pay on the local heads that fail at 60 s?

* HLW1 (exp72, notes/2026-11-23-tail-allocation.md) runs plain 60 s on the 940 local heads (unsolved goals whose
  previous goal is proved). It proved 4 of its first 123 at 1.32 per CPU h, all within 27 s of their 60 s.
* On the first heads, CC67D's long hinted runs (30 siblings, 400 kNN, production's hints, 552 CPU s each) proved 6 of
  their 9 after 150 CPU s (exp67, notes/2026-11-23-climber-restart.md).
* Before: plain runs longer than 60 s were only exp74's 1,200 s on 7 cluster heads (1 of 7, already proved
  elsewhere). The plain lemma-size tests (notes/2026-11-23-plain-sizes.md) were all at 5 or 60 s.
* Siblings before: REPORT 2r (14 Nov), hinted 20 s runs with up to 20 siblings: 6 beat 3, 10 and 20 added little, and
  a proof uses about 20% of the siblings it is offered almost regardless of distance (19% of those 11 or more
  away); all kNN ranks were used. Hundreds of siblings in plain 60 s runs (P81C) were not tried.

## Set

60 of HLW1's failed goals that are still unsolved at launch, random.seed(81) from the sorted list (cond/EXP81.set,
written at launch). HLW1's rows are in two contexts (cond/HLW1.trusted to 04:50, cond/HLW1.trusted2 after).

## Arms

Plain (no hints, no rule model, no PG), H's lemma lists (100 earlier and 30 later siblings, 400 kNN), the context
loops/UL/solved.tsv at launch for both (cond/EXP81.trusted), condprove.py --proved, 2 threads each, at the same time:
* P81A: 60 s, the control. The context has moved since HLW1, so a P81A proof is the context's, not time's.
* P81B: 300 s.
* P81C (added 05:06, after P81A on its 2 threads): 60 s with every earlier sibling (`--sibs 1000`) and 100 later,
  400 kNN. No plain run at 60 s had more than 100+30 siblings (at 5 s, 200+60 with 1,000 kNN). A long original's
  later goals miss most of their proved earlier siblings, and those are steps of the same Prover9 proof. Smoke:
  aK2_eq_aK3_1243b 606 got 499 sibling and 400 kNN lemma axioms (6.5 s wall for a 2 s run).
* P81D (added 05:21, after P81C): 60 s, 100+30 siblings, the kNN lemmas ranked 400-799 (`condprove.py --knn-skip
  400`, lemmas.lemma_problem_knn skip=): a disjoint slice that costs what A's does. HLW1's proofs use kNN lemmas up
  to rank 397 of 400 (below), and 1,600 at once lost at 60 s by its cost (HDG1). Smoke: skip 0 gives a byte-identical
  problem; skip 400 on aK2_eq_aK3_1243b 606 gives ranks 400-618 (its pool ends there), none of the first 400.

It waits for exp76's end (loops/EXP76.pids "exp76 done") so that the total stays near 20 twee processes. Proofs go
into loops/CI3 and loops/UL at each arm's end (cond/EXP81.status).

## Measures

* Proofs per arm, B only and A only; CPU h per arm (results.tsv seconds are wall; 300 abstract s cost about 2.4 CPU s
  each with these lemma lists: exp80).
* B's proofs' times: how many came after 60 s.
* C against A: proofs only with the full sibling window, at equal time.
* D against A: proofs only with the second kNN slice; A ∪ D against B at about the same CPU (two 60 s runs against one
  300 s run).
* Decision: if B's proofs beyond A's come at 0.5 per CPU h or better (production makes 0-0.4), a 300 s plain pass over
  the local heads that fail at 60 s follows (a W2 setting in the live loop or a sweep).

## What HLW1's proofs use (05:19)

The printed proofs of HLW1's first 5 (cond/HLW1/proofs), by lemma axiom:

| proof | earlier siblings (farthest back, goal numbers) | later siblings | kNN lemmas (highest rank) |
|---|---|---:|---|
| aa1_45_c 365 | 4 (29) | 1 | 24 (385) |
| aa3_45 485 | 2 (87) | 0 | 26 (381) |
| aa_instances_4 384 | 11 (106) | 1 | 45 (395) |
| aK2eq_1234 427 | 5 (33) | 0 | 5 (218) |
| aK2_eq_aK3_d 542 | 16 (131) | 0 | 29 (397) |

* Two proofs reach more than 100 goal numbers back (the window is the 100 nearest proved earlier siblings, so it can
  reach past 100 numbers): P81C asks what the rest of the window gives.
* Later siblings are rarely used (2 of 5 proofs, one each).
* Four of 5 use a kNN lemma ranked 381-397 of 400: the useful kNN lemmas are spread over the whole list, as "size, not
  order" found (23 Nov); 1,600 at 60 s on the first heads still lost (HDG1), by its cost.

## HLS2: the second kNN slice on all local heads (24 Nov 09:05)

Interim at 09:00: P81D (kNN ranks 400-799, 60 s) proved 2 of 60 of HLW1's failed heads (aK2_eq_aK3_a 658, aK2_eq_aK3_d
571), P81A (ranks 0-399, 60 s) 0 of 60, P81C (all earlier siblings) 0 of 60; P81B (300 s) 2 of 30 so far. HLW1's own
proofs used kNN ranks up to 397. With 5 CPUs free (exp81's 60 s chain done, the climber at its -j 8), abs/hls2.sh
(exp/prod/side/hls2.sh) sweeps P81D's setting over every unsolved local head and first head of plainlive6's cycle c39:
1,012 goals, context 48,625, 3 threads, cond/HLS2; proofs into loops/UL through loops/CI3 every 30 minutes
(cond/HLS2.parts). First problem: aa1_14 537, 103 sibling and 400 kNN lemma axioms, ranks 400-799. This acts on an
interim reading (2 against 0): it is a production sweep with the reading in its own rows (proofs per CPU h against
HLW1's 0.90), not exp81's decision.

## Result (exp81 done 24 Nov 11:23:56, cond/EXP81.status)

| arm | setting | proved of 60 | wall h | per wall h |
|---|---|---:|---:|---:|
| P81A | 60 s, 100+30 siblings, kNN ranks 0-399 (HLW1's) | 0 | 1.53 | 0 |
| P81B | 300 s, the same lemmas | 2 (aK2_eq_aK3_a 658 at 270 s, aK2_eq_aK3_b 568 at 137 s) | 10.44 | 0.19 |
| P81C | 60 s, every earlier sibling and 100 later | 0 | 1.70 | 0 |
| P81D | 60 s, kNN ranks 400-799 | 2 (aK2_eq_aK3_a 658 at 78 s, aK2_eq_aK3_d 571 at 102 s) | 1.59 | 1.26 |

(Wall seconds of single-threaded runs, about their CPU.) The goals are 60 that HLW1's 60 s run had failed.

* **B against A:** +2 −0, but 0.19 per h, below the 0.5 the decision asked for: **no 300 s pass.** One of B's two (568)
  took 137 s, so a 160 s run would have had it; the other (658) also fell to D at 60 s.
* **C against A:** 0 −0: hundreds of earlier siblings (on average 367 against 123) add nothing at 60 s.
* **D against A:** +2 −0 at the same cost; **A ∪ D** (two 60 s runs, 3.1 h) proves as many as B (10.4 h). The second kNN
  slice is the cheap way to more lemmas: HLS2 (started 09:05) runs it on all 1,012 local heads.
* Caveat: 2 proofs per arm; B and D share 658.

**HLS2 stopped (24 Nov 15:30:45):** 750 of the 1,012 heads ran, 9 proved (all imported), 19.05 CPU h, 0.47 per CPU h
(HLW1's 60 s pass on the first slice: 0.90). None after 13:18 (the last 300 or so runs). The second kNN slice adds
little on the whole set: 9 of 750, against exp81's 2 of 60 on a sample of HLW1's failures, which overstated it. Its 3 threads went to exp83
([notes/2026-11-24-quick-finals.md](2026-11-24-quick-finals.md)).

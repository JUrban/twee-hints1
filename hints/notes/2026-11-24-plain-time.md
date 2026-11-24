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

It waits for exp76's end (loops/EXP76.pids "exp76 done") so that the total stays near 20 twee processes. Proofs go
into loops/CI3 and loops/UL at each arm's end (cond/EXP81.status).

## Measures

* Proofs per arm, B only and A only; CPU h per arm (results.tsv seconds are wall; 300 abstract s cost about 2.4 CPU s
  each with these lemma lists: exp80).
* B's proofs' times: how many came after 60 s.
* C against A: proofs only with the full sibling window, at equal time.
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

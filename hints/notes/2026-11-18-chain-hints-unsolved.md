# Chain hints on production's unsolved goals (exp8)

Started 18 Nov 2026, 07:19 UTC. Directory /project/hintwork/exp8; scripts and sets in hints/exp/exp8_*.

## Question

In exp3 (47 late unsolved goals, 320 s), arm K did best. K keeps production's lemmas, but its hints are the
expanded proofs ("chain") of the 10 nearest proven siblings below the goal, instead of the original's pool. At
07:10, K had proved 11 of 39 goals in 11.9 CPU h, and C (production's own setting) 8 of 41 in 18.4 h. Every goal
C proved, K proved too (notes/2026-11-17-deep-runs-expanded-chains.md).

Does the chain beat the pool on a second, larger set, at production's L1 budget? If so, production's deeper
levels should use chain hints.

## Set and setting

* exp6's 78 captured goals (exp6/stall78_e48.cmds; sets/exp8_goals78). These are unsolved goals whose production
  runs at L1/L2 in round r5 ended without stats, with commands captured in production's context at 05:22.
* 80 abstract s, CPU cap 800 s, twee-e48, everything else as captured.
* **Control:** exp6's arm s_b0 (the same commands, the original's pool as hints; still running, 1 worker).
* **Arm s_K:** the same commands with `--hints-file` replaced by the chain.
  * Siblings: the 10 nearest UL-proven siblings below each goal (pick.py, as exp3_pick.py; UL at 07:11). All 78
    goals have 10, 566 distinct siblings.
  * Expansions: `expand.py sibs10 xd` over the 16 loops' records (39,476 proofs; 472 s). Median closure 715
    goals, median 2,875 hints.
  * Per goal, the chain is the siblings' expansions, nearest first, duplicates dropped, as exp3/mkhints.py. On
    average 12,741 chain hints against 11,902 pool hints.

```
cd /project/hintwork/exp8
python3 pick.py goals78; python3 /project/twee/hints/expand.py sibs10 xd
python3 run.py stall78_K.cmds s_K 2
```

## Caveats

* UL has proofs that were found with these goals' siblings in context. Of the 78, only aK2_eq_aK3_q 252 was
  proved in UL when the siblings were picked (merged from exp3 at 07:09); see the interim result.
* exp6's s_b0 runs at 1 worker and s_K at 2, so they share the machine differently. The comparison is by
  proved goals and pairs to proof, which do not depend on load.

## Results

* **Interim (08:24, 36 of 78 s_K rows; s_b0 has 55).** On the 36 goals both arms have run:
  * chain proves 4 (aK2_eq_aK3_q 252, nil3_1K_d 364, ns_to_aa1_b 587 and 628), the pool 2 (aK2_eq_aK3_o 422,
    364); exp6's gb100 arm (pool, branch limit) proves the same 2;
  * 364: 6,001 pairs with the chain against 22,476; 422 fails with the chain at 160,000;
  * 587 (47,691 pairs) and 628 (89,245) are new to UL. 252 is not new: exp3 proved it at 320 s and it was merged
    into UL at 07:09, two minutes before the siblings were picked. Its own proof is not in its siblings'
    closure (781 goals, chain_records.tsv), so its chain holds no proof of it; 317 of its 1,079 proof lines
    are steps its siblings' proofs share.
  * The s_K runner started before run.py kept proved outputs (07:47), so 587 and 628 were rerun (08:25,
    `python3 run.py re2.cmds s_K_re 1`, exp/exp8_re2.cmds): the same pairs (47,691, 89,245). Merged into UL at
    08:27 (`exp3/tomerge.py exp8/out_s_K_re exp8/xm1`, `merge.py loops/UL exp8/xm1`).

* **Final (complete by 09:40): chain 9, pool 5 (+6 −2) on all 78.**
  * Against the exact control s_b0 (e48, same commands, pool hints): CPU 16,822 s against 15,263 (+10%). Against
    s_gb100 (e57 with the branch limit, same proofs as s_b0): 18,031 s.
  * Chain only: aK2_eq_aK3_q 252, nsmr_to_aa1 623 and 624, nsmr_to_aK1 455 (12,006 pairs), ns_to_aa1_b 587 and
    628. Pool only: aK2_eq_aK3_o 422 and nslm_to_aa1 932. Both: nil3_1K_d 364 (6,001 against 22,476 pairs),
    nslm_to_aa1 921 and nsmr_to_aa1 641.
  * Chain run ends: 73 normal, 4 at the CPU cap, 1 out of heap.
  * Combined with exp3 (320 s: 12 against 9, the pool's proofs a subset), the chain wins at both deep budgets.
  * Seven of the proofs were not in UL (364, 921, 623, 641, 455 from the chain; 422, 932 from the pool). The arms
    kept no outputs, so they are rerun with outputs (re5.cmds as s_K_re5, re2p.cmds as s_b0_re) to merge.

## In production (ul43 from 08:28, ul44 from 09:23)

* Check (09:25): production's L1 rows since 08:28 carry chain-sized hint counts (HINTSTATS `hints=`); 3 of
  10 sampled equal the chain sibchain gives now, the others differ by siblings proven since.
* L1 yield, 09:25: **6 of 24 L1 runs proved** (0.9 wall h). Pool L1 before: 11 of 385 in ul41's 2,200 runs
  before the 07:09 burst (19.3 wall h), 2 of 20 during the burst and ul42.
* Not an A/B: the scheduler picks different goals at different times, and after the burst many goals had new
  contexts. The A/B evidence is exp3 and this experiment's arms.


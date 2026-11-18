# How big should the chain be? (exp13)

Started 18 Nov 2026, 12:14 UTC. Directory /project/hintwork/exp13; scripts and data in hints/exp/exp13_*.

## Question

On exp8's 78 stalled goals at 80 s, the chain (the 10 nearest proven siblings' proofs, expanded through the proven
goals they used; mean 12,741 hints) proved 9 against the pool's 5. Adding more hints made it worse:
* exp10's transfer-filled chain (mean 14,707) proved 7, with more pairs on the shared proofs;
* exp3's E arm (pool + chain) proved 10 against K's 12 at 320 s.

Would a smaller hint set do better?

## Arms (both launched 12:14, 2 workers each)

Each arm uses exp8's commands, siblings and records, with only the hints file changed. **The control is exp8's
s_K** (9 of 78).
* **S5:** the chain of the 5 nearest of the 10 siblings (exp13/mk.py 5). Mean 11,300 hints, 89% of the full
  chain: the nearest siblings' closures overlap heavily, so the sibling count barely changes the size.
* **D:** the 10 siblings' own proofs only, without the expansion (exp13/mkd.py; their hint files, nearest first,
  duplicates dropped). Mean 1,876 hints, so the expansion multiplies the set about sevenfold.

```
cd /project/hintwork/exp13
python3 mk.py 5; python3 run.py S5.cmds S5 2
python3 mkd.py;  python3 run.py D.cmds D 2
```

## Results

Complete at 14:40, all 78 goals in both arms (exp13/res_S5.tsv, res_D.tsv), against exp8's s_K:

| arm | mean hints | proved | against the chain | CPU s |
|---|---:|---:|---|---:|
| chain, 10 siblings (exp8 s_K) | 12,741 | **9** | | 16,822 |
| S5: chain of the 5 nearest | 11,300 | 7 | +1 −3 | 17,386 |
| D: the 10 siblings' own proofs, no expansion | 1,876 | 4 | +1 −6 | 16,075 |

* S5 gained nslm_to_aa1 932 and lost ns_to_aa1_b 628 and nsmr_to_aa1 623 and 624. Where both prove (6 goals), the
  pairs are nearly the same.
* D gained aK2_eq_aK3_t 342 and lost 252, 587, 628, 455, 624 and 641.
* **So the expansion through the lemma records is what makes the chain work.** Without it, the sevenfold
  smaller set loses 6 of the 9. Fewer siblings in the chain lose a little, within noise.
* Together with exp10 (transfer-filled, 7) and exp3 (pool + chain, 10 against 12 at 320 s), the 10-sibling
  expanded chain is the best of the five sizes tried. Production keeps it.
* The two gains (932, 342) were already in UL by 14:45, so there was nothing to merge.

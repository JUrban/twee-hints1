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

(pending)

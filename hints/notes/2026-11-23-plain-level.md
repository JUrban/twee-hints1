

## 4 hours (14:55)

| | 120 min | 180 min | 240 min | equal abstract work |
|---|---:|---:|---:|---:|
| P4A | 19,434 | 20,440 | 21,146 | 19,433 at 120 min, 20,439 at 180 min, 21,131 at 238 min |
| P4B | 19,669 | 21,053 | 21,547 | 19,578 at 118 min, 21,046 at 179 min, 21,528 at 237 min |

P4B by wall time: +401 at 240 min; at equal work (the points above, in order): +145, +607, +397.

exp/armdiff.py P4A P4B --at 240:

```
at 240 min: P4A 21146, P4B 21547, P4A-only 87, P4B-only 488, union 21634
P4A-only 87, by how P4A proved them: synced 21, first L0 20, later L0 18, later Vunf 14, later L1 11, later Vk100 2, later Vk200 1
   the proved-by-a-run ones had from P4B (rows so far): 0 runs 1, 1-2 runs 15, 3+ runs 50
   proved at their first run (20): minute of the first run, quartiles: P4A 77/172/212, P4B 101/150/170
P4B-only 488, by how P4B proved them: first L0 233, later L0 92, later Vplk100s40 80, synced 70, later L1 7, later Vplk400s130 3, later Vunf 2, later Vk400 1
   the proved-by-a-run ones had from P4A (rows so far): 0 runs 229, 1-2 runs 124, 3+ runs 65
   proved at their first run (54): minute of the first run, quartiles: P4B 154/165/171, P4A 178/215/231
```

Runs so far by level: P4A L0 21787, Vunf@0 939, Vk100@0 234, Vk200@0 212, Vkd@0 206, Vk400@0 184, L1 127, Vk60@0 5, L2 1; P4B L0 22555, Vplk100s40@0 1549, Vplk400s130@0 239, Vunf@0 227, Vk100@0 199, Vkd@0 198, Vk200@0 189, Vk400@0 172, L1 85.

Now the plain level proves P4B-only goals itself (later Vplk100s40: 80, against 3 at 2 h), and P4B ran Vunf@0 227 times against P4A's 939: the cheap plain runs take goals the unfiltered member would have run, and that work goes to L0 instead (the P4B-only "first L0" goals that P4A has not run yet). The lead grows with time; the 6-hour reading decides, and a replica pair comes before a production change.

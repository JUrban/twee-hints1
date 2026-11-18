# No parental guidance, and no rule model, at 80 s on the walls (exp22)

Prepared 18 Nov 2026, 17:50 UTC; it starts when exp21's twee runner (PID 2452454) ends. Directory
/project/hintwork/exp22; scripts in hints/exp/exp22_*. Part of the portfolio task (notes/2026-11-18-portfolio-review.md).

## Why

* Parental guidance (PG) and the rule model change twee's search more than any hint setting. Both won in count
  where they were tested:
  * PG: PGA 18,987 against 18,410 on half1 at 2 hours (2av);
  * the rule model: 2b, 2q.
* Neither was tested as a portfolio member on the hard tail. Twee's chaos makes it likely that each proves walls
  the other settings fail.
* exp21 found nothing at 5 s on goals that failed 5 s, for any arm. The walls at 80 s are where the other
  variants had unique proofs (3-7 each).

## Set and setting

* exp11's 107 walls at 80 s, exp11's commands (twee-e48, chain hints, CPU cap 800 s), with one change each:
  * **G80:** `--pg-threshold 0.25` dropped (e48 then matches e44, production's setting before 17 Nov 19:00);
  * **N80:** no rule model, and so no PG either.
* The control is exp11's runs, exact for both (twee is deterministic in abstract time).
* Order: the 92 walls exp11 failed first, then its 15. 4 workers, G80 then N80.

```
cd /project/hintwork/exp22
python3 mk.py
bash stage.sh 2452454   # then: python3 run.py G80.cmds G80 4; python3 run.py N80.cmds N80 4
```

## Measures

* New walls (exp11 failed) and losses (of exp11's 15).
* New per CPU hour, against the other members (portfolio review, ratio table).

## Results

**G80 (no PG), the 92 walls exp11 failed (19:37):**
* 2 new at 4.6 CPU h, 0.43 per CPU hour: aK2_eq_aK3_a 455 (111,103 pairs) and a_instances 363 (122,855).
* Of these, a_instances 363 was also proved by an 80 s variant (60 kNN lemmas). After k60, two, unf and sub, no PG
  adds 1, about 0.22 per CPU hour. aK2_eq_aK3_a 455 is also among exp20's 160 s proofs.
* Of exp11's 15, G80 proved aK2_eq_aK3_1243 339 at 26,007 pairs. The rest of the 15 and N80 follow.
* Merged at 19:38: aK2_eq_aK3_a 455 and mbol_nil3_a 476 (`exp3/tomerge.py exp22/out_G80 exp22/xm`, then merge.py).
**N80 (no rule model, so no PG either), the 92 walls (21:20):**
* 4 new at 5.5 CPU h, 0.72 per CPU hour: aK2_eq_aK3_a 455 (69,989 pairs), a_instances 363 (105,893),
  gbol_to_osb 196 (43,401) and mbol_lem2 508 (49,237). Two of these are also G80's.
* Of exp11's 15, N80 proves 3 of the 7 run so far.
* **Conditional, in production's order** (160 s increment, k60, Prover9 + chain, unf, two, nopg, nom):

| member | runs | new | CPU h | conditional per CPU h |
|---|---:|---:|---:|---:|
| chain to 160 s | 92 | 12 | 6.79 | 1.77 |
| 60 kNN lemmas | 80 | 5 | 4.19 | 1.19 |
| Prover9 + chain | 75 | 2 | 1.23 | 1.62 |
| unfolded | 73 | 5 | 12.65 | 0.40 |
| two-sided chain | 68 | 1 | 4.04 | 0.25 |
| no PG | 67 | 0 | 3.48 | 0 |
| no model | 67 | 1 | 4.38 | 0.23 |

* The union is 26 of 92 at 36.8 CPU h. No model adds 1 after the rest, about as much as the two-sided chain. It
  becomes the last 80 s variant (`nom`, prior 0.23) at the next restart. No PG stays out: 0 after the rest.
* Merged at 21:21: mbol_nil3_a 476 (already proved in G80's output, now from N80's too: 1 merged).
* **Production (earlier):** `nopg` was the last 80 s variant in ul50, with prior 0.22 (19:39).

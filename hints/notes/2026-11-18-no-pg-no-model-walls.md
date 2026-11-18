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

(pending)

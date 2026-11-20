# The derived-rule transfer without waiting for the loop's failure (exp43, 20 Nov)

Written 20 Nov 2026, 13:05 UTC; launched 13:28. Script abs/exp43.sh ([hints/exp/exp43.sh](../exp/exp43.sh)).
Follows exp42 ([notes/2026-11-20-given-cap.md](2026-11-20-given-cap.md)).

## Why

* The live loop runs a derived-rule hit (an unsolved goal that is a variant of a rule another run derived) only
  after the main loop has failed on that goal. That avoids work the loop would do anyway.
* In exp42 the ancestry runs proved 322 of 345 (93%) at about 4 s each. Meanwhile 120–310 hits waited, per cycle,
  for the loop to reach and fail their goals. A hit is strong evidence of a cheap proof.
* givenmatch.py `--no-wait` (20 Nov 12:14) runs hits, and the same-statement candidates, as soon as they are found.

## Set and setting

* **Set:** sets/half2, from zero (loops/EMPTY).
* **P2G (the arm):** abs/or_test2.sh, `GIVENARGS="--every 300 -j 2 --cap 200 --same-cap 20 --no-wait --no-inst"`,
  otherwise solve_new.sh's defaults: 6 workers, 2 hours.
* **Control: exp42's P2F,** the same without `--no-wait`. P2E (exp41) is the second reference.
* **CPUs:** as in exp42. Production at 6 workers, the re-proofs at 2.

## Measures

* `abs/setcurve.py sets/half2 P2E P2F P2G --at 10,30,60,90,120`.
* One-arm goals against P2F.
* The live loop's runs, proofs and CPU by kind, and how many of its proofs the loop would also have made: goals
  the live loop proved that P2F's loop proved on its own.
* **Decision:** if P2G ≥ P2F + 185 at 2 hours, `--no-wait` joins the default. If it is ahead early but within noise at
  2 hours, it is a speed gain only, and is reported as such.

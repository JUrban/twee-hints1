# E with chain hints as a watchlist on the walls (exp28)

Written 19 Nov 2026, 07:28 UTC. Queued to start when exp23's V100 ends (about 08:50), on its 1 CPU. Directory
/project/hintwork/exp28; scripts hints/exp/exp28_*. Part of the portfolio task (notes/2026-11-18-portfolio-review.md).

## Why

* The portfolio rule is to measure a member before leaving it out. Prover9 with chain hints is production's p9
  level: on the walls it proved 4 of 107, 3 of them not twee's (exp16).
* E is the other mature prover on the machine. Its source is in ext/eprover (built 07:20, E 3.5.9, a08e78c). Its
  hint mechanism is the watchlist, as used in ProofWatch (Goertzel, Jakubuv, Schulz, Urban 2018).
  * `--static-watchlist=F` marks a generated clause that subsumes a watchlist clause.
  * Clause selection prefers marked clauses through the `PreferWatchlist` priority. The built-in heuristic
    `UseWatchlist` is two refined weights plus `OrientLMaxWeight(PreferWatchlist)` and `FIFOWeight(PreferWatchlist)`.

## First checks (07:21-07:27, scratchpad)

Two walls, 60 CPU s:
* nil3_23_32_to_28 392 (twee's chain run proves it in 20.7 CPU s, exp25);
* KK_Kcom_to_aK1 276 (exp11 failed it).

| E mode | 392 | 276 |
|---|---|---|
| `--auto` | ResourceOut | ResourceOut |
| `-xUseWatchlist -tKBO6 --static-watchlist` (4,580 / 7,668 chain hints) | ResourceOut | ResourceOut |

* The watchlist is in use: in 5 s on wall 392 it changes the counts (2,314 processed and 226,902 generated clauses
  against 2,483 and 312,522 without it).
* E is slow on these: about 500 processed clauses a second, with hundreds of thousands unprocessed.

## Set and setting

* exp11's 107 walls (goals107), each with its own .p (sibling lemmas as axioms, cap/tb/tmp) and chain hints
  (h_chain), as twee's exp11 and Prover9's exp16 had them.
* Hints are turned into TPTP clauses (mkwl.py, `lhs = rhs` per hint line).
* E: `-s --proof-object --cpu-limit=60 -xUseWatchlist -tKBO6 --static-watchlist=...`, 1 worker.

## Measures

* Proved (SZS Theorem/Unsatisfiable); proved and not by exp11, exp14-18, exp20 or exp22 (the walls' members); CPU.
* Its conditional yield per CPU hour, against Prover9's 1.62 (exp16 Q). If it proves nothing, it is a genuine
  negative. If it proves walls nothing else did, it joins the portfolio as a variant like p9.

## Results (08:50:51 - 10:38)

**0 of 107 walls: a genuine negative** (hints/exp/exp28_results.tsv).
* All 107 ended ResourceOut at 60 CPU s: 6,436 CPU s in all (1.79 CPU h). Peak RSS was 2.3 GB.
* One wall (aK2_eq_aK3_d 435) failed first on a hint TPTP cannot read (`-e`). mkwl.py now skips such hints (1 of
  its 10,709), and the rerun was ResourceOut too.
* Prover9 with the same chain hints proved 4 of the 107 at 60 s (exp16 Q, 1.62 per CPU hour). E's 95% upper bound
  is about 1.7 per CPU hour (3 proofs in 1.79 h), so the sample cannot rule out a small rate. But it shows nothing
  that would put E beside p9.

## Reading

* E's watchlist guidance (ProofWatch's static form, `UseWatchlist`) does not reach these walls in 60 s. It runs at
  about 500 processed clauses a second, against twee's thousands of rules, with hundreds of thousands of clauses
  unprocessed.
* Not tried: E's dynamic watchlists and its auto schedule with the watchlist, longer limits, and smaller watchlists
  (the 10 nearest siblings' proofs give 3,000-10,000 clauses). None of these is cheap to test in a way that could
  change the verdict, so E stays out of the portfolio.

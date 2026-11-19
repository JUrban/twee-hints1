# Prover9 with Veroff's AIM settings and chain hints on the walls (exp23)

Started 19 Nov 2026, 02:15 UTC. Directory /project/hintwork/exp23; scripts in hints/exp/exp23_*. Part of the portfolio
task (notes/2026-11-18-portfolio-review.md).

## Why

* Production's `p9` level runs Prover9 on its defaults, plus prolog-style variables. That means LPO, back
  demodulation and max_weight 100, with chain hints and 6 sibling lemmas.
* On the walls it is the strongest member per CPU after the 160 s resume: 1.62 new per CPU hour, conditional on the
  earlier members (exp16 Q: 4 of 107, 3 of them not twee's).
* Veroff's own runs for these very problems used other settings. The AIM_REDONE `.in` files (fetched 02:10 for
  aK2_eq_aK3_a and nil3_15) all have:
  `assign(order, kbo). set(lex_order_vars). clear(back_demod). set(restrict_denials). set(para_from_small).
  assign(max_weight,5).` nil3_15 also has `clear(cac_redundancy).` Each file then lists "hints extracted from
  previously found proofs".
* Prover9 sets a hint matcher's weight low (ladr/hints.c adjust_weight_with_hints), so with max_weight 5 the search
  keeps little beyond the hint matchers and very light clauses. This is strict hint following.
* **Tried before, on 15 Nov (REPORT 2af).** On the 2 goals Prover9 had proved with whole-original pools, these
  settings failed both: max_weight 5 used up the search in 4 s, and 40 timed out. That was judged by count on 2 goals,
  with weaker hints than the chain.
* **Why it matters for the portfolio:** a run that uses up its search in a fraction of a second is nearly free. A
  member proving 1% of walls at 1 CPU s a run would make 36 per CPU hour, which would put it first in the ratio order.

## Set and setting

* exp16's 107 walls (walls107), its proven state (UL's first 45,414 solved rows) and its chain hints
  (chain_records.tsv, 10 siblings) and 6+6 sibling lemmas. The only change against exp16's Q arm is the settings.
* p9twee.py `--settings` (new, 19 Nov) appends the directives after the defaults.
* Arms: max_weight 5, 10, 20, 40, in turn, at 60 s, 1 worker (production uses 19).
* Check at 02:15: aK2_eq_aK3_j 382 (which Q proved in 21 s) at max_weight 5 used up its search in 0.30 s (exit code
  2) and failed.

```
cd /project/hintwork/exp23; bash stage.sh
```

## Measures

* Per arm: proved; proved and not by Q (exp16); proved and not by any earlier wall member (exp11, 14, 15, 17, 18, 20,
  22); CPU.
* Its conditional yield per CPU hour, for a place in the cascade's ratio order.

## Results

**V5 (max_weight 5), 02:45: 0 of the first 46 walls at 1,709 CPU s.**
* That is 37 CPU s a run: 28 used up their search space (exit code 2; median 22 s) and 18 hit the 60 s limit. The
  hint matchers are kept whatever their weight, and with chain hints there are many.
* It failed aK2_eq_aK3_j 382 in 0.34 s, a wall the default settings (exp16 Q) proved in 21 s.
* So strict hint following does not suit sibling hints. Veroff's hint lists came from earlier attempts at the same
  goals, which is what lets a max_weight 5 search follow them through.
* **Change of plan (02:46).** V10 and V20 dropped. stage2.sh runs V40, Veroff's settings with a usable weight limit,
  and then V100, his settings at the default weight, which isolates KBO, lex_order_vars, no back_demod,
  restrict_denials, para_from_small and no cac_redundancy from the weight limit. V5 finishes its 107 first.

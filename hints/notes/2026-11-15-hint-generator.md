# A hint generator (GNN2Seq) and instance matching of hints

*Reconstructed on 17 Nov from REPORT 2ah (15 Nov, about 12:00–19:00). Abstract time.*

**Question.** The user, 15 Nov: could the GNN2Seq model of Chvalovský, Suda and Urban ("Neural Conjecturing for
Saturation Theorem Provers", IWIL 2026; github.com/JUrban/E_conj_dev1, branch vampire4) be trained here to
propose new hints from a run's current situation, rather than rank clauses?

**Why it might help.** Ranking only reorders what twee produces. Of the future proof steps of 188 solved test
goals (cut halfway through each proof), the original's pool holds 63% (median pool 4,774 hints). The other 37%
must come from somewhere else. A false generated equation costs little, since twee matches hints by variant
and every critical pair is a theorem.

**Setup.**
* **Model** (hints/gen.py), CPU, 0.58M parameters, about 0.5 s per step on 4 threads after two speed fixes:
  * encoder: gnn.py's symbol-aware graph over the axioms, the goal and the last 256 rules before a cut;
  * decoder: a causal Transformer (2 layers, 4 heads) with cross-attention, writing an equation in prefix order
    (SYM points at a symbol node, VAR picks a variable slot, EOS), with arity-constrained decoding.
* **Samples:** a given log cut before a proof rule; targets are up to 16 later proof rules. Logs are weighted
  by size^0.5. Data: given/train_only, ul45 and loops/UL/given (17,725 logs); the 400 newest round-5 logs
  (sets/ultest) held out.
* **Variants:**
  * gen4 fine-tunes gen2 on novel targets only (`--novel loops/UL/hints`: steps no other goal of the original
    has as a hint);
  * gencopy.py adds a COPY action: point at a term node, then map its variables. Novel steps have a median of
    18 symbols, and the largest context subterm covers 40–70% of a side.
* **Online** (`loop.py --gen-model M --gen-n N`):
  * a failed run saves its axioms and last 256 rules (genctx/; twee-e39 `--print-given-unsolved`);
  * the goal's next resume gets N sampled equations on top of its pool;
  * abs/gen_test.sh on sets/gen200 from snapshot ULsW, fresh 5 s then resume +15 s;
  * GQ is a re-queue-alone control.
* **Instance matching** (twee-e41 `--eqhint-instances`, `--eqhint-instance-factor` 0.1).

**Results.**

Offline, at the halfway cut (exact variant recall of the future steps):

| model, step | n, T | recall | hits not in the pool |
|---|---|---:|---:|
| gen1, 1000 | 200, 0.7 | 4/2,891 | |
| gen2, 3000 | 400, 0.7 | 24/2,891 | 2 of 1,251 missing |
| gen4, 4000 | 400, 0.7 | 9/2,025* | 3 of 1,040 missing* |
| gc1 (copy), 1000 / 2000 / 3000 / 4000 | 400, 0.7 | 37/2,025* at 1000 | 10 / 12 / 12 / 11 of 1,040* |
| gc1, 2000 | 1,600, 0.7 | 51/2,025* | 19 of 1,040 (1.8%)* |

\* on gen4's own 29 test goals.

Online (200 goals):

| arm | fresh 5 s | resume +15 s |
|---|---:|---:|
| GC, control | 0 | 4 |
| GG, gen2 (n 400) | 0 | 2 |
| GC1A, copy model gc1 at 1000 (n 400) | 0 | 4 (+1 −1) |
| GQ, re-queue alone | 0 | 2 |

* GG's hints steer the search: on one goal 243 of 353 became joinable and 117 were matched. None was on a proof
  path. For GC1A's extra goal, none of its 280 generated hints is among the proof's 234 lemmas.
* Instance matching: 637 of 1,866 missing steps looked like instances of a pool hint, mostly of false hints
  (`X0=X1` 783 times, `m(X0,X1)=m(X2,X3)`, `X0=m(X0,X1)`, `ld(X0,X1)=rd(X1,X0)`). One hint matched 270,716 pairs
  in a 5 s run. With clean hints only, instances cover 142 of 2,480 missing steps (3%), at 1.6–5× the wall time.

**Reading.**
* The generator learns the common lemmas the pool already holds (22 of 24 hits). On the steps that matter it
  finds at most 1.8%.
* Online nothing gains. GC1A's +1 is search perturbation, as the re-queue control shows.
* The old pools' false generalised hypotheses (from before HINTS-HYP) are inert under variant matching and
  harmful under instance matching. They remain in the pools and in the 17 Nov expansions.
* Not tried: their full model size (3M parameters, GPU) or more training. The copy model plateaued at step
  2,000–4,000.

**Decision and next.** No generator online; instance matching off (output identical to e22 without it). REPORT
2ah.

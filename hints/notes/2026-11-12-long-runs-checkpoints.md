# Long runs on hard dev goals: the stall cutoff and checkpoints; what was ported from Prover9-new

*Reconstructed on 17 Nov from REPORT 2c–2d (12 Nov 21:00 – 13 Nov 01:00). CPU-time limits.*

**Question.** The user, 12 Nov 20:51: hints help in harder proofs that run longer, and Veroff stops a job when no
hint matches after many given clauses. In 60 s runs, how much do the model and hints give? Does a stall cutoff
pay? Can runs be checkpointed and resumed with new hints? And which Prover9-new branches are worth porting?

**Setup.**
* **The 59** (sets/hard_near, 2026-11-13-lemma-import.md): 6 per dev10 original that no 2 s or 8 s setting solved,
  chosen to have solved goals shortly before them. rm3 never saw them, but was trained on easier goals of the same
  originals.
* **60 s variants:** plain; kNN hints (100); hints = statements of solved earlier goals of the original (50–213);
  hints = all earlier goal statements, solved or not; rule model; combinations; `--eqhint-stall 2000`.
* **Stall cutoff:** `--eqhint-stall N` gives up when no new rule has matched a hint for N rules. HINTSTATS reports
  `lastmatch` and `maxgap`.
* **Checkpoints:** `--load-state F` resumes a run saved with `--dump-state`, with the current hints; it
  re-normalises the hints and re-scores the queue. Plain 30 s with dumps, then the 40 unsolved resumed 30 s more,
  with and without kNN hints. `loop.py --resume` builds a checkpointed loop on it.
* **Prover9-new:** a reading of the branches (packed matchers, generalised hint hash, proof replay,
  target-directed inference, long-run scalability, back-demodulation, indexing).

**Results.**

| setting (60 s) | solved | CPU total |
|---|---:|---:|
| plain | 26 | 2,682 s |
| kNN hints (100) | 28 | 2,623 s |
| statements of solved earlier goals | 26 | 2,494 s |
| all earlier goal statements | 29 | 2,403 s |
| rule model | 36 | 2,110 s |
| rule model + kNN hints | 36 | 2,116 s |
| rule model + earlier-goal hints + kNN hints | **37** | 1,920 s |
| rule model + kNN hints + `--eqhint-stall 2000` | 18 | 777 s |

* Checkpoints: plain 30 s solves 19 (16 MB states). Resumed 30 s more: +8 without hints (27, against one plain
  60 s run's 26), +9 with kNN hints (28, the same as hints from the start). A 1 s run dumped (1.5 MB) and resumed
  solves in 1.4 s against 2.3 s from scratch. A 19 MB state loads in about 1 s and dumps in about 2 s.

| Prover9-new branch | decision |
|---|---|
| packed matchers, lazy hash gate, hint masks (millions of hints) | not ported: with ≤ 10^3 hints, matching costs about 7% after the fingerprint prefilter |
| generalized hint hash | ported as `--eqhint-generalise`; neutral (2026-11-13-enigma-loop.md) |
| proof-parent guidance, proof-recipe replay | covered by self-replay; not useful for new problems |
| target-directed inference | the branch reports a no-go |
| long-run scalability, ancestor store, checkpoints | checkpoints ported as `--load-state`; memory limits far away |
| back_demod_hints, sos back-demodulation | ported as `--eqhint-normalise`, `--eqhint-requeue` |
| paramodulation and back-demod indexes | ported on 14 Nov as the overlap index and interreduction filter (2026-11-14-long-run-speed.md) |

**Reading.**
* In long runs the model gives +10. Hints give +2 to +3 without it and +0 to +1 with it, at CPU-time noise of a
  few problems.
* Earlier goal statements (lines of the original Prover9 proof, close to Veroff's sketches) help a little, mostly
  when unsolved goals are included.
* A 2,000-rule stall cutoff loses half the proofs of runs that reach 20k rules. It would need a much larger N. Later
  replays (2026-11-13-long-runs-stall.md) found no informative cutoff at all.
* Late hints do as well as hints from the start, so a resumed run is a true continuation. On 15–17 Nov fresh runs
  with new hints beat resumes, because a resumed queue was scored without them.
* The 59 favour lemma- and hint-based guidance by construction.

**Decision and next.** `--load-state` and `loop.py --resume` in; no stall cutoff. REPORT 2c, 2d.

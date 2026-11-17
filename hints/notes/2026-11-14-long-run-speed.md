# Long runs slow down: the overlap index and the interreduction filter

*Reconstructed on 17 Nov from REPORT 2v (14 Nov, from about 10:00). CPU timings on a loaded machine (load
35–40 on 112 cores), so ±15%.*

**Question.** The user, 14 Nov: long runs slow down. By how much, why, and what from Prover9-new's long-run
work carries over?

**Setup.**
* `twee --progress N` (twee-e23) prints critical pairs, rules, active rules, queue size, CPU and the
  housekeeping tasks' CPU every N abstract s.
* Test run: the profiled failing nil3_1K goal in the full configuration (rm4t, 2,743 hints), to 640
  abstract s. Profiled at 60 abstract s (12.9k rules).
* Changes:
  * twee-e24, Twee/FPIndex.hs: fingerprint index for overlap partners (Schulz), 8 sampled positions, two
    tries (rule left-hand sides; subterms at overlap positions). The candidates are sorted back into the
    old order, and the renaming bound comes from a multiset of per-rule bounds.
  * twee-e26: backward-demodulation filter for interreduction. An old active is re-checked only if a rule
    added since the last interreduction matches one of its subterms.
  * twee-e27: `--queue-cost K` charges a queue renormalisation pass K pairs per queued pair, so that its
    budget binds under the abstract clock.
* Checks: byte-identical output on 6 solved problems, all counts on a 30k-pair guided run, and a resumed
  state. `TWEE_DEBUG_FILTER=1` for the filter's misses.
* Real workload: sets/u3n150 (the 150 nil3_31 goals), 20 abstract s, online, 6 lemmas, e27 against N3l6's
  e22.

**Results.**
* Old twee, per abstract s of CPU: 3.0 s at 0–10 abstract s (3.7k rules), 8.4 s at 20–30, 26 s at 120–130
  (20k rules, a renormalisation pass of 177 s).
* Under the abstract clock, interreduction and queue renormalisation were free, so they ran without limit:
  33% of the CPU by 130 abstract s. Under CPU time each is capped at 5%.
* Profile at 60 abstract s: trying overlaps 18%, index lookups 18%, building terms 15%, simplify 13%. Partners
  were found by trying every active rule at every position.

| long guided run, CPU | 30 abs s | 70 abs s | 150 abs s |
|---|---:|---:|---:|
| old (e23) | 150 s | 411 s | 1,148 s |
| new (e26) | 87 s | 232 s | 623 s |
| interreduction, old → new | 14 → 4 s | 59 → 10 s | 201 → 24 s |

* To 360 abstract s the new twee settles at 3.2–3.5 s of CPU per abstract s; renormalisation adds about 25%.
* Six solved problems up to 60 abstract s: 1.05–2.6× less CPU.
* u3n150, first 97 goals: e27 solves 69 against 68, in 18% less wall time.
* The overlap index is byte-identical. The interreduction filter is nearly exact: two misses in a 6k-pair run,
  and 2 of 6 test problems differ by 1 rule in about 3,000.
* No gain: larger GHC allocation areas (-A16m/-A64m slower); skipping simplify's copy of normal forms with a
  lazy overlap top term (within noise).

**Reading.**
* Of Prover9-new's long-run work, the memory side (compact stores, mmap ancestors, about 80% less RAM) and fast
  matching against 10^5 hints do not apply: twee uses 0.4 GB at 60 abstract s, and its hint matching is a
  hash lookup. Its indexing ideas do apply.
* Queue renormalisation remains the long-run cost: twee stores only parents and positions, so a pass costs as
  much as making all those pairs again. `--queue-cost` defaults to 0; whether renormalising less often hurts
  guidance was not tested.
* **A reproducibility trap I made.** Since 14 Nov 13:39 the path /project/bin/twee-e22 holds the e27 code.
  It was overwritten again at 16:15 (e31) and 18:44 (the resume fix); the original is twee-e22.orig. So runs
  labelled e22 before and after 13:39 used different binaries. The running cascade, HL and EHL picked up
  the change mid-run. JOURNAL 3 has the table.

**Decision and next.** Overlap index and interreduction filter on by default. REPORT 2v.

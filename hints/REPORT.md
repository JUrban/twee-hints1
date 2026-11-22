# Hint guidance for twee: report

Branch `hints` of the twee repo. Scripts are in `hints/`. Runs and data are
in `/project/hintwork` (not in git).

**Detailed reports.** Each experiment has its own report in [notes/](notes/): the question and who asked, the exact setup, the numbers, the noise, and what they do not show. The index is [JOURNAL.md section 9](JOURNAL.md#9-experiment-reports-hintsnotes). Each section below links the notes it rests on.

**Summary.** On all 51,784 public AIM60k problems, with 4 s per problem:

| system | solved | holdout | CPU h |
|---|---|---|---|
| plain twee, 4 s | 31,060 | 3203 | 28.1 |
| loop, 2 + 2 s | **33,249** (+7.0%) | **3417** (+6.7%) | 24.5 |
| the loop, a third 2 s round | 33,668 | 3473 | 35.0 |
| + Veroff-style online loop, 5 abstract s round (2o)\* | **36,057** (+16.1% over plain) | 3747 | +18.9 |
| + its 20 abstract s round (2o)\* | **39,008** (+25.6% over plain) | 4196 | +167.8 |
| + cascade round, 3 lemmas (2p) | 39,746 | 4291 | +33.7 |
| + cascade round 4, 6 lemmas (2r), 14 Nov 08:31–17:25 | 41,074 (+32.2% over plain) | 4460 | +123.7 |
| + cascade round 5 (2w–2ac), from 14 Nov 17:26; at 15 Nov 07:00 | **43,462** (+39.9% over plain) | **4717** (+47.3%) | +199.5 (+15.4 side workers) |
| + round 5 continued: climbers, proof-step transfer, 30 kNN lemmas (2aj–2an); at 16 Nov 14:00 | **44,710** (+43.9% over plain) | **4898** (+52.9%) | – |
| + round 5 continued: --mix, parental guidance, deep runs with chain hints and their merges (2at–2ay); at 18 Nov 14:37 | **45,510** (+46.5% over plain) | **4991** (+55.8%) | – |
| + round 5 continued: wall experiments merged, a ratio-ordered portfolio of variant levels, 160 s resume (2ay–2az); at 18 Nov 20:16 | **45,608** (+46.8% over plain) | **5003** (+56.2%) | – |
| + variant tiers ordered by live yield (2az); at 18 Nov 23:41 | **45,901** (+47.8% over plain) | **5043** (+57.4%) | – |
| + optional attempts, context-exact restarts (2az); at 19 Nov 04:08 | **46,203** (+48.8% over plain) | **5084** (+58.7%) | – |
| + a 40 s chain level, lemma-set variants at 5 s (2az); at 19 Nov 08:21 | **46,822** (+50.7% over plain) | **5161** (+61.1%) | – |
| + exploration of 5 s members: more lemma sets and counts (2az); at 19 Nov 10:20 | **47,101** (+51.6% over plain) | **5193** (+62.1%) | – |
| + retrained rule models as members, the transfer loop's cascade, rules other runs derived (2av, 2al); at 20 Nov 04:09 | **48,098** (+54.9% over plain) | **5325** (+66.3%) | – |
| + failed runs' derived rules and the same statement in stronger theories, live (2al); at 20 Nov 05:31 | **48,142** (+55.0% over plain) | **5332** (+66.5%) | – |
| + the same, from zero by default (solve_new.sh GIVEN=1, exp40: half1 +282 at 2 hours; 2az); at 20 Nov 09:14 | **48,178** (+55.1% over plain) | **5337** (+66.6%) | – |
| **corrected:** proofs resting on unsound Prover9 proofs removed or re-proved (2ba); step joins; at 20 Nov 12:10 | **48,108** (+54.9% over plain) | **5320** (+66.1%) | – |
| + re-proofs of quarantined goals with trusted lemmas, step joins, the live and transfer loops; at 20 Nov 13:38, all trusted | **48,172** (+55.1% over plain) | **5336** (+66.6%) | – |
| + the 20 s sweep of never-deep unsolved goals, the live and transfer loops (production paused for Z6); at 20 Nov 18:45, all trusted | **48,201** (+55.2% over plain) | **5340** (+66.7%) | – |
| + Z6's two derived-rule proofs, the sweep (production paused); at 20 Nov 23:35, all trusted | **48,208** (+55.2% over plain) | **5341** (+66.7%) | – |
| + the sweep and the side loops, exp44/45's two unique proofs (production paused); at 21 Nov 04:41, all trusted | **48,221** (+55.3% over plain) | **5342** (+66.8%) | – |
| + the sweep, the side loops and step joins, exp48's unique proof (production paused); at 21 Nov 09:56, all trusted | **48,234** (+55.3% over plain) | **5343** (+66.8%) | – |
| + the live transfer loops on the unsolved goals (production paused to 16:50, then restarted at 6 workers); at 21 Nov 18:06, all trusted | **48,238** (+55.3% over plain) | **5344** (+66.8%) | – |
| + production's own loop at 6 workers, its side loops, the sweep's last chunk and Z7's unique proof; at 22 Nov 00:26, all trusted | **48,260** (+55.4% over plain) | **5347** (+66.9%) | – |
| + production's own loop (ul74, 6 workers) and its side loops; at 22 Nov 07:21, all trusted | **48,280** (+55.4% over plain) | **5348** (+67.0%) | – |
| + production with the head class (ul75), the given-rule retry and its lemma-axiom fix (2al, exp56); at 22 Nov 12:41, all trusted | **48,329** (+55.6% over plain) | **5359** (+67.3%) | – |

**Correction (20 Nov 10:40; [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md)).** The counts
from 15 Nov on include proofs that are not proofs.
* p9twee.py's TPTP-to-LADR conversion wrote `~ a = b` as `- a = b`, which Prover9 reads as the equation (-a) = b.
  So every conditional sibling lemma became a false axiom.
* 16 goals in production rested on such Prover9 proofs (P9C, P9L, P9T, exp16), and further proofs used them as
  lemmas.
* Production's solved list was re-verified (2ba). A proof counts if it is older than 15 Nov 08:56, or lies outside
  the 43 theories that contain a bad goal's, or if every lemma it used is recorded and trusted.
* By 12:09 the untrusted proofs had either been re-proved with trusted lemmas only, or left the list. The last 96
  were removed, 20 of them in circular pairs: production had re-proved a quarantined goal from a lemma whose own
  proof used that goal.
* 12:10: **48,108** solved, all trusted. The re-proofs of what is still out continue in loops/REVER4.
* The rows above stay as they were measured. The 48,178 at 09:14 included 16 void proofs and 143 more that rested
  on them (the closure over the lemma records). The rest of the quarantine was proofs without records, not known
  to be void.
* The from-zero arms never ran Prover9 and are not affected.

**On unseen originals** (2aq): the 11 whole holdout originals from
scratch, in 1 hour per batch on 4 workers plus the transfer. Plain twee
at 4 s solves 2,887 of 4,720 (61.2%). With the 13 Nov proofs of the
other originals as context, `hints/solve_new.sh` solves 3,513 (74.4%).
With today's proofs it solves 4,106 (87.0%), against 4,203 (89.0%) for
3.5 days of production. Today's context partly leaks the 8 originals
of one batch, so 87.0% is an upper bound; the other batch (1,085 of
1,320, 82.2%) is nearly clean.

**From zero on the whole benchmark** (2as, 2at): `solve_new.sh` with an
empty context on all 51,784 problems, 12 workers plus the transfer.

* With the current run order (Z4), it proves 15,398 in 10 minutes,
  29,814 in 30 minutes (plain twee at 4 s gets 31,060 in 28 CPU hours),
  35,511 in 1 hour and 37,713 in 2 hours.
* Without the new order and the faster dispatcher (Z0, Z1), it proved
  6,215 and 7,942 in 10 minutes, and Z1 had 36,552 at 2 hours.
* **The 20 Nov system (Z6, 12 workers; 2az):** 15,802 in 10 minutes, 31,133 in 30, 37,378 in 1 hour, 40,238 in 2,
  42,920 in 4 and **44,095 in 8 hours**. Production took 3.5 days and many side methods for its first 44,844.
* **The 21 Nov late-phase default (Z7, 6 workers; [notes/2026-11-21-z7-pair.md](notes/2026-11-21-z7-pair.md)):**
  beside its control (Z7C, the 20 Nov system, also 6 workers), 32,154 against 34,522 at 1 hour, 40,786 against 40,479
  at 3 hours, **42,478 against 41,237 at 4 hours** (+1,241). It loses early, while its retry and head classes take
  workers from the first pass, and gains from about 3 hours. **At 8 hours Z7 had 43,767 on 6 workers, against Z6's
  44,092 on 12** (cross-time). From 4 to 8 hours Z7 gained 1,289 and Z6 1,172. Z7 also proved one goal production
  never had (merged into production).
* Production, with every method since 12 Nov, has **48,329** (22 Nov 12:41).

\* Starts from 33,720 proofs: the third round plus 52 from long runs on
two families (2m). Its time is the summed wall time of the runs, close
to their CPU time.

**Totals over time** (all 51,784 problems; holdout 5,880). From 14 Nov
20:00 on, the counts come from the times the proofs' hints files were
written in loops/UL. Merged proofs count from their merge.

| time | solved | holdout | what ran |
|---|---|---|---|
| 14 Nov 07:00 | 39,008 | 4196 | online loop round done (2o) |
| 14 Nov 08:31 | 39,746 | 4291 | cascade round 3 done (2p) |
| 14 Nov 17:25 | 41,074 | 4460 | cascade round 4 done (2r) |
| 14 Nov 20:00 | 41,369 | 4486 | round 5: resumes without requeue (2w), consider-emulation off (2y) |
| 14 Nov 22:00 | 41,686 | 4512 | proof-line distance (2z) |
| 15 Nov 00:00 | 42,053 | 4558 | stalled goals retried fresh (2aa), sketch climber (2ab) |
| 15 Nov 01:32 | 42,234 | 4576 | fresh run first for goals without one in round 5 (2ab) |
| 15 Nov 03:28 | 42,734 | 4645 | UL13, then retry line gap 21 → 80 (UL14, about 610 an hour) |
| 15 Nov 04:00 | 43,001 | 4680 | A/B 1 of the learned scheduler starts (2ac) |
| 15 Nov 05:15 | 43,272 | 4706 | A/B 1 merged; A/B 2 starts |
| 15 Nov 05:51 | 43,360 | 4709 | A/B 2 merged: the scheduler with 10 s fresh runs wins |
| 15 Nov 07:00 | 43,462 | 4717 | stall: resumes to 80 s, then tail heads first at 320 s (2ac; 8%, dropped at 07:36) |
| 15 Nov 09:05 | 43,502 | 4720 | production cut to 6–12 workers for model tests (2ad); Prover9 side worker from 08:56 |
| 15 Nov 10:12 | 43,661 | | `--retry-knn` (2ae): kNN lemma changes reach the cascade |
| 15 Nov 12:05 | 43,735 | 4745 | unfolded-twee side worker from 11:18 (2af) replaces Prover9's |
| 15 Nov 18:00 | 43,963 | 4784 | 5 s first level (2ag), production 14 workers from 17:31, generator tests (2ah) |
| 15 Nov 22:00 | 44,060 | 4800 | sketch tests with stronger theories, climbing up and down (2aj) |
| 16 Nov 00:00 | 44,110 | 4813 | live up-down climber from 22:07, 12 test proofs merged at 22:50 (2aj) |
| 16 Nov 02:00 | 44,148 | 4820 | learned move policy and theory sampling in the climber (2ak) |
| 16 Nov 04:00 | 44,234 | 4831 | 86 in two hours (climber burst 02:22–03:10 and production; heads first was not its cause, 2ak) |
| 16 Nov 06:30 | 44,434 | 4858 | proof-step transfer (2al): about 110 merged; long climbs on heads 12 of 65; production at 10 workers from 05:12 |
| 16 Nov 10:28 | 44,630 | 4882 | production with 30 kNN lemmas from 07:20 (2am), 152 new; live transfer 21; head climbs 17 of 111 (14.7 CPU h), then the live head climber 4 of 55 (8.5 CPU h) |
| 16 Nov 14:00 | 44,710 | 4898 | production on 16 workers from 11:05 (2an): 49 new by 14:00, about 16 an hour, fresh retries now 0 of 281; live transfer 27 of 35 in all; replays on 4–6 CPUs (2aq) |
| 16 Nov 18:00 | 44,798 | 4914 | production on 12, then 8 workers (ul35 15:10, ul36 17:20); replays of unseen originals (2aq); same statement in other theories (2ar) |
| 17 Nov 00:00 | 44,838 | 4919 | production on 4–6 workers beside the 4-hour from-zero curves (2as) |
| 17 Nov 12:00 | 44,858 | 4921 | --mix 0.25 (ul39, 03:30), e44 (ul40); most CPUs on from-zero runs (Z4, ORG/ORH; 2at, 2au) |
| 17 Nov 20:00 | 44,906 | 4925 | parental guidance in production from 17:25 (ul41, 2av); the half1 A/B PGA/PGB |
| 18 Nov 04:00 | 44,987 | 4933 | deep runs on late goals from 20:03 (exp3, 320 s), the lattice (exp4), 640 s runs (exp5) (2aw) |
| 18 Nov 07:00 | 44,995 | 4934 | 1–4 an hour since 02:00 |
| 18 Nov 08:00 | 45,172 | 4952 | exp3's deep proofs merged at 07:09; 152 cheap 5 s proofs followed by 08:20 (2ax); twee-e61 (ul42, 07:30) |
| 18 Nov 10:00 | 45,385 | 4979 | chain hints at the 80 s level from 08:28 (ul43; ul44 on 8 workers from 09:47) (2ax) |
| 18 Nov 12:00 | 45,486 | 4991 | merged deep proofs: exp8–exp10, and 15 walls from exp11 (2ax, 2ay) |
| 18 Nov 14:37 | 45,510 | 4991 | ul45 (fresh 80 s chain level, 12:02); one gap head (exp12) merged at 12:12 and 6 proofs above it; none since about 13:20 (2ay) |
| 18 Nov 20:16 | 45,608 | 5003 | the variant levels (ul47-ul52) and the wall experiments merged (2az) |
| 18 Nov 23:41 | 45,901 | 5043 | variant tiers by live yield (ul55) |
| 19 Nov 04:08 | 46,203 | 5084 | optional attempts, context-exact restarts (ul56, 289 new in 5 h 50 min) |
| 19 Nov 08:21 | 46,822 | 5161 | the 40 s chain level (ul58, 06:02) and a cascade from about 06:59 across the aK2_eq_aK3 and nil3 families (ul58-ul60, about 400 in 80 minutes) |
| 19 Nov 10:20 | 47,101 | 5193 | lemma-set members at 5 s (ul60-ul63): k100@0, kd@0, k200@0; `--explore` (ul62, 10:05) |
| 19 Nov 14:00 | 47,190 | 5204 | explored members; ENIGMAWatch and the climber as a member (exp31, exp32; 2az) |
| 19 Nov 18:00 | 47,239 | 5211 | the climbs' hints and fill lemmas as member sk@0 (ul70); exp33-exp36 on 4-6 CPUs (2av, 2az) |
| 19 Nov 22:20 | 47,278 | 5214 | retrained rule model m9a@0 (ul71); exp37's replay arms on 9-13 CPUs, production on 8-10 workers (2av) |
| 20 Nov 00:00 | 47,906 | 5295 | a cascade from 22:20: one L1 chain proof (aK2_eq_aK3_1243b 506) and its siblings, whose steps were 22 unsolved goals of other originals (the transfer loop), then their sibling chains (2av) |
| 20 Nov 02:13 | 48,049 | 5319 | the cascade's tail; members m9f@0, m9h@0, m9i@0 (ul72) (2av) |
| 20 Nov 04:09 | 48,098 | 5325 | ul73 (m9e@0); exp38: unsolved goals that are variants of rules other runs derived, 16 proved (2al) |
| 20 Nov 05:31 | 48,142 | 5332 | ul74 (04:15): `--given-scan` (failed runs' derived rules) and the live loop every 5 minutes, which proved 27 of 49 in 0.38 CPU h; production's own runs 9 in 13.9 CPU h (2al) |
| 20 Nov 09:14 | 48,178 | 5337 | production at 4 workers 07:06-09:07 while exp40 ran (its own runs: 0 new in 2,200); the live loop and the transfer loop; ul74 back at 12 workers from 09:08 (2al, 2az) |
| 20 Nov 12:10 | 48,108 | 5320 | corrected (2ba): 1,130 goals quarantined at 10:07, re-proved with trusted lemmas or removed (the last 96 at 12:09); step joins (24); production at 4-12 workers while exp41 and exp42 ran |
| 20 Nov 13:38 | 48,172 | 5336 | 83 of the 125 quarantined goals proved again with trusted lemmas (REVER4 and production), 42 still out; production at 6 workers while exp42 and exp43 ran; all 48,172 trusted (trust.py, 2ba) |
| 20 Nov 18:45 | 48,201 | 5340 | production paused 15:30 for Z6 (from zero on all goals, 41,789 at 3 h); the 20 s sweep (9 of 600), Z6's and production's live and transfer loops; REVER4 stopped 17:33 (0 of 15 at 300 s); all 48,201 trusted (trust.py) |
| 20 Nov 23:35 | 48,208 | 5341 | Z6 from zero ended: 44,095 in 8 hours on 12 workers (Z4 38,044); its 2 unique proofs merged, trusted; the sweep 14 of 1,200 |
| 21 Nov 04:41 | 48,221 | 5342 | production paused for exp44/45 (half2 from zero, 5 h: P2J 21,706, P2H 21,597, P2K 21,147); their 2 unique proofs merged; the sweep 18 of 1,500 and the step-join and live loops 11; all 48,221 trusted (trust.py --exposed) |
| 21 Nov 09:56 | 48,234 | 5343 | production still paused (exp48: P2O 21,940, P2N 21,702 of half2; exp49/50 from 09:45); P2O's 1 unique proof merged (R1dist_to_aa1 614); the sweep 27 of 2,100, the step joins and live loops; all 48,234 trusted (trust.py --exposed) |
| 21 Nov 18:06 | 48,238 | 5344 | 4 new from production's live transfer and derived-rule loops (XFL, GML); exp49/50 rejected; the Z7 pair on all goals (LATE +1,241 at 4 hours); production restarted 16:50 (ul74, 6 workers) and the sweep; all 48,238 trusted (trust.py --exposed) |
| 22 Nov 00:26 | 48,260 | 5347 | 22 new: production's own loop 15 (ul74, 6 workers), its derived-rule transfer (GML) 5, the sweep's last chunk 1 (the sweep is done: 30 of 2,874), Z7's unique proof 1 (merged; merge.py now copies the record); exp52 accepted (--floor-ratio 20); all 48,260 trusted (trust.py --exposed) |
| 22 Nov 07:21 | 48,280 | 5348 | 20 new: production's own runs 16 (ul74, 6 workers), its side loops (transfer, derived rules) 4; Z8 from zero at 4 hours 42,007 (Z7 42,478); production restarted 07:13 as ul75 (`--head-class`); all 48,280 trusted (trust.py --exposed, loops/TRUSTNOW/t0712x, run 07:09-07:21) |
| 22 Nov 12:41 | 48,329 | 5359 | 49 new: production's own runs 23 (ul75, `--head-class`, 6 workers), the given-rule retry of goals the live loop had given up on 18 (exp56: newest hits, then the failed runs' lemma axioms named by proven goal), the live given-rule loop 7 (with both changes from 12:06), the transfer loop 1; exp54 ended (+8, not adopted); all 48,329 trusted (trust.py --exposed, loops/TRUSTNOW/t1240, run 12:41-12:50) |

From 15 Nov 05:30 the rate fell from hundreds an hour to 50–100. The
cheap new contexts are used up; 58% of the unsolved goals sit behind the
95 originals' tail heads (2ac).

On 18 Nov the merged deep proofs and the chain hints raised it again, to
about 130 an hour from 07:00 to 10:00 (2ax). Since then it has fallen
back to tens an hour, and to none after about 13:20 (2ay).

The loop's first round is twee with a learned ENIGMA-style rule filter
plus kNN hints from training proofs. Its second round adds hints from its
own proofs and proven sibling goals as lemmas. The online loop then runs
every goal left in goal order. Each new proof joins its original's hint
pool and the lemma source for the next runs at once, and an original is
given up after 30 failures in a row (2o). On hard holdout problems
at 60 s, it solves 56 against 44 for plain twee. Section 3 says where the
gains come from, and why hints from other problems help little in long
runs. Section 5 has the commands.

## 1. What is implemented

### Equation hints in twee (`src/Twee.hs`, `executable/SequentialMain.hs`)

* **Hint input.** `--hints-file F` reads one hint per line as
  `lhs<TAB>rhs[<TAB>factor]`, in TPTP term syntax. Uppercase names are
  variables. A fast hand-written parser is used, because putting hints into
  the TPTP problem (`cnf(h,axiom,'$hinteq'(l,r))`, also supported) costs
  about 0.12 ms per hint in jukebox. Hints with symbols that are not in the
  problem are dropped.
* **Matching** follows Prover9's equivalence match. A critical pair matches
  a hint if its simplified equation is a variant of the hint, in either
  orientation. The match is done on canonical forms stored in a `Map`. A
  matching critical pair gets the score `s * eqhint-factor + eqhint-weight`
  (factor 0.01 by default), so it is selected next.
* **Back-demodulation of hints** (Prover9's `back_demod_hints`). Live hints
  are re-normalised with the oriented rules every 20 ms, within at most 5%
  of the time. Every form a hint has had is remembered. A hint that
  normalises to `t = t` counts as joined.
* **Goal constants.** Twee flattens goals by default: `ld(x0,e)` becomes a
  constant `ld2`, and so on. Without flattening twee solves 1176/3052 on
  dev10 instead of 1753, so flattening must stay on. Before matching,
  flattening constants are replaced by their definitions and skolems by
  variables. Hints are stored in this general form, so they also transfer
  between problems.
* **Consider-emulation.** If the fingerprint matches but the simplified
  equation does not, the steps of `allSteps` (oriented and unoriented
  rewriting, connectedness) are run on the critical pair, and the rules it
  would produce are looked up. This catches pairs that differ from the hint
  only by ordered rewriting with permutative rules such as
  `t(t(x,y),z) = t(t(x,z),y)`.
* **Fingerprint prefilter.** A hash of the symbol multiset of an equation
  is invariant under renaming, orientation and permutative rewriting. Only
  critical pairs whose fingerprint occurs among the hints are canonicalised
  and looked up. This cut the matching overhead from about 30% to about 7%
  of throughput.
* **Hint-triggered requeue** (`--eqhint-requeue F`). This is Prover9's
  back-demodulation of sos. Twee keeps queued critical pairs in the form
  they had when they were generated. When the rule that would normalise a
  pair into a hint arrives later, the pair would otherwise never match.
  The new task re-simplifies the queue whenever new rules have matched
  hints, using at most the fraction F of the time.
* **Output and diagnostics.**
  * `--print-hints` prints all lemmas of the raw proof, after flattening
    definitions are eliminated, plus the goals.
  * `--track-hints F` reports when rules match the given equations, without
    changing the search.
  * `--eqhint-debug` traces matching critical pairs.
  * `HINTSTATS` line: hints, live, joined, matched, tracked.
* **Per-hint factors.** The optional third column of the hints file
  overrides the boost factor for that hint.

### Scripts (`hints/`)

*Proofs (20 Nov 15:03, the user's request).* The loops search with `--no-proof`, so until now their proofs were never
printed. Now every proved twee run in loop.py is queued for a rerun with the proof printed (DIR/proofq/,
exp/proofq.py), and the proof is kept in DIR/proofs/<goal>. (21 Nov 23:58) `--no-proof` saves no CPU in twee's
search: it only gates the presentation after a proof, and 42 proved runs took 61.1 CPU s with the proof against
61.2 s without, with the same output otherwise ([notes/2026-11-21-proof-cost.md](notes/2026-11-21-proof-cost.md)). So the reruns cost a second run per
proved job (about 3 CPUs at -j 3); printing the proof in the search run would cost nothing. Left to the user.

* `run.py`: parallel runner.
* `loop.py`: Veroff-style hint loop. Round 0 runs without hints, and later
  rounds run every unsolved problem with hints. Pools can be `original`,
  `all`, or `knn:K:N`.
* `transfer.py`: leave-one-out transfer benchmark.
* `hintsel.py`: kNN hint selection.
* `feats.py`: term-shape features.
* `diag2.py`: replay diagnosis, showing which hint was late and its parents.
* `mkhints.py`: generalised hint files from a twee proof.
* `given.py`: given-rule logs labelled for training (`--print-given`).
* `rulemodel.py`, `enigfeats.py`, `lgb2bin.py`: the ENIGMA rule model
  (section 2b).
* `lemmas.py`: lemma import (2g). `sketch.py`, `chainhints.py`: sketches.
* `summary.py`: solved problems per AIM60k part.

## 2. Results so far

*Notes: [notes/2026-11-12-hint-selection.md](notes/2026-11-12-hint-selection.md), [notes/2026-11-12-hints-dev10.md](notes/2026-11-12-hints-dev10.md).*

The dev10 set has all 3052 goals of 10 originals of mixed difficulty:
`aK1_to_aK2 mbol_com aa1_15 aK2_eq_aK3_q a_of_aa aa2_to_aa3 nil3_15
aa1_45_c Ka_eq_aK3 aK2_eq_aK3_b`. All runs use 20 processes in parallel.

| system on dev10 | solved |
|---|---|
| E 2.6, 1 s (README baseline) | 1036 |
| Prover9, 1 s (README baseline) | 1112 |
| twee 2 s, no hints | 1753 / 1771 (two runs) |
| twee 2 s `--no-flatten-goal` | 1176 |
| loop L1: 2 s, pool = all proofs of the same original | 1771 → 1833 → 1835 → 1836 |
| loop L2: 2 s, kNN pool (30 neighbours, 100 hints) | 1771 → 1836 → 1845 → 1848 |
| L2 continued at 8 s (two rounds) | → 1944 → 1955 |
| no hints: 2 s, then 8 s on the unsolved | 1771 → 1928 |

### Self-replay: a problem rerun with hints from its own twee proof

`aK2_eq_aK3_b__goal_315`, 89 generalised hints:

| setting | rules | time |
|---|---|---|
| no hints | 2283 | 2.4 s |
| hints, before goal-constant expansion | 2221 | 2.3 s |
| + goal-constant expansion | 1192 | 1.2 s |
| + requeue 0.1 | 334 | 0.16 s |

The diagnosis tool showed what was still late before requeue. The critical
pairs were generated before the rule that normalises them into the hint
existed, and they were not looked at again.

### Transfer benchmark T1

Leave-one-out with hints from the other 1835 proofs, 4 s limit. The set has
176 problems solved in 0.8–2 s plus 100 problems unsolved at 2 s.

| hint selection | slow-solved (176) | PAR2 | unsolved (100) |
|---|---|---|---|
| none | 176 | 1.51 | 6 |
| all of the same original (~1000 hints) | 164 | 1.84 | 11 |
| 10 nearest by proof line | 171 | 1.14 | 8 |
| kNN 30 neighbours, top 100 hints | 175 | 0.71 | 10 |

### Why pools from all proofs of an original fail

Offline over 200 solved problems: the pool of all other proofs of the same
original contains 71% of the lemmas of the problem's own proof, but only
2.4% of the pool's hints are in that proof. Every matched hint becomes a
rule at top priority and then forms critical pairs with every other rule.
In one traced case, `aa1_45_c__goal_224`, 223 irrelevant hint rules came
first and delayed the real proof's lemmas by about 230 rules.

kNN by goal-statement similarity (idf-weighted Jaccard on term shapes of
depth ≤ 3) across all originals does better: recall 0.74 and precision 0.26
at 100 hints. With 400 hints, recall is 0.81.

### Hints against extra time

Plain twee at 2 s and then 8 s on what is left solves 1928. The hint loop
with the same final limit solves 1945 after its first 8 s round. Hints add
only +17 at these limits; the union is 1958. Most dev10 goals are solved
early or not at all, so at 2–8 s there is little room for hints. Hints
should matter more in long runs that would otherwise lose their way (see
the stall cutoff below).

### Learned hint ranking (ENIGMA features, LightGBM)

`lgbsel.py` reranks the kNN candidates with LightGBM. A row has pair
features (kNN score, frequency) plus ENIGMA-style features of the hint and
of the goal. Training and testing are on different originals.

| hints | recall@100 | precision@100 |
|---|---|---|
| kNN | 0.838 | 0.154 |
| LightGBM rerank | 0.849 | 0.156 |
| all 600 kNN candidates | 0.856 | |

Reranking gains little, because kNN candidates already cap recall at 0.856.
The missing lemmas are in no neighbour's proof.

## 2b. ENIGMA for twee: a learned rule filter

*Notes: [notes/2026-11-12-rule-model.md](notes/2026-11-12-rule-model.md).*

ENIGMA's "enigmatic" featurizer (E prover, ai4reason `enigma` branch,
`che_enigmaticvectors.c`) is ported for unit equations:

* vertical walks of length 2–3 from the `=` root (variables as `*`)
* horizontal features `f.head(arg1)...`
* symbol counts and symbol max depths
* length statistics
* the conjecture as a separate goal block
* overlap counts between rule and goal, and log(rule number)

Python (`enigfeats.py`) and Haskell (`src/Twee/Enigma.hs`) compute the same
features. On test rules, twee's raw scores equal LightGBM's exactly.

**Training data.** `--print-given` logs every rule added. `given.py` labels
each rule: 1 if it is a proof lemma, 0 otherwise, -1 for axioms. Round 0 of
dev10 gives 1771 runs, with 26.7k positive and 605k negative rules.

**Offline**, on 3 held-out originals (253 problems):

* AUC 0.969.
* At threshold 0.1, 97.9% of proof rules are kept and 68.5% of the others
  are rejected.
* The rules up to the proof shrink to 36%.

**In twee** (`--rule-model M --rule-vocab V --rule-goal G`), a critical
pair that would become a new rule is first scored. If the predicted
probability is below the threshold, the pair goes back into the queue once,
with its score times the penalty (default 2). Hint-boosted pairs come back
at once, because their scores are tiny.

The test set is the 345 problems of the held-out originals (aa1_45_c,
mbol_com, nil3_15) that are unsolved at 2 s, run at 8 s:

| system | solved |
|---|---|
| twee, no guidance | 42 |
| hint loop, all rounds (2 s ×3 + 8 s) | 46 |
| rule model, threshold 0.1 | 57 |
| rule model, threshold 0.2 | 40 |
| rule model + kNN hints (100) | **68** |
| union of all runs | 83 |

mbol_com gets 0 with the model, against 4 without. Its theory is unlike
the 7 training originals. Next step: train on many more originals.

### More training data, and ProofWatch

* **Model rm2** is trained on 30 more training originals (12,414 problems;
  7059 solved at 2 s without guidance) plus dev10's 7 training originals.
  On the 3 held-out originals: AUC 0.975 (0.969 before). At threshold 0.1
  it keeps 99.5% of proof rules and rejects 61.6% of the others. Online on
  the 345: 65 solved at threshold 0.1 and 69 at 0.2, both with kNN hints.
  mbol_com is still weak (0–2 against 4). The union of all variants is 93.
* **ProofWatch** (`--eqhint-watch F`). Each hint carries the neighbour
  proofs it comes from, as a 4th column of the hints file. Its factor moves
  from F to its own factor (0.01) as its best source proof gets matched.
  With F = 0.3, on the same 345 with rm2: 67 solved, against 69 without
  (+2/−4). This setting does not help.

### Fixes after the first holdout run, and tuning

The first holdout loop (H1: rm3, threshold 0.2, penalty 2, text model)
solved 3132 at 2 s against 3049 for plain twee. But it lost 123 problems
that plain twee solves, many in under 0.1 s. Two causes:

* **Loading the text model** took about 0.25 s per run, because Haskell's
  `read` is slow on about 100k numbers. `lgb2bin.py` now writes a binary
  forest. It loads in 0.07 s and gives identical predictions.
* **Repeated deferral.** The same equation, reached through different
  critical pairs, was deferred up to 18 times. Each equation is now
  deferred at most once.

Tuning on dev (all 818 goals of the 3 held-out dev10 originals, 2 s, rm2):

| setting | solved |
|---|---|
| plain | 473 |
| threshold 0.1, penalty 2 | 498 (+27/−2) |
| threshold 0.1, penalty 3 | 499 (+29/−3) |
| threshold 0.2, penalty 1.5 | 490 |
| threshold 0.2, penalty 2 | 488 |
| threshold 0.05, penalty 2 | 488 |
| threshold 0.5, penalty 1.2 | 476 |

Parent features (ENIGMA's parental blocks, or a cheap Deepire substitute)
reach AUC 0.971 against 0.969 without them, so they are left off for now.

## 2e. Holdout evaluation (AIM60k `holdout.names`, 5880 problems)

The README reserves the holdout split for reporting. Nothing below is
trained or tuned on it:

* Model rm3 is trained on the 30 extra training originals plus dev10,
  with every holdout problem removed (`given/train_only`).
* The hint pool starts as the proofs of those training problems
  (`hints/train_pool`, 8562). The loop then adds the holdout problems it
  solves itself, as a Veroff loop would.
* Threshold and penalty were tuned on dev originals.
* *Correction, 17 Nov:* the design was not quite clean. dev10, where the
  first choices were made (kNN 30:100, requeue, the model's settings),
  holds two whole holdout originals (aK1_to_aK2, a_of_aa: 380 problems)
  and 66 moved late goals. The tuning set of 818 held 22 moved late
  goals. The training data and hint pools were clean
  ([notes/2026-11-12-holdout.md](notes/2026-11-12-holdout.md)).

All runs use 20 processes in parallel on a 112-core machine.

| system | 2 s | after the 8 s round(s) |
|---|---|---|
| E 2.6, 1 s (README) | 1853 | |
| Prover9, 1 s (README) | 1911 | |
| H0: twee, plain (2 s, then 8 s on the unsolved) | 3049 | **3385** |
| H3: twee + rule model | 3105 (+126/−70) | (stopped after 2 s) |
| H2: twee + rule model + kNN hints, loop 2, 2, 8, 8 s | 3177 (+190/−62) → round 1: 3221 | round 2: 3505 → round 3: **3551** |

Against H0 at the same final limit, H2 gains 195 and loses 29; the union
is 3580 (+4.9% over plain twee). Round 3 runs 8 s again, with hints
refreshed from the loop's own new proofs, and adds 46. That is the hint
loop's own contribution at a fixed time limit.

Most problems the model loses at 2 s are boundary cases solved by plain
twee in 1–2 s. The model's overhead is now about 6% of throughput, after a
binary model file, a dense feature array and hashed feature names.

## 2f. The ENIGMA loop, and generalisation matching

*Notes: [notes/2026-11-13-enigma-loop.md](notes/2026-11-13-enigma-loop.md).*

* **ENIGMA loop.** Guided runs (rm3, kNN hints, 4 s) on the 5355 training
  problems that plain twee leaves unsolved at 2 s solved 757 of them.
  Their given-rule logs (`given/tr30_g1`) are added to the training data
  of model rm4. These are harder proofs than the plain 2 s ones, from the
  guided search the model has to work in.
  * On 600 random holdout problems still unsolved after H2: 8 for rm3 and
    8 for rm4 at 8 s (4 different each), too few to tell.
  * On the 345 hard dev goals (`ho3_unsolved`, 8 s, model only, no hints):
    rm3 60, rm4 **63** (+4/−1).
  Both rm3 and rm4 were trained on the solved goals of these three
  originals (not on the 345 themselves), so this compares the two models
  in the setting of a loop over one batch, not on unseen originals.
  rm4 is used from here on.
* **Run-to-run noise.** Twee's background tasks are time-based, so runs
  differ. rm4 repeated on the 345 gives 61 against 63 (+0/−2). Differences
  of ±3 there are noise.
* **A second turn (rm5)** adds the 2687 training-split problems that the
  full-benchmark loop (below) solved with rm4 in 0.3–2 s, giving 2.7M rows
  and 290k positives. It does worse on the 345: 58 against 61–63 for rm4
  (+2/−7). More guided proofs of medium difficulty do not help as they
  are. The model may need more capacity or a retuned threshold for the
  larger data; rm4 stays.
* **More capacity (rm4b):** rm4's data with 400 trees of 127 leaves (four
  times the model). On the 345: 65 against 61–63 (+9/−7), within noise.
  Loading takes 0.15 s instead of 0.07 s. Not worth it at short limits.
* **Generalisation matching** (`--eqhint-generalise`, after Prover9-new's
  generalized hint hash). Each hint is also stored with its one-step
  generalisations (one proper non-variable subterm of one side replaced
  by a fresh variable), so a critical pair more general than a
  hint gets the hint's boost. On the 345 with rm2 and kNN hints at 8 s:
  68 against 69 without it. Neutral, left off.

## 2g. Lemma import: proven sibling goals as axioms

*Notes: [notes/2026-11-13-lemma-import.md](notes/2026-11-13-lemma-import.md), [notes/2026-11-17-lemma-circularity.md](notes/2026-11-17-lemma-circularity.md).*

All goals `X__goal_N` of one original `X` have the same axioms (checked).
A sibling goal that twee has proven is therefore a theorem of the theory
and a sound extra axiom for the others. This is what CASC's LTB division
allows within a batch: conjectures proven earlier may be used later. It
leans on the batch structure more than hints do, so it is reported
separately from the hint results.

* `lemmas.py` adds the statements of up to M proven siblings, those with
  the nearest goal numbers below N (unit equations only), to the problem.
* `loop.py --lemmas M` does this in rounds after the first, with lemmas
  proven in earlier rounds only. So the chain of lemma proofs is
  well-founded, and each final proof can be expanded into one from the
  axioms. In the training logs, lemma axioms are labelled as axioms.

On the 59 hard dev goals at 20 s (lemmas from the 1966 dev10 problems
solved at 2–8 s):

| setting (20 s) | solved |
|---|---|
| plain (the 60 s run, solved within 20 s) | 12 |
| plain + 10 lemmas | 21 |
| rm4 | 19 |
| rm4 + 3 lemmas | **28** |
| rm4 + 10 lemmas | 27 |
| rm4 + 30 lemmas | 26 |
| rm4 + 10 lemmas + kNN hints | 27 |

Lemmas and the rule model add up. Three lemmas are enough, and more do not
help. Hints add nothing on top.

On the 345 hard goals of the three dev originals at 8 s, lemmas come from
the 473 goals plain twee solves at 2 s, and every goal gets three. rm4
solves 63 and rm4 + 3 lemmas 68 (+10/−5): a smaller gain than on the 59.
Those 59 were chosen to have solved goals shortly before them. With 6
lemmas: 70 (+6/−4 against 3), within noise.

* **Which lemmas are used.** Most proofs that had lemmas use at least one
  (46 of 56 on the hard holdout set below), and not only the nearest: the
  third nearest is used most often there (29).
* **Lemmas into a resumed run** (`--load-state` adds the problem's new
  axioms). *Corrected 13 Nov:* the first test said this does not work, but
  that was a bug. A saved state stores each symbol with its precedence and
  id, and both depend on the problem text. A problem with new lemmas
  therefore got a second signature under the same names, and its lemmas
  and hints could never reach the saved rules. twee-e20 makes the problem
  reuse the saved symbols and recognises new axioms by equation, not name.
  Redone on three goals that 13 lemmas solve (2 s states, 4k critical
  pairs):

  | goal | resumed, old binary | resumed, e20 (after resume) | fresh with lemmas | fresh without |
  |---|---|---|---|---|
  | aK2_eq_aK3_d__goal_353 | fails (+40k) | 134 | 288 | fails at 40k |
  | aK2_eq_aK3_d__goal_354 | fails (+40k) | 55 | 456 | fails at 40k |
  | aK2_eq_aK3_d__goal_357 | fails (+40k) | 13.6k | 12.9k | fails at 40k |

  So resumed runs now take new lemmas about as well as fresh runs, and lemma
  rounds can continue saved searches instead of restarting them.

### Sketches (Veroff): hints from proofs under extra assumptions

Veroff's sketches are proofs found with extra assumptions; their steps then
serve as hints for the real problem. Here the extra assumptions are the
nearest sibling goals below N, proven or not (`sketch.py`). That is
unsound as a proof but sound as a source of hints.

* On the 59 at 5 s, with rm4: 15 sketch problems are proven with 3 assumed
  siblings, and 19 with 10. Six of those goals are unsolved by rm4 + 3
  proven lemmas at 20 s.
* The real run (rm4 + 3 proven lemmas, 20 s) with these sketch hints: 28,
  the same as without them. The 6 stay unsolved. A sketch covers only the
  stretch from the assumed siblings to the goal. Deriving the assumed
  siblings is the hard part, and it is not covered.
* **Chained sketches.** Sketch every unsolved dev10 goal (389 of 1204
  proven at 5 s with 10 assumed siblings). The hints for goal N are then
  the sketch hints of N and of the sketched siblings in [N−30, N], nearest
  first, at most 400 (`chainhints.py`, 154 on average). Result: 29
  against 28 (+2/−1), within noise. Only a third of the links have
  sketches, so the chains have gaps.

## 2h. The full public benchmark (all 51,784 problems, 4 s per problem)

*Notes: [notes/2026-11-13-full-benchmark.md](notes/2026-11-13-full-benchmark.md).*

Every system gets at most 4 s per problem:

* plain twee: one 4 s run, 8 in parallel;
* the loop:
  * round 0: 2 s with rm4 and kNN hints from the start. The pool is the
    training-split proofs (`train_pool` 8562, `tr30_g1_pool` 757).
  * round 1: 2 s on the unsolved, with the pool extended by the loop's own
    round-0 proofs. 12 in parallel.
* the loop + lemmas: the same round 0, then round 1 with 3 proven siblings
  as axioms as well (section 2g).

| system | train | devel | holdout | all | CPU h |
|---|---|---|---|---|---|
| E 2.6, 1 s (README) | | | | 18,369 | |
| Prover9, 1 s (README) | | | | 18,973 | |
| twee, plain, 4 s | 25,416 | 2,441 | 3,203 | 31,060 | 28.1 |
| loop, round 0 only (2 s) | 26,144 | 2,551 | 3,257 | 31,952 | 13.5 |
| loop, 2 + 2 s | 26,493 | 2,578 | 3,306 | 32,377 (+4.2%) | 24.8 |
| loop + lemmas, 2 + 2 s | 27,190 | 2,642 | **3,417** | **33,249 (+7.0%)** | 24.5 |

* Against plain 4 s, the loop with lemmas gains 2530 and loses 341, of
  which 247 plain twee solves in 2–4 s. On holdout it is +265/−51. The
  union of the two is 33,590.
* Round 0 alone, at half the time limit, already solves more than plain
  twee at 4 s.
* Lemmas triple what round 1 adds (1297 against 425 new), at the same CPU.
* **A third round** (2 s, lemmas and hints from rounds 0–1) adds 419,
  giving **33,668** (holdout 3473, +8.4% over plain 4 s), with up to 6 s
  per problem.
* **Speed.** Problems solved within a time, holdout only:

  | within | plain | loop round 0 |
  |---|---|---|
  | 0.25 s | 2309 | 2697 |
  | 0.5 s | 2541 | 2924 |
  | 1 s | 2776 | 3067 |
  | 2 s | 3005 | 3248 |

  Within 1 s the loop solves more than plain twee within 2 s.
* **What is clean.** On the train split, rm4 and the kNN pool contain
  proofs of many of these very problems' siblings (and rm4 of many 2 s
  proofs of the problems themselves), so the train and devel columns are
  optimistic. Holdout is clean as the README defines it:
  * no holdout problem is in any training data or pool;
  * its originals are unseen, except the 1160 late goals moved from
    training originals in step 2 of the split;
  * the loop learns from holdout only what it proves itself during the
    loop.

### Long runs on hard holdout problems (60 s)

The set is 300 random holdout problems that neither plain twee at 4 s nor
the loop (2 + 2 s) solved. Lemmas are 3 proven siblings, from everything
proven in the full-benchmark runs.

| setting (60 s) | solved | vs plain | CPU h |
|---|---|---|---|
| plain | 44 | | 4.7 |
| rm4 | 53 | +11/−2 | 4.5 |
| plain + 3 lemmas | 50 | +12/−6 | 4.5 |
| rm4 + 3 lemmas + kNN hints | **56** (+27%) | +17/−5 | 4.4 |

The union with plain is 61. On unseen originals at long times, the model
and the lemmas each give about +6 to +9 net, and together +12.
**A final 60 s round on all remaining holdout problems.** It covers the
2366 holdout problems that no 4–6 s run solved (rm4, 3 lemmas, kNN hints,
2 hours on 18 cores) and solves 399. That brings
holdout to **3913 of 5880 (66.5%)**. The count includes 40 problems
solved only by the plain 4 s run. For comparison, plain twee at 2 s and
then 8 s solved 3385.

No time-sliced portfolio beats the guided run alone. Plain for 15 s
followed by the guided setting for 45 s solves 50, and rm4 for 40 s
followed by lemmas for 20 s solves 56.

## 2i. Control: a Prover9 hint loop on two families

Prover9-new (master, built from `/project/Prover9-new`, default settings)
in the same loop as twee (`p9loop.py`). The families are aa1_15 (198
goals) and aK2_eq_aK3_q (273 goals), 471 problems, with rounds of 2, 2, 2
and 8 s. Hints are the positive proof steps of all solved goals of the
same original, with skolems generalised to variables (Veroff's practice).
They are given as `formulas(hints)`, about 14 per proof. twee runs plain,
without the model, with the same pool (`--pool original`).

| | round 0, 2 s | +2 s, hints | +2 s, hints | +8 s, hints |
|---|---|---|---|---|
| Prover9 | 240 | 248 | 270 | **288** |
| twee | 347 | 361 | 362 | **376** |

Controls on the round-0 failures, 8 s each:

| control | Prover9 | twee |
|---|---|---|
| no hints | +3 of 231 (243) | +20 of 124 (367) |
| hints = statements of all earlier goals of the original, solved or not | +11 | |

* **Prover9 is a good hint user.** Without hints, four times the time
  gives it almost nothing (+3). Proof-step hints from solved siblings give
  +48, a 19% gain, and the gain grows as the pool grows (+8, then +22).
  Goal statements alone are much weaker hints (+11) than proof steps.
* **Twee gains less from hints:** +29 from the loop against +20 from the
  same time without hints.
* **In absolute terms twee without hints (367) is far ahead of Prover9
  with the hint loop (288).** Prover9's base search on these problems is
  the limit, not its use of hints. Prover9 was run with defaults; Veroff's
  tuned settings might do better.

## 2j. Skolem-free hints, and conditional goals

*Notes: [notes/2026-11-13-hyp-hints-abstract-time.md](notes/2026-11-13-hyp-hints-abstract-time.md).*

Veroff turns each proof into a strictly forward, demodulation-free (SFDF)
proof before using it as hints. He iterates Prover9 until the proof no
longer uses the denial, so the hints contain no skolems and carry over to
other problems.

* **Twee gets skolem-free hints without this work.** Completion never
  draws inferences from the negated goal; the goal is only rewritten.
  Every proof lemma therefore follows from the axioms plus the flattening
  definitions, which are conservative. Eliminating the definitions and
  replacing the skolems by variables gives general lemmas.
  * Check: 40 random solved problems, all 814 of their pool hints posed as
    conjectures from the problem's axioms. 807 were proved by twee within
    15 s, and one more within 90 s.
  * The other 6 are false, e.g. `m(X0,X1) = m(X2,X3)`.
* **The hole: conditional goals.**
  * 9,052 of the 51,784 public problems (17%) have goals of the form
    `A = B → C = D`.
  * The hypothesis becomes a ground clause with skolems. Lemmas derived
    from it, and the conclusion itself, hold only for those skolems.
  * Generalising them gave the 6 false hints.
  * In 300 solved conditional problems, 27% of the hints depended on the
    hypothesis.
  * Proofs stayed sound: hints only steer the search, and lemma import
    takes only unit-equation goals. The pools got noise, however.
* **Fix (twee-e14).**
  * `--print-hints` traces each lemma's derivation, and lemmas and goals
    that use a hypothesis go into a new `HINTS-HYP` section.
  * Pools skip that section, while rule-model labels still count those
    lemmas as proof lemmas.
  * `cleanpool.py` cleans existing pools. It removed 19% of the hints of
    the conditional problems in `train_pool` (2,965 hints) and 3% in
    `tr30_g1_pool`.
* **Effect: none measurable.**
  * Test set: the 310 conditional holdout problems that plain twee does
    not solve in 4 s. Settings: rm4 + kNN hints (30 neighbours, 100 hints)
    from `train_pool` + `tr30_g1_pool`, 8,000 critical pairs each
    (`--abstract-time 2000 --max-time 4`).
  * rm4 alone solves 11. With the old pools it solves 17, and with the
    cleaned pools also 17: the same 17 problems.
  * The time-limited version of this test (4 s on a loaded machine) gave
    20 against 18. The two extra solutions of the old pools were finished
    at 4.0–4.1 s, so they were load noise (see section 2k).
  * kNN hints do help on conditional problems (+6 of 310). The false
    generalised hints were noise, not harm, at this budget.
* **Demodulation-free hints do not fit twee.** Twee normalises every
  critical pair before it can match a hint, so unnormalised intermediate
  steps would never match. Twee's counterpart of SFDF robustness:
  * back-demodulated hints, with every form a hint has had remembered;
  * requeue of the passive queue.

  Self-replay goes from 2,283 to 334 rules with them (section 2).
* **The Prover9 control (2i) did not use SFDF hints.** `p9loop.py` drops
  the denial-side clauses instead.
  * Of 120 Prover9 proofs in those families, 99 were already strictly
    forward; the other 21 had 27 denial-side steps.
  * 327 of the 734 steps used demodulation, so SFDF hints might help
    Prover9 somewhat.
  * The two families have unit goals, so the hypothesis problem does not
    affect them. On conditional goals, `p9loop.py`'s skolem
    generalisation would have the same flaw.
* **A cheaper reorientation than iterating the prover.**
  * A twee proof is already a chain of single rewrite steps per lemma and
    for the goal. Each prefix `s = t_i` follows from `s = t_{i-1}` by one
    paramodulation.
  * So an SFDF derivation can be read off the proof in linear time, with
    no search; the same holds for Prover9's denial chain read backwards.
  * For a conditional goal, "forward" means from the axioms plus the
    hypotheses, which is what the dependency trace marks.

## 2k. Abstract time

Earlier comparisons in this report used time limits on a shared machine.
The load from other jobs was up to about 22 on the 20 CPUs. Both the
`--max-time` limit and twee's housekeeping tasks (hint normalisation,
requeue, interreduction) follow CPU time, so results depended on the load.
That is part of the ±3 noise on 345 problems (section 2f).

* **Implementation (twee-e15).** `--abstract-time N` makes the clock count
  critical pairs considered, with N of them per second. Both `--max-time`
  and the task scheduling follow this clock.
* **Determinism.** Runs now repeat exactly: two problems, 6 runs each,
  gave identical results and counts.
* **Calibration.** On 60 holdout problems twee considers a median of 1,800
  critical pairs per CPU second (quartiles 1,700 and 2,300). So
  `--abstract-time 2000` keeps the old budgets roughly comparable.
* **Reporting.** Twee prints `WORK considered=N rules=M`, and `run.py`
  stores it as a fourth column. `run.py --wall-factor 5` (and `loop.py`
  when its args contain `--abstract-time`) allows the wall-clock safety
  limit to be exceeded.
* **Real time is a cost, measured separately.** Abstract time leaves out
  the overhead of the rule model and of hint matching. That overhead
  should be reported on its own, measured on a quiet machine.

## 2l. Axiom groups: lemmas and hints across originals

*Notes: [notes/2026-11-13-axiom-groups.md](notes/2026-11-13-axiom-groups.md).*

Lemma import (2g) used only proven siblings of the same original, because
those have the same axioms. But originals share axioms too.

* **Facts** (all 51,784 public problems):
  * The 129 originals use 68 distinct axiom sets. Axioms are constant
    within an original.
  * The largest groups of identical axioms have 15 originals (7,116 and
    7,200 goals), 13 (5,426) and 6 (3,557).
  * 66 of the 68 axiom sets have strict subsets among the others (127
    pairs). A theorem of a weaker theory holds in the stronger one. For
    example, mbol_KK_a has 279 goals with the same axioms, but 12,873
    goals of weaker theories.
  * Exact duplicates are common: 5,842 groups of identical axioms and
    goal across originals, covering 16,048 problems; 41,578 problems are
    distinct. The loop already solves them together: only 24 unsolved
    problems have a solved duplicate.
  * Only 15% of the kNN hint neighbours (from `train_pool`) of the ho3u
    targets have the target's axioms (median 4 of 30).
* **Tools.**
  * `lemmas.py --knn K [--subsets] --pool F` adds the K proven goals
    most similar to the target goal (idf-weighted Jaccard on term-shape
    features), taken from problems with the same axioms, or with subset
    axioms when `--subsets` is given, from any original.
  * `loop.py --lemma-knn K` does the same inside the loop.
  * `hintsel.py knnfiles ... --subsets` restricts hint neighbours to
    subset theories.
* **Results on ho3u** (345 problems, 16,000 critical pairs each =
  8 abstract s, deterministic). Lemmas from the same axiom group only (no
  `--subsets`); the kNN pool is everything plain twee solves in 4 s on the
  full benchmark, plus the 473 solved ho3 siblings:

  | setting | solved |
  |---|---|
  | plain | 70 |
  | rm4 | 81 |
  | rm4t (theory block) | 87 |
  | rm4 + 3 nearest siblings (old lemma import) | 77 |
  | rm4 + 6 nearest siblings | 78 |
  | rm4t + 3 nearest siblings | 83 |
  | rm4 + 3 nearest + 3 group-kNN lemmas | 83 |
  | rm4 + 6 group-kNN lemmas | 85 |
  | rm4 + 3 nearest + 10 group-kNN lemmas | **91** |

  * In abstract time the old lemma import does not help on ho3u (77 vs
    81: 7 problems lost, 3 gained). Its gains in the time-limited runs
    were within the load noise.
  * Lemmas chosen by goal similarity from the whole axiom group help:
    +10 with 13 lemmas.
  * The theory block (rm4t) gives +6, confirming 2f.
* **Results on r1sim**, a simulated loop round:
  * Set: 1,000 random problems (116 originals) that plain twee does not
    solve in 4 s.
  * Lemma pool: the 31,060 problems plain twee solves in 4 s.
  * Budget: 8,000 critical pairs each (4 abstract s).

  | setting | solved |
  |---|---|
  | rm4 | 92 |
  | rm4t | 94 |
  | rm4 + 3 nearest siblings (old lemma import) | 126 |
  | rm4 + 6 kNN lemmas, subset theories | 150 |
  | rm4 + 3 nearest + 3 kNN, subset theories | 166 |
  | rm4 + 3 nearest + 10 kNN, subset theories | **176** |

  * Relevance-chosen lemmas from the target's own and weaker theories
    nearly double what rm4 solves (+91%), and add 40% over the old lemma
    import.
  * On this broad set the theory block is flat (94 vs 92).
  * **kNN hints on top of the lemmas: +18** (battery 6). rm4 + 3
    nearest + 10 kNN lemmas solves 176. With kNN hints (30 neighbours,
    100 hints) it solves 194 from a pool of all solved problems, and 191
    from a pool limited to the target's own and weaker theories. rm4t
    with the same lemmas solves 180.
  * **Noise floor.** rm4 with `--abstract-time` 1990 and 2010 instead of
    2000 (budget ±0.5%, task timing shifted) solves 93 and 95. At most 3
    problems flip, and none of rm4's 92 is lost. Differences of 10 or more
    on r1sim are real.

## 2m. Long runs: how long do runs stay on hints?

*Notes: [notes/2026-11-13-long-runs-stall.md](notes/2026-11-13-long-runs-stall.md).*

Veroff keeps a hinted run going while it keeps matching hints, with gaps
of up to about a minute, and stops it when it falls off. With abstract
time a run is deterministic, so `stallsim.py` replays every stall limit
from one long run. twee-e16 prints `HINTLOG`, the critical-pair count of
each hint's first match. A run with stall limit G stops at the first gap
of G without a new match; the proof counts if it came before that.

**fam_long:** 60 problems, 30 goals each of aK2_eq_aK3_d and nil3_30
that the full-benchmark loop left unsolved. *Corrected 17 Nov:* they are
not the first 30 but those with the most solved goals among the 10
before them, so the set favours lemmas. Each run gets 120
abstract s (240k critical pairs), rm4t, 3 sibling lemmas plus 10
subset-kNN lemmas, and kNN hints (median 144, at most 200).

| stall limit (abstract s) | 5 | 10 | 20 | 30 | 45 | 60 | none |
|---|---|---|---|---|---|---|---|
| solved (with hints) | 33 | 37 | 43 | 49 | 51 | 52 | 52 |
| work (abstract h) | 0.09 | 0.13 | 0.19 | 0.22 | 0.25 | 0.27 | 0.30 |

* **No hints: 51, with hints: 52.** This set is too easy at 120 s to
  show a hint effect.
* **A 60 s gap loses nothing and saves 10% of the work; 30 s loses 3 and
  saves 27%.** Short limits lose many: proofs often come long after the
  last new match. Proofs came at quartiles 1, 4, 20 and 78 s; the last
  new matches of solved runs at 0.7, 2.3, 9.7 and 43.5 s.
* **Runs fall off the hints because the hints run out.** The 3 unsolved
  runs had matched 41 of 76, 50 of 76 and 106 of 200 hints. With small
  kNN lists the stall signal means "list used up", not "search lost".
  Veroff's lists are large, so the next test uses whole-original pools.
* **Five runs got no result.** They are the same five with and without
  hints. Their rate fell below 300 critical pairs per CPU second late in
  the run, so 120 abstract s took more than the 780 s wall limit, and the
  kill lost all output. `--max-cpu S` (twee-e18) is a real-CPU safety
  limit that stops like `--max-time`, prints `CPULIMIT` and keeps the
  output. Counting critical pairs is deterministic, but it is not
  constant work per unit: late critical pairs on big rule sets cost more.
* `--load-state` now counts hints that the loaded rules already match as
  matched, and restarts the stall clock at the loaded count (twee-e17).
  Before, a resumed run counted old matches as new, and
  `--eqhint-stall-cps` fired at once.

**Harder eval:** `sets/v2_hard` has the 8 fam_long failures plus the
next 30 unsolved goals of each original (68). Each run gets 300 abstract s
with rm4t and lemmas, in three versions (`abs/v2.sh`, `loop.py
--keep-out`):

* hints from the whole original pool, all lemmas of the solved siblings,
  most frequent first (1,994 hints for aK2_eq_aK3_d, 1,693 for nil3_30);
* kNN hints;
* no hints.

Each run also has a 1,200 s CPU cap.

* **Whole pool (V2p): 48 of 68.** This includes 3 of the 8 that kNN
  hints left unsolved at 120 s; nil3_30__goal_360 is proved at 60 s.
* **All 19 unsolved runs hit the CPU cap** at 115–261 abstract s, and all
  were still on hints. They had matched 520–690 hints, the last one near
  the end of each run. Per gap limit up to 60 s, 47–48 are solved, and
  all 19 failures count as "keep going" in Veroff's terms.
* **Large pools were expensive.** In the same search (hint score made
  neutral), 20 hints cost +2% CPU, 144 hints +4%, and 1,994 hints +53%.
  The cause was the abstract clock: it does not move while a
  housekeeping task runs, so task budgets never bound and hint
  normalisation ran every 40 critical pairs. Tasks can now report an
  abstract cost (`newTaskCost`); hint normalisation charges live/100
  critical pairs. With that, 1,994 hints cost +11% instead of +43%
  (twee-e19). The other tasks cost about 7% more under the abstract
  clock than under real-time scheduling, which is acceptable. Rarer
  normalisation does not weaken the guidance: 12 round-1 proofs rerun
  with e19 take the same or fewer critical pairs (251k in all, against
  285k) and match nearly the same number of hints.
* **Whole pool 48, kNN 40, no hints 36** (same 300 abstract s, same
  model and lemmas). The whole pool solves 13 that the no-hint run
  misses (and misses 1 it solves); kNN only 5. The two hint versions
  differ in how long the runs stay on hints. kNN runs stop matching
  early: the last new match came at a median of 3 abstract s, in solved
  and unsolved runs alike. With a 60 s gap, 34 kNN runs are solved and
  only 1 unsolved run is still on hints. The whole-pool runs keep
  matching until late: unsolved runs' last matches came at 131–228 s.
  So the stall signal is only informative with a large pool.
* **48% of the new proofs' lemmas were already in the pool** (8,196
  lemmas in 48 proofs; per-proof quartiles 52, 64 and 72%). The other
  ~4,300 are new and roughly double the pools for round 2.
* **Round 2** runs the 20 unsolved with the round-1 proofs added to the
  pools (4,109 and 3,494 hints): 900 abstract s, stall gap 60 s, CPU cap
  3,600 s, states kept for later rounds. Round 1 kept no states, so these
  are fresh runs.
  * **13 of the 20 solved (61 of 68 after two rounds).** By per-run
    limit: 7 by 60 abstract s, 9 by 120, 12 by 300, 13 by 600. Four
    took under 15k critical pairs, where round 1 failed at 230k–520k.
    All 7 unsolved hit the 3,600 s CPU cap, at only 222–445 abstract s,
    and 6 of them were still on hints at a 60 s gap. Their saved states
    take 0.3–1.1 GB each.
  * Both new inputs matter. With the new lemmas and no hints, goal_353
    and goal_354 fall in under 500 critical pairs; the big pool costs
    5k there. The others need the hints: goal_357 takes 9.1k without
    them against 6.2k, nil3_30__goal_381 51k against 14k, and goal_336
    and goal_284 fail at 60 s against 31k and 80k with hints.
  * Critical pairs get expensive on these problems. goal_336 without
    hints made only 270 critical pairs per CPU second (18.7k rules), so
    the abstract clock understates the real cost of long runs.
* **Round 3 (invalid, redone as round 4).** The 7 unsolved resumed their
  states with the round-2 proofs: +1 (nil3_30__goal_370). But the resumed
  aK2_eq_aK3_d runs matched only 1–9 hints, against about 1,260 in round
  2. Their problems had new lemmas, which hit the signature bug above
  (twee-e20 fixes it; a polluted state also resumes correctly). Five runs
  stopped exactly 120k critical pairs (the 60 s stall gap) after resuming.
  Round 4 repeats the round with e20 from the round-3 states.
* **Round 4 (round 3 redone with twee-e20): +2, 64 of 68.** The 6
  unsolved resumed their round-3 states with the same new lemmas and
  pools. Now the hints reach the saved search: each resumed run makes
  24–209 new hint matches (2 for goal_371), most within 10k critical
  pairs of the resume, as the new lemmas join. aK2_eq_aK3_d__goal_332
  is proved 24k critical pairs after the resume and nil3_30__goal_371
  after 4k (12 and 2 abstract s). Resuming costs CPU: the two proofs
  took 737 and 1,183 CPU s for those few critical pairs, so most of it
  goes to resuming itself. Measured on nil3_30__goal_355 (477 MB state,
  111k rules, 19.4M queued critical pairs, 3,787 hints, twee-e22
  `RESUMETIME`): loading takes about 130 s, normalising the hints 5 s,
  and re-scoring the saved queue against the new hints 333 s (each queued
  pair is rebuilt and rewritten). `--no-resume-requeue` skips the
  re-scoring; whether guidance suffers without it is not yet tested.
  Of the 4 unsolved, three stopped exactly 120k critical pairs after
  their last match (the 60 s stall gap), at +162k to +549k, and goal_360
  hit the CPU cap 93k after its last match.
  Hints from proofs of siblings keep feeding these runs, but each
  resume gives a short burst of matches, not a long hint-led run.

**Prover9 long runs (`long/P1`, `long/P0`).** fam2_long has 40 fam2
goals that the short loop left unsolved, run at 3000 given clauses.
Hints are all proof steps of the solved siblings (`p9_long.sh`).

* With hints 18, without 16 (both 13, hints only 5, no hints only 3), at
  the same CPU (9,560 vs 9,490 s). Proofs come late: median 997 givens
  with hints, 583 without. The short loop's 150–220 givens never get
  there.
* Prover9 picks hint matchers in bursts (`(H,` given clauses). Many
  solved runs have gaps of more than 750 givens without one, and a 750
  limit would keep 7 of the 18. The unsolved runs keep matching until
  late (last match at 2,047–2,949 givens). So for Prover9, "still on
  hints" does not separate the runs that will succeed from the rest.

## 2n. Prover9: SFDF reorientation of proofs

*Notes: [notes/2026-11-13-p9-sfdf.md](notes/2026-11-13-p9-sfdf.md).*

Veroff turns each proof into a strictly forward, demodulation-free
(SFDF) proof before using its steps as hints. `p9loop.py` now does this
without search:

* `--convert expand`: `prooftrans expand` writes each rewrite step as its
  own step, so the proof is demodulation-free.
* `--convert direct`: LADR's `directproof` gives a direct, forward,
  expanded proof.

Both are linear time: 9 ms per proof (279 proofs, 2.4 s in all). The
search-based conversion (rerun the problem with its own proof as hints
under `set(restrict_denials)` and no demodulation) converted only 2 of
34 proofs, at about 20 s each.

The loop runs on fam2 (aa1_15 and aK2_eq_aK3_q, 471 problems). Budgets
are in given clauses, so the runs are deterministic. Round 0 (150 givens,
no hints) solves 237 in every version.

| hints | hinted search | round 1 (150) | round 2 (150) | round 3 (220) | total |
|---|---|---|---|---|---|
| original proof steps | default | +26 | +9 | +11 | **283** |
| `prooftrans expand` (2.2× as many) | default | +26 | +9 | +7 | 279 |
| `directproof` (2.6× as many) | default | +26 | +9 | +7 | 279 |
| original proof steps | SFDF settings | +1 | +0 | +0 | 238 |
| `directproof` | SFDF settings | +3 | +0 | +0 | 240 |
| `directproof` | SFDF settings, 1500 givens | +3 | | | 240 |

* **In the default search the extra steps never match.** Round 1 is
  byte-identical in all three versions (same given counts on all 234
  problems). Prover9 matches hints against kept clauses, and with
  demodulation on only the normal form is kept. The intermediate
  equations that expansion adds never appear. In round 3, where the runs
  differ, the longer lists lose 4.
* **The SFDF search can match them, but it is far weaker here:** +3 even
  at 1500 givens (280 s per round, against 81 s for the default round 1).
* What Veroff gets from SFDF proofs our hints already have: only positive
  steps, nothing derived from the denial, skolems generalised. For twee
  this holds by construction (2j). For Prover9 the expanded proof only
  adds steps that the guided search never keeps.

## 2o. Online pools on the unsolved frontier

*Notes: [notes/2026-11-13-online-pools-cascade.md](notes/2026-11-13-online-pools-cascade.md).*

`sets/u3`: all 996 goals of three originals (R1dist_to_aa1,
aK2_eq_aK3_a, nil3_31) that the 4 s benchmark loop left unsolved (after
round 2 and the fam_long runs). Each run gets 20 abstract s, with rm4t,
3 nearest sibling lemmas and 10 subset-kNN lemmas, and twee-e19, on 5 cores
per variant.

* **Online pools** (`loop.py --online`). Each proof joins the hint pool
  and the sibling-lemma source as soon as it is found, for the runs not
  yet started. Goals run in goal-number order, and only `-j` runs are
  queued. Before this, the pools were fixed for the whole round.
* **Tiered pool** (`--pool tier:K:TOPN:F`). The kNN hints get the full
  boost, and the rest of the original's pool gets the weaker factor F.
  This was meant to avoid the cost of a big pool at short limits (2a).

On the first 189 aK2_eq_aK3_a goals, which every variant ran (all later
goals failed in every variant):

| variant | solved | wall s |
|---|---|---|
| kNN hints (30 neighbours, 100 hints), fixed pool | 44 | 10,744 |
| kNN hints, online | 55 | 9,422 |
| whole-original pool, online | 60 | 9,866 |
| tiered pool (kNN + rest at 0.3), online | 61 | 10,209 |

* **Online pools give +25% (44 to 55) at the same cost.** Proofs of
  earlier goals reach later goals within the round.
* **A whole-original pool adds about 10% more (60–61).** At 20 s, unlike
  2 s (2a), the big pool no longer hurts. The tiered pool is as good as
  the whole pool, but it needs the kNN index rebuilt as proofs arrive.
  So the full-benchmark run uses the whole pool.
* **Whole pool, online, all three originals:** 272 of the first 695 goals,
  against 0 for the 4 s loop.
* **The tail is hopeless at 20 s.** In goal order each original has a
  mixed zone, then only failures. The longest run of failures before a
  later success was 27 (R1dist_to_aa1); elsewhere 17–21. Replayed on the
  online runs, giving up an original after 30 consecutive failures keeps
  every proof and saves 15% (whole pool, cut short) to 50% (kNN variants)
  of the time. After 20 failures it loses 14 of 272. So
  `loop.py --give-up 30`.
* **Frequency-weighted boosts do not help.** A hint from 20 or more
  sibling proofs is right half the time, one from a single proof 0.8%
  (2m). Weaker boosts for rare hints (`--freq-factors 1:0.2,4:0.05`:
  factor 0.2 for hints from 1 proof, 0.05 for 2–4, 0.01 above) solve 60
  of the 189, the same as the uniform pool (+5/−5), in 19% more run time.
* **Hint signals at 5 s do not say which runs need 20 s.** Replayed on
  the whole-pool online runs: of the 517 runs unsolved at 5 s
  (10k critical pairs), 482 had matched a hint within the last 1 s, and
  18–20% of those were solved by 20 s. Runs with longer gaps did no
  worse or better (16% for 2–5k CPs). The number of late matches and
  the pool size do not separate them either (15–26% per quartile). So
  at short limits there is no Veroff stall rule to prune the next round,
  and the 20 s round reruns every unsolved goal (with the give-up rule).

**Full benchmark, Veroff style.** `abs/unleash.sh` runs every
goal the benchmark loop left unsolved: 18,064 of 51,784, starting from
its 33,720 proofs. The loop uses online whole-original pools, gives an
original up after 30 failures, and has rounds of 5 and then 20 abstract s
on 14 cores (twee-e20, kill after 15× the limit, CPU cap 400 s).

* **Round 1 (5 abstract s): +2,337, to 36,057 of 51,784** (holdout
  3,475 to 3,747 of 5,880). The give-up rule ran 10,079 of the 18,064
  goals and skipped the rest. All 129 originals gained (most:
  R1dist_to_aa1 +48, aK2eq_1234 +46). The round took 82 minutes on 14
  cores: 2.1 h of run time on proofs (median 2.4 s wall) and 16.8 h on
  failures (median 7.5 s wall).
* **Round 2 (20 abstract s): +2,951, to 39,008** (holdout 4,196, +449).
  The give-up rule ran 10,405 of the 15,727 unsolved goals. 125 of the
  129 originals gained; the most were R1dist_to_aa1 +113,
  mbol_aa1sqrd_to_aa1 +81 and nslm_to_aa1 +77. The round took 12 h on 14
  cores: 16 h of run time on proofs and 152 h on failures. At 20 abstract
  s a failing run takes about 53 s wall, because the CP rate falls on
  hard runs.
* Round 3 uses the cascade (2p) and runs from 06:03 on 14 Nov.

## 2p. One search for many goals, and the gap to the nearest proof

* **Multi-goal search** (twee-e21 `--multi-goal`, `loop.py --multi W`).
  All goals of an original have the same axioms, and twee's completion
  does not depend on the goal. So one search can serve several goals: the
  goals become skolemised negated conjectures of one problem, twee prints
  `SOLVEDGOAL` for each goal it proves and goes on until all are proved.
  A window of W consecutive unsolved goals gets the union of their lemmas
  and W times the budget.
* **It loses to separate runs.** On the 189 aK2_eq_aK3_a goals (20 s per
  goal, 100 s per window of 5): 21 against 28 for separate online runs on
  the first 33 goals (stopped there). On one window of 10 nil3_31 goals
  at 200 s: 4 against 5. A separate run for goal k+1 starts with goal k as
  an axiom, so its overlaps are among the first critical pairs. In the
  joint search goal k is only joinable. It never becomes a rule, so its
  consequences come late or never. Restarting with the new lemma is what
  makes the sibling chain work.
* **Success falls off with the distance to the nearest proof below.** In
  the full-benchmark round 2 (20 s, after failing at 5 s), by the gap in
  goal numbers to the nearest sibling proven before the run:

  | gap | runs | solved |
  |---|---|---|
  | 1 | 537 | 58% |
  | 2–3 | 176 | 42% |
  | 4–10 | 66 | 26% |
  | more than 10 | 5 | 0 |

  So the loop advances along each original's proof, and a hard goal
  blocks the goals after it. Conditional goals are not a weak spot: 83%
  of them are solved overall, against 68% of the unconditional ones.
* **Lemmas from both sides** (`loop.py --lemma-after`). The nearest
  proven siblings above a goal are lemmas too. They are proven before the
  run, so every proof still expands to one from the axioms. Test set: the
  222 goals of sets/u3 that the online whole-pool run left unsolved and
  that have a proven sibling at most 10 above (20 s, from that run's
  proofs). With lemmas from both sides 67 of 222 are solved. On a random
  74 of them: 26 against 20 for the same rerun with lemmas from below only
  (+6/−0). So most of the 67 come from rerunning with the full set of
  proofs below: with 3 originals on 5 cores, goal k+1 had often started
  before goal k was proved (the full benchmark interleaves 129 originals,
  so this rarely happens there). Lemmas from above add about 30% on top.
* **Cascade scheduling** (`loop.py --cascade T0,T1,...`), written from
  this. In place of rounds, a goal is retried at T0 as soon as a sibling
  at most `--retry-gap` places below it gets proved. Otherwise the goal
  right after a proof (`--frontier 1`) is deepened to the next budget
  level, resuming its saved state. A few workers stay free for the
  retries, so a new proof's consequences run at once.
* **The cascade wins.** The test set is sets/u3: 724 goals left unsolved
  after the online 20 s run, starting from its proofs (loops/U3poI). Both
  schedules get 5 workers for 2 h wall.
  * The cascade (20, 80 and 320 s levels; every goal near a proof first
    gets a 20 s run) proves **90** goals with 336 runs on 248 goals.
  * One online round at 80 s (give-up after 30 failures) proves **69**
    with 117 runs.
  * They share 58 proofs; the cascade alone has 32, the round alone 11.

  Proofs over time:

  | wall s | 600 | 1800 | 3600 | 5400 | 7200 |
  |---|---|---|---|---|---|
  | cascade | 27 | 57 | 64 | 77 | 90 |
  | 80 s round | 10 | 18 | 40 | 58 | 69 |

  The cascade is ahead from the start, and it was still gaining at the
  end (7 proofs in the last 10 min). Short runs on the goals right after
  new proofs pay off more than long runs in goal order. Only 30 of its
  336 runs reached the 80 s level, and 16 of those succeeded. Round 3 of
  the full benchmark therefore uses the cascade (abs/ul3.sh: 20, 80,
  320 and 960 s, with lemmas from above).

## 2q. Ablation: ENIGMA, hints and lemmas

*Notes: [notes/2026-11-14-ablation-lemma-count.md](notes/2026-11-14-ablation-lemma-count.md).*

The user asked how far the ENIGMA guidance gets, alone or with hints. The
test set is the 189 aK2_eq_aK3_a goals of sets/u3 (one hard original).
Each goal gets 20 abstract s, in an online loop that starts from the
proofs of loops/V2base and uses 5 workers. Only the guidance changes:

* **ENIGMA** is the rm4t rule filter: LightGBM with the theory block,
  threshold 0.1, penalty 2.
* **Hints** come from the whole-original pool, online.
* **Lemmas** are the 3 nearest proven siblings plus 10 subset-kNN lemmas.

| variant | ENIGMA | hints | lemmas | solved /189 | wall s, all 189 runs |
|---|---|---|---|---|---|
| full (U3po, run with the other two originals of sets/u3) | yes | yes | yes | **60** | 9,866 |
| full (U3xf, these 189 alone, like all rows below) | yes | yes | yes | 58 | 10,506 |
| U3xh | – | yes | yes | 59 | 14,979 |
| U3xm | yes | – | yes | 58 | 10,064 |
| U3xl | – | – | yes | 49 | 16,372 |
| U3yb | yes | yes | – | 49 | 11,805 |
| U3ym | yes | – | – | 42 | 10,501 |
| U3yh | – | yes | – | 37 | 15,063 |
| U3x0 (plain twee) | – | – | – | 28 | 18,151 |

The wall seconds are indicative only, because the machine was shared.
Every run had the same CP budget, so a lower total means that more runs
end early with a proof.

All nine runs together solve 70 goals; U3po misses 10 of them.

**Reading.**

* **Without lemmas, ENIGMA and hints add up.** ENIGMA alone gives +14,
  hints alone +9, and the two together +21 (28 → 49). ENIGMA plus hints
  solves every goal that hints alone solve, and 12 more.
* **ENIGMA is the stronger and cheaper guide.** Alone it beats hints
  alone (42 against 37) at about 70% of the wall time. Its failing runs
  do not pay for hint matching, and its proofs come earlier.
* **Lemma import is worth as much as ENIGMA and hints together**
  (49 = 49).
* **With lemmas, ENIGMA and hints overlap.** Each adds about 10 on top of
  lemmas, but together they add only 9–11: the full system on these 189
  goals alone (U3xf) solves 58, the same as ENIGMA plus lemmas. U3po (60)
  ran them interleaved with two other originals, so on 5 workers goal k+1
  less often started before goal k was proved. That ordering effect is
  as large as the second guide. Hints and lemmas carry the same
  information, the sibling proofs: hints as steps, lemmas as finished
  results. Once the lemmas are there, the hints mostly point to steps
  that are no longer needed. ENIGMA's knowledge is general, learned from
  other problems, so it adds most where sibling information is missing,
  and at less cost.
* The full system is the cheapest of all variants.
* The 10 goals that only some variant solves show the variance at 20 s.
  The search order changes with the guidance, so a cheap portfolio over
  variants could pick up a few of them. Earlier portfolio tests were
  within noise.

Earlier no-lemma data, on other sets, points the same way:

* Hard holdout 300 at 60 s: plain 44, rm4 53, rm4 plus lemmas plus kNN
  hints 56.
* ho3u: rm4 81, rm4t 87.

## 2r. How many sibling lemmas

Twenty abstract s per goal, online from loops/V2base, rm4t plus the
whole-original pool plus 10 subset-kNN lemmas. Only the number of
nearest proven siblings imported as axioms changes.

| siblings | aK2_eq_aK3_a, 189 goals | nil3_31, first 150 unsolved goals |
|---|---|---|
| 3 nearest below | 58 (U3xf) | 62 |
| **6 nearest below** | **64** (+8/−2) | **76** (+16/−2) |
| 10 nearest below | – | 74 |
| 6 nearest on either side (`--lemma-after`) | – | 76 |
| 3 below, 20 subset-kNN lemmas in place of 10 | 59 | – |

Six siblings beat three on both originals, by 10% and 23%, at less time.
Ten are no better than six. Lemmas from above do not change the result
here, where few goals above are proven. The retry test of 2p, where many
were, gave +6/−0. Extra subset-kNN lemmas add nothing.

The full loop's round 3 (cascade, 3 lemmas, from 06:03) found 738 proofs
in 2,481 first-level runs, bringing the total to 39,746. It was then
restarted at 08:35 as round 4, with 6 lemmas from either side
(abs/ul4.sh, `--cascade-start -1`): every unsolved goal near a proof
gets a 20 s run in its new context first.

Two cascade fixes went in with the restart:

* The lemma context is now the N nearest proven siblings on either side,
  the same ones lemma_problem picks.
* A retry starts fresh but saves its state, so a later deepening
  continues that search, not an older one.

**Retrained model rm6t:** rm4t's data plus the full loop's 5,303 proofs,
with the u3 originals held out. Alone (no hints, no lemmas, aK2 189) it
solves 40, against 42 for rm4t, so the new proofs do not improve the
filter. The full-system test is running.

**Which lemmas proofs use (14 Nov, twee-e31 `USEDAXIOMS`).** 60 goals the
full loop solved in round 4 were rerun at 20 s on a snapshot of all
40,961 proofs, offered the 20 nearest proven siblings plus 10 kNN lemmas.
All 60 were solved, each proof using 7.6 lemmas on average. A proof uses
about 20% of the siblings it is offered, almost regardless of distance:

| sibling | offered | used |
|---|---|---|
| before, 1–3 goals away | 120 | 30% |
| before, 4–6 | 132 | 27% |
| before, 7–10 | 173 | 17% |
| before, 11+ | 296 | 19% |
| after, 1–3 | 115 | 20% |
| after, 4–10 | 245 | 20% |
| after, 11+ | 119 | 16% |

All ten kNN ranks are used, 13–28 times each. Lemmas act as shortcuts to
whatever is available, not as a specific needed step. With 6 nearest
siblings instead of 20, on the same snapshot, 58 of the 60 are solved,
median 3.4 s against 2.7 s; 20 lemmas give fewer rules in only 18 of 58.
The large difference is with the original round-4 runs (median 9.7 s):
the same goals are about 3× faster now because more of their neighbours
are proven. More lemmas at a time add little (as with 10 against 6
above); a richer context does, which is what the cascade's retries on
new nearby proofs exploit.

## 2s. Frequent hints as axioms: no gain, and false hints in old pools

*Notes: [notes/2026-11-14-hint-axioms-profile.md](notes/2026-11-14-hint-axioms-profile.md).*

`loop.py --hint-axioms K:F` adds the K most frequent pool hints that
occur in at least F sibling proofs to the problem as axioms. Pool hints
are consequences of the axioms and proven lemmas, so the proofs stay
sound.

Test set: nil3_31, 150 goals, at 20 s, on top of 6 lemmas (baseline
76).

| hint axioms | solved |
|---|---|
| none | 76 |
| 10, each from at least 20 proofs | 72 (+1/−5) |
| 45, each from at least 10 proofs, all verified as theorems | 73 (+3/−6) |

The high-precision hints are more useful as hints. As axioms they add
critical pairs from the start and crowd the search.

**False hints in the pools.** The first 45-axiom run solved all 150 goals
in 28 s. One of its "hints" was `X0 = X1`, which occurs in 1,422 proof
hint files of loops/V2base (and so of loops/UL). They are proofs of
conditional goals such as `X0 = X1 ⇒ …`, made before the HINTS-HYP fix
(twee-e14, 2j). There, the hypothesis with its skolems generalised was
logged as a hint.

As a hint this was harmless. Twee matches hints by variant (canonical
form), not by instance, so `X0 = X1` only matches the critical pair
`X = Y`. The other false generalised hypotheses are wasted hint entries
in the same way.

As an axiom it is unsound, so `--hint-axioms` now counts only proofs of
unconditional goals. The 45 top nil3_31 hints from those all prove from
the axioms in under 10 s each.

## 2t. Where twee's time goes, and the rule penalty

**Profile.** twee-e22 built with `-f profile` (Twee.Profile now uses GHC's
monotonic clock instead of rdtsc). The test run is one failing
nil3_1K goal at 20 abstract s (40k critical pairs considered) in the full
configuration. Its share of the time, excluding the profiler's own
overhead:

| phase | share |
|---|---|
| making critical pairs (6,115 new rules against the active set) | 51% |
| … of which normalising both sides of each new pair (8.2M `simplify` calls) | 41% |
| considering the 27k dequeued pairs (normalisation, joining) | 22% |
| the rest | 27% |

Without hints or the model, the same run takes 67 s against 49–53 s. The
model keeps fewer rules, which saves more than it costs. Hint matching
and logging the given rules cost about 8%. Ground joining is cheap here:
limiting it changes nothing.

So the cost per abstract second grows with the square of the number of
rules. Twee normalises every new critical pair at creation, by design,
and changing that would be a large redesign.

**Rule penalty.** Larger deferral penalties would keep low-scored rules
out longer and make the rule set smaller. On nil3_31, 150 goals at 20 s
with 6 lemmas: penalty 2 solves 76, 5 solves 77 and 20 solves 75. Wall
time does not change. Penalty 2 stays.

## 2u. ENIGMA-style looping and a Deepire-style model (user's question, 14 Nov)

*Notes: [notes/2026-11-14-enigma-looping-deepire.md](notes/2026-11-14-enigma-looping-deepire.md).*

**Offline, in the loop setting.** The test set is the 298 proofs of
nil3_31, aK2_eq_aK3_a and R1dist_to_aa1 goals that the full loop found
in rounds 1–4. These are later goals of originals whose earlier goals
are solved. Training gets every other given log, including the other
proofs of the same originals, as an ENIGMA loop would. Mean per-problem
AUC on the proofs' rules:

| model | AUC |
|---|---|
| rm4t (base data: train_only + tr30_g1) | 0.850 |
| **rm7t: LightGBM retrained with the loop's proofs** (negmax 150, 34 GB, 24 min) | **0.882** |
| Deepire-style, derivation only (`deepire.py`, d = 32, 4 epochs, 2 min) | 0.765 |
| rank fusion rm4t + 0.5 × Deepire | 0.861 |

* **Retraining on the loop's own proofs helps offline:** +0.03 AUC on
  later goals of the same originals. rm6t gained nothing (2r), but it
  held these originals out of training entirely.
* **Deepire-style embeddings** (axiom equations as learned leaves; a rule's
  embedding computed from its two parents) are weaker than the ENIGMA
  term features. They are somewhat complementary: fusion adds +0.011.
  Only 6,746 training logs have parent columns; the older train_only
  logs do not.
* **Hybrid neural model** (`deepire.py --feats --goal`): the derivation
  embedding plus hashed bags of the rule's and the goal's ENIGMA
  features, trained on 2,500 problems for 6 epochs. AUC 0.814, still
  rising, against 0.885 for rm7t on the same test. Rank fusion with rm7t
  adds nothing (0.885 at weight 0.1, lower above). At this data size,
  LightGBM on ENIGMA features stays the better model, and the
  derivation history adds no usable signal on top of the retrained
  model.
* **The online ENIGMA loop** (`loop.py --rerun-solved`, abs/el.sh) is
  running on all 1,934 goals of these 3 originals at 5 abstract s, without
  lemmas. Each round retrains on base data plus the loop's shortest proof
  per problem, then reruns every goal. Round 0, with a base-trained model
  like rm4t, solves 920. Round 1, retrained with those proofs, solves 936
  of them on its own (+21 new, −5 lost), bringing the total to 941.

| loop on sets/e3 (1,934 goals), 5 abstract s, no lemmas | round 0 | +round 1 | +round 2 | +round 3 | CPU (wall-sum, rounds 0–2) |
|---|---|---|---|---|---|
| EL: rule model retrained each round, no hints, reruns all | 920 | 941 | 943 | 947 | 6.1 h |
| HL: hints from the loop's proofs, no model | 905 | 944 | 951 | 953 | 7.9 h |
| EHL: both (retrained model + hints), reruns all | 920 | 963 | **971** | (stopped) | 6.5 h |
| FHL: hints + EHL's round-0 model kept fixed (production setting) | 920 | 970 | **987** | (not run) | 6.2 h |

* The ENIGMA loop alone gains little after its first retraining (+21,
  then +2 and +4); the hint loop gains more (+39, +7, +2).
* The combination solves 971 after two rounds, as many as EL and HL
  together (973), with 11 that neither solves, and at less CPU than the
  hint loop (the model makes runs cheaper).
* **Retraining adds nothing online; it loses.** With the round-0 model
  kept fixed and only the unsolved goals rerun, round 1 solves 970 and
  round 2 987, against 963 and 971 with retraining (after round 2: 19
  only in FHL, 3 only in EHL), at 4.40 h of CPU for rounds 1–2 against
  4.79 h. The gain over HL comes from having a model at all, not from
  training it on the loop's proofs. The same was seen with rm6t and rm7t
  (2r), so the full loop keeps the fixed rm4t.

## 2v. Long runs slow down: overlap index and interreduction filter (user's question, 14 Nov)

*Notes: [notes/2026-11-14-long-run-speed.md](notes/2026-11-14-long-run-speed.md).*

**How much slower.** `twee --progress N` (twee-e23) prints a PROGRESS line
every N abstract seconds. Each line gives critical pairs, rules, active
rules, queue size and CPU, plus the CPU of the housekeeping tasks. The
test is the profiled nil3_1K goal in the full configuration (rm4t, 2,743
hints), run for 640 abstract s, on the loaded machine (load 35–40 on 112
cores). The nominal rate is 2,000 critical pairs per abstract second.

| abstract s | rules | queued pairs | CPU per abstract s (old twee) | of which interreduction | of which queue renormalisation |
|---|---|---|---|---|---|
| 0–10 | 3.7k | 0.3M | 3.0 s | 0.2 s | 0.5 s |
| 20–30 | 8.2k | 1.4M | 8.4 s | 0.7 s | 2.9 s (one pass) |
| 50–70 | 14k | 4.3M | 6.8 s | 1.2 s | 0 |
| 120–130 | 20k | 6.9M | 26 s | 2.0 s | 17.7 s (one pass, 177 s) |
| 170–190 | 26k | 11.5M | 8.6 s | 2.3 s | 0 |

So a long run costs 3–9 s of CPU per abstract second, against 1–3 s at the
start. On top of that come queue renormalisation passes that each cost
about 25 µs per queued pair. Under the abstract clock two housekeeping
tasks were free and so ran without limit. Interreduction ran every
abstract second over all active rules. The queue was renormalised
whenever the critical-pair sample went stale. Together they took 33% of
the CPU by 130 abstract s; with CPU time, twee caps each at 5%. At 20
abstract s, the wall time of the full loop's runs grows with the rule
count, from 52 s per run (2–4k rules) to 104 s (12–14k rules).

**Profile at 60 abstract s** (12.9k rules): trying overlaps 18%, index
lookups 18%, building terms 15%, `simplify` 13% (profiler overhead
excluded). Twee looked for overlap partners by trying every active
rule at every position, so each new rule cost time linear in the active
set, before any critical pair was normalised.

**What the Prover9 branches suggest, and what was done.** The
Prover9-new long-run work is mostly about memory (compact clause and
passive stores, mmap ancestor stores, about 80% less RAM) and fast
matching against 10^5 hints. Twee's runs do not need either: 0.4 GB at
60 abstract s, and hint matching is a hash lookup. Two indexing ideas do
carry over:

1. **Index the partners for inference** (Prover9's paramodulation
   indexes; here Schulz's fingerprint indexing). twee-e24,
   `Twee/FPIndex.hs`, samples 8 positions of each term. It keeps two
   tries, one of rule left-hand sides and one of the subterms at every
   overlap position. The candidates are sorted back into the old loop
   order, and the renaming bound comes from a multiset of per-rule
   variable bounds instead of a scan over all rules. **The output is
   byte-identical** (given lists and proofs on 6 solved problems, all
   counts on a 30k-pair guided run, and a resumed state).
   `--no-overlap-index` turns it off.
2. **Backward demodulation for interreduction** (Prover9's back-demod
   index). twee-e26 re-checks an old active only if a rule added since
   the last interreduction matches one of its subterms. This is nearly
   exact: `TWEE_DEBUG_FILTER=1` found two misses in a 6k-pair run (a
   ground-joinability and a model change). 4 of 6 test problems stay
   byte-identical; the other two differ by 1 rule in about 3,000.
   `--no-interreduce-filter` turns it off.

| long guided run, CPU | 30 abs s | 70 abs s | 150 abs s |
|---|---|---|---|
| old (e23) | 150 s | 411 s | 1,148 s |
| new (e26) | 87 s | 232 s | 623 s |
| speedup | 1.7× | 1.8× | 1.8× |
| interreduction CPU, old → new | 14 → 4 s | 59 → 10 s | 201 → 24 s |

Continued to 360 abstract s (22.7M queued pairs, 1.4 GB), the new twee
settles at 3.2–3.5 s of CPU per abstract second between 120 and 360 s,
with no further growth. The old run reached 1,837 s of CPU by 230
abstract s; the new one used 911 s there (2.0×). The queue renormalisation passes
(126 s at 80 abstract s, 282 s at 240 abstract s) add about 25% on top.

Six solved problems at up to 60 abstract s: 1.05–2.6× less CPU. Real
workload (sets/u3n150, 20 abstract s, online, 6 lemmas; N3l6 with e22
solved 76): on the first 97 goals e27 solves 69 against 68, in 18% less
wall time, on a busier machine.

The state file format is unchanged; the index is rebuilt on load. Since
13:39 the path `/project/bin/twee-e22` holds the e27 code (the original is
`twee-e22.orig`). The running full-loop cascade and the HL/EHL runs
therefore use it, and the deep cascade levels get the speedup.

**Queue renormalisation** is the remaining long-run cost. One pass
renormalises every queued pair from scratch: twee stores only the
parents and position, so there is no normal form to filter. That makes
it as costly as making all those pairs again. `--queue-cost K` (e27)
charges a pass K critical pairs per queued pair, so that its 5% budget
binds as it does in CPU-time mode. An honest K is about 0.008. Whether
renormalising less often hurts hint guidance (queued pairs can become
hint matches) needs a deep-run test; the default stays 0.

Also tried, no gain: larger GHC allocation areas (`-A16m`/`-A64m` were
slower), and skipping the copy that `simplify` builds of normal forms
together with a lazy overlap top term (exact, but within the ±15% timing
noise of the loaded machine).

## 2w. Veroff's P9loop and Bigloop in twee (user's question, 14 Nov)

*Notes: [notes/2026-11-14-p9loop-bigloop.md](notes/2026-11-14-p9loop-bigloop.md).*

**What Veroff does** (AITP 2026 slides). A P9loop reruns the *target*
theorem over and over. At the end of each failed run, every derived
clause that matches a hint (a *hint matcher*) is kept, and all later runs
get these as extra input lemmas. The runs cycle through settings,
mainly term orderings: 36 per P9loop in the NIL3 proof. A Bigloop runs
several P9loops at once, all sharing one lemma pool. In the NIL3 proof,
1,155 of 3,594 steps were Bigloop lemmas, and 25 of 60 output files
contributed.

**In twee.**

* `--print-hint-matchers` (twee-e30) prints every rule that matches a hint
  as a TPTP formula (`HINTMATCHER n fof(...)`).
* `loop.py --p9loop` keeps a goal's matchers in `DIR/p9lem/<goal>` and adds
  them as axioms to its later runs. They are consequences of the problem's
  axioms and lemmas, so they are sound; matchers with a skolem of a
  conditional goal are dropped. `--p9-max N` keeps only the most recent N.
* `--p9-orders N` gives attempt k its own KBO precedence (`--precedence`, a
  seeded shuffle of the problem's symbols; attempt 1 = twee's default).
  Hint matching is by variant in either orientation, so hints and matchers
  carry over between orderings.
* `--p9-parallel P` is Bigloop: P runs of each goal per round at once, each
  with its own ordering, all adding to the one lemma pool.

**Test 1: the 73 nil3_31 goals the 20 s system left unsolved** (sets/u3n73,
from all of N3x6's proofs, production config, 4 rounds of 20 abstract s):

| arm | solved after rounds 1 / 2 / 3 / 4 | wall per goal and round |
|---|---|---|
| P9loop, matcher lemmas only | 1 / 3 / 3 / 3 | 39–43 s |
| P9loop, lemmas + a new ordering each round | 1 / 1 / 2 / 2 | 40–57 s |
| resume (continue the saved run) | 1 / 3 / stopped | 55 s, then 115 s |

The resume arm was stopped after round 2 to stay within the CPU budget.
Its round 2 took 4,418 s of wall time with 2 workers, against 1,413 s
for the lemmas-only arm.

* All arms solve the same goals (400, 323, 341); these goals are hard
  and four 20 s rounds add only 2.
* After round 2, the matcher lemmas reach the same hint coverage as
  resuming: 2,220 of 3,728 hints joined and 1,508 live, against 2,214 and
  1,514. They do it in half the wall time, because a fresh run on a small
  state is cheaper per critical pair than continuing a big one. A resume
  also re-scores the whole saved queue first, which costs 20–55 s here.
* Lemmas pile up: about 880 per goal after round 1 and 1,440 after round
  2. New matchers then dry up (about 115 per run in round 3). Each run
  matches fewer hints itself (945 in round 1, about 730 later), because
  many hints are already joinable from the lemmas.
* Different orderings derive largely different matchers. In a 1 s smoke
  test of one goal, the default ordering found 204 and another found 528.

**Test 2: the cascade's frontier** (sets/fr100: 100 goals the full loop
left unsolved at 20 s whose nearest lower sibling is proven; every arm
starts from the full loop's 40,961 proofs, production config, 2 workers
each):

| arm | solved after rounds 1 / 2 / 3 / 4 | wall (sum over runs) |
|---|---|---|
| resume, saved queue re-scored (BRS) | 9 / 17 / 23 / 26 | 5.3 h for 3, 7.8 h for 4 |
| resume, queue kept as saved (BRSn, `--no-resume-requeue`) | 9 / 18 / 27 / 29 | 4.1 h for 3, 5.3 h for 4 |
| P9loop, matcher lemmas + a new ordering each round (BP9) | 9 / 16 / 18 / 18 | 4.1 h |
| Bigloop, 2 orderings per goal and round (BBL) | 14 / 19 | 4.2 h |

All four arms solved 33 goals together. Four of them only BRSn solved;
BP9 and BBL each solved one goal no other arm did; BRS solved none on
its own.

* **Keep searching, do not restart.** On goals right next to a proof,
  continuing the saved search beats restarting with matcher lemmas: 27
  against 18 at the same 4.1 h. The P9 arm stalls after round 2 (BP9 adds
  nothing in round 4), as in test 1.
* **Skip the re-scoring.** Re-scoring the saved queue against the new hints
  costs 20–55 s per resume and buys nothing: after four rounds BRS
  solves 26 in 7.8 h, BRSn 29 in 5.3 h. The full loop now resumes with
  `--no-resume-requeue` (round 5 continued at 19:35).
* **Orderings do add something.** In BBL's round 1, a second ordering per
  goal solves 14 against 9 for one run, but at twice the wall time. At
  equal time, resume is still ahead (18 at 2.9 h against 14 at 2.6 h).
  Orderings are a candidate for goals whose resume has stalled, not a
  replacement for it.

## 2x. A resume bug that grew one run to 100 GB (14 Nov)

*Notes: [notes/2026-11-14-resume-bug-consider-cost.md](notes/2026-11-14-resume-bug-consider-cost.md).*

A resumed run of the full loop grew to 100 GB before the user killed it.

**The cause.** Twee numbers its symbols when it interns them, and it
numbers them afresh when it loads a saved state. The saved state also
holds the hint matcher's tables of goal constants, and these are keyed by
the *old* numbers. Resume added the new axioms (lemmas proven since the
save) while those stale tables were still in place, and only then put in
the current run's tables. With the stale tables, a goal constant could
look up a definition that contains itself. Scoring one critical pair
(hint lookup after expanding goal constants) then never stopped.

**The fix** (17ffcd3).

* The current run's hint tables go in, normalised, before the new axioms
  are added.
* Goal-constant definitions whose expansion is cyclic or longer than 1,000
  symbols are dropped from hint matching.
* twee is built with a default heap limit (`-with-rtsopts=-M6g`, 110d93a).
  A run that would grow past 6 GB stops with "Heap exhausted" (exit 251).
  `loop.py` then marks the run HEAP and deletes its saved state.
* A watchdog (`abs/memwatch.py 7 45`) kills any twee over 7 GB and, while
  all twee processes together use more than 45 GB, the largest one.

**Check.** The saved state plus one lemma used to exhaust any heap; it
now proves its goal in 1.9 s at 190 MB. Fresh and resumed hinted runs on
six current goals do the same work as before, counted in critical pairs.

## 2y. Consider-emulation costs a quarter of the CPU (14 Nov)

**Profile.** Twee's stamp profiler (`twee-e32prof`) on one failing
nil3_15 goal, 30 abstract s, production config (3,088 hints). It made 16.4M
`simplify` calls and 202M index lookups. Without consider-emulation
(`--no-eqhint-consider`, 1b) it makes 10.9M calls and the total time drops
by 16%, profiler overhead included. With today's large pools, many critical
pairs have the symbol fingerprint of some hint form, and each of them goes
through `allSteps`.

| consider-emulation | CPU (nil3_15 / lra2aa, 30 abstract s) | hints matched |
|---|---|---|
| on, all hints (default) | 67.9 s / 57.6 s | 973 / 1,608 |
| only for hints no rule has matched yet (`--eqhint-consider-open`, new) | 48.0 s / 50.7 s | 971 / 1,608 |
| off | 46.4 s / 46.4 s | 981 / 1,602 |

With `--eqhint-debug`, it adds 8 and 20 distinct hints over 8,811 and
26,697 plain matches.

**Solving** (sets/u3n150, 20 s, 6 lemmas, online, as N3x6):

| arm | solved | wall (sum over runs) |
|---|---|---|
| on (N3x6) | 77 | 4,405 s (another time, other load) |
| off (N3c) | 76 | 3,023 s |
| open hints only (N3o) | 74 | 3,504 s |

The three arms solve 79 goals between them. Most differences come from
sibling lemmas. For example, N3c and N3o prove goal 341, and its lemma then
gives goal 400 a 4 s proof. Only about three goals differ directly, which
is within noise. On the goals all three solve, the median wall time is
6.1, 4.2 and 4.7 s.

**Decision.** The full loop runs with `--no-eqhint-consider` from 20:15
(round 5 continued). This buys about 30% more runs per hour, at the cost
of at most a few goals per hundred. Rewriting `simplifyOutermost` so that
it does not rebuild unchanged terms was 0–5% slower and was reverted.

## 2z. Distance in proof lines, not goal numbers (user's remark, 14 Nov)

*Notes: [notes/2026-11-14-line-gaps-stalled.md](notes/2026-11-14-line-gaps-stalled.md).*

A goal's name gives its position among the goals selected from the
original's Prover9 proof. Its LADR file also gives the proof line
(`% goal_313 line_1531`). The original proofs themselves are not in
AIM60k or Prover9-new, so the parents of a step are unknown. Goals were
picked in stripes 3, 5, 8, 13, 21, 34 and 55 lines apart. A gap of one
goal is therefore anywhere from 3 to 55 proof lines.

The table replays the full loop's round 5 in order and measures each run's
distance to the nearest proven goal below it at the time of the run. Line
distance predicts success much better than the goal-index gap the cascade
used:

| distance to nearest proven goal below | L0 retries (20 s) | L1 (resume to 80 s) |
|---|---|---|
| ≤ 8 lines | 9/29 (31%) | 36/100 (36%) |
| 9–13 lines | 69/216 (32%) | 125/495 (25%) |
| 14–21 lines | 36/172 (21%) | 47/296 (16%) |
| 22–34 lines | 29/219 (13%) | 37/155 (24%) |
| 35–144 lines | 41/356 (12%) | 11/75 (15%) |
| index gap 1 / 2 / 3 | 22% / 12% / 14% | 23% / 17% / 40% (5 runs) |

`loop.py --line-gaps R,F` (6b76a1b) orders the cascade's retries and
deepening by proof-line distance. It also admits goals within R lines for
retries and within F lines for deepening. Every gap-1 goal still deepens:
the late goals, 55 lines apart, block the rest of their chains. The full
loop runs with `--line-gaps 21,13` from 20:58. Admission barely changes
(1,407 goals against 1,406 deepen, because the dense early parts are
solved). The gain is in the order: near goals (36%) run before far ones
(12%).

The full loop's rate (round 5, about 16 workers): 129 proofs/h with
re-scoring off (19:35–20:13), and 203/h with consider-emulation also off
(20:15–20:57).

## 2aa. Stalled goals: run fresh with the new hints, do not resume (14 Nov)

The test set is sets/sg1: 32 gap-1 goals that failed L1 (resume to 80
abstract s) in the full loop's round 5. All arms run from the snapshot
loops/ULsJ (41,473 proofs) in the production config.

| arm | solved | proofs per CPU-hour |
|---|---|---|
| resume to 320 s (+240), as the cascade's L2 (SG1) | 0 of 13 run (stopped) | 0 |
| fresh 80 s, another term ordering (SO) | 8 / 32 | 5.9 |
| fresh 80 s, default ordering (SD) | 4 of 11 run so far | 12 |
| fresh 20 s, default ordering (S20) | 4 / 32 | 14 |
| for comparison: gap-2 goals, L0 state resumed to 80 s (SG2) | 5 / 48 | 2.8 |

None of these goals had a new sibling lemma since its last fresh run, so
the cascade never retried them. Their hint pools had grown, though, by up
to 75%. Success follows that growth:

| pool growth since the last fresh run | S20 | SO |
|---|---|---|
| < 10% | 0/12 | 1/10 |
| 10–25% | 1/11 | 3/13 |
| ≥ 25% | 3/9 | 4/9 |

* **Resuming does not use new hints.** The saved queue was scored without
  them. `--no-resume-requeue` saves the re-scoring (2w), so a resumed run
  only sees the new hints in the critical pairs it creates later.
* **The ordering is not the main effect.** SD solves as well as SO, at an
  equal or better rate.
* **`loop.py --retry-hints G`** (4a34404) also retries a goal, fresh at
  T0, when its original's hint pool has grown by the factor G since its
  last fresh run. On a restart, the growth is read from the `hints=` of
  each goal's last fresh run in the round results. Such goals are retried
  instead of deepened. The full loop runs with `--retry-hints 1.25` from
  22:28. 1,633 unsolved goals qualify, most of them far from a proof.

## 2ab. Sketch climbing (user's suggestion, 14 Nov)

*Notes: [notes/2026-11-14-sketch-climbing.md](notes/2026-11-14-sketch-climbing.md).*

The idea: make a hard goal easy with extra assumptions, then climb the
lattice of assumption sets down to the empty set. Hints from every solved
sketch guide the next ones. The earlier test (2g, sketches) used one
fixed set of assumed siblings below the goal and gained nothing. For a
gap-1 goal, every sibling below it is already proven, so that version
assumed nothing new.

`climb.py` (1e46a74) implements the climb on top of `loop.py`'s
production context: lemmas, kNN lemmas, hint pools and the rule model.

* **Candidate assumptions:** the M nearest unproven siblings of the target,
  by proof line, on either side. They are lines of the same Prover9 proof,
  so they are true.
* **Each sketch run:** the target with an assumption set S as extra axioms.
  twee reports the axioms the proof used (USEDAXIOMS), giving the used
  set U. The proof's steps become sketch hints of the original, shared by
  all its targets and placed before the pool hints. The sets U − {u} are
  queued next, smallest first.
* **End of the climb:** a proof that uses no assumption is a real proof.
  Otherwise the climb ends with a real run that has all the sketch hints.
  If even the full set S fails, its time is doubled.

**First test (CL1, siblings only):** sets/sg1, M = 8, up to 6 sketch runs
of 5 s, then a real run of 20 s. The comparison is S20. CL1 was stopped
after 7 goals and 982 s on 2 threads.

* It found 1 real proof (c_344). S20 solves that goal too.
* There were sketch proofs for 5 of the 7 goals. Often one sibling is
  enough: j_294 follows from goal_292 in 2 s, j_363 from goal_367, c_369
  from goal_353. The 20 s real runs still failed. The steps from the
  sibling to the target are the easy part, and the hints cover only that
  part. The hard part is the sibling itself, which is stalled as well.
* When no sibling set helped, the budget doubling cost a lot: b_364
  reached 547 s in a single run. The doubled budget is now capped at
  4 × the sketch time.

**Laws (user's remark, "frequent extra axioms like commutativity").**
`--laws` adds Veroff-style simplifying laws over the axioms' signature.
They may be false.

* Commutativity of each binary operation.
* Associativity of each binary operation that no axiom defines.
* Each defined operation (an axiom f(X1..Xn) = s) equal to a constant or
  to its first argument.

A law with which twee proves X = Y in 2 s collapses the theory and is
dropped. For the AIM signature, 6 of 18 collapse: t = e, l = e, r = e,
a = x, k = x and comm(t). `--freq K` adds the K most frequent equations of
the original's unconditional proofs. These are true.

The laws make every sketch trivial. A single law, such as l(X,Y,Z) = X or
comm(ld), proves the target in 0.3 s with a dozen hints, and the climb
never reaches the empty set. **The descent alone gives few, short hints.**

**Gap filling (Veroff 2001, "proof sketches").** Veroff does not stop at a
sketch proof. The steps of the sketch that use the extra assumption become
targets of their own. twee-e37's `--print-hints` lists the lemmas that
depend, transitively, on axioms named `assume_*` (HINTS-ASSUMED).
`climb.py --fill S` (b506481) works as follows:

* After each sketch proof, one `--multi-goal` run of S s tries to prove
  those lemmas without the assumptions.
* It uses the true lemmas so far and the sketch hints.
* The proven lemmas become axioms `true_i` of all later runs on the
  original's goals.
* A final proof that uses true lemmas is a chain of real proofs. It is
  also tried once without them.

In the smoke test (b_364), the sketch proofs had 7–27 dependent lemmas.
Each 3 s check proved 0–7 of them, giving 18 true lemmas after 8 sketches.
The 10 s real run still failed.

`--knn K` adds true assumptions: the K unproven goals of other originals
most similar to the target, from problems whose axioms are a subset of
the target's. These are lines of Prover9 proofs, so every lemma that
depends on them is true too.

**Results on sets/sg1** (32 stalled goals; up to 12 sketch runs of 5 s,
then 20 s real; CPU s = the sum of run times, fill runs included):

| arm | solved | CPU s | proofs per CPU-hour |
|---|---|---|---|
| fresh 20 s (S20) | 4 | ~1,000 | 14 |
| fresh 80 s (SD, stopped at 23 goals) | 7 | 3,158 | 8.0 |
| fresh 80 s, ordering 1 (SO) | 8 | 5,898 | 4.9 |
| CL2: siblings + laws + freq, no fill | 4 | 1,458 | 9.9 |
| CL3: CL2 + fill 3 s | 5 | 3,013 | 6.0 |
| CL4: siblings + kNN (true only) + fill 3 s | 6 | 3,618 | 6.0 |

* **CL2 adds nothing.** It solves exactly the S20 four.
* **Gap filling finds a goal no fresh run solved.** That goal is
  mbol_lem1_393, in both CL3 and CL4. CL3's 302 checks proved 369 of
  3,377 dependent lemmas; CL4's 150 checks proved 220 of 1,975.
* **3 of CL4's 6 are chain proofs.** These are t_358, 1243_332 and
  mbol_393. They use 1–4 true lemmas, and one run without the lemmas
  fails at 20 s. With laws, the final proof was always also found
  without them, in 2–10 s; the sketch and fill hints alone carry it.
* **Fresh 80 s solves goals no climb did.** j_294 and t_283 fall to fresh
  80 s runs only. The union of all arms is 9 of 32.
* **The climb is not cheaper than fresh 80 s, but it reaches other
  goals.** In CL4, failing sketches cost 1,257 s, failing final runs
  866 s, fills 677 s and successful sketches 574 s.

**Larger test: sets/sg3.** These are 64 goals of the current loop that
failed L1 (snapshot loops/ULsK, 41,996 proofs).

* CL5, the CL4 config, solved 10/64 in 6,817 CPU s: **5.3 proofs per
  CPU-hour**.
* F3, fresh 80 s, solved 12/64 in 9,919 s: 4.4 per CPU-hour.
* **CL5's 10 are a subset of F3's 12.** On sg3 the climb is only cheaper
  per proof; it reaches no goal that fresh 80 s misses.
* Fresh 20 s was the cheapest arm on sg1 (14 per CPU-hour), and the
  climb ends with a fresh 20 s run. So the right control for the climb
  is fresh 20 s in the same context.

**The loop's own deepening is worse.** After the restart at 23:56, UL10's
runs gave these yields:

| level | runs | proofs | average run | proofs per CPU-hour |
|---|---|---|---|---|
| L0, fresh 20 s | 72 | 8 | 33 s | 12 |
| L1, resume to 80 s | 53 | 17 | 113 s | 10 |
| L2, resume to 320 s | 71 | 21 | 420 s | 2.5 |

L2 took 78% of the CPU. L2 and the climb work on the same goals, those
that failed L1, and the climb yields twice as much per CPU-hour.

**Deployed (15 Nov 00:43).**

* UL11 (`abs/ul11.sh`) runs only L0 and L1 (`--cascade 20,80`) on 12
  workers, with `--sync 60`.
* `climb.py --live loops/UL` (`abs/clive.sh`, 6 workers, 8 once F3 ends)
  takes UL's goals whose last result is a failed L1+ run, nearest proven
  goal below first. Each real proof goes into UL: first the hints file,
  then a solved.tsv row.
* `loop.py --sync S` reads the appended rows every S s and treats them as
  its own proofs: pools, lemmas, and retries of the neighbours. A synced
  cascade with nothing to run waits for such proofs instead of ending
  its round.
* `merge.py` merged the 5 earlier probe proofs (S20, SD, SO, CL3) into UL.

**Control: fresh 20 s beats the live climber on its own targets (01:28).**
The climber's first 102 targets were rerun fresh at 20 s, as UL's L0
(FV). The context was a UL snapshot without the climber's proofs,
loops/ULsL.

| arm | solved | CPU s | proofs per CPU-hour |
|---|---|---|---|
| live climber (CLV) | 29–31 | 7,657 | 15 |
| fresh 20 s (FV) | 36 | 2,861 | 45 |

27 goals were solved by both, 2 by the climber only and 9 by FV only.
The snapshot is 20 minutes newer and includes UL proofs the climber
helped produce, but that cannot explain a 3× gap.

**The cause is in the loop, not the climb.** Round 5 started with
`--cascade-start 0`, which marks every goal as freshly tried. 63 of the
97 targets had no fresh run in round 5 at all; they only resumed states
saved in earlier rounds and contexts. Fresh 20 s proved 28 of those 63
and 8 of the other 34, whatever their pool growth.

The same holds for the sg3 test: CL5's proofs were a subset of fresh
80 s. The climb's apparent advantage was mostly its final fresh run.

**Changes (d2625d2).**

* `loop.py --fresh-first`: with `--cascade-continue`, goals without a
  fresh run in the round get a T0 run first. 8,634 goals qualify; the
  retry gap rules and the line-distance order still apply.
* UL12 (`abs/ul12.sh`) runs it on 16 workers and made 18 new proofs in
  its first 108 s.
* The climber is now a filler (`--cpus 20`, up to 8). It takes only
  goals whose fresh run in the latest round failed as well.

**Fresh runs far from a proof beat resumes near one (UL13, 03:28).**
UL13 ran 2,600 runs in 115 minutes and made 465 new proofs; the climber
added 27. Afterwards I replayed its rows in order. Each run was binned by
its goal's distance, in proof lines, to the nearest goal proven below it
at the time. The proofs-per-1,000 s column uses wall seconds per run.

| level | proof lines | runs | proved | rate | proofs per 1,000 s |
|---|---|---|---|---|---|
| L0 (fresh 20 s) | 0–13 | 613 | 159 | 26% | 8.0 |
| L0 | 14–21 | 491 | 75 | 15% | 4.4 |
| L0 | 22–40 | 515 | 99 | 19% | 5.7 |
| L0 | 41–80 | 527 | 85 | 16% | 4.6 |
| L0 | 81+ | 157 | 6 | 4% | 1.0 |
| L1 (resume to 80 s) | 0–13 | 227 | 36 | 16% | 1.2 |
| L1 | 14–21 | 120 | 21 | 18% | 1.4 |

Fresh runs up to 80 lines away are 3–4× as productive per second as the
resumes. However, with `--line-gaps 21,13` the goals beyond 21 lines came
only from `--far-retry`, after every L1 run. UL14 (`abs/ul14.sh`) uses
`--line-gaps 80,13`, so they now come before the resumes. 7,256 goals
still had no fresh run in round 5.

## 2ac. A learned scheduler for the cascade (15 Nov)

*Notes: [notes/2026-11-15-learned-scheduler.md](notes/2026-11-15-learned-scheduler.md).*

UL14 (`--line-gaps 80,13`) made 258 new proofs in its first 25
minutes, about 610 an hour, against UL13's 243 an hour. Moving the fresh
runs up to 80 lines away ahead of the resumes was worth about 2.5×
(2ab).

The next question was which goals to run fresh first. The loop has run
16,000 fresh runs in rounds 3–5. `schedfeats.py` replays them in order
and records each run's features as they were when it started:

* distances in proof lines to the nearest proven goal below and above;
* failed runs so far, and failed fresh runs with the same nearest proven
  goal below (`nfail_ctx`);
* growth of the original's proven goals since the goal's last fresh run;
* the original's success rate over its last 30 fresh runs;
* the goal's size and number of variables.

**Fresh runs in a new context win.** A fresh run succeeds 43% of the
time when its nearest proven goal below has changed since its last
failure. It succeeds 11–15% when that goal has not changed, at any
distance: 22% even 81+ lines away with a new context. (UL r5, 5,534
fresh runs.)

| failed fresh runs, same nearest proven goal below | runs | proved |
|---|---|---|
| 0 | 1,232 | 43% |
| 1 | 695 | 15% |
| 2 | 776 | 13% |
| 3 | 846 | 14% |
| 4+ | 1,985 | 11% |

**The model.** `schedmodel.py` is logistic regression on one-hot
quantile bins, 61 weights. It was trained on rounds 3–4 and the first
60% of round 5, and tested on the last 40% of round 5 (2,253 runs, 21%
proved).

| ordering | AUC | top 10% | top 25% | top 50% |
|---|---|---|---|---|
| model | 0.737 | 54% | 43% | 32% |
| proof-line distance | 0.599 | 30% | 29% | 25% |

The weights (log-odds) were these:

* a new context: +0.93;
* 1 to 4+ earlier failures in the same context: −0.11 to −0.63;
* growth of the original's proven set above 8%: +0.55;
* a hot original (recent success rate above 35%): +0.49;
* more than 84 lines from the nearest proof below: −0.86.

**In the loop.** With `loop.py --sched-model M.json`, the fresh-run
candidates are the goals whose context or pool changed, at any distance.
They are ordered by predicted success. Goals predicted below
`--sched-pmin` (0.06) wait until slots are idle, after the resumes; an
L1 resume proves about 17% in 3× the time. The history is replayed at
start (2 s). Each finished run and each synced proof updates it, and the
scores of the changed original are recomputed.

A 2-worker check (loops/SMT, a reflink copy of UL) made 16 proofs in 23
fresh runs in its first 5 minutes; these were the model's top picks.

**A/B 1: a tie after an hour.** ABa (distance order) and ABb
(`--sched-model sched/m2.json`, retrained with UL14's runs) ran from the
same reflink copy of UL, 9 workers each, from 04:05 to 05:07.

| minutes | ABa (distance) | ABb (model) |
|---|---|---|
| 8.5 | 11 | 60 |
| 29 | 97 | 128 |
| 43 | 122 | 156 |
| 53 | 166 | 171 |
| 62 | 177 | 180 |

The union was 255; at 29 minutes only 30 proofs were common.

* ABa began with 76 resumes (L1, 16% at 3× the cost of a fresh run).
  Then it worked the near goals in proof order: 35% of its fresh runs
  succeeded, each proof giving a new context to the goal above it.
* ABb ran no resumes. Its fresh runs proved 53, 53, 18, 27, 6 and 14
  per 10 minutes. In the fifth bin, 65 of 132 runs went to one
  original, nslm_to_aa1, at a median of 702 lines from the nearest
  proof: 6 proved, 22 predicted.

**The cause** was the quantile bins: one bin held every distance beyond
84 lines, so 700 lines scored like 100. In rounds 3–5 the gain from a
new context also falls with the distance:

| proof lines | new context | same context |
|---|---|---|
| 0–13 | 59% | 19% |
| 22–40 | 48% | 15% |
| 41–80 | 27% | 11% |
| 81–160 | 16% | 5% |
| 161–320 | 15% | 8% |
| 321–640 | 11% (28 runs) | 6% (16 runs) |

**Fixes.**

* Fixed bins for the distances (13, 21, 40, 80, 160, 320 lines).
* `lg_new`: the distance when the context is new, crossed into one
  feature.
* `--sched-max-lgap 320`: farther goals run only in idle slots.
* `--sched-retrain 200`: retrain on all replayed and new fresh runs.

On ABb's last 515 fresh runs, the fixed bins raised AUC from 0.751 to
0.807. Both arms (251 proofs) were merged into UL, and the climber was
stopped.

**A/B 2: the scheduler with a 10 s first level wins.** Three arms ran
from one copy of UL (43,272 solved), 7 workers each, from 05:16:

* ABc: distance order;
* ABd: `--sched-model sched/m3.json --sched-max-lgap 320 --sched-retrain 200`
  (m3: fixed bins and `lg_new`, AUC 0.736 against 0.671 for distance);
* ABe: as ABd, with a 10 s first level (`--cascade 10,80`).

New proofs (ABc / ABd / ABe):

| minutes | ABc | ABd | ABe |
|---|---|---|---|
| 12 | 15 | 34 | 33 |
| 22 | 19 | 43 | 63 |
| 33 | 22 | 52 | 68 |
| 35 (stopped) | 22 | 52 | 69 |

Union 88. ABe ran twice as many fresh runs for the same CPU (14% proved
against 24% for ABd).

After 25 minutes all three arms ran dry: 5 proofs in 10 minutes on 21
CPUs. A/B 1 and UL14 had taken most of the new contexts. The remaining
candidates had already failed in their current context. With the same
settings, such a rerun repeats a deterministic search, so it can only
succeed if the hint pool has grown.

The arms were stopped at 35 minutes and merged into UL (43,360 solved).

**Next: a portfolio for stalled goals.** sets/st80 holds 80 of the
1,575 goals within 80 lines of a proof whose last fresh run failed with
the same nearest proven goal below (`abs/stalled_set.py`). Each goal gets
fresh 20 s runs in 8 variants of the L0 configuration (`abs/port.sh`,
snapshot loops/ULsM, 2 workers each):

* the base configuration;
* term orderings 1 and 2 (`--p9-orders 4 --p9-order-offset k`);
* no rule model;
* 12 or 2 sibling lemmas;
* the 500 most frequent hints;
* rule threshold 0.3 with penalty 5.

Production (UL15, `abs/ul15.sh`) meanwhile ran the scheduler with
`--cascade 10,80` on 4 workers: 8 new proofs in 100 fresh runs in
7 minutes, about 16 proofs per CPU-hour.

**The portfolio does nothing on stalled goals.** After 35–41 goals per
variant, every variant except the 500-hint one proved exactly one goal,
the same one: com_Ralt__goal_246, whose pool had grown with the merges.
On about 35 stalled goals, 7 variants at 20 s proved nothing beyond it:

* other term orderings;
* no rule model;
* more or fewer sibling lemmas;
* other rule-model settings.

The probe was stopped there (06:00).

So a stalled goal needs new information: a proof nearby, or much more
search. Settings make no difference. Production went to 20 workers
(UL16, `abs/ul16.sh`, 06:01).

**Breakthrough probes.** On sets/st79 (st80 without
com_Ralt__goal_246), from ULsM, 2 workers each, 06:05–06:22:

* the sketch climber as CL5 (8 unproven siblings and 8 kNN goals as
  true assumptions, `--fill 3`; `abs/clst.sh`): 0 of 15 goals;
* fresh 80 s runs (`T=80 V=base abs/port.sh`): 1 of 11.

These goals resist everything tried at these budgets.

> **Correction (15 Nov, 09:40): these probes are invalid.** loop.py
> `--init` imports only the rows of round 0, and the snapshot loops/ULsM
> kept the loop's round numbers. So every probe from it ran with the
> 33,720 round-0 proofs as context (lemmas, pools, kNN lemmas) instead
> of 43,484. This covers the portfolio, the breakthrough probes and the
> stalled-goal probes of 2ad (`--pool tier`, `--pool knn`, rm7t).
> In the full current context, fresh 20 s runs prove about 15% of these
> goals (2ae). The snapshots for the paired model tests (ULsT) and later
> probes (ULsN) have the column set to 0.

**Resumes are now the productive work.** UL16 made 43 new proofs in
20 minutes, about 6.5 per CPU-hour. Its fresh runs proved 27 of 424
(6%, predicted 41). Its resumes (10 s to 80 s) proved about a quarter.

In round 5, resumes succeed equally at every distance: 23% within 13
lines, 19% at 14–21, 23% at 22–40, 23% at 41–80, 29% beyond (24 runs).
However, `--line-gaps 80,13` allowed resumes only within 13 lines.
UL17 (`abs/ul17.sh`, 06:23) uses `--line-gaps 80,80`. It made 26 new
proofs in its first 6.5 minutes, then 5 in the next 9.

**Where the unsolved goals are (06:45).** The 8,335 unsolved goals form
1,006 runs of consecutive unsolved goals within their originals:

* 559 single holes, between two proven goals;
* 95 open tails, from the goal after an original's last proven goal to
  its end, with 4,851 goals (58%);
* the rest are runs closed by a proven goal above.

The 95 tail heads are the best breakthrough targets: a head's proof
gives the goal above a new context (about 50%), and so on up the chain.
They had barely been tried. 93 had never run beyond 80 s, and the
median head had 6 runs and 416 wall seconds in all.

**Changes** (`loop.py --head-first --head-only-from L`, 9cc44be):

* within a cascade level, tail heads deepen first;
* only heads go to levels ≥ L;
* heads deepen at any distance.

UL19 (`abs/ul19.sh`, 06:43) runs `--cascade 10,80,320,1280 --head-first
--head-only-from 3`. The order follows proofs per CPU-second. Resumes
to 80 s go first (about 20%, 150 wall s), then the heads' 320 s runs,
then the others' (about 30% of L1 failures in r5, about 480 wall s).
The heads' 1,280 s runs come last.

That left about 2,185 goals waiting for an 80 s resume (about 4 hours)
before any head ran at 320 s. UL20 (`abs/ul20.sh`, 06:58) therefore put
the heads first for their 80 s and 320 s levels.

**Negative: the heads at 320 s.** In UL20's first 36 minutes the heads'
320 s resumes proved 5 of 62 (8%, not the 30% assumed), about 0.4 proofs
per CPU-hour. There were 4 new proofs in all. The tail heads are the
hardest goals, not the cheapest breakthroughs.

UL21 (`abs/ul21.sh`, 07:36) goes back to level order:
* `--cascade 10,80,320` without `--head-first`;
* the 80 s resumes first (16–20%), then the 320 s runs.

## 2ad. Retraining the guidance on hard proofs, and a GNN (user's questions, 15 Nov)

*Notes: [notes/2026-11-15-retrain-gnn-p9side.md](notes/2026-11-15-retrain-gnn-p9side.md).*

**Is ENIGMA retrained?** No. Production has used rm4t, fixed, since
round 4, because three earlier tests found no online gain from
retraining:

* rm6t (2r) did not help;
* rm7t (+0.03 offline AUC, 2u) did not help;
* the online ENIGMA loop on sets/e3 lost, 971 against 987 with the
  round-0 model kept fixed (2u).

Those tests used easier goals and short runs. The user notes that the
later long proofs should be worth more for training than the many easy
ones. Rounds 4–5 have 3,274 given logs; round 5's median log is 203 KB,
against 51 KB in round 1.

**Stalled goals again** (INVALID, see the correction in 2ac: ULsM gave
the probes only the round-0 proofs) (sets/st79u: 73 unsolved goals of st79, snapshot
ULsM refreshed at 07:35, fresh 20 s, 2 workers each):

| variant | proved |
|---|---|
| base (rm4t, own original's pool) | 0 of 64 |
| `--pool tier:20:500:0.1` (kNN hints from other originals, then own pool) | 0 of 62 |
| `--pool knn:20:1000` | 0 of 73 |
| rm7t | 0 of 34 |

Neither hints from other originals nor rm7t move these goals at 20 s.

**Offline test set.** The 400 newest round-5 given logs (sets/ultest,
given/ultest) are hard proofs that neither rm4t nor rm7t saw.
rulemodel.py's new `--load M.txt,V --test-only` mode evaluates a saved
model on exactly those. rm4t: AUC 0.846.

* **rm7t** (base data plus loops/UL/given at 14 Nov 11:00, rounds 1–3):
  AUC **0.897**, better than rm4t on 341 of the 400 problems.
* **rm8h** (`abs/rm8h.sh`): rm4t's base data plus the 2,875 other
  round 4–5 logs (given/ul45), negmax 150: AUC **0.894** (26 GB, 22 min).
  The long proofs add nothing over rm7t's in-loop data from rounds 1–3.
  What helps offline is training on proofs of the same originals.

Calibration differs. At threshold 0.1, rm4t keeps 93.2% of proof rules
and defers 35.1% of the others; rm7t keeps 97.7% and defers 24.5%; rm8h
keeps 98.8% and defers 15.4%. At the production threshold the better
models therefore filter less.
* **GNN** (`gnn.py`, after Chvalovský, Korovin, Piepenbrock and Urban,
  LPAR 2023): a name-independent graph network with dynamic samples,
  CPU torch. Each sample is a problem cut at a random point, with the
  axioms, the goal and the last 512 rules added as context, and the next
  128 rules to score.
  * The graph has nodes for equations (axiom, goal, context or query),
    terms, variables and symbols; symbols are typed by arity only.
  * Messages pass along the left-side, right-side, symbol and argument
    edges, with mean aggregation; d = 32, 8 layers.
  * Evaluation scores every added rule of a test problem, chunk by chunk,
    with its preceding rules as context, giving a per-problem AUC like
    rulemodel.py's.
  * A 200-step smoke test reached AUC 0.726 on 5 test problems. The main
    run (6 threads, models/gnn1.log, 08:00) reached AUC **0.809** on 100
    test problems at step 2,000 and **0.802** at step 4,000. Its training
    loss kept falling (0.49 to 0.38), so it was stopped at step 4,000
    (models/gnn1.pt). At this size, 32,000 samples and about 25 CPU
    minutes, it is below both LightGBM models.
    The iProver results came with much longer training, and with the GNN
    scoring every generated clause for given-clause selection. Here a
    model only defers a rule once, at double cost (below).

**Online, paired** (`abs/mab.sh`; snapshot loops/ULsT = UL minus the 400
test goals, so each is unsolved, and the context is the same for every
arm; fresh 20 s, production L0 settings, no `--online`):

| model, threshold | proved of 400 | only this arm | work on shared proofs |
|---|---|---|---|
| rm4t, 0.1 (production) | 271 | 8 | 1 |
| rm7t, 0.1 | 273 | 10 | 0.98 (geometric mean; median 1.00) |

| rm7t, 0.2 (rm4t's proof-rule loss, 47.6% of the others deferred) | 269 | 9 | 1.00 |
| rm4t, 0.2 (control) | 261 | 4 (14 lost) | 1.04 |

`abs/mabcmp.py` compares the arms. The +0.05 AUC gives nothing online:

* at the production threshold, rm7t ties rm4t;
* at its stricter matching threshold, rm7t ties rm4t too;
* the stricter threshold alone loses 10.

| oracle rmO (trained on these 400 goals' own logs: AUC 0.956; at 0.1 keeps 99.3% of proof rules, defers 57.3% of the others), 0.1 | 273 | 9 (7 lost) | 1.03 |

So the better model only cancels the cost of a stricter filter. The
searches are driven by the pools and lemmas. 52 of the 263 shared
proofs have identical work under both models, and the rest differ by a
few per cent either way. **Even a near-oracle model gains nothing
through the defer-once filter** (rmO: 273 against 271, work 1.03).
Production keeps rm4t. Rule-model quality cannot pay off through this
mechanism, whether ENIGMA or GNN. A GNN would need a stronger hook, such
as the passive queue's order, where twee would have to score millions of
critical pairs per run. So the GNN is compared offline only; its twee
integration (a scoring server with batched calls) was not built.

The work ratio on shared proofs is a BliStr-style proxy: abstract time
to the same proofs (Urban 2013, user's remark). Counts of proved goals
stay the main measure, because hints may guide in a roundabout way.

**GNN version 2** (user, about 09:05: the signature is small, so the GNN should
be symbol-aware; mark the conjecture terms; expand the goal constants
from flattening; follow the dynamic data collection; train more on the
harder proofs and clauses).

* twee prints its given rules with the goal constants already expanded
  (`expandGoalConsts`): flattening constants become their definitions,
  and skolem constants become fresh variables. The ENIGMA model scores
  the same expanded forms. So the logs have no goal constants, but they
  also lose any mark that a term came from the conjecture.
* Changes in `gnn.py`:
  * symbol nodes get a learned embedding per name (the vocabulary is 9
    symbols) besides their arity type;
  * the conjecture's variables become skolem nodes, and its terms are
    typed as goal terms;
  * every rule term that is a variant of a conjecture subterm with at
    least two function symbols is typed as marked and linked to that
    goal term by a goal-match edge (about 25% of rule term nodes);
  * the query's index in the run goes into the scoring layer;
  * training draws problems with weight (log size) ** 0.5 and anchors
    samples on proof rule i with weight i + 1. Long proofs and their
    late rules dominate.
* The samples stay dynamic: the rules added so far are the context, and
  the next added rules are the queries. That is the decision twee's rule
  model makes.
* Positives and negatives are balanced, as in Chvalovský et al.:
  * the loss is weighted per batch so that each class carries half the
    weight;
  * half the samples are anchored on a proof rule.
  Both versions do this.
* A 200-step smoke test gave AUC 0.847 on 5 test problems; version 1 gave
  0.726 at the same point. The main run (models/gnn2.log, 8,000 steps,
  6 threads, from 09:14; production on 11 workers) is evaluated on the
  same 100 test problems as version 1.

| on the same 100 test problems | AUC |
|---|---|
| GNN version 1 (names ignored), step 2,000 / 4,000 | 0.809 / 0.802 |
| **GNN version 2**, step 2,000 / 4,000 / 6,000 / 8,000 (final) | **0.864 / 0.879 / 0.876 / 0.887** |
| rm4t (production ENIGMA) | 0.837 |
| rm7t (ENIGMA with in-loop data) | 0.892 |
| oracle rmO (trained on these problems) | 0.958 |

The user's changes add about 0.07–0.08. Version 2 ends at 0.887: well
above the production ENIGMA model, level with rm7t. Online, the oracle
results (above, and with repeated deferral in 2af) mean the filter would
not use it.

**Prover9 on stalled goals** (`p9twee.py`): a LADR problem with
prolog-style variables, so TPTP names and twee hints need no
translation. It holds:

* the axioms, plus 6 proven siblings on either side as assumptions;
* the conjecture;
* the original's whole twee pool as `formulas(hints)`.

*(20 Nov: this proof, like 15 more Prover9 proofs, used a lemma that p9twee.py had turned into a false axiom, and is
not a proof; [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md).)* The first hit is aK2_eq_aK3_r__goal_241, a goal every twee variant failed
(settings, pools, models, the climber and 80 s runs). Prover9 proved it
in 44 s with 320 given clauses. The proof has 448 steps at level 64, with
clauses up to weight 1027, and 277 of its steps are hint matchers. The
proof's positive steps become the goal's twee hints, minus steps with the
goal's skolem constants.

* On all 72 stalled goals at 60 s (loops/P9T), Prover9 proved only that
  one: 1 in 72 CPU minutes, about 0.8 proofs per CPU-hour, on goals
  where twee gets 0.
* One run crashed inside Prover9-new ("stack smashing detected" after
  3,300 demodulation-limit hits, im2_24_to_25__goal_382), which looks
  like a bug in that build.
* Twee with the Prover9 proof as hints but without the sibling lemmas
  still fails the goal (30 s): the proof leans on the lemmas.
* Veroff's own AIM settings (from the AIM_REDONE `.in` files: kbo,
  `lex_order_vars`, no `back_demod`, `restrict_denials`, `para_from_small`,
  no `cac_redundancy`, `max_weight` 5) fail both goals Prover9 has proved
  so far.
  * `max_weight` 5 exhausts the search in 4 s, and 40 times out.
  * These settings depend on hint lists from earlier attempts at the
    same goal, so the defaults stay for our sibling pools.

**In production since 08:56:** `p9twee.py --live loops/UL loops/P9L -j 3
--timeout 60` (`abs/p9live.sh`), a Prover9 side worker.

* Targets: the loop's stalled goals within 80 proof lines (957 at the
  start), nearest first.
* A goal is retried only when its nearest proven goal below changes or
  its pool grows by 25%.
* Proofs go straight into loops/UL (hints file, then a solved row; the
  loop reads them with `--sync 60`).
* Its first proof came after 3 minutes: nslm_to_aa1__goal_688, in 53 s,
  with a pool of 15,182 hints.

Production runs beside it on 17 workers (UL24).

## 2ae. The stall was partly an artefact: kNN lemmas the cascade did not see (15 Nov)

*Notes: [notes/2026-11-15-retrain-stall-artefact.md](notes/2026-11-15-retrain-stall-artefact.md).*

**Control in the full context.** Snapshot loops/ULsN is UL at 09:30
with every row imported. On sets/st79u (goals whose fresh run and resume
failed in round 5 with an unchanged nearest proven goal below), fresh
20 s runs prove **7 of 71 goals without the lemma change and 10 with it**
(`abs/unit_probe.sh`, PU_0 and PU_1; +3/−0; work on shared proofs 0.99).
That is 18–25 proofs per CPU-hour, against production's 2.

* Some are now easy: nil3_24__goal_356 takes 1.7 s, nil3_32__goal_380
  1.4 s and nil3_29__goal_388 1.9 s.
* nil3_24__goal_356 had failed twice on 14 Nov, the last time a 141 s
  resume, and was never retried.
* **All six proofs of the first 35 use kNN lemmas**, proven goals of
  other originals with the same or a subset of the axioms
  (`--lemma-knn 10 --lemma-subsets`), proven after the goal's last run.
  For example nil3_24__goal_356 used TLRproperties_2__goal_314 and
  nil3_26__goal_372.

**Two leaks in the cascade:**

1. The retry gate looks only at the sibling context and the pool's
   growth. A change in a goal's kNN lemmas never made it eligible. The
   scheduler ranked these goals near the top (p 0.12–0.26, above its
   0.06 cutoff), but they were never candidates.
2. The kNN lemma index was built once, when the cascade started, so new
   proofs reached other goals' kNN lemmas only at a restart.

**Fix** (`loop.py --retry-knn`, 3f05146):

* the kNN index is rebuilt every 30 minutes or 300 proofs;
* each fresh run's kNN lemma set is recorded (DIR/knn_at.tsv);
* a goal whose current set differs from its recorded one is eligible for
  a fresh retry;
* the scheduler's order is walked best first, and the kNN check (27 ms
  a goal) runs only as far as free slots need;
* goals with no record count as changed. The first run after deployment
  is therefore one fresh pass in the full current context, best-scored
  goals first.

A smoke test from ULsN (sets/st79u, `--cascade 10,80`, 2 workers) proved
5 of these goals in 16 runs and 135 s. **Production since 09:44: UL26**
(`abs/ul26.sh`, 11 workers). Its first 100 fresh runs made **41 new
proofs in 132 s**, against about 2 proofs per CPU-hour before. The cap
on kNN checks per scheduling pass (b4c5cb5) arrives with the next
restart.

**Unit forms of conditional lemmas** (`lemmas.lemma_form`). A conditional
goal `~ s = X | C = D` whose hypothesis binds a variable X that does not
occur in s is equivalent to the unit equation `C = D` with X replaced by
s.

* That is 6,235 of AIM60k's 9,052 conditional goals (12% of all
  goals), and lemma import had skipped them all, as siblings and as
  kNN lemmas. The other 2,817 stay out: they are genuine Horn clauses.
* Prover9 had used such a sibling. Its proof of aK2_eq_aK3_d__goal_405,
  the goal twee failed 9 times, uses
  `-m(k(A,B),t(t(B,C),D)) = E | m(t(t(B,C),D),k(A,B)) = E`.
* The change gives 2,234 of the 8,270 unsolved goals a different set of
  sibling lemmas. On st79u: +3 (10 against 7 of 71).
* `TWEE_LEMMA_UNITIZE=0` turns it off.

## 2af. Repeated deferral, and definitions that twee folds (15 Nov)

**Repeated deferral** (`twee-e38 --rule-defer-max K`, 239245f). The
oracle rule model gained nothing online with the defer-once filter (2ad:
273 against 271). Could a stronger filter let a better model matter? A
critical pair below the threshold is now deferred up to K times, its
score multiplied by the penalty each time.

* With the default K = 1, e38 gives the same runs as e22 (20 of 20
  identical in rules and deferral counts).
* Paired test, fresh baseline (sets/ultest, the current lemma code,
  `abs/defer_test.sh`): rm4t with defer-once against the oracle rmO with
  K = 3 and penalty 5. **270 for the oracle against 269 for the
  baseline** (of 400; +8/−7), and 11% more work on shared proofs.
* So a better model does not pay through a stronger filter either. The
  GNN (2ad) stays offline: wiring it into twee is not worth it while the
  oracle itself gains nothing.

**Prover9's side worker partly races twee.** Of its 9 proofs, 4 are
short (1, 3, 10 and 130 steps). Rerun fresh at 20 s in today's context,
twee proves 2 of the 9. aK2_eq_aK3_r__goal_212 is a 1-step proof for
Prover9 (0.2 s) from sibling 209, which twee had too. Twee fails it in
20 s with 12,880 rules.

**The cause: twee folds definitions, Prover9 unfolds them.**

* AIM's defined operations are `a, k, l, r, t`, for example
  `t(A,B) = ld(B,m(A,B))`.
* Twee's KBO orients each definition right to left, since the defining
  term is bigger: `ld(X,m(Y,X)) -> t(Y,X)`. Prover9's default LPO in
  `p9twee.py` unfolds them (Veroff's own runs used KBO and folded, which
  is why the goals contain t and r).
* In goal 212 Prover9 unfolds t, and sibling 209 then rewrites the goal
  in one step. Twee needs the critical pair of 209 with the t rule, a
  pair of weight about 58, and never selects it.
* Twee has no option for this. `--kbo-weight0` and `--precedence` cannot
  make `t(A,B)` bigger than `ld(B,m(A,B))`, because B occurs twice.

**`unfold.py`** substitutes a problem's definitions away and drops them:
axioms, lemmas, conjecture and hints are then over m, ld, rd and e.
`loop.py --unfold` does this for every run. Hints are unfolded with the
problem's definitions. Folded runs normalise unfolded pool hints back,
because hints are kept normalised by the rules (`--eqhint-normalise`, on
by default).

* Goal 212 unfolded: **1.2 s, 2,755 critical pairs**.
* Unfolded terms are bigger. Unfolded runs take about 4.5 times as long
  in real time for the same abstract time (plain twee on 200 frontier
  goals, stopped after 14 runs: unfolded 1, folded 0). Most failed
  unfolded runs stop at `--max-cpu 200` before 20 abstract seconds.

**Results** (fresh 20 s runs in the production context: 6 sibling
lemmas, 10 kNN lemmas, the original's pool, rm4t; snapshots of UL at
10:24 and 10:44):

| goals | folded | folded + lemma instances | all unfolded | only t unfolded |
|---|---:|---:|---:|---:|
| the 9 Prover9 proved (sets/p9l9) | 2 | 3 | **7** | 3 |
| the first 10 of 231 that Prover9 failed (sets/p9no40) | 0 | 0 | **3** | |
| random frontier goals (sets/unf80), first 28 | 1 | 1 | 1 (0 of 25 without rm4t) | |
| sets/lf116 (p9no40 + unf80), 111 run | 4 | 4 | | |

The folded column is a control in the same snapshot (loops/LF_ctl).
Without it, "stalled" overstates the gains: the 4 folded proofs on
lf116 come from context that has arrived since production's last try
of these goals.

* Unfolding is not a better representation in general: on random
  frontier goals it gains nothing.
* It works on the goals Prover9's worker picks: the stalled goals
  nearest to a proof, in proof lines. There it proves goals both Prover9
  and folded twee fail.
* Unfolding everything beats unfolding only t (7 against 3).
* **Folded lemma instances** (`loop.py --lemma-fold 8`,
  `unfold.lemma_fold_text`) add, for each lemma subterm that unifies
  with a definition's body, the lemma under the unifier, folded. Goal
  212's missing critical pair is one of these, and 212 then takes
  2,000 critical pairs. Elsewhere they gain nothing: the same 4 of 111 on
  lf116 as the control, with 1.5 times the work. Most unfolded proofs
  need more than one such step.
* The 4 new proofs were merged into UL.

**In production since 11:18: an unfolded-twee side worker**
(`uflive.py`, `abs/uflive.sh`, 4 workers). It replaces the Prover9
worker, which was stopped at 10:24 after 9 proofs in 283 tries. Each
cycle:

1. syncs UL's proofs into loops/UFL;
2. takes 24 of p9twee's targets, nearest first;
3. runs one `loop.py --unfold` round on them;
4. merges the proofs into UL.

Its first two cycles proved 8 of 48 goals in 27 minutes on 4 workers,
about 4.5 proofs per CPU-hour. Production makes about 4 per CPU-hour
(UL27: 54 in 79 minutes on 10 workers).


## 2ag. Tail heads, and the cutoff between fresh runs and resumes (15 Nov)

*Notes: [notes/2026-11-15-heads-fresh-vs-resume.md](notes/2026-11-15-heads-fresh-vs-resume.md).*

**Tail heads** are the first unsolved goal after an original's last
proof. There are 92, with lines gaps 13–68 (median 34), and most
unsolved goals sit behind them. On 30 random heads (sets/heads30,
snapshot ULsV at 11:57, fresh 20 s, production context):

| arm | heads proved |
|---|---:|
| folded (control) | 0 of 30 |
| cross-original pool (`--pool tier:20:500:0.1`) | 0 of 30 |
| unfolded (2af) | 0 of 28 |

This also retests the tier pool, whose earlier negative came from the
invalid snapshot.

* **20 sibling lemmas** instead of 6: 0 of 30.
* **Later goals as hints** (`loop.py --hint-after 10`): the statements of
  the next 10 unsolved unit goals of the original. They are unproven, so
  hints only. 0 of 30 heads.
* **Twee settings on stalled goals, retested** (`abs/var_test.sh`, from
  ULsV, 36 goals Prover9's worker failed). The earlier portfolio
  negative also came from the invalid snapshot. Every arm proves 0:
  * the control;
  * `--no-flatten-goal`;
  * `--flatten-goal-lightly`;
  * `--flip-ordering`;
  * `--kbo-weight0`.

  On these goals only unfolding (2af) has proved anything.

**Fresh runs against resumes.** The last 1,500 UL27 runs:

| level | proved | runs | rate | CPU-hours | proofs per CPU-hour |
|---|---:|---:|---:|---:|---:|
| fresh (10 s) | 54 | 1,039 | 5.2% | 5 | 10.8 |
| resume to 80 s | 47 | 461 | 10.2% | 20 | 2.4 |

* A resume now costs 9 fresh runs (156 against 17 wall seconds). The
  0.06 cutoff, below which fresh candidates wait behind the resumes,
  assumed 3.
* The scheduler also overpredicts, 2.3 times (33 proofs against 77
  predicted).
* So a fresh run predicted at about 0.025 or more pays better than a
  resume.

**UL28 from 12:17** (`abs/ul28.sh`): `--sched-pmin 0.025`, 12 workers.
UL27's rate, for comparison: 93 proofs in 129 minutes on 10–11 workers,
plus 18 synced from the side workers.

**A 5 s first level?** Of the last 194 fresh proofs, 84% came within
10,000 critical pairs (5 abstract s), 69% within 5,000. The median is
3,390. A 5 s run costs 7.8 wall s against 17.8 for a 10 s run (8
failing goals). That is about 1.9 times the fresh proofs per CPU.

* **A/B from 12:48** (`abs/lvl_ab.sh`): reflink copies UA and UB of UL
  at 16,416 r5 rows, 6 workers each. UA uses levels 10,80,320, UB
  5,80,320.
* UB first ran with the 0.025 cutoff. After its scheduler retrained on 5
  s outcomes, the fresh candidates fell below it, and UB went to resumes
  after 360 fresh runs. The break-even scales with the fresh run's cost
  (0.44 × 0.025), so UB restarted at 13:08 with `--sched-pmin 0.011`.
* **Result after 62 minutes (13:50): 5 s 33 proofs, 10 s 20**, with 15
  in both (UB 18 alone, UA 5 alone).

  | arm | fresh proved / runs | resumes proved / runs |
  |---|---:|---:|
  | UA, 10 s, cutoff 0.025 | 13 / 476 | 7 / 91 |
  | UB, 5 s, cutoff 0.011 from 13:08 | 19 / 1,254 | 14 / 77 |

  Both arms were merged into UL (37 new).
* **UL29 from 13:55** (`abs/ul29.sh`): `--cascade 5,80,320`,
  `--sched-pmin 0.011 --sched-pmin-auto 400`, 12 workers.
* **`--sched-pmin-auto W`** (loop.py) sets the cutoff online from the
  last W fresh runs and W resumes: resume proofs per wall second, times
  the mean fresh wall seconds, divided by the scheduler's calibration
  (fresh proofs over predicted). With UL27's numbers it gives 0.026.

**Sibling lemmas in unfolded runs** (`abs/ufl_lem.sh`, sets/p9no_v, ULsV,
fresh 20 s, unfolded): 6 lemmas 3 of 36, 12 lemmas 4 of 36. The 12-lemma
arm proved all three of the 6-lemma arm's goals, plus one more. One goal
is within noise, so the side worker keeps 6.

**Long budgets on heads (15 Nov 18:15–19:05; `abs/heads_long.sh`, sets/heads_u,
the 30 heads still unsolved, fresh 160 abstract s, snapshot ULsW).**

* **Unfolded (HLU), stopped after 8 heads: 0.** Every unfolded run hit the
  800 s CPU cap (797–1,123 s) before 160 abstract s. Unfolded terms are
  bigger, and at long budgets the runs become CPU-bound.
* On the same 8, folded (HLF) proved 1 (aK2_eq_aK3_q__goal_270, 500 s).
  HLF continues; at 12 of 30 it has 3.
* So unfolding, which proved stalled goals at 20 s (2af), does not
  scale to the long budgets heads need.

**What a head proof is worth.** Replaying production's round 5
(loops/UL/r5/results.tsv, 21,784 runs, 2,751 new proofs), 69 proofs
were of the goal right after an original's furthest proof.

| proofs of the same original after a head proof | within 500 runs | 2,000 | 8,000 |
|---|---:|---:|---:|
| mean | 3.2 | 3.6 | 4.6 |
| median | 1 | 1 | 2 |
| none | 30 | 28 | 22 |

Other proofs are followed by 5.3 within 2,000 runs. So a head proof does
not unlock a chain; the goals behind a head are each hard. At about 0.4
proofs per CPU-hour for heads at 320 s, a head is worth about 2 proofs
per CPU-hour counting what follows. That is below production's current
3.5, so the scheduler's equal weighting of proofs does not starve the
heads.

## 2ah. A hint generator (user's suggestion, 15 Nov)

*Notes: [notes/2026-11-15-hint-generator.md](notes/2026-11-15-hint-generator.md).*

The user asked whether the GNN2Seq model of Chvalovský, Suda and Urban
("Neural Conjecturing for Saturation Theorem Provers", IWIL 2026;
github.com/JUrban/E_conj_dev1, branch vampire4) could be trained here
to propose hints from a run's current situation: generate new hints
rather than rank clauses.

* **No GPU is needed.** Their model has about 3M parameters and trained
  on a GPU in 48 minutes per 100 epochs. Ours is smaller (0.58M) on
  small AIM graphs and trains on 4 CPU threads at about 1.7 s per step.
* **Why it might help where ranking stopped helping.** The ranking
  models (2ad) can only reorder what twee produces. Stalled goals lack
  hints for steps that no sibling proof contains. Of the future proof
  steps of 188 solved test goals (cut halfway through each proof), the
  original's hint pool holds 63% (median pool 4,774 hints); the other
  37% must come from somewhere else.
* **Generated hints cost little when wrong.** Twee matches hints by
  variant, and every critical pair is a theorem, so a false generated
  equation never matches anything.

**Model** (`hints/gen.py`):

* **Encoder:** gnn.py's symbol-aware graph (version 2: symbol nodes,
  goal skolems, goal-term marks) over the axioms, the goal and the last
  256 rules before a cut; 6 message-passing layers, dimension 64.
* **Decoder:** a causal Transformer (2 layers, 4 heads) with
  cross-attention to all the sample's nodes. It writes an equation in
  prefix order with three actions: SYM points at one of the sample's
  symbol nodes (pointer decoding, as their PointerTreeDecoder), VAR
  picks a variable slot numbered by first occurrence, EOS ends. An
  arity count keeps every sample a well-formed pair of terms, as their
  arity-constrained decoding.
* **Training samples:** a given log cut just before a proof rule (later
  cuts likelier); the targets are up to 16 of the proof rules from the
  cut on, in random orientation; logs weighted by size^0.5 (hard
  proofs). Data: given/train_only, ul45 and loops/UL/given (17,725
  logs), with the 400 newest r5 logs (sets/ultest) held out.
* **Sampling** decodes incrementally (cached self-attention; memory
  keys and values computed once for all samples): 200 equations in
  about 2 s on one thread.

**Online use** (`loop.py --gen-model M --gen-n N`): a failed run saves
the axiom rows and its last 256 rules (`genctx/`). twee-e39 adds
`--print-given-unsolved` for this; before, the given rules were printed
only with a proof. When the goal's next level resumes the saved state,
the run gets N sampled equations on top of its pool hints.

**Sanity check:** trained on one problem for 300 steps, the model
reproduces 4 of that problem's 8 proof steps after the halfway cut.

**Training speed.** The first version took 2.4 s per step. Two fixes
brought it to about 0.5 s:

* Dropout on the attention weights alone took half the time.
* Cross-attention was run per sequence over a copy of its sample's
  memory. It now runs once per sample over all its targets' queries.

**Offline results** at the halfway cut of held-out solved goals (exact
variant recall of the future proof steps; n samples per cut; T is the
temperature):

| model, step | n, T | recall | generated, derived later in the run | hits not in the pool |
|---|---|---:|---:|---:|
| gen1, 1000 | 200, 1.0 | 1/2,891 | 0.1% | |
| gen1, 1000 | 200, 0.7 | 4/2,891 | 0.2% | |
| gen2, 3000 | 200, 0.7 | 13/2,891 | 0.7% | |
| gen2, 3000 | 400, 0.7 | 24/2,891 | 0.6% | 2 (of 1,251 missing) |
| gen4 (novel targets), 4000 | 400, 0.7 | 9/2,025* | 0.3% | 3 (of 1,040 missing)* |

\* gen4 is evaluated in its own training run, on a different 29 test
goals.

The generator learns the common lemmas, which the pool already holds:
22 of its 24 hits are pool hints. The steps that matter are the 1,251
the pool lacks, and it finds 2 of them.

So gen4 fine-tunes gen2 at step 3000 on novel targets only
(`--novel loops/UL/hints`): the cuts and targets are proof steps that no
other goal of the original has as a hint. After 1,000 steps it finds 3
of 1,040 novel steps, about the same as before.

**A copy action** (`hints/gencopy.py`). Novel steps are long (median 18
symbols). On each side, the largest subterm already in the context
covers typically 40–70% of the step. So COPY points at a term node of
the sample, then one VAR action per distinct variable of the copied term
maps it to the equation's variable slots. Copies make about 22% of the
target tokens.

* The encode-decode round trip is exact.
* Overfitting one problem recovers 3 of its 8 future steps.
* gc1 trains on novel targets from gen2's encoder. On the same 29 goals
  as gen4 it finds:
  * step 1000: 10 of 1,040 novel steps (gen4: 3), 37 of 2,025
    future steps (gen4: 9);
  * step 2000: 12 of 1,040 novel steps, 32 of 2,025 future steps;
  * step 2000 with n 1,600: 19 of 1,040 novel steps (1.8%), 51 of 2,025
    future steps. Four times the samples gives 1.6 times the hits;
  * step 3000: 12 novel; step 4000: 11 novel. A plateau, so training was
    stopped at 18:13 (models/gc1_4000.pt).

**Online test** (`abs/gen_test.sh`, sets/gen200, snapshot ULsW):

| arm | fresh 5 s | resume +15 s |
|---|---:|---:|
| GC, control | 0/200 | 4/200 |
| GG, gen2 at 3000 (n 400, T 0.7), re-queued | 0/200 | 2/200 |
| GC1A, copy model gc1 at 1000 (n 400, T 0.7), re-queued | 0/200 | 4/200 |
| GQ, re-queue alone (no generator) | 0/200 | 2/200 |

GC1A proved one goal the control did not, `Ka1_eq_Ka2__goal_403`, and
missed one the control proved. None of the 280 hints it generated for
that goal is among the proof's 234 lemmas. GQ (re-queue alone) proved
2 of the control's 4 and nothing else, so neither the re-queue nor the
generated hints gain; GC1A's +1 is search perturbation.

* GG proved 2 of the control's 4 and nothing else.
* Its hints do steer the search. On one goal, of 353 generated hints,
  243 became joinable and 117 were matched by new rules (boosted
  critical pairs get selected).
* None of that is on a proof path.

**Instance matching of hints (negative).** Of the future proof steps
missing from the pool, 637 of 1,866 looked like instances of a pool
hint. Most of those came from false hints in the pools:

* `X0=X1` (783 matches);
* `m(X0,X1)=m(X2,X3)`;
* `X0=m(X0,X1)`;
* `ld(X0,X1)=rd(X1,X0)`.

They are generalised conditional facts: skolems of hypotheses become
variables. Under variant matching they are inert, because no critical
pair is false. Under instance matching they flood the queue: one hint
matched 270,716 critical pairs in a 5 s run.

twee-e41 has `--eqhint-instances` (a term index over the hints' sides;
`--eqhint-instance-factor`, default 0.1). It leaves out hints whose two
sides have different variables. It is off by default, and without it
the output is identical to e22.

With clean hints only (equal variable sets, no flat or variable
sides), instances cover 142 of 2,480 missing steps (3%), and the run
is 1.6–5 times slower in wall time. Dropped.

## 2ai. Conjecture cuts (user's suggestion after IWIL 2026, 15 Nov)

*Notes: [notes/2026-11-15-conjecture-cuts.md](notes/2026-11-15-conjecture-cuts.md).*

The IWIL 2026 paper (Chvalovsky, Suda, Urban) proves generated
conjectures separately and uses them as cuts. On Mizar60 that gave
+582 of 11,881 hard or unsolved problems, with the first useful
conjecture at median rank 3.

**Implementation** (`loop.py --gen-cuts K`, 1128103). Before a
goal's resumed level:

1. The generator (gencopy.py, `--counts`) samples equations from the
   goal and the last 256 rules of its failed level.
2. The K most often sampled ones become cut candidates, leaving out
   variants of the goal.
3. The candidates are proved in one `twee --multi-goal` run of
   `--gen-cut-time` abstract s, on the goal's axioms and lemmas, with
   its hints and rule model.
4. Those proved after at least one considered critical pair become
   axioms of the resumed level.

`--gen-cut-sep` proves each cut in its own run instead. That run uses
the kNN lemmas of the cut's own statement (`LemmaIndex.select(eq=)`) and
the rule model's goal block of the cut (`write_goalfile(lits=)`).
`cutoracle.py` supplies oracle candidates instead: rules of the goal's
later production proof.

**Results** on sets/cut9 (9 gen200 goals that production proved later,
in 5–128 s), snapshot ULsW, fresh 5 s then resume +15 s:

| arm | cuts proved | goals proved |
|---|---:|---:|
| control GC, +15 s | – | 1/9 |
| control, +20 s | – | 1/9 |
| oracle, 40 rules spread across the proof, one shared 5 s run | 14–27 of 40 | 1/9 |
| oracle, the 40 rules nearest the goal, shared | 2–22 of 40 | 1/9 |
| oracle, the 20 nearest the goal, each alone with its own guidance (5 s each) | 3–15 of 20 | 1/9 (7.3 s against 21.5 s) |
| generator gc1_4000, top 40, shared (3 gen200 goals) | 0 of 120 | 0/3 |
| generator, top 10 at T 0.7, each alone | 8 of 90 | 1/9 |

* **A shared cut run is uninformative.** Twee's completion barely
  depends on the goal: only the rule model's goal features and the
  lemma and hint selection do. A cut proved in a fresh 5 s run on the
  goal's own problem is essentially in the state of the goal's own
  failed 5 s level. In the IWIL setting, E and Vampire are
  goal-directed, so a separate proof of a cut searches elsewhere.
* **Separate runs with the cut's own guidance do differ.** Of the 20
  proof rules nearest the goal, they prove 69 against 35 for the
  shared run (34 only there). But they cost 20 runs instead of one.
* **Even oracle cuts gain nothing at this budget.** Up to 15 true proof
  lemmas as axioms made no new proof in +15 s; one goal went 3× faster.
  The proofs are 110–700 rules long, and the cuts that can be proved
  are the easy part.
* **The generator's cuts** are mostly small identities (for example
  `t(k(X0,X1),k(X0,X1)) = k(X0,X1)`).
* **AIM60k already has the strong form of cuts.** Its goals are
  Prover9's intermediate goals, and the sibling-lemma chain imports
  them as axioms once proved (section 3, item 1). That is the oracle
  conjecture-cut mechanism, and it is the loop's largest gain.

Not pursued further. Cut generation in the middle of a run (the user's
question) has the same limit: a cut proved by the run's own saturation
is already in its state. Only a cut proved by a differently guided
search adds information.

## 2aj. Sketches in stronger theories, climbing up and down (user's suggestions, 15 Nov evening)

*Notes: [notes/2026-11-15-sketches-stronger.md](notes/2026-11-15-sketches-stronger.md).*

The user's points:

* Assume stronger theories instead of laws. They are mathematically
  relevant (Bol loops for loops) and should not trivialise the sketch.
* Dream up new axioms with the generator.
* When a sketch is still too hard, make the theory stronger or the goal
  weaker. Climb both up and down, and learn from the climbs.
* This follows the over- and under-approximation of Hernandez and
  Korovin, IJCAR 2018.

**What `climb.py` now does** (04617bc–493f9cd):

* `--min-sketch-steps N`: a law, theory or generated equation whose
  sketch proof has fewer than N steps is banned for the target.
* `--theories K`: the extra axioms of up to K stronger theories, one
  theory at a time.
  * A stronger theory is the axiom set of another original that
    strictly contains the target's. 74 of the 129 originals have one;
    the 17-axiom base theory has 115.
  * Theories are ranked by the similarity of their solved goals to the
    target.
  * `--theory-lemmas 10` adds the stronger theory's proven goals most
    similar to the target (`LemmaIndex.select_in`). They are true in B,
    not in A.
* `--gen-assume K`: the generator's most sampled equations, one at a
  time.
* `--updown` (`climb2`): when no sketch proves the target, go up.
  * Up: unions of the theories, and weaker goals, which are instances
    of the conjecture (two variables merged first, then a variable set
    to e). They go in through `loop.py`'s new `goal_override` hook.
  * Down, from every proof: drop a used assumption, or restore the goal.
  * Every proof's steps become hints of the original.
* `--chain`: a proof in the climb is a sibling lemma and hints for the
  original's later targets at once.

**sets/gen48** (the first 48 of gen200: unsolved, each with one failed
fresh 5 s run; snapshot ULsW, 1 worker each):

| arm | proved | CPU s |
|---|---:|---:|
| fresh 20 s (control) | 1 | 1,589 |
| fresh 20 s `--backwards-goal 1` | 1 (the same, 35.68 against 35.69 s) | 1,545 |
| fresh 20 s `--hint-goal` | **2** | 1,822 |
| CL6A: siblings + kNN goals + gap filling (CL5's config) | 2 | 4,903 |
| CL6L: laws only, trivialising laws banned | 2 | 4,168 |
| CL6T: 6 stronger theories + their lemmas | 2 | 4,546 |
| CL6U: CL6T + up/down | 2 | 4,051 |
| CL6G: 6 generated equations | 2 | 4,483 |

* Every 2 is aK2_eq_aK3_d__goal_462 (the control's) plus
  Ka1_eq_Ka2__goal_403.
* `--hint-goal` alone proves 403 too, so 403 falls to any change in the
  search. On gen48 the sketches gain nothing beyond perturbation.
* **Sketches are trivial on these goals** whatever the assumption:
  * a nearby unproven sibling or kNN goal proves the target in 0.3–2 s;
  * so does a stronger theory's proven goal (one lemma, 1.7 s);
  * so does a generated equation (0.3–2.8 s; the generator writes
    near-restatements of the goal);
  * so does a weaker goal (an instance, 0.5–1.4 s).

  The assumptions that help are as hard as the target, so the sketch
  covers only the easy last steps.
* gen48 spreads its goals over many originals, so sketch hints and true
  lemmas, which are shared within an original, barely accumulate.

**Family test** (`abs/fam.sh`): sets/fam24 holds the first 12 unsolved
goals, in proof order, of aK2_eq_aK3_1243b (66 stronger theories) and of
nsmr_to_aa1 (3). Snapshot loops/ULsX is UL at 20:15. Goals run in
order with `--chain`, 1 worker.

* **The full up-down climb (FUD) proved 3/24 in 2,652 s:** 1243b
  goals 441, 445 and 448, none of nsmr_to_aa1.
  * 441: the final run used 17 true lemmas proved by gap filling (a
    chain of real proofs); without them it fails.
  * 445 and 448: the runs with the hints alone also prove them, in
    14.2 s and 2.7 s.
* **Final numbers:**

  | set | arm | proved | CPU s | proofs per CPU-hour |
  |---|---|---|---:|---:|
  | fam24 | full climb (FUD) | 3 (1243b 441, 445, 448) | 2,652 | 4.1 |
  | fam24 | control: the same climb without assumptions, one fresh 80 s run per goal (F80) | 3 (1243b 446, nsmr 614, 616) | 6,032 | 1.8 |
  | fam24 | climb without stronger theories (FUDnt) | 1 (448) | 1,738 | 2.1 |
  | next 24 unsolved 1243b goals | full climb (FUD2) | 1 (455) | 2,904 | 1.2 |
  | next 24 unsolved 1243b goals | control (F80b) | 1 (455) | 4,981 | 0.7 |
  | fam24 | full climb + one-axiom up steps (FUDs, `--up-single`, 24 runs per goal) | 3 (the same as FUD) | 3,402 | 3.2 |

* The climb and long fresh runs prove different goals: 6 distinct
  between them on fam24.
* The stronger theories are what the climb adds on the base-theory
  family: 3 against 1 without them.
* Per CPU the climb is at least as productive as long fresh runs on
  goals production has stalled on.

* Adding one axiom at a time when going up (FUDs, the user's
  suggestion) proved the same goals as FUD at 28% more CPU.
* `--hint-goal` on the other 152 goals of gen200 (fresh 20 s from
  ULsW): the same 3 proofs as the control, at 13% more CPU. Dropped.
* The 12 proofs of today's probes that production lacked were merged
  into UL at 22:50 (`merge.py`; among them the heads
  aK2_eq_aK3_q__goal_270, mbol_12lemmas__goal_528 and
  mbol_nil3_a__goal_500 from the 160 s probe HLF).

**Deployed as a live side worker (22:07, `abs/clu.sh`, loops/CLU).**

* It runs the FUD config with `--up-single` (one more axiom when going
  up).
* It takes production's stalled goals and fills idle CPUs (`--cpus 20`,
  at most 6 climbs).
* Its proofs go into loops/UL.
* It saves every sketch's proof steps (loops/CLU/sketches). These are
  the data for learning the lattice moves, which the user asked for
  (15 Nov): which step, up or down, to take for a given problem, as a
  randomized policy.
* In its first 50 minutes, 73 climbs gave 2 proofs:
  aK2_eq_aK3_1243b__goal_445 and aK2_eq_aK3_gen__goal_495, the first
  unsolved goal of its original.
* `latticedata.py` turns climb directories into one row per move. The
  features describe the target (goal size, variables, axioms, number of
  stronger theories) and the move (assumptions by kind, theories and
  their rank, weakened goal, step). The labels are proved, nontrivial
  (an assumption used, at least 30 proof steps) and credit (the share of
  the target's real proof found in the sketch's proof).
* In its first 1.6 hours (to 23:43), 202 climbs gave 3 proofs:
  1243b_445, gen_495 and 1243_342. (An earlier version of this line said
  6. Three names were misread from a directory listing; their climbs
  failed.)
* By 01:30 the climber had 9 proofs, all in production: Kproperties_1
  314, aK2_eq_aK3_1243 342, 1243b 445, gen 495, aK2_eq_aK3_r 266,
  aa1_45_c 323, nil3_18 290, nsmr_to_aa1 612 and 732. Production then
  proved 9 later goals of the same originals: 1243b 446, 447, 448, 455;
  r 268, 269; nsmr 735, 737.

## 2ak. Learning the lattice moves (user, 15 Nov: "what are the best steps in the lattice given a problem")

*Notes: [notes/2026-11-16-lattice-moves.md](notes/2026-11-16-lattice-moves.md).*

The climb walks a lattice of (assumptions, goal) nodes. Going up adds
assumptions: a stronger theory's axioms and lemmas, siblings, kNN goals
of other originals, one more axiom, or a weaker goal (an instance of the
conjecture). Going down drops assumptions from the sketch's used set.
Until now the order of the queued moves was fixed by hand: the real goal
before weaker ones, fewer assumptions first.

**What the logged moves say** (climb.tsv of the FUDs arm and the live
climber, 1,346 moves on 100 targets):

| move (assumption kinds) | moves | proved | nontrivial |
|---|---:|---:|---:|
| theory + siblings + kNN | 552 | 43% | 9% |
| siblings + kNN, weaker goal | 203 | 100% | 11% |
| theory + siblings + kNN, weaker goal | 139 | 100% | 11% |
| siblings + kNN | 116 | 30% | 16% |
| theory + kNN | 71 | 52% | 41% |
| kNN | 61 | 51% | 25% |
| kNN, weaker goal | 53 | 100% | 40% |
| siblings only | 45 | 4% | 0% |
| theory only | 43 | 28% | 28% |

* Nontrivial = proved, used an assumption, at least 30 steps.
* Weaker goals always prove. Siblings alone almost never help.
* A stronger theory with kNN goals but without the siblings gives the
  most nontrivial sketches.

**The pieces (commits 57a0b00 to 25d0e6c):**

* `latticedata.py` gives one row per move. Its features are shared
  with climb.py (`move_features`).
* Labels:
  * nontrivial;
  * credit, the share of the target's real proof found in the sketch
    (only when the target is proved);
  * realized, the share of the sketch's non-axiom steps that the real
    final run derived as given rules, proved or not. Realization is the
    dense one: Korovin's concretisation measured on the search.
    climb.py saves the final run's given rules (`realized/<t>`) for it.
* `latticepolicy.py train` fits a logistic model with a split by
  target. On nontrivial: held-out AUC 0.654. The largest weights are
  siblings (negative), the number of stronger theories (positive) and
  theory lemmas (negative).
* `climb.py --move-model M` samples the next move by softmax over the
  scores (`--move-temp`, default 1), with `--move-eps` (0.1) uniformly
  random moves.

**First test** (abs/fam4.sh, FUD2's config on the next 24 unsolved
1243b goals, policy lattice1): 1 of 24 (goal 455) in 2,410 CPU s,
against the fixed order's 1 of 24 (the same goal) in 2,498 CPU s. A
draw: one proof per arm can't tell them apart. 4 of the 24 targets were
in the policy's training rows; the live climber had visited them.

**A/B in the live climber (23:50, abs/clu2.sh).**

* `--move-ab`: targets with an odd crc32 of the name sample by the
  policy, the others take the fixed order.
* The comparison is proofs per CPU over many stalled production goals.
* The policy is retrained as labels accumulate.

**Which label (16 Nov 01:00, 478 targets, 5,714 moves of the live
climber):**

* Realization overrates weaker goals. Their steps are theorems of the
  real theory, so the final run re-derives them (mean realization
  0.5–0.76) whether or not they help.
* On the 7 targets the climber proved, weaker-goal steps had little
  credit (0.03–0.09). A theory with kNN goals and no siblings had the
  most (0.20). Siblings in a step lowered credit (theory + siblings +
  kNN: 0.06).
* Where both labels exist (proved targets) they agree: correlation 0.96
  over 18 sketches.
* A model on realization puts weaker goals first (weight +1.0). The
  model on nontrivial has held-out AUC 0.757 (0.654 at 100 targets), and
  siblings are its largest negative weight. It is `models/lattice2n.json`,
  in the live A/B since 01:19.

**Which stronger theory (`latticedata.py --theories-out`, 363 offered
theories on 157 targets):**

| offered theories | moves | proved using an assumption | nontrivial |
|---|---:|---:|---:|
| the heuristic's (similarity of solved goals in the theory) | 625 | 50% | 20% |
| random others (`--theory-explore 2`) | 152 | 73% | 36% |

* The similarity rank misleads. Its most offered theories (ns_to_aa1_c,
  ns_to_aa1_b, aK2_eq_aK3_o, on 33–51 targets) give nontrivial sketches
  2–6% of the time.
* aa1_45_a, aK2_eq_aK3_1243, osb_Kcom_to_aa1 and aK2_eq_aK3_i give
  31–54%.
* **Thompson sampling (`--theory-ts`).** Each theory has a Beta posterior
  of its nontrivial-sketch rate (prior Beta(0.4, 1.6)), filled from the
  logs at start (57 theories, 793 sketches) and online after every
  single-theory sketch. The climb ranks theories by a draw from it, so
  good theories come first and untried ones still get tried.
* Live since 01:15 (abs/clu4.sh) as a second A/B: `--theory-ts-ab` uses
  bit 1 of the crc32, crossed with the move policy on bit 0.
**The A/B after 205 climbs (01:19–02:16):** 3 proofs, no difference on
either bit (move policy 1 vs 2, p = 0.60; theory sampling 1 vs 2,
p = 1.0). At a 1.5% proof rate, a 2× gain needs more than a thousand
climbs per arm to show.

**Heads first (02:22, `--reclimb-heads 4`, abs/clu5.sh).** The climber
had climbed each target exactly once (696 targets over 96 originals).
Now every other free slot goes to an original's first unsolved goal
(111 heads; 27 never climbed), interleaved with new targets.

* In the next 150 climbs: 8 proofs (5%, against 1.5% before; but see
  the correction below):
  * aip_to_aK1 185;
  * mbol_to_aK1 550, 552, 554 (a chain: each proof makes the next goal
    the head);
  * mbol_lem2 512;
  * mbol_nil3_a 494, 342;
  * nil3_1K_f 325.
* Re-climbing a head whose context hadn't changed gave 2 proofs in 87
  climbs (0.45 per CPU hour, new targets 2.1). Since 03:05 a head is
  re-climbed only after its original has gained a proof since its last
  climb.
* The theory-sampling bit split 0 vs 8 proofs (p = 0.007), but that is
  chance:
  * targets without stronger theories, where the theory ranking can't
    matter, split 0/21 vs 3/25;
  * three of the 8 are the mbol_to_aK1 chain, which all fell on one
    side.
  The proofs cluster by original, so the tests should count originals,
  not targets.
* Production since 01:30: 73 new proofs. 12 are the climber's, and 21
  more are in originals where the climber proved a goal (ns_to_aa1_b 12,
  mbol_to_aK1 7, aK2_eq_aK3_r 4). The climber's 6 CPUs connect to
  almost half of production's progress.

* **After 03:10:** 2 proofs in 213 climbs (aK2_eq_aK3_r 275,
  Kproperties_1 310), with the A/B arms by original and no difference.
* **Correction (04:30): the burst was not the heads' doing.** The state
  just before each of the climber's 19 proofs since 22:07 shows:
  * 3 were the first unsolved goal of their original (aip_to_aK1 185,
    mbol_nil3_a 342, nil3_1K_f 325);
  * 1 was a tail head, the first unsolved goal after the last proof
    (aK2_eq_aK3_r 275);
  * the other 15 sit inside holes, with proved goals on both sides.
  In the 02:22–03:10 burst, 3 of the 8 proofs were heads. Heads had half
  the slots, so they did no better than the ordinary targets.
* **First unsolved is not the tail head.** In 109 of the 111 originals
  with unsolved goals, later goals are proved past the first unsolved
  one, so `--reclimb-heads` targets holes. 4,710 of the 7,543 unsolved
  goals are at or behind the tail heads, and 2,833 are in holes.
* The yield varies by window: 3 of 202, then 3 of 205, 8 of 150, 2 of
  213. It follows the supply of targets whose context changed (chains
  such as mbol_to_aK1 550, 552, 554, and production's new proofs), not
  the ordering.

* A bug in the first exploration code (a sample larger than the rest of
  the theories) stopped the live climber from 00:02 to 00:19. A failed
  climb is now logged as ERROR and the climber goes on.

## 2al. Goals that are steps of existing proofs (16 Nov, 04:20)

*Notes: [notes/2026-11-22-src-used.md](notes/2026-11-22-src-used.md).*

*Notes: [notes/2026-11-22-lemma-ax-replay.md](notes/2026-11-22-lemma-ax-replay.md).*

*Notes: [notes/2026-11-22-gm-retry.md](notes/2026-11-22-gm-retry.md).*

*Notes: [notes/2026-11-20-base-saturation.md](notes/2026-11-20-base-saturation.md).*

*Notes: [notes/2026-11-20-given-transfer.md](notes/2026-11-20-given-transfer.md).*

*Notes: [notes/2026-11-16-step-transfer.md](notes/2026-11-16-step-transfer.md).*

**The observation.** 2,905 of the 7,543 unsolved goals are, up to
variable names, a step of a proof found earlier. 101 of those proofs
come from goals with the same or weaker axioms, so the goal is a theorem
with its proof written down. The other 2,804 come from other theories:
2,222 with one axiom more than the goal's, 450 with two.

Production's hint pool (`--pool original`) offers only the goal's own
original's proofs, and the kNN lemmas are proven goals, not proof steps.
So these proofs never reached the goals. Only 12 of the 101 had the
proof in their own original.

**`transfer.py`:**

* `find LOOPDIR --out GOALS.tsv [--any-theory]` lists the unsolved unit
  goals whose canonical equation is a step of some hints file. With
  `--any-theory` the source may have more axioms. Its step is then
  maybe true only there, but false hints are inert (they only match
  critical pairs, which are theorems).
* `run GOALS.tsv DIR -- LOOP-OPTIONS` makes one fresh run per goal. The
  source proofs' steps come first (up to 3 sources: own original first,
  then the fewest extra axioms, then the shortest), then the usual pool
  and lemmas. Proofs go to DIR for `merge.py`.

**Same or weaker axioms** (abs/xfr.sh, sets/transfer1.tsv, snapshot
ULsY at 04:15, fresh 20 abstract s, 3 workers):

* **32 of 101 proved** in 2,675 run seconds, **about 43 proofs per CPU
  hour**: more than 20 times production's average and about 70 times
  the climber's.
* Proved runs took 4 s on average. 30 merged into UL at 04:40; the
  other 2 had been proved by production meanwhile.

* Split by where the source proof was: sources only in other
  originals 29 of 89; a source in the goal's own original 3 of 12. The
  own original's proofs were already in the goal's pool.

**From other theories** (abs/xfr2.sh, sets/transfer2b.tsv, the 2,804
others, fewest extra axioms first, from 04:42): 1 of 28 (about 4 per CPU
hour). A step of a stronger theory's proof is mostly not derivable in
the weaker one. Paused at 04:46 for the instances below. The live
climber was stopped at 04:42 (about 0.5 proofs per CPU hour).

**Instances of steps** (`find --instances`: the goal is σ(step) for a
step of a proof from the same or weaker axioms; one-way matching over
all hints files, 3.5 minutes): 3,108 unsolved goals, 3,007 beyond the
exact ones.

* Proofs of goals with hypotheses can have hypothesis-dependent steps,
  which are false once generalized. Such candidates just fail.
* Sources in the goal's own original first (sets/transfer3b.tsv): 1 of
  61. Those proofs were already in the pool, so the order was wrong.
* Sources in other originals only (sets/transfer3c.tsv, 2,581 goals):
  3 of the first 45, about 7.7 proofs per CPU hour. Running from 05:13
  on 6 workers.
* For that, production went from 14 to 10 workers at 05:12
  (abs/ul32.sh, `--cascade-continue`). Its marginal runs make about 0.8
  proofs per CPU hour.
* **Most instance candidates were junk.** Every one of the 2,581 had a
  conditional goal among its sources. Proofs of conditional goals have
  steps that use the hypotheses, and these are false once generalized.
  With sources restricted to proofs of unit goals (`find --instances`
  since 05:30), there are 132 candidates, and only 28 are new with
  sources in other originals. The noisy batch still yields about 3 per
  CPU hour (6 of 216 with source lemmas), more than production's
  marginal runs, so it goes on, on 4 workers.

**Source lemmas (`run --src-lemmas K`, 05:05).** A source proof was
found with its own original's proven goals as lemma axioms, and the
target run lacked them. Now the source goal and its K−1 nearest proven
goals below are lemma axioms of the target run. These are proven goals
of the same or weaker axioms, the kind `--lemma-knn --lemma-subsets`
already adds, so the trust level stays the same.

* On the 69 goals of transfer1 that failed: **63 proved**, in 338 run
  seconds.
* 30 of the 63 proofs are one step. 12 goals are identical to a source
  goal. So many unsolved goals were, up to renaming or instantiation,
  proven goals of other originals with the same or weaker axioms. The
  kNN lemmas (10 by goal features) did not bring them; exact step
  matching does.
* `find --goals` lists unsolved goals that are instances of proven
  goals of other originals with the same or weaker axioms. After the
  merges only 5 were left; 3 of them proved, together with 3 of the 28
  clean instance candidates (sets/transfer6.tsv).

**Why the kNN lemmas missed them: a filter in `LemmaIndex._select`.**
Since the first kNN lemma code (13 Nov, d6b6bf9) the selection started
with `seen = {target's formula}`, so it dropped every proven goal stating
exactly the target, from any original. Such a goal of the same or a
weaker theory proves the target. 46 of the 63 source-lemma proofs above
were of this kind (identical lemma formula strings). Fixed on 16 Nov
06:00: the identical proven goal now comes first. Production reads it
at its next restart; until then the live worker's `find --goals`
catches these cases.

**Live (05:37, `transfer.py live`, abs/xfrlive.sh, 2 workers, every 20
minutes).** With production's current proofs as context (symlinked
hints, its solved.tsv with rounds zeroed), it finds the new step and
goal-instance candidates, runs the untried ones with source lemmas, and
puts the proofs into UL. Its first cycle had 10 step candidates, 6 of
them new. **By 10:28 it had proved 21 of 25 new candidates.** These are
mostly goals that production's fresh proofs make into steps, and each
takes seconds.

**Totals of the transfer so far:** 32 + 63 + 6 + 7 proved, of which
101 were merged into UL. UL went from 44,240 (04:12) to 44,398 (05:35).

* **A decision for the user.** A step of a proof from the same or weaker
  axioms (and without hypotheses) is a proven theorem, exactly like the
  proven sibling goals the loop already adds as lemmas. As a lemma axiom
  it would prove its instances at once, so most of the 3,108 would
  count as solved modulo lemmas. The runs here instead give the steps as
  hints, so twee re-derives them and each proof stays at the current
  trust level.

**Beside it, long climbs on the heads** (abs/clh.sh, the 111 first
unsolved goals, the live climber's config with a 160 s final run, 4
workers): 2 of the first 8 heads proved (KK_Kcom_to_aK1 255, Ka1_eq_Ka2
361) in 4,128 CPU s, about 1.7 per CPU hour.

**Rules other runs derived and did not use (exp38, 20 Nov 02:20-; [notes/2026-11-20-given-transfer.md](notes/2026-11-20-given-transfer.md)).**
Matching against proof steps covers only about 22 M of the given logs' 400 M rules.
* **The rest.** Every successful run's given log also holds the 379 M rules it derived and did not use. In a run on an
  unconditional unit goal they follow from that original's axioms and proven lemmas. So an unsolved goal (of the
  same or more axioms) that is a variant of one of them is a theorem, with that run's log as its sketch.
* **The full scan** (givenmatch.py, 494,373 logs) found 19 such goals. 13 were proved, at about 28 per CPU h:
  * the rule's ancestry as hints at 20 s proved 8;
  * with the source run's axioms at 40 s, 3 more;
  * the log's whole prefix as hints, 2 more.
  The log's parents are rule numbers (position + 1). They were read as positions at first, which mangled the
  ancestries, and were fixed at 04:08.
* **Negatives:**
  * a sibling run's whole rule set as lemma axioms: 0 of 40;
  * instances, the rule more general than the goal: 2 hits, nothing new;
  * a replay close to the source run: 0 of the 8 that resist.
* **The frontier's logs are where the hits are:** 5 in the 696 logs written after the index, against 19 in 494,373.
  So `givenmatch.py live` (loops/GML, every 5 minutes) scans each new log.
* **Failed runs.** Given logs exist only for proofs. loop.py `--given-scan` (ul74, 04:15) checks every failed run's
  given rules against the unsolved goals. That costs twee about 6% more time, for printing them. The live loop runs
  the hits. In the first 15 minutes there were 5 goals, some across originals, and all 5 were proved in 34 s.
* **The same statement in a theory with more axioms** (2ar), redone on today's proofs (exp/sofree.py): 9 of 46 in
  0.34 CPU h, against 4-5 per CPU h on 16 Nov. It now runs in every live cycle.
* **The hit stream thins fast.** New goals from production's failed runs per hour: 19 (04:15-05:00), 17, then 1
  (06:00-07:00). The first hour harvested hits that had accumulated.
* **The failed runs' lemmas were missing (exp56, 22 Nov; [notes/2026-11-22-gm-retry.md](notes/2026-11-22-gm-retry.md)).**
  * The live loop ran a hit goal once and then never again. 30 goals it had tried stayed unsolved, although later
    failed runs kept deriving them: ns_to_aa1_b 673 had 229 hit rows from 32 source runs.
  * Rerun on their newest hits (exp/gmretry.py): the 20 s ancestry pass proved 0 of 30, the 40 s prefix pass 5.
  * The cause is in loop.py's given scan, which marks only the original's axioms as axioms. A failed run's lemma
    axioms (its sibling and kNN lemmas, all proven goals) therefore reached the target run only as hints.
  * Fix: givenmatch.lemma_ax names each such rule after the proven goal it states, if that goal's axioms are within
    the target's, and passes it as a lemma axiom that trust.py resolves. All 105 checked in one problem match their
    goal's statement.
  * With it, the 20 s pass proved 7 of the first 12 left goals, several in 3-4 s.
  * Production's live loop has run with `--lemma-ax` and `--retry-tried 3` (newer hits, newest first, at most every
    3 hours) since 12:06.
  * From zero (exp58a, [notes/2026-11-22-lemma-ax-replay.md](notes/2026-11-22-lemma-ax-replay.md)): replayed on the 59
    goals Z8's live loop failed in its ancestry pass, each in Z8's context at the time of its run, the fix proved 46
    (27 of the 36 Z8 never solved), and the unchanged sketches 0 of 15. solve_new.sh's live loop has it
    by default since 22 Nov 13:26.
  * The same gap in same-statement runs (exp58b, [notes/2026-11-22-src-used.md](notes/2026-11-22-src-used.md)): a
    proof's hint file lacks the lemma axioms it used. transfer.py `--src-used` adds them, named by goal. On 100 of
    Z8's failed same-statement runs it proved 6 (controls 0 of 20). Most of the source proofs' lemmas are of the
    stronger theory and do not fit the target (a median of 1 added). Not adopted.

**Base-theory runs as generators (exp39, 20 Nov 05:39-07:24;
[notes/2026-11-20-base-saturation.md](notes/2026-11-20-base-saturation.md)).**
* 13 originals share the 17 base axioms, which are within almost every theory. So their rules hold for 3,001 of
  3,133 unsolved unit goals, and 19 of the first 27 failed-run hits came from their runs.
* Dedicated base runs (exp/gensat.py; scan as `--given-scan`, hits into the live loop):

| setting | runs | CPU h | new goals hit | proved |
|---|---:|---:|---:|---:|
| 30 s, 6 siblings + 30 random base lemmas, the pool | 120 | 2.62 | 9 | 6 + 1 direct |
| 8 s, 6 siblings + 100 kNN lemmas | 300 | 1.17 | 3 | 0 |
| 8 s, steered: a stronger theory's goal on the base axioms, 100 base lemmas nearest to it | 300 | 1.17 | 8 | 1 |

* About 1.8 proofs per CPU h in all: 3 times production's own runs now (0.56), but not a standing member.
* **The hypotheses dropped** (exp39b): 60 unsolved goals of the stronger theories without their extra axioms,
  with the same lemmas and hints, against the full problem: 0 and 0 of 60 at 20 s.

## 2am. How many kNN lemmas (16 Nov, 06:50)

*Notes: [notes/2026-11-16-knn-lemma-count.md](notes/2026-11-16-knn-lemma-count.md).*

**Use by rank.** Production's outputs (`--keep-out`, r*/out) list each
proof's used axioms (USEDAXIOMS), and the kNN lemma names carry their
rank (`lemma_knn_<rank>_<source goal>`).

* 2,625 of 2,755 proved runs use a kNN lemma, and 2,016 use a sibling
  lemma.
* Use barely falls with rank: rank 0 in 1,686 proofs, rank 1 in 1,320,
  rank 5 in 1,127, rank 9 still in 1,053. So 10 looked too few.
  (2r had found no gain from 20 on one original, on 14 Nov.)

**Paired test** (abs/knn_test.sh, sets/unsol150 = 150 random unsolved
goals of ULsZ, fresh 20 abstract s from ULsZ, 2 workers per arm):

| kNN lemmas | proved | wall s |
|---|---:|---:|
| 10 (production) | 3 | 4,981 |
| 20 | 3 (the same) | 4,953 |
| **30** | **6** (+3/−0) | 4,919 |
| 60 | 9 (+4/−1 against 30) | 5,466 |
| 100 | 5 (+1/−2 against 30) | 5,685 |

* 60 and 100 were run later (07:46–08:34) on the same goals and
  context. 60 proves the most, 9, at 11% more wall time; 100 proves
  fewer and is slower. The numbers are small: 30 against 60 is +4/−1,
  so not significant on its own. The peak lies somewhere around 30–60.
* The 3 extra proofs use lemmas of rank 11–27 (a_instances 361: ranks
  26 and 27; aK2rev 323: 11, 14, 20, 23; nil3_32 343: 25). So the gain
  comes from the extra lemmas, at no cost in time.
* **Production since 07:20** (abs/ul33.sh) uses `--lemma-knn 30` and
  the lemmas.py fix (2al), on 12 workers. Every goal's kNN set changes,
  so `--retry-knn` makes them all eligible for a fresh retry.
* **Its rate:** 32 new in the first 26 minutes, about 74 an hour (6.2
  per worker). Before, at 10 workers with 10 lemmas, it was 59 in 2
  hours, about 29 an hour (2.9 per worker). Part of this is the
  restart: fresh runs in new contexts come first.
* **Over 3 hours (07:20–10:27):** 152 new, about 49 an hour or 4.1
  per worker hour. 88 of them came from 4,325 fresh retries (2%). The
  rest came from deeper cascade levels.

**Choosing the lemmas better (08:00).** kNN lemma use is spread widely.
12,205 uses in 2,755 proofs fall on 3,369 distinct proven goals. The 200
most used cover 44% of uses, and a proof uses 4.4 of its 10 on average.
Two ways to choose the 30 differently, both in `lemmas.LemmaIndex`:

* **Use counts** (`loop.py --lemma-pop B`): similarity × (1 + B log(1 +
  the number of proofs whose USEDAXIOMS name the lemma);
  `lemmas.lemma_uses` greps the kept outputs in a second). B = 0.3
  changes a quarter of the top 30.
* **MaSh-style dependencies** (`--lemma-deps W`). This is the k-NN
  premise selection of Sledgehammer's MaSh, with *proof dependencies*
  taken from the stored proofs. A proven goal depends on another proven
  goal (same or weaker axioms) when the other's equation (canonical, as
  in transfer.py) is a step of its proof. `lemmas.proof_deps` finds
  these in 20 s over all 44k stored proofs. 36k proofs have some, about
  60 on average; the most common are near-axioms shared by half the
  proofs, which the idf weight removes.
  * A lemma's score is the similarity of each of the 50 nearest proven
    goals it is, plus W × similarity × idf / √(#deps) for each whose
    proof has it as a step.
  * W = 1 changes 23% of the top 30.
* **Offline**, on 288 round 4–5 proofs, with the target's own proof
  left out: recall at 30 of the step lemmas from other originals is
  0.183 with plain similarity and 0.189 with W = 1. Those proofs were
  found with plain-similarity lemmas, so the offline measure favours
  plain similarity. The paired runs below decide.

Paired runs (30 lemmas, as KN30, same 150 goals):

| selection | proved | against plain 30 | wall s |
|---|---:|---|---:|
| plain similarity (KN30) | 6 | – | 4,919 |
| use counts, B = 0.3 (KP03) | 7 | +3/−2 | 5,042 |
| MaSh-style dependencies, W = 1 (KD10) | 5 | +1/−2 | 4,927 |

Neither selection beats plain similarity. Across all the arms, 10
distinct goals were proved, so the arms differ by one or two goals each,
which is noise. I stopped the stronger weights (B = 1, W = 3) after a
few minutes: they could not settle anything on 150 goals. Instead,
30 against 60 is replicated on 300 other unsolved goals (sets/unsol300b,
RN30/RN60, from 09:20).

**The rerun does not bear out 60** (10:46): 30 lemmas prove 10 of 300,
60 lemmas 8 of 300 (+1/−3), at 3% more wall time. Taken together with
the first test (+4/−1 there), 30 and 60 are even at 19 and 17 of 450
goals, so production stays at 30.
Selection tests on 150–300 goals at 20 s resolve only differences of
several proofs. Production changes only on effects that large.

## 2an. Where the proofs come from now, and what a head is worth (16 Nov, 11:00)

**Production's round 5 by cascade level** (UL/r5/results.tsv, 32,768
runs):

| level | runs | proved | wall h | proofs per wall h |
|---|---:|---:|---:|---:|
| 5 s (first or fresh) | 25,205 | 2,191 | 133.3 | 16.4 |
| 80 s | 6,962 | 1,064 | 282.4 | 3.8 |
| 320 s | 603 | 119 | 116.0 | 1.0 |

Over 07:20–10:27 production made 4.1 proofs per worker hour. The 320 s
level alone gives about as much as the climbers did (1.2 per CPU hour
for the batch of long climbs on heads), so a level above 320 s would
give less.

**By 17:15 the 320 s level was the CPU sink.** Production's last 450
runs:

| level | proofs | CPU h | proofs per CPU h |
|---|---:|---:|---:|
| 320 s | 6 | 20.2 | 0.3 |
| 80 s | 11 | 3.7 | 3 |
| 5 s | 3 | 0.8 | 4 |

So production went down to 8 workers (abs/ul36.sh, 17:20). The freed
CPUs go to side batches that make 2–5 an hour: the cross-theory
candidates (2ar, SOR) and the instance batch (XFR3L). Both lists are
finite. When they are done, production gets the CPUs back.

**Is a head worth more than its own proof?** The 111 stuck heads of
03:10 (sets/heads_stuck): 69 of them are proved now, 17 by the long
climbs and the rest by production and the transfer. Goals proved per
original-hour:

| originals | goals per hour |
|---|---:|
| 69 with the head proved, after its proof | 0.53 |
| the same 69, in equal windows before their head's proof | 0.43 |
| 42 whose head is still unproved, since 05:13 | 0.24 |

A proved head raises its original's later rate by about 0.1 goals an
hour, so over the 5 hours measured it brings about half a further goal.
Most of the difference to the unproved ones is selection: the active
originals get their heads proved. So a head is worth little beyond its
own proof.

* The live head climber (abs/clhl.sh, 30 kNN lemmas, 160 s final
  runs) made 4 proofs from 60 heads in 8.5 CPU h, which is 0.47 per CPU
  hour. **Stopped at 11:05.** Its 4 CPUs went to production, which now
  runs 16 workers (abs/ul34.sh).
* **Proof steps as lemma axioms (the open decision in 2al) is now worth
  little.** Only 39 unsolved goals are instances of a step of a proof
  of a unit goal from the same or weaker axioms. 34 of them failed with
  the steps as hints and the source goals as lemmas. So the
  decision would bring at most about 39 proofs now. Beyond that it is
  a larger lemma pool, and more than 30 kNN lemmas did not help (2am).

## 2ao. The rule model ordering the queue (16 Nov, 11:20): too slow, and the oracle says no

*Notes: [notes/2026-11-16-queue-model-lemma-proof-hints.md](notes/2026-11-16-queue-model-lemma-proof-hints.md).*

2ad left a stronger hook for a learned model open: ordering twee's queue
instead of deferring a rule once. **twee-e42 `--cp-model-factor F`**
does this. It multiplies each new critical pair's score by F ** q,
where q is rm4t's probability that the pair is a proof rule, with the
parents' features as in the deferral. F = 1 is off and identical to e41.

**Smoke test** (abs/cpm_test.sh, sets/kn30thm: the 6 goals KN30 proved,
same context):

| arm | proved | wall s, the 4 proved by both |
|---|---:|---:|
| F = 1 | 6 | 25.6 (work identical to e39) |
| F = 0.1 | 4 (2 hit the 200 s CPU limit) | 264.9 |

* **Scoring every new pair costs about 10× the wall time.** Twee makes
  millions of pairs and normalises each, and the model adds three
  featurisations and 200 trees per pair.
* **Work in abstract time is mixed:**
  * nil3_32 343: 2,597 considered against 4,623;
  * a_instances 361: 8,012 against 6,879;
  * aK2_eq_aK3_o 439: unproved in the 40,000 it was allowed.
* Earlier, the oracle model with deferral up to 3 times at penalty 5
  (2af) tied the baseline. Deferring non-proof pairs 125× is close to
  this boost of proof pairs, so there is no sign that the order is
  worth the cost.

Not pursued. The option stays in, off by default.

**Update (19 Nov 17:10): only the most expensive point of this hook was tried** (the user: the forest can be as small
as the weight function). rm4t's 200 trees ran on every pair, with both parents featurised again each time, on 6 goals.
The cheap end is twee-e62 `--pg-order F`: score × F ** sigmoid(q1 + q2), from the parents' stored scores, two lookups
per pair. exp35 tests it paired on the 400 ultest goals, from about 18:45
([notes/2026-11-19-pg-order.md](notes/2026-11-19-pg-order.md)).

**Result (stopped 19:43): the cheap end does not pay either.** Against exp33's rm4t arm on the same goals, F = 0.5
proved 228 of 284 (control 240, +0 −12) at 2.2× the CPU, and F = 0.1 proved 56 of 83 (control 69, +0 −13) at 6.8×.
Neither arm proved a goal the control missed, so neither is a member.

## 2ap. Hints from the kNN lemmas' proofs (16 Nov, 11:35): no gain

The cross-original hint pools of earlier tests were never measured
where the control proves anything. 2ad's snapshot was invalid, and 2ag
used heads, where every arm proved 0 of 30.

`loop.py --hint-lemma-proofs F` (`--hint-lemma-proof-max 300`) adds, after the
own pool, the proof steps of each of the run's 30 kNN lemmas as hints
with factor F. These are proven goals of the same or weaker axioms,
mostly of other originals. It adds 200–600 hints per goal once the own
pool's duplicates are removed. Paired, as KN30 (abs/hlp_test.sh,
unsol150, ULsZ, fresh 20 s):

| arm | proved | against KN30 | wall s |
|---|---:|---|---:|
| KN30 (control) | 6 | – | 4,919 |
| F = 0.1 (KH01) | 5 | +1/−2 | 5,323 |
| F = 0.01, the own pool's boost (KH001) | 5 | +1/−2 | 5,240 |

No gain, and 7–8% more wall time. What transfers across originals is
exact: a goal that is a step of another proof (2al), or a proven goal as
a lemma axiom (2am). Similar proofs' steps as hints do not.

## 2aq. From scratch on unseen originals: a replay (16 Nov, from 11:55)

*Notes: [notes/2026-11-16-replay-unseen.md](notes/2026-11-16-replay-unseen.md).*

What would the final system do on a new benchmark part, such as the
secret 10,016 problems? The replay (abs/replay.sh) takes 3 whole holdout
originals: a_of_aa, lra2aa and nil3_23_32_to_26 (sets/rp3, 1,320 goals).
It removes their proofs (loops/RPs = UL at 11:50 minus them) and runs
them from scratch.

* **Settings:** production's cascade (abs/ul34.sh) on 4 workers,
  without the learned scheduler, which was trained on production's
  history of these goals.
* **Transfer:** the live proof-step transfer runs beside it (abs/rpx.sh,
  `transfer.py live --set sets/rp3`, every 10 minutes, 2 workers).
* **Context:** the other 126 originals' proofs, as kNN lemma sources
  and transfer sources.

| system | proved of 1,320 | time |
|---|---:|---|
| plain twee, 4 s (runs/ALL_plain_t4) | 731 | 0.8 CPU h |
| production, 3 days of loops (all versions) | 1,109 | – |
| **replay, after 25 minutes** | **1,039** | about 2.5 CPU h |

* **A third of these goals are instances of proven goals of other
  originals** with the same or weaker axioms. The transfer worker's
  first scan found 452 such goals (`find --goals`) and 546 candidates in
  all, and proved 545 of the 546 in 91 s of runs.
* The cascade itself proved 852 goals, 482 of them in the first minute,
  mostly with kNN lemmas that state the goal itself. These became
  possible with the fix in 2al.
* Curve of the cascade's own proofs (minutes, proved, CPU h): 1: 482,
  4: 804, 10: 846, 25: 852. The rest is the transfer's (189 synced).
* **Caveat:** the other originals' proofs were found partly with these
  3 originals' proofs in context, for example as kNN lemmas. A clean
  replay would need a context computed without them. For the secret
  part, the public proofs are a clean context.

**At 60 minutes** (stopped at 12:58): **1,041 of 1,320**. 854 came from
the cascade, in 3.25 CPU h: 1,000 runs at 5 s, 54 at 80 s and 12 at
320 s. 545 came from the transfer, in about 0.1 CPU h, and the two
overlap. Production has 1,109 after 3 days. The replay's last 35 minutes
added only 2.

**Clean replay** (abs/replayc.sh, abs/rpxc.sh, abs/replaycurvec.sh;
loops/RPc, from 12:59). The context is loops/ALL minus the 3
originals: 31,605 proofs of the 13 Nov 2 + 2 s loop, from before kNN
lemmas, so none of them used these originals. Settings and budget are
the same.

| minutes | cascade, full context | cascade, clean context |
|---:|---:|---:|
| 1 | 482 | 539 |
| 4 | 804 | 681 |
| 10 | 846 | 724 |
| 25 | 852 | 755 |
| **with the transfer, 25 min** | **1,039** | **893** |

* With the clean context, the transfer's first scan finds 384 goals
  that are steps of proofs and 356 that are instances of proven goals,
  against 546 and 452. It proves 385 of the 387 it tried.
* **So on unseen originals the system makes 893 in 25 minutes (about
  1.7 CPU h) from a context of 2 + 2 s proofs alone, against 731 for
  plain twee.** That's 22% more.
  * With today's richer context it makes 1,039. Part of the 146
    difference is the contamination above.
  * Part is legitimate: the 12k later proofs of other originals are
    harder theorems that new originals can use too.
  * For the secret part, both kinds of context are clean.
* **Clean replay at 60 minutes** (stopped at 13:59): **934 of 1,320**.
  795 came from the cascade in 3.92 CPU h (1,379 runs at 5 s, 747
  proved; 97 at 80 s, 48 proved), and 386 from the transfer. Unlike the
  full-context replay it was still growing: 755 at 25 minutes, 795 at
  60.

| 3 holdout originals, 1,320 goals | proved |
|---|---:|
| plain twee, 4 s | 731 |
| replay, clean context, 60 min, about 4 CPU h | 934 |
| replay, full context, 60 min, about 3.4 CPU h | 1,041 |
| production, 3 days | 1,109 |

**The other 8 whole holdout originals** (abs/ho8.sh, sets/ho8, 3,400
goals) ran from 14:00 to 15:01 with `solve_new.sh` and the clean
context, on 4 workers for 1 hour plus the transfer: **2,451 of 3,400**.

* The cascade made 1,723: 2,628 runs at 5 s with 1,674 proved, and 90
  at 80 s with 49 proved, in 3.9 CPU h.
* The transfer made 1,385, and the two overlap.
* Curve of the cascade (minutes: proved): 1: 526, 4: 1,340, 10: 1,541,
  25: 1,661, 60: 1,723.

**All 11 whole holdout originals** (4,720 goals), from scratch with the
clean context:

| system | proved | share |
|---|---:|---:|
| plain twee, 4 s | 2,887 | 61.2% |
| **`solve_new.sh`, 1 hour per batch (3 + 8 originals), about 8 CPU h in all** | **3,385** | **71.7%** |
| production, 3 days, every version, full context | 4,190 | 88.8% |

**Will the reuse carry over to the secret part?** It depends on how
the axiom sets relate. Every whole holdout original has 12–30 public
originals with the same or weaker axioms, which are the kNN lemma and
transfer sources. In 6 of the 11, those include originals with
identical axioms. The 129 public originals have 17–28 axioms each, and
68 of them have 18. The secret originals were picked from the same
groups (README), so they will most likely have such neighbours too.

**A 20 s level from scratch** (abs/lv_test.sh, 15:05–16:06, sets/rp3,
clean context, 4 workers plus the transfer, 1 hour):

| levels | proved | the cascade's own | runs (proved) beyond 5 s |
|---|---:|---:|---|
| 5, 80, 320 s (LVA, control) | **933** | 791 | 95 at 80 s (48) |
| 5, 20, 80, 320 s (LVB) | 925 | 792 | 198 at 20 s (38), 48 at 80 s (8) |

* No gain, so production's levels stay.
* The control repeats RPc (934) to within one proof, so this testbed's
  noise is small. Effects of about 20 proofs are visible.

**Two more knobs** (abs/lv2_test.sh, 16:08–17:10, same setting; control
LVA 933):

| arm | proved | the cascade's own |
|---|---:|---:|
| 60 kNN lemmas (LVC) | 920 (−13) | 764 |
| the transfer every 2 minutes instead of 10 (LVD) | **942** (+9) | 799 |

* 60 lemmas again bring nothing (2am). The early sweep is slower with
  them: 645 against 671 at 4 minutes.
* The faster transfer cycle passes reuse on sooner. +9 is near the
  noise, but it costs only the scans, so `solve_new.sh` now cycles
  every 2 minutes by default (XEVERY=120).

**From zero** (abs/lvz_test.sh, LVZ, 17:50–18:51): the same 3 originals
with an empty context, so there are no other originals' proofs for
kNN lemmas, hint pools or the transfer. Totals over time, cascade and
transfer together (abs/totcurve.py, from the proof files' times):

| minutes | 1 | 4 | 10 | 25 | 40 | 60 |
|---|---:|---:|---:|---:|---:|---:|
| clean public context, transfer every 10 min (LVA) | 634 | 807 | 849 | 896 | 905 | 933 |
| the same, every 2 min (LVD) | 628 | 809 | 847 | 884 | 921 | 942 |
| **from zero (LVZ)** | 565 | 732 | 806 | 858 | 883 | **890** |
| plain twee at 4 s, 0.8 CPU h | | | | | | 731 |

* **The loop alone does most of it.** From zero it reaches 890 of
  1,320 in 1 hour on 4 workers, 22% over plain twee (731).
* **The 13 Nov context adds 43–52 proofs (5–6%).** The transfer
  proves 420 goals in seconds, but the cascade from zero proves most
  of those within minutes as well. The context's lead is largest
  early (+75 at 4 minutes). *Today's context, filtered, adds 195
  (22%): 1,085 (LVU, below).*
* Caveat: the rule model rm4t is still the fixed one. It was trained
  on plain 2 s proofs of the training split (2e, 2f), the kind a
  from-zero run makes in its first sweep.

**The learned scheduler from scratch** (abs/lvs_test.sh, LVS,
18:51–19:52). Production's scheduler options (2ac: its model m4, the
probability floor 0.011 with auto-tuning, retraining every 200 runs)
with the clean context. The control is LVD.

| minutes | 1 | 4 | 10 | 25 | 40 | 60 |
|---|---:|---:|---:|---:|---:|---:|
| LVD (no scheduler) | 628 | 809 | 847 | 884 | 921 | 942 |
| **LVS (scheduler)** | 431 | 830 | 868 | 917 | 943 | **972** |

* ~~+30, against about 1 of noise~~. **Corrected at 21:50: the +30 is
  noise.** LV4 has LVS's settings exactly (the same context file, the
  same options except the 4-hour stop), and it had **919** at 60
  minutes against LVS's 971. Without the scheduler, runs repeat to
  within one proof (LVA 933, RPc 934). With it, small timing
  differences move the retraining points and the auto-tuned floor
  (LVS 0.054–0.058, LV4 0.087, then 0.048 down to 0.022), and with
  them which goals get the 80 s level. The scheduler arms' mean at 60
  minutes is 943 (971, 919, and LVS2 940, below), the same as LVD's 942.
* The wall-clock hour is not the cause. Counting each run's abstract
  seconds (`abs/workcurve.py`) gives LVS 947 and LV4 917 at 7,000
  abstract seconds of cascade work.
* `solve_new.sh` kept it by default (`SCHED`) until 17 Nov, because
  with `--sweep-first` it is no worse from scratch and production's
  long-run evidence (2ac) is for it. Since then the default is
  `--mix 0.1 --fail-order` without it (2at). A single 1-hour run of the
  scheduler on this testbed cannot tell effects under about 50 proofs.
* **From zero it starved originals** (LZ4, first try, 19:52–20:03:
  232 proofs at 10 minutes against 806). All 427 runs were a_of_aa
  goals. The model orders fresh runs by predicted success, and an
  original with no proven goal scores below the floor or beyond the
  line-gap limit. Production never shows this: every original has
  proofs. With context the transfer gives each original proofs
  within seconds, but LVS still started slowly (431 against 628 at
  1 minute).
* **Fix: `loop.py --sweep-first`** (d8e36da). Goals never run in the
  round go first, in goal order across originals, and the model ranks
  only the retries it was trained on. It is in `solve_new.sh`'s SCHED
  default. LZ4 restarted with it at 20:05: 724 at 4 minutes against
  732 without the scheduler, and all three originals ran evenly. LV4
  runs without it.
* **With context, sweep-first gives 940** (LVS2, 20:41–21:42; LVS 972
  and LV4 919 without it). It runs every goal at 5 s first: 2,103
  runs at 5 s and 51 at 80 s in the hour, against 1,439 and 86 for
  LVS. 260 of its 783 cascade proofs are goals that the transfer
  proves too. Within the noise, so it stays in the default.
* **From zero, 4 hours** (LZ4, scheduler with sweep-first, to 00:50):
  **977**. Minutes: 60 906, 90 928, 120 955, 180 974, 240 977. LVZ (no
  scheduler, 1 hour) 890; at 60 minutes 906 against 890, at equal
  cascade work (7,000 abstract s) 879 against 884, the same. In all:
  2,426 runs at 5 s (875 proved, 3.2 h), 272 at 80 s (89, 8.2 h), 26 at
  320 s (8, 5.7 h). So from zero the 3 originals pass the 13 Nov
  context's 2-hour 952, without any other original's proofs.

**Why the replays level off near 950** (21:50). LV4 had 948 at 2 hours
(stopped there) and LZ4 937. Production has 1,111 of the 1,320, and
the 4-hour replays' proofs are a subset of it. Of the 159 goals
production has and LV4 has not, production proved 151 with its own
runs: median 7.9 s wall, three quarters under 25 s. 88 came at the
5 s level, 18 at 80 s, 3 at 320 s, and 42 in rounds 1–2, before the
cascade. So they are not hard. 56 of those runs kept their output.
* 42 of the 56 use a sibling lemma that is itself one of the 159, so
  they follow from a few earlier ones.
* **45 of 54 with named kNN lemmas use one from another original's goal
  proven after 13 Nov.** loops/ALL, the replays' context, is a snapshot
  from 13 Nov 02:58 with 32,377 proofs. Production now has 44,838.
  For example nil3_23_32_to_26's late goals use goals of
  nil3_23_32_to_25, _27, _28 and _31, which production proved later.
* So the replays measure the method under a context that is 3 days
  older than the one new problems will get. The morning's replay with
  the full context (RPs, 1,041) showed this too, but its context was
  contaminated, and the later arms all used loops/ALL. The secret part
  will run with all of today's public proofs.
* **Today's context, filtered (LVU, 21:53–22:53, stopped at 23:35
  when its last runs ended): 1,085 of 1,320 in 1 hour.** The settings
  are LVS2's, with loops/ULX as the context. That is loops/UL at 21:52
  minus the 3 originals, 43,681 proofs (`abs/freshctx.py`). 46 proofs
  are left out because a kept output names an rp3 goal among their kNN
  lemmas (41), or a transfer row names one among its sources (5).

| minutes | 1 | 4 | 10 | 25 | 40 | 60 |
|---|---:|---:|---:|---:|---:|---:|
| loops/ALL, 13 Nov (LVS2, same settings) | 580 | 799 | 856 | 875 | 903 | 940 |
| **loops/ULX, today (LVU)** | 416 | 969 | 1,036 | 1,065 | 1,075 | **1,085** |
| production, 3.5 days | | | | | | 1,111 |

* The transfer proves 575 (417 with loops/ALL). The cascade made 1,510
  runs at 5 s (803 proved), 76 at 80 s (25), and 8 at 320 s (2).
* **Leaks** (`abs/leakcheck.py`). LVU has 137 proofs that LV4 lacks.
  44 of them use only sources that are old, verified clean, or from
  the 3 originals themselves. 88 use at least one newer source whose
  output was not kept. Among the newer proofs whose output was kept,
  1.6% used an rp3 goal (41 of 2,609), so few of those 88 can be
  leaks.

**The other 8 holdout originals** (sets/ho8, 3,400 goals, 4 workers, 1
hour, each run stopped when its last runs ended):

| minutes | 1 | 4 | 10 | 25 | 40 | 60 |
|---|---:|---:|---:|---:|---:|---:|
| HO8, 14:00: loops/ALL, no scheduler, transfer every 10 min | 456 | 2,060 | 2,260 | 2,384 | 2,417 | 2,451 |
| HO8b, 21:43: loops/ALL, today's defaults (`abs/ho8b.sh`) | 473 | 2,046 | 2,274 | 2,474 | 2,520 | **2,573** |
| HO8U, 22:47: loops/HOX, today's proofs (`abs/hou_test.sh`) | 155 | 1,012 | 2,701 | 2,940 | 2,995 | **3,021** |
| production, 3.5 days | | | | | | 3,092 |

* **Today's defaults: +122 on the same context** (2,573 against
  2,451; at 7,000 abstract s of cascade work 2,504 against 2,420). The
  scheduler with sweep-first and the 2-minute transfer cycle changed
  together, so this does not say which of them helped.
* **HO8U is an upper bound.** Here the context leaks a lot.
  loops/HOX leaves out 1,114 proofs that are known to use a ho8 goal:
  941 with it among their kNN lemmas, 173 with it among their transfer
  sources. But among the newer proofs whose outputs were kept, **37%
  used a ho8 goal** as a kNN lemma (941 of 2,513), against 1.6% for
  rp3. The 8 originals (aK2_eq_aK3_1243b and _f, aa1_12, aa1_45_b,
  aK1_to_aK2, mbol_KK_to_aK1, mbol_lem2, ns_to_aK1) belong to the big
  aK and aa families, and the families' later public proofs used
  their goals as lemmas. The most frequent users among the excluded
  1,114 are the rp3 originals themselves (154) and nslm_to_aa1,
  aK2_eq_aK3_a, nsmr_to_aa1. About 9,000 newer proofs could not be
  checked.
  Of HO8U's 449 extra proofs over HO8b, 353 use at least one of them.
* So for these 8 originals the result with a clean context of
  today's size lies between 2,573 and 3,021. For rp3, whose
  originals have few close public relatives, the leak rate is small
  and 1,085 stands.

**All 11 holdout originals, 1 hour per batch, today's defaults:**

| context | proved of 4,720 | share |
|---|---:|---:|
| plain twee, 4 s | 2,887 | 61.2% |
| loops/ALL, 13 Nov (LVS2 940 + HO8b 2,573) | 3,513 | 74.4% |
| today's proofs, filtered (LVU 1,085 + HO8U 3,021; HO8U leaks) | 4,106 | 87.0% |
| production, 3.5 days | 4,203 | 89.0% |

The secret part's context will be today's public proofs, which never
saw a secret goal. How close the secret originals come to the upper
row depends on how many close public relatives they have.

So about half the gap between plain twee and three days of production
is closed in the first hour, on originals the system has never seen.
Most of it comes in the first 10 minutes. Exact reuse of other
originals' proven goals and proof steps does most of the work: goals
that state, or are instances of, proven goals of the same or weaker
axioms.

## 2ar. The same statement proven in another theory (16 Nov, 16:20)

*Notes: [notes/2026-11-16-same-statement-other-theory.md](notes/2026-11-16-same-statement-other-theory.md).*

`transfer.py find --same-other` lists the unsolved goals whose statement,
up to renaming, is a proven goal of an original whose axioms are not
within theirs. On 16 Nov that is **1,887 of 7,025**. For 1,361 of them
the source theory has only one axiom the goal's lacks. Such a proof
holds for the goal if neither it nor its lemmas use the missing axioms.

* **They mostly do.** In 359 of 400 source proofs (90%), the missing
  axiom is itself a step of the proof. The shared statements hold there
  because of the hypothesis that differs.
* **Pilot with the source original's whole pool as hints**
  (`run --src-pool`, sets/so60.tsv): 0 of 25. Stopped.
* **The 323 whose source proof has no missing axiom as a step**
  (sets/so_free.tsv): source proof steps as hints, 20 s, 60 of them
  (sets/sof60.tsv): **3 of 60**, in 0.6 CPU h. That's 5 per CPU hour,
  more than production's 1 per worker hour now. The 3 proofs are
  merged. The other 263 (sets/sof_rest.tsv, run SOR, 4 workers, to
  17:47): **10 of 263** in 2.4 CPU h, 4.2 an hour, 9 of them new to
  production. All 323 are now tried.
* So the lemma chains carry the dependence, even when the final proof
  does not show it. Exact reuse works within the same or weaker
  axioms (2al, 2am) and rarely across them.

## 2as. The whole benchmark from zero, and a faster dispatcher (16–17 Nov night)

*Notes: [notes/2026-11-21-dispatch-profile.md](notes/2026-11-21-dispatch-profile.md).*

*Notes: [notes/2026-11-16-from-zero-dispatcher.md](notes/2026-11-16-from-zero-dispatcher.md).*

**Z0** (`abs/z0_test.sh`, from 23:49): the final system from zero on
all 51,784 public problems. `solve_new.sh` with an empty context,
without the learned scheduler (from zero it needs `--sweep-first`,
which at this size would run every goal once before any retry), the
transfer every 5 minutes, 12 workers.

| minutes | 5 | 10 | 20 | 30 | 40 | 50 | 60 | 66 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Z0, proved | 1,877 | 6,215 | 17,435 | 22,979 | 27,397 | 30,275 | 32,475 | 33,459 |

* **In 50 minutes on 14 CPUs it matches plain twee at 4 s on the whole
  benchmark** (31,060, 28 CPU h). At 66 minutes 33,459, past the 2 + 2 s
  loop of 13 Nov (33,249, 24.5 CPU h).
* The transfer did 12k of them: goals that are instances of proven
  goals of other originals with the same or weaker axioms, or steps of
  their proofs.
* **But the dispatcher was the bottleneck.** Busy workers (summed run
  wall time over the window) by 10-minute window: 4.8, 2.7, 3.7, 5.3,
  7.3 of 12. Most runs were proofs in under a second, and loop.py's
  main thread ran at 100% CPU.

**Where the main thread's time went.** A cProfile of the same start (3
workers, 4 minutes) put most of it in `ctx()`, the goal's sibling-lemma
context: 43M calls, 260 of 472 s. It ran for every waiting goal,
several times in every scheduling pass, and the pass ran after every
finished run. Three changes:

| change | runs in the first 1 / 2 / 3 minutes (12 workers) |
|---|---|
| none (Z0) | 872 / 1,403 / 1,765 |
| `ctx()` cached per original (b1bb8c5) | 1,030 / 1,596 / 1,905 |
| + kNN picks memoised in the lemma index (c9d1341): each run's picks were computed at dispatch and again when its problem was written; same picks, 30.7 → 16.8 ms a goal | 1,058 / 1,605 / 1,916 |
| + **`--pass-every 1`** (a2b03ec): the full pass at most once a second, its lists used up in between, each goal checked again when taken | **1,454** / 1,872 / 2,079 |

* Timers in the status line (`main s: pass … submit … wait …
  results …`) showed the cause before the last change: the passes took
  134 of the main thread's 180 s. After it 29 of 170, and the main
  thread mostly waits for workers.
* The first two help most later, with tens of thousands of proofs in
  the index; the 3-minute tests start with almost none.
* **No proofs lost:** PE1 (rp3 from zero, 4 workers, `--pass-every
  1`) gave 733, 809 and 830 at 4, 10 and 15 minutes, against LVZ's 732,
  806 and 830.
* `solve_new.sh` now passes `--pass-every 1` (`PASS_EVERY`); production
  keeps 0.

**Z1** (`abs/z1_test.sh`, from 00:56): Z0 again with the new
dispatcher, 12 workers, 10 hours. Z0 was stopped at 66 minutes; its
curve above is the comparison.

| minutes | 2 | 5 | 10 | 15 | 20 |
|---|---:|---:|---:|---:|---:|
| Z0 | 600 | 1,877 | 6,215 | 12,001 | 17,435 |
| **Z1** | 1,167 | 2,064 | 8,095 | 15,460 | **22,577** |
| busy workers, Z0 (5-minute windows) | 6.4 | 3.2 | 2.2 | 3.2 | |
| busy workers, Z1 | 9.6 | 7.4 | 7.4 | 7.6 | |

* +30% at 20 minutes. Z1 reaches Z0's 30-minute count (22,979) about
  10 minutes earlier.
* Z1's main thread at 20 minutes: passes 266 s, submitting 329 s,
  waiting 471 s, results 114 s. Submitting now costs most, largely the
  kNN picks over an index of 20k proofs. The main thread waits 40% of
  the time, so the workers are mostly the limit now.

**Z1 at 2 hours (stopped at 126 minutes, 03:02).** Counts by proof-file
times at the stop. Some files were rewritten later, so the 20-minute
count read then (22,577) is now 22,165.

| minutes | 10 | 20 | 30 | 45 | 60 | 90 | 120 | 126 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Z0 | 6,215 | 17,435 | 22,979 | 28,909 | 32,475 | | | |
| **Z1** | 7,942 | 22,165 | 28,996 | 32,664 | 34,181 | 35,514 | 36,552 | **36,760** |

| Z1, 15-minute windows | 0–15 | 15–30 | 30–45 | 45–60 | 60–75 | 75–90 | 90–105 | 105–120 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| loop runs | 14,706 | 8,660 | 2,733 | 1,818 | 1,469 | 1,626 | 1,565 | 1,874 |
| proved by them | 14,469 | 8,357 | 2,059 | 959 | 573 | 434 | 435 | 415 |
| busy workers (of 12) | 8.1 | 9.4 | 11.4 | 11.7 | 11.7 | 11.9 | 11.8 | 11.8 |

* Production (loops/UL, days of runs) has 44,841. Z1 found no proof
  production lacks, and production has 8,116 that Z1 has not.
* **Every one of Z1's 34,579 runs was at the first level (5 s).**
* **12,998 of its 15,062 unsolved goals never ran at all.** The other
  2,064 were retried, many of them 6 or more times.
* **6,080 of production's 8,116 extra proofs are on goals Z1 never
  ran.** By production's rounds: 2,799 from its cascade, 690 from
  round 0 (plain twee and the first lemma runs), the rest from rounds
  1–4.
* **The cause is the dispatch order.** A near retry is a goal at most
  `--retry-gap` places (or 80 proof lines) after a proven sibling,
  with a changed context. Near retries go first, then deeper levels.
  Goals beyond the gaps, including every goal with no proven goal
  below it, run only on idle slots (`--far-retry`). On 51,784 goals,
  some context changes all the time, so there is always a near retry
  waiting and no slot is ever idle.
* The near retries still paid: 22–27% of them proved their goal in
  the second hour. But the goals beyond the gaps never got one run.
* **Replays have the same flaw on a small scale.** PE1 (rp3, 15
  minutes) left 438 of its 489 unsolved goals never run, and made 26
  deeper runs out of 1,151.
* **So does production.** 4,114 of its 6,943 unsolved goals have not
  run in round 5, its cascade round of several days. 680 goals ran
  there 10 or more times. ul37's last 2.5 hours on 4 workers gave 4
  proofs, mostly from 320 s resumes.

## 2at. Repeats cost most of the time: `--mix` and `--fail-order` (17 Nov, from 03:10)

*Notes: [notes/2026-11-17-mix-fail-order.md](notes/2026-11-17-mix-fail-order.md).*

**`--mix M`** (f065848, 187832f) splits the runs into three kinds:

* near retries;
* far goals: those beyond the retry gaps, including the never-run ones;
* deeper levels.

Each kind that has goals waiting keeps M of the workers. The other
slots go to the kind with the most proofs per run second over its
last 300 runs. The seconds its running jobs have taken so far count
as spent without a proof. Without that, a 320 s resume, which takes
about 25 wall minutes, kept the deeper levels first until one ended
(seen in production).

| run | 4 min | 10 min | 15 min |
|---|---:|---:|---:|
| PE1 (rp3 from zero, 4 workers) | 733 | 809 | 830 |
| MX1, `--mix 0.1` (one worker each) | 734 | 807 | 831 |
| MX3, `--mix 0.5` (two each) | 717 | 789 | 824 |

**Z2** (`abs/z2_test.sh`): Z1 plus `--mix 0.1`, which keeps 2 of the 12
workers each for far goals and deeper levels.

| minutes | 10 | 20 | 30 | 45 | 60 |
|---|---:|---:|---:|---:|---:|
| Z1 | 7,942 | 22,165 | 28,996 | 32,664 | 34,181 |
| Z2 | 5,724 | 18,540 | 25,967 | 31,226 | 33,539 |

Proofs per worker-hour by kind, from Z2's status lines:

| minutes | 25 | 30 | 50 | 60 |
|---|---:|---:|---:|---:|
| near retries | 4,147 | 1,994 | 1,189 | 517 |
| far goals | 431 | 276 | 118 | 127 |
| deeper levels | 15 | 15 | 15 | 15 |

* At 5 s, far goals pay less than near retries for the whole first
  hour, so the reserved slots cost. Z2 was stopped at 65 minutes, 2%
  behind Z1.

**What the time goes to.** In Z1's second hour the first-level runs,
by how often the goal had failed before in the round:

| earlier failures | runs | proved | | proofs per run hour |
|---|---:|---:|---:|---:|
| 0 | 3,516 | 1,800 | 51% | 365 |
| 1 | 1,270 | 78 | 6% | 29 |
| 2 | 882 | 35 | 4% | 19 |
| 3–8+ | 1,443 | 63 | 4% | 17–32 |

* **A goal's first run pays 12–20 times as well as a repeat after a
  failure, and the repeats took 61% of the workers' time.**
* A repeat comes after a change in the goal's context: a nearer
  sibling proved, or the original's hint pool grown by 25%. On a large
  set something changes all the time.
* Z2 after 30 minutes: first runs 4,760/5,408 (1,749 an hour) against
  7–17% (52–106 an hour) for repeats. LVZ (rp3) after 15 minutes: 36
  first runs against 316 repeats.

**`--fail-order`** (3db0e8d): one list holds every goal with a new
context, near and far (with `--far-retry`). The goals with the fewest
failed fresh runs in the round go first, then those within the retry
gaps, then the nearest. It is for runs without the learned scheduler,
whose model ranks retries itself. It is used with `--mix`, which
keeps a share for the deeper levels.

* rp3 from zero, 2 workers, 2.4 minutes: 617 proved with `--fail-order
  --mix 0.25`, against 383 with `--mix 0.25` alone. At most 2 runs per
  goal, against 6.

**Z3** (`abs/z3_test.sh`): Z2 plus `--fail-order`.

| minutes | 2 | 5 | 10 | 15 | 20 | 22 |
|---|---:|---:|---:|---:|---:|---:|
| Z1 | 1,167 | 2,064 | 7,942 | 15,094 | 22,165 | 24,678 |
| Z3 | 1,438 | 5,975 | 11,825 | 19,224 | 22,953 | 24,876 |

* Far ahead early (+65% at 10 minutes), level at 22 minutes.
* **The dispatcher was the limit again.** Only 4.6–7.8 of the 12
  workers were busy. The new list holds every waiting goal and is
  sorted in every pass, so a pass took 0.2–0.35 s; passes took 409 of
  the main thread's 1,431 s.
* A cProfile (4 workers, 4 minutes) puts the time in the list's
  generator and in `ctx()`. `ctx()` is called twice per goal per pass:
  once for this list and once for the deeper levels' list.
* **Fix (5b15fc9):** with `--pass-every`, the full pass now waits at
  least 8 times its own last length. The time of a kNN index rebuild
  is left out of that length. On rp3 (2 workers, 2.4 minutes) 619
  against 617. Z3 was stopped at 24 minutes. **Z4** (`abs/z4_test.sh`)
  is Z3 with this fix.
* At 3.7 minutes Z4 had made 8,250 runs, against 13,150 in Z3's first
  9.5 minutes. Its loop.py is at 100% CPU: one Python process
  (main thread plus the worker threads' file and output handling) is
  now the limit. Its main thread at 224 s: passes 41 s, submitting 67,
  waiting 71, results 45.

| minutes | 5 | 10 | 15 | 20 | 25 | 30 |
|---|---:|---:|---:|---:|---:|---:|
| Z1 | 2,064 | 7,942 | 15,094 | 22,165 | 26,339 | 28,996 |
| **Z4** | **8,101** | **15,398** | 20,785 | 24,215 | 27,397 | 29,814 |
| busy workers, Z1 (5-minute windows) | 9.6 | 7.4 | 7.4 | 8.0 | 9.8 | 10.4 |
| busy workers, Z4 | 6.8 | 7.3 | 8.1 | 8.6 | 12.7 | 6.8 |

* **Twice Z1's count at 10 minutes, 3% more at 30.**

| minutes | 45 | 60 | 75 | 90 | 105 | 120 |
|---|---:|---:|---:|---:|---:|---:|
| Z1 | 32,664 | 34,181 | 34,974 | 35,514 | 36,036 | 36,552 |
| **Z4** | 33,569 | 35,511 | 36,675 | 37,328 | 37,556 | **37,713** |
| Z4's runs in the 15 minutes before | | | 2,043 | 1,899 | 1,569 | 1,471 |
| proved by them | | | 822 | 518 | 182 | 122 |

* **Z4 reaches Z1's 2-hour count at about 84 minutes, and has 1,161
  more at 2 hours.**
* Its rate then falls fast: 122 proofs in the last quarter-hour,
  against Z1's 415. At equal counts Z4 does better (518 per quarter-hour
  at 36.7k, Z1 415 at 36.5k), but by 90 minutes it has used up the
  goals that are easy next to a proof.
* All of Z4's second-hour first-level runs were first runs: 1,621 of
  6,895 proved (168 an hour). Most were goals beyond the gaps, which
  prove 8–12% of the time now. 7,189 goals were still unrun at 2
  hours.
* The deeper levels made 164 runs in 2 hours, and 54 of them (34%)
  proved at the 80 s level. That is 15 proofs per worker-hour, against
  33 for the first-level runs at 2 hours.
* In the first 30 minutes 25,250 of Z4's 25,527 runs proved their goal,
  yet 21,646 goals had not run at all. In this phase every run is a
  proof, so the limits are how fast one Python process hands out runs
  and the chains: a goal becomes easy only once the goal below it is
  proved.
* Repeats in Z1 after 30 minutes, split by whether a sibling among the
  10 goals below was proved since the goal's last run: 11.0% (50 an
  hour) with one, 4.6% (20 an hour) without. Both are far below a
  first run, so ordering by failures alone loses little.

**rp3 over an hour** (from zero, 4 workers, no scheduler):

| run | 15 min | 30 min | 45 min | 60 min |
|---|---:|---:|---:|---:|
| LVZ | 830 | 871 | 885 | 890 |
| MX60, `--mix 0.25` | 828 | 872 | 887 | **914** |
| FO60, `--mix 0.25 --fail-order` | 828 | 872 | 888 | 891 |

* MX60's gain came after 45 minutes: 22 first-level proofs then,
  against none in LVZ, whose last 15 minutes gave 5 deeper proofs.
* FO60 ran every goal at least once (LVZ left 385 of its 430 unsolved
  goals never run, MX60 194) but proved no more. On this small set
  the goals that never ran are mostly ones a 5 s run does not prove.
  MX60 against FO60 (914 against 891) is one run each.

**The replay with today's context** (rp3, context loops/ULX with every
proof of rp3's originals left out, 4 workers, 1 hour, 2aq):

| run | 1 min | 4 min | 10 min | 25 min | 40 min | 60 min |
|---|---:|---:|---:|---:|---:|---:|
| LVU, learned scheduler (`solve_new.sh` default then) | 416 | 969 | 1,036 | 1,065 | 1,075 | 1,085 |
| **LVF**, `--mix 0.25 --fail-order`, no scheduler | 455 | 1,004 | 1,041 | 1,068 | 1,085 | **1,095** |

* Ahead at every mark, and every goal ran at least once. Production
  took 3.5 days to reach 1,111. Scheduler runs vary by about 25, so
  this is a lean, not proof.
* **`solve_new.sh` now defaults to this order** (`ORDER`, 2db27bf),
  with `--mix 0.1`, which keeps one worker each at 4 workers and two
  at 12. `SCHED` turns the scheduler back on.

## 2au. The tail: which goals get the longer runs (17 Nov, from 08:40)

*Notes: [notes/2026-11-17-tail-states-e44.md](notes/2026-11-17-tail-states-e44.md).*

**`--fail-reset` (FR60)** gives no gain. A goal's failure count restarts
when the nearest proven goal below it changes (rp3 from zero, 4 workers,
1 hour, otherwise as FO60):

| run | 15 min | 30 min | 45 min | 60 min | 80 s runs (proved) |
|---|---:|---:|---:|---:|---:|
| FO60, `--fail-order` | 828 | 872 | 888 | 891 | 93 (42) |
| FR60, + `--fail-reset` | 835 | 855 | 859 | 886 | 53 (32) |

It stays off.

**Z4 stopped at 3 h 56 min** with 38,044 goals (60 min 35,511, 2 h 37,713,
3 h 37,962, 3.5 h 38,017). It was adding about 120 proofs an hour.
* Every goal but 782 had had a 5 s run. Only 545 had an 80 s run (112
  proved) and 25 a 320 s run (4).
* In its last 3,261 runs, 5 s runs proved 48 of 3,012 (19,778 s) and
  80 s runs 30 of 240 (26,098 s).
* Its 14 proofs that production lacked are merged into loops/UL (44,858).

**What production's extra goals needed.** Production has proved 6,818
goals Z4 has not. They took much longer in production, even with
production's richer context:

| goals | ≤ 0.5 s | ≤ 2 s | ≤ 5 s | ≤ 20 s | ≤ 80 s | ≤ 320 s | more |
|---|---:|---:|---:|---:|---:|---:|---:|
| proved by production only | 443 | 330 | 1,265 | 2,342 | 2,011 | 384 | 43 |
| proved by both | 29,897 | 4,684 | 1,646 | 1,229 | 515 | 47 | 8 |

* 70% of the gap took more than 5 s. So the tail is a question of which
  goals get the longer runs. Giving every one of Z4's 13,740 unsolved
  goals an 80 s run would take about 25 hours on 12 workers.

**The failed 5 s run's hint statistics do not predict an 80 s success.**
The statistics are hints, live, matched, lastmatch, maxgap, deferred and
rules, as raw values and as ratios.
* On production's 6,351 80 s runs every feature has an AUC of 0.43–0.55.
  On Z4's 544 it is 0.42–0.58.

**The original's recent proof rate does predict success.** It is computed
online, from earlier runs only, smoothed towards the overall rate with
weight 5:

| runs | AUC | top fifth by the rate proved | the rest proved |
|---|---:|---:|---:|
| production, 5 s (38,182) | 0.73 | 25% | 8% |
| production, 80 s (7,659) | 0.66 | 29% | 12% |
| production, 320 s (965) | 0.57 | 20% | 14% |
| Z4 after 30,000 runs, 5 s (14,777, all first runs) | 0.84 | 50% | 10% |
| Z4 after 30,000 runs, 80 s (494) | 0.70 | 35% | 14% |

* Weighting older runs by 0.9 per newer run of the same original (about
  its last 10 runs) raises the 5 s AUC to 0.85 (Z4) and 0.82
  (production).
* For the 80 s level, the original's 80 s rate does better on production
  (0.67) and its 5 s rate on Z4 (0.68). A blend, with the 5 s rate as
  the prior of the 80 s one, gives 0.60 and 0.66.
* Z4 never used this signal. Without the scheduler, both queues sort
  by failure count and distance only.

**`loop.py --orig-rate`.** Goals of the originals whose recent runs proved
most go first:
* within `--fail-order`'s failure counts, before near-or-far and
  distance;
* within each deeper level.

Details:
* The rates are kept per original and kind (5 s, or deeper), with
  weight 0.9 per newer run. The deeper rate's prior is the original's
  5 s rate times the overall ratio.
* They are used in bins of 0.1, with everything above 0.9 in one bin.
  From zero, when nearly every run proves, the order stays nearest
  first. The learned scheduler's per-original ranking starved originals
  there (2aq).

**The A/B test** is ORA (control, `solve_new.sh`'s defaults) against ORB
(`--orig-rate`), both from zero (abs/or_test.sh, from 09:02). They run
on sets/half1: 64 of the 129 originals, chosen at random with seed 17,
25,937 goals. Z4 proved 18,887 of them and production 22,291. Each arm
has 6 workers, a transfer every 5 minutes, and 2 hours.

| arm | 10 min | 30 min | 60 min | 90 min | 120 min | never run | 80 s runs (proved) |
|---|---:|---:|---:|---:|---:|---:|---:|
| ORA, control | 9,412 | 15,349 | 17,381 | 18,074 | **18,319** | 3,923 | 103 (37) |
| ORB, `--orig-rate` | 9,105 | 15,401 | 17,356 | 18,015 | 18,228 | 4,107 | 122 (58) |

* No gain, so it stays off. The arms are level to 1 hour, as
  expected: while most runs prove, every rate is in the top bin.
* After that ORB's 80 s runs proved more (58 against 37), but its
  first runs proved fewer.
* The rate predicts well on its own. But putting a promising
  original's far goals ahead of other originals' near goals does not
  pay: a predictive feature can still lose to the order in place. The
  AUCs above should have been measured within the existing key.
* A repeat of the control (ORD) is running beside a 20 s level (ORC)
  to measure the noise at this scale.

**Saved states cost a fifth of a failing run.** Every fresh run dumps its
search state so that a deeper level can resume it.
* Z4 left 13,427 states, about 10 MB each (123 GB on disk). Only 545
  goals were ever resumed.
* On a goal Z4 never proved (aa1_14 goal 505, 5 s, rule model, twee
  alone), the dump adds 0.6–0.9 s to a 2.7–2.9 s run and raises its
  peak memory from 67 MB to 267 MB. Proved runs dumped too (a 0.3 MB
  state took 0.1 s of a 0.3 s run), and loop.py then deleted the state.
* Breakdown of that run: plain 2.0 s, with hints 2.3 s, with the rule
  model 2.9 s, both 3.05 s, with the dump 3.6 s. In the loop such runs
  take a median 6–6.5 wall seconds: real runs have hundreds of hints,
  36 lemma axioms and bigger states, on a loaded machine.

Two fixes (0903499):
* **twee-e43** writes no state when the problem is solved. On 150 AIM
  goals with sibling hints it gives the same result, work counts and
  hints as e22 (124 proved, 26 not).
* **`loop.py --lean-states`**: a fresh run of a goal that may not
  deepen now keeps no state, and an older state of the goal is removed.
  Such a goal is beyond `--frontier` and the line gap, and not a head.
  If it deepens later, its next level starts over with the full
  budget.

**A 20 s level at scale, and the noise** (sets/half1, 6 workers, 2 h,
from zero, 11:04–13:05):

| arm | 10 min | 30 min | 60 min | 90 min | 120 min | never run | deeper runs (proved) |
|---|---:|---:|---:|---:|---:|---:|---:|
| ORA, control (09:02) | 9,412 | 15,349 | 17,381 | 18,074 | 18,319 | 3,923 | 80 s: 103 (37) |
| ORD, control repeat | 9,303 | 15,330 | 17,422 | 18,254 | 18,504 | 3,902 | 80 s: 107 (51) |
| ORC, 5, 20, 80, 320 s | 9,575 | 15,216 | 17,502 | 18,277 | **18,552** | 4,031 | 20 s: 388 (103), 80 s: 3 (2) |

* **Noise:** two identical runs differ by up to 185 (1%) after an
  hour. Earlier single-run comparisons at this scale (ORB's −91) are
  within it.
* ORC is 48 above ORD and 233 above ORA: a lean towards the 20 s
  level, not proof.
  * Its 20 s level proved 27% of its runs. They cost a quarter of an
    80 s run each.
  * Its deeper class got more slots (388 runs against 107) without
    costing first runs (4,031 never run against 3,902).

ORE (e43 + `--lean-states`) and ORF (also 5, 20, 80, 320 s) ran from
13:05 (abs/or_queue.sh).

**Both died after 70 minutes.** The cause was a bug in `--lean-states`.
* The check for whether a goal is a head used `hs`. A finished run's
  result reuses that name for its hints, which is `None` when the run
  failed.
* So a fresh run of a goal that may not deepen, dispatched between two
  full passes, raised a TypeError.
* The heads set is now `hds` (7d376a2). The bug cannot have
  touched ORA–ORD, which ran without `--lean-states`.

Their first hour is valid:

| arm | 10 min | 30 min | 60 min | runs an hour, rows 15,000–17,000 | first runs that proved: median wall s |
|---|---:|---:|---:|---:|---:|
| ORD, control, e22 | 9,303 | 15,330 | 17,422 | 4,157 | 1.80 |
| ORE, e43 + `--lean-states` | **10,282** | 15,858 | 17,596 | 4,455 | 1.22 |
| ORC, 5, 20, 80, 320 s, e22 | 9,575 | 15,216 | 17,502 | 4,311 | 1.77 |
| ORF, ORC + e43 + `--lean-states` | 10,094 | 15,891 | **17,733** | 4,832 | 1.24 |

* The gain is e43's, not the lean states'. A proved run no longer
  writes a state: its median wall time fell by a third. That matters
  most in the first half hour, when nearly every run proves.
* `--lean-states` hardly ever applied. ORE kept a state for 1,790 of
  its 1,815 failed first runs: nearly every failing goal is within 80
  proof lines of a proof, so it may deepen.
* Failed first runs still took a median 5.9 s, with their dump. In
  ORE's second hour they took 68% of the workers' time, while 1% of runs
  resumed a state.

**`--no-fresh-states`** (new) keeps no state for any fresh run. A goal's
first deeper level then starts over with its full budget, for example
20 s instead of the 15 s left after a resume. The deeper levels keep
their states.

**Where the 2-hour run falls short of production.** Production has
proved 3,785 half1 goals that ORD did not:
* 3,074 had failed one 5 s run and were never run again;
* 660 were never run;
* 51 had also failed an 80 s run.

ORD never retried a failed goal fresh. With `--fail-order`, a goal that
has never run comes first, and new ones kept coming as proofs moved the
frontier on. In ORD's last 2,400 runs, 18% of first runs proved.

Would retries have paid there? 200 random goals of these failed ones
got a fresh 5 s run with ORD's 20,026 proofs as context
(`solve_new.sh`). 29 proved (14.5%), against 18% for first runs at
the end. So putting never-run goals first is about right. Only 135 of
ORD's 3,529 failed goals saw their nearest proven goal below change
after they failed, 79 of them before the last 10 minutes.

ORG (as ORF: e43, `--lean-states`, 5, 20, 80, 320 s) and ORH (the same
with `--no-fresh-states` instead) run from 14:19, side by side under
the same load.

**Where a failing run's time goes.** 30 of those 200 goals that failed
again, with the loop's exact twee commands (`LOOP_PRINT_CMD`,
`LOOP_KEEP_TMP`), 5 abstract s, 3 at a time, mean CPU seconds:

| variant | CPU s | peak memory |
|---|---:|---:|
| as in the loop, without the dump | 5.45–5.61 | 93 MB |
| + `--dump-state` (6.8 MB states) | 6.66 | 349 MB |
| without the rule model | 4.87 | 91 MB |
| hints at `--eqhint-factor 1` (matched, but the search unchanged) | 4.34 | 88 MB |
| `--no-eqhint-normalise` | 4.45 | 75 MB |
| without hints | 3.29 | 70 MB |
| startup only | 0.17 | 42 MB |

* Hints cost 2.3 s of 5.6:
  * about 1.3 s is the hinted search itself, which is dearer per
    pair (bigger queue);
  * about 1 s is overhead. Twee's own timer puts renormalising the
    hints at 12% of the CPU (0.58 of 4.78 s). It redid every live
    hint against every rule whenever new rules had come.
* The dump adds 22% and 3.7× the peak memory.

**twee-e44** (99dbf15) renormalises incrementally. A hint is skipped
when no rule added since its last normalisation rewrites a subterm of
it or of its full normal form. Deleting a rule cannot make a normal
form reducible, and interreduction re-adds a changed rule under a new
id. The full forms are kept outside the saved state, so states from
e43 still load. `TWEE_HINTNORM_FULL=1` restores the full pass.

On the 203 captured runs (29 proved, 174 failed) against e43:
* 186 outputs are byte-identical.
* 11 differ only in 2–6 fewer extra hint forms, out of 2,000–8,000.
  These are full normal forms reached through a term that a new rule
  rewrites. Their searches are the same.
* 3 searches diverge slightly. The same goals prove.
* Proved 29 against 29; CPU 851 s against 960 s (**−11%**).

With e44, at `--eqhint-factor 1`, skipping every hint lookup after the
fingerprint saves 0.05 s (3.72 against 3.67 s), so lookups cost about
1%. Larger GC allocation areas are slower: by default 4.82 s, with
`-A16m` 5.21 s, with `-A64m` 5.24 s, all with the same output.

**A cost-centre profile** (`ghc-prof` installed by the user; a profiling
build with `-fprof-auto-top`, kept outside the repo). Three of the
failing goals, each with and without hints. Times are inherited
shares of the run; profiling makes it about 5× slower, with the same
search.

| goal | total s, hinted / unhinted | new pairs (`indexedOverlaps`) | `simplify`, all callers | joining selected pairs | rule model | hint renormalisation |
|---|---:|---:|---:|---:|---:|---:|
| aK2_eq_aK3_i 233 | 26.9 / 18.2 | 54% / 45% | 34%, in pair generation alone | 10% / 18% | 6% / 11% | 1.8% / 0 |
| Ka1_eq_Ka2 297 | 37.4 / 27.3 | 58% / 55% | 48% / 44% | 9% / 14% | 4% / 7% | 1.4% / 0 |
| mbol_to_nil3 371 | 24.6 / 15.8 | 58% / 52% | 46% / 39% | 8% / 15% | 3% / 8% | 2.4% / 0 |

* Most of a run goes into making the critical pairs of each new rule.
  Above all that is normalising both sides of each pair before it is
  scored and queued.
  * In the first goal's hinted run, 290,299 pairs were made in 5
    abstract s. Only 10,000 pairs are ever taken from the queue.
  * Hint matching needs these normal forms, since both hints and pairs
    are matched in normal form. So normalisation cannot simply be
    skipped.
* Hinted runs make fewer rules but more pairs, because hinted rules
  overlap more. That is the 1.7 s difference at factor 1, not the
  hints' bookkeeping.
* A `simplify` call averages 1.32 passes and about 10 rule-index
  lookups.
  * Skipping the rebuild of a term with no reducible subterm gives
    the same output on all 200 goals. It is 4.6% slower (864 against
    826 s), because the lookups are the cost, not the rebuild.
    Reverted.
  * Skipping, in later passes, the subterms an earlier pass found
    irreducible would cut about 17% of the lookups, about 6% of a
    run. Not done.

## 2av. Parental guidance (17 Nov, from 15:50)

*Notes: [notes/2026-11-19-retrained-models.md](notes/2026-11-19-retrained-models.md).*

*Notes: [notes/2026-11-19-oracle-pg.md](notes/2026-11-19-oracle-pg.md).*

*Notes: [notes/2026-11-17-pg-learned-dense.md](notes/2026-11-17-pg-learned-dense.md), [notes/2026-11-17-pg-sum-filter.md](notes/2026-11-17-pg-sum-filter.md).*

The user suggested this: the "parental guidance" of E (Goertzel,
Chvalovský, Jakubův, Olšák, Urban, *Fast and Slow Enigmas and Parental
Guidance*, FroCoS 2021, arXiv 2107.06750). A cheap model judges an
inference by its two parents, before the child is made. In E, a child
of a poor pair goes to a freezer. The freezer is emptied only when
nothing else is left, so the search stays complete. The paper's best
models are LightGBM forests on the two parents' feature vectors, side
by side. Positives are the parents of proof clauses; negatives are
sampled at about 8 to 1. They solved 11.7% more on the holdout set.

**Why it fits twee.** The profile (2au) puts 52–58% of a run in making
each new rule's critical pairs, mostly normalising them, to score and
queue about 290,000 pairs, of which 10,000 are ever selected. A pair
twee does not make costs nothing.

**In twee (e47–e50, branch `hints`).**
* `--pg-threshold P` makes no critical pairs of a new rule with an
  active when the pair's probability is below P. Since e51 the check
  comes, as in E, after the overlap is found and before it is
  simplified, once per partner (e47–e50 checked before unification;
  the same pairs are made). The probability is, by default,
  sigmoid(q1 + q2), where q is the rule model's raw score of the pair
  each rule came from. Rules without a score (axioms, rules re-added by
  interreduction, rules of a loaded state) are always paired.
* The freezer: each decision depends only on two stored scores, so the
  skipped pairs need no list. When the queue empties, twee makes them
  all, each active with itself and its older partners, and turns the
  filter off. A second empty queue is then saturation as before.
  * A small satisfiable problem at P = 0.999 emptied the freezer once
    and ended "Satisfiable" with the same 16 rules as without it.
* `--pg-model FILE` replaces the sum by a learned additive forest (see
  below).
* `--pg-log` traces each rule (id, parents, score, features, canonical
  form), each new rule's pairs per partner, and the proof's lemmas.
* With the flags off, the output is identical to e44 on all 200
  captured runs.
* Abstract time counts pairs *selected*, so the filter does not lengthen
  a run in abstract time. It changes which pairs are selected. Skipping
  their generation saves CPU on top.

**The sum filter on the 200 late hard goals** (5 abstract s, the loop's
exact commands; this set was picked because the current settings failed
on it, so any change tends to win a few; model tweaks gave +5):

| P | CPU s | proved | +/− against base |
|---|---:|---:|---:|
| off | 749–843 | 29 | |
| 0.047 | 715 | 40 | +12 −1 |
| 0.119 | 686 | 43 | +16 −2 |
| 0.269 | 737 | **52** | +23 −0 |
| 0.4 | 831 | 49 | +21 −1 |
| 0.6 | 960 | 48 | +21 −2 |
| 0.8 | 1,046 | 45 | +20 −4 |
| 0.95 | 1,067 | 45 | +20 −4 |

On the 29 runs proved without it, the 0.269 filter keeps 32% of the
generated overlaps and 80% of the parent pairs of the old proofs' steps
(where both parents have a score). The extra proofs are therefore new
proofs, not the old ones made cheaper.

**The learned parental model.**
* Data:
  * 20 minutes of the loop on half1 from zero (8 workers, every twee
    command captured). It proved 15,577 goals.
  * 1,500 random goals of those proved in the second half (harder ones)
    re-run with `--pg-log`.
  * Train on 1,300 runs (2,963 positive pairs, 8 negatives each);
    test on 200 held-out runs with all their 3 million pairs.
* Features per rule (`pgRuleFeatures`), fixed when the rule is added:
  raw score, lhs and rhs size, number of variables, depth, hint match
  (none, tracked, already matched, new), orientation, id, the queue
  score of its pair, number of actives.
* A full forest on both rules' features, side by side, was good. But
  in twee it cost about 3 s of a 2.3 s run. The cause is about 25 µs
  per evaluation of a 100-tree forest. (I first blamed "about 840,000
  candidate partners" judged before unification; that was an
  unmeasured estimate, and after the move to the paper's placement,
  e51, the cost was the same.)
* An *additive* forest is as good offline. Interaction constraints put
  each tree on the new rule's features or on the partner's. Twee then
  scores each rule once in both roles and adds two numbers per pair.

| filter | test2, at 95 / 90 / 85% of proof pairs kept: share of overlaps kept | hard 29 runs, same |
|---|---|---|
| full forest, 100 trees | 22.0 / 10.8 / 7.4% | 46.5 / 26.1 / 15.4% |
| additive forest, 100 trees | 19.2 / 11.1 / 7.6% | 45.4 / 30.0 / 16.4% |
| sum of scores | 50.7 / 36.1 / 30.0% | 62.8 / 48.6 / 39.5% |

The most useful features are the two rules' queue scores, their lhs
sizes and their raw scores. In twee, the additive model at a near-zero
threshold costs 10% of a run (2.79 against 2.53 s); at 0.05 that run
took 1.23 s.

**Running now** (from 16:54): the half1 2-hour A/B, PGA (sum filter at
0.25) against PGB (the new defaults), 6 workers each. Measured with
abs/setcurve.py: PGA 11,467 / 18,529 / 18,912 at 10 / 60 / 100
minutes, PGB 10,061 / 17,608 / 18,316 ([notes/2026-11-17-pg-ab-half1.md](notes/2026-11-17-pg-ab-half1.md)).
An earlier "9,458 against 8,986 at 10 minutes" was read before minute
10. **At 2 hours: PGA 18,987, PGB 18,410 (+577, three times the noise
of identical runs).** The gain is front-loaded (+1,406 at 10 minutes)
and flat over the last 20 minutes. PG at 0.25 is solve_new.sh's
default from 19:00 (`PG=` turns it off).

**Pcat models as in the paper, online (pgtest6, 19:06).** Full forests
on hashed ENIGMA vectors (named features on the goal-expanded rule,
1,024 buckets) prove 36 (ENIGMA only) and 39 (with the 20 numbers) of
the 200, against 52 for the sum filter, at the same abstract budget and
5–6 times the CPU. Offline they kept 93.5–97.5% of the proof pairs
against the sum's 84.1%. As with the dense models, offline ranking on
the old proofs' pairs does not predict the online result
([notes/2026-11-17-pg-pcat-enigma.md](notes/2026-11-17-pg-pcat-enigma.md)). The additive forms (pgtest7,
19:12) cost what the sum costs and prove 36–38 (each −16 or −17 against
the sum). So every learned parental model tried, dense or ENIGMA, full
or additive, has lost to the untrained sum filter. The sum stays. The additive model is under test on the 200 goals.

**The near-oracle through PG (exp33, 19 Nov 16:44-18:22; [notes/2026-11-19-oracle-pg.md](notes/2026-11-19-oracle-pg.md)).** On the 400
ultest goals at 20 s, with PG 0.25 in both arms, rmO (trained on these goals' own logs) proves 307 against rm4t's
317 (+8 −18), with 9% more CPU on shared proofs. PG and today's binary lift rm4t from 15 Nov's 271 to 317 on the same
goals. A better rule model does not raise the count at either hook. But it proves 8 goals rm4t does not (union 325):
model diversity is complementary. rmO cannot be deployed (trained on these goals' logs), so the members are other
models (m4b@0 and m7t@0 since 10:20, both kept). Still unchecked: a threshold matched to rm4t's freeze rate (rmO's raw
scores are spread differently).

**Retrained rule models with the papers' sampling tricks (exp37, 19 Nov 19:50-; [notes/2026-11-19-retrained-models.md](notes/2026-11-19-retrained-models.md)).**
The user asked for retrained members with subsampling, and for the tricks of the ENIGMA, Mizar60 and related papers.
* **The papers' tricks.** Mizar60 caps the proofs per problem (up to 6 random, or the shortest, a medium and the
  longest). It also trains several models with different hyperparameters and covers with the best set.
  ENIGMA Anonymous and Hammering Mizar found much bigger trees paid. Suda (CADE 2021) weighs every run equally,
  half on positives and half on negatives. Only compatible strategies are mixed.
* **The data.** Production keeps one proof per goal, but about 100 earlier loops kept theirs too: 643,782 logs
  over 47,482 goals, most of them easy. The median goal's shortest proof has 4 positives.
* **The test.** The 400 newest production proofs are held out of every model. They are replayed as of each proof
  (exp/modelreplay.py) at 20 s with PG 0.25. A single snapshot without all 400 broke their sibling chains: the
  control proved 2 of 126.
* **Offline AUC on the 400:**

| model | AUC |
|---|---:|
| rm4t | 0.835 |
| production's logs, as rm7t (rm9a) | 0.876 |
| 3 shortest proofs per goal over all loops (rm9b) | 0.740 |
| 2 longest (rm9e) | 0.854 |
| rm9a's data + Suda's weighting (rm9f) | 0.892 |
| rm9a's data + 255 leaves (rm9g) | 0.886 |
| 2 longest + weighting (rm9h) | 0.891 |
| weighting + 255 leaves (rm9i) | 0.900 |

  Short proofs of easy goals hurt, long ones help, and weighting and bigger trees help most.
* **Replayed, fresh 20 s each (final, 20 Nov 02:12):** rm4t 202 of 400; the weighted models 203-204 (rm9f +16 −14,
  rm9h +14 −13, rm9i +17 −15); the unweighted ones 181-187. **The union of all arms proves 226 (+12%).**
  * Greedy cover: rm9f 204, rm4t +14, rm9e +5, rm9h +2, rm9a +1.
  * The weighting is what makes retraining pay, and the models are complementary.
  * Shifting a model's scores so it prunes as much as rm4t hurt or did nothing (e.g. rm9a 4 gained, 29 lost on 274),
    so the gain is in the ranking.
  * **Time-matched control (final, 20 Nov 07:20):** rm4t at 40 s proves 225 of 400 in 5.09 CPU h, against 218 for
    rm4t and rm9f at 20 s each in 5.08 h; 14 goals only at 40 s, 7 only by the pair, 232 by all three. Twice the
    time for one model beats two models by 7, about the noise, and each side has goals of its own.
* Members: m9a@0 since 20:30 (ul71); m9f@0 and m9h@0 since 23:30 (ul72); m9e@0 since 02:17 (ul73), in place of m9i@0,
  which added nothing beyond rm9f.
  m10f@0 (rm9f's recipe on all data, 4.97 M rows from 22,158 logs) since 20 Nov 04:15 (ul74), in place of m9f@0.
* **Production's burst** (783 proofs 22:20-02:13) was the transfer loop. One L1 proof (aK2_eq_aK3_1243b 506, chain
  hints) and its siblings had steps that were unsolved goals of 22 other originals. Those then started sibling chains
  of their own.

## 2aw. Expanded proofs, deep runs and a lattice with small steps (17 Nov, from 19:00)

Three of the user's questions, one experiment each. The records are in [notes/2026-11-17-expanded-proofs.md](notes/2026-11-17-expanded-proofs.md),
[notes/2026-11-17-deep-runs-expanded-chains.md](notes/2026-11-17-deep-runs-expanded-chains.md) and [notes/2026-11-17-lattice-construction.md](notes/2026-11-17-lattice-construction.md). Scripts are exp/exp1_* to exp/exp4_*.

**Expanded proofs (exp1, exp2).** Veroff expands lemma-based proofs back to the axioms for more hints.
expand.py closes each proof under the proofs of the lemmas it used. On 200 sampled goals the closures have a
median of 817 proven goals, 15 levels deep, and 4,134 distinct hints.
* From the axioms alone at 20 s, the expansion proves 18 of 200. Without hints the runs prove 6, with the
  goal's own lemma-based proof steps 10, and with the original's whole pool 9. So expansion is worth twice the
  pool, as Veroff says.
* In production's setting (lemmas as axioms, the pool as hints) the extras are mostly redundant: 51 → 47 at
  5 s, and 86 → 90 at 20 s (+7 −3). Not adopted.

**Deep runs on late goals (exp3).** Veroff's question: can hints guide a search from the axioms to a late goal,
with the rate of hint matches as the signal to stop or go on? Arms:
* C: production's command;
* K: lemmas with the expanded chain of the 10 nearest proven siblings as the only hints;
* E: the pool plus that chain;
* V: from the axioms with the chain.

47 late goals no loop has proved, 320 abstract s each, deterministic pick (exp/sets/exp3_goals47). Interim
(68 of 188 runs):
* the first proofs are new to the benchmark: R1dist_to_aa1 619, aK2_eq_aK3_q 252, aK2_eq_aK3_t 369 and 372;
* V, from the axioms, proved aK2_eq_aK3_q 211, which no other arm proved, and proved 372 with the fewest pairs;
* unproved runs still find new hint matches at the end (median 313–317 s), so a stall rule would stop none of
  them early. A stall limit of 40 abstract s keeps every proof and saves about 5% of the work.
* 29% of the chain's siblings lack a record of their used lemmas. These are older proofs and transfer proofs, so
  the chains have holes.

**A lattice with small steps (exp4).** The user: if the assumptions that help are as hard as the target, there
is no lattice with reasonable steps, so build one. Moves follow Korovin and Hernandez (IJCAR 2018):
* signature grouping and argument filtering;
* loop laws;
* weaker goals (instances of the goal);
* generalisations of the goal;
* subgoals by decomposing the goal's normal forms (twee-e56 --print-goal-nf).

Mace4 screens out moves that collapse the theory or force a group, and conjectures with a countermodel in T.
Results on the 47 goals:
* weaker goals: in every goal some instance proves within 5 s (178 of 377; median 26 lemmas). Setting a
  variable to e proves 142 of 238, identifying two variables 36 of 139;
* strengthenings: 382 of 654 sketches prove within 5 s, in 45 goals, with proofs of median 39 lemmas, but none
  without its assumption. Almost all used instances of the assumption have countermodels in T (re-screen with
  corrected extraction running);
* on the first goal, giving only the plausible used instances proves nothing. So a sketch's route needs
  statements false in T;
* generalisations: 36 of 214 survive Mace4 and none proves in 20 s;
* decompositions of the goal's normal forms: none survives Mace4 (31 of 47 goals so far);
* the steps of the sketches as hints for the real goal at 80 s: 0 of 20 runs at the pool's factor (the sketch
  adds under 5% of hints). A boosted arm (factor 0.001) is running.

So far the cheap syntactic moves make no lattice with small, true steps around these goals. They give easy
special cases below, and false theories above.

Update (18 Nov 01:11). After fixing a fault in the instance extraction (filterings' instances had come out as
x = y), rungs appear.
* The refinement proves 16 of the 47 goals from plausible conjectures alone (47 of 186 runs).
* Proving those conjectures closes 2 goals: aa2_12 517 (conjecture in 21 s, goal from it in 1.6 s) and
  nil3_30 508 (conjecture at 80 s, goal from it in 1 s).
* Neither is new. exp3's K and E arms proved 517 in about 17 s, and production proved 508 itself at 00:15.
* The open rung conjectures are being climbed recursively (ladder.py).

## 2ax. Hangs, Prover9's subsumption matching, and chain hints (18 Nov, from 04:00)

*Notes: [notes/2026-11-18-chain-transfer-records.md](notes/2026-11-18-chain-transfer-records.md).*

Records: [notes/2026-11-18-ground-joining-hangs.md](notes/2026-11-18-ground-joining-hangs.md) (exp6), [notes/2026-11-18-subsumption-matching.md](notes/2026-11-18-subsumption-matching.md) (exp7),
[notes/2026-11-18-chain-hints-unsolved.md](notes/2026-11-18-chain-hints-unsolved.md) (exp8), [notes/2026-11-18-chain-hints-short.md](notes/2026-11-18-chain-hints-short.md) (exp9); [notes/2026-11-17-long-runs-late-goals.md](notes/2026-11-17-long-runs-late-goals.md) (exp5),
[notes/2026-11-17-deep-runs-expanded-chains.md](notes/2026-11-17-deep-runs-expanded-chains.md) (exp3) and [notes/2026-11-17-lattice-construction.md](notes/2026-11-17-lattice-construction.md) (exp4).

**Runs that ignored their limits.** Some twee runs went on for hours past --max-time and --max-cpu (up to 8.7
CPU h for a 320 s run).
* twee checks its limits only between main-loop steps, and one step never ended. Ground joinability
  (Join.hs, groundJoinFrom) splits on cases and adds a model's literals to the case context at each split. With
  permutation laws over many variables that context grows without bound (44,992 literals in one dump).
* twee-e57 adds `--ground-joining-branch-limit B`: past B literals the pair counts as not ground-joinable and is
  kept, as when the existing tick limit runs out.
* With B = 100, on the PG testbed's 200 hard goals at 20 s: the same 87 proofs with identical pair counts on all
  87. All 5 known hangs now end, at 1,054–3,930 CPU s; none of them proves.
* A watchdog (abs/cpuwatch.py) kills experiment runs at 1.5 × their CPU cap + 60 s.
* On the way I found a 10% slowdown from e51 (the parental filter judged after unification). twee-e61 judges it
  before again, using e50's strict set, and its output is byte-identical to e50's.
* **Production since 07:30** is abs/ul42.sh: twee-e61 with the branch limit 100.

**Hint matching by subsumption (the user: "in P9 the hint matchers subsume the hints").** twee boosted a pair
only when it was a variant of a hint. twee-e58/e59 `--eqhint-subsume` also boosts a pair that subsumes a hint,
using an index of hint forms by top symbols to depth 1.
* On the 200 hard goals at 20 s: 87 against 87 (+2 −2), with pairs to proof about equal (873k against 878k) and
  17% more CPU. Neutral, so it stays off.
* A likely reason: a pair more general than a hint is smaller than the hint, so twee's size weight already
  ranks it well.

**Deep runs on late goals (exp3, 320 s, 47 goals; complete 09:30).**
* Proved: K (lemmas + the expanded chain of the 10 nearest proven siblings as the only hints) 12 of 47 in
  15.3 CPU h. E (pool + chain) 10 of 47 in 16.7 h. C (production's command) 9 of 47 in 20.7 h. V (axioms + chain)
  4 of 47 in 42.8 h.
* Every goal C proved K proved too, plus three more, with 26% less CPU. The last new one (nsmr_to_aa1 624) was
  merged at 09:30.
* The 10 proofs that UL lacked were merged at 07:09.
* **What that set off.** UL had gained 1–4 proofs an hour from 02:00 to 07:00. Between 07:10 and 08:20 it gained
  152, all from 5 s runs of goals that had failed at 5 s two to eight times.
  * 13 of the 152 descend from merged proofs through their lemma records (nil3_27 472 opened nil3_27 462–477,
    aK2_eq_aK3_t 372 opened 368 and 373).
  * 72 use a new proof of their own original.
  * Other chains started with no merged ancestor, and the 07:30 restart overlaps the rest.
  * So a deep proof at a stalled place can open a run of cheap proofs around it, in both directions.

**Longer is not the answer (exp5).** 15 late goals at 640 s (1.28M pairs each): 0 proved, 1,234–3,785 CPU s and
2.2–4.1 GB each.

**The lattice (exp4), continued.**
* The open rung conjectures at 320 s: 0 of 20 proved, so they are not easier than their goals.
* The conjecturer's rungs: 6 of 49 proved at 20 s, then 1 of 4 at 320 s. That closes aK2_eq_aK3_q 252 through
  its refinement proof, which is not new (exp3's C and K proved it directly).

**Chain hints in production (in progress).**
* `loop.py --chain-level L` (with `--chain-sibs`, `--chain-max`, `--chain-records`) gives levels ≥ L the
  goal's chain as hints instead of the pool. The chain comes from hints/sibchain.py over a records file of all 16
  loops (39,554 records); new proofs' records are added live.
* A resumed state takes new hints only for new pairs (`--no-resume-requeue`). I took production's 80 s level
  for a fresh run. **It is not** (found 11:55): it resumes the 5 s run's state, so under ul43/ul44 the chain
  reached only pairs made after 5 s, and the queue kept its pool scores. loop.py now runs the chain level fresh
  (ul45).
* exp8 tests that budget, chain against pool at 80 s on 78 stalled goals: **chain 9, pool 5 (+6 −2)**, CPU +10%.
  With exp3 the chain wins at both deep budgets, so production uses it from 08:28 (ul43; ul44 at -j 8 from 09:23).
* On exp6's stalled goals the branch limit changes nothing (5 = 5, identical pairs; no hang without it).
* Filling chain holes with transfer sources (exp10, same 78 goals): 7 against 9 (+1 −3), more pairs and +9% CPU.
  A bigger chain is not a better one; off.
* exp9 tests the short levels on 199 frontier goals: at 5 s, 0 against 0 (chain +20% CPU); at 20 s pool 3, chain 2
  (+0 −1), and the chain needs more pairs where both prove. So the chain stays out of the 5 s level.

## 2ay. The hard tail: walls, gap heads, and where production's proofs come from (18 Nov, from 10:30)

*Notes: [notes/2026-11-18-chain-size.md](notes/2026-11-18-chain-size.md), [notes/2026-11-18-knn60-walls.md](notes/2026-11-18-knn60-walls.md), [notes/2026-11-18-prover9-chain-walls.md](notes/2026-11-18-prover9-chain-walls.md), [notes/2026-11-18-set-join-walls.md](notes/2026-11-18-set-join-walls.md), [notes/2026-11-18-subsumption-deep.md](notes/2026-11-18-subsumption-deep.md), [notes/2026-11-18-two-sided-chain.md](notes/2026-11-18-two-sided-chain.md), [notes/2026-11-18-unfolded-walls.md](notes/2026-11-18-unfolded-walls.md).*

**Walls (exp11, [notes/2026-11-18-wall-breaking.md](notes/2026-11-18-wall-breaking.md)).** Each original's first unsolved goal at 10:29 (107), with
the below-only chain at 80 s: **15 of 107 proved, 4.8 CPU h, 3.1 proofs per CPU hour.** Production's pool runs
had failed on all 107 at 80 s and on 86 at 320 s. But nearly all walls are isolated holes, so their proofs open
nothing, except through the transfer: Ka1_eq_Ka2 400, merged at 10:48, gave aKperms_1 344 (another original)
at 10:53.

**Gap structure (11:21).** A gap is a maximal run of consecutive unsolved goals of an original. There are 812:
* by length, 338 of 1, 228 of 2-4, 150 of 5-19, 92 of 20-99 and 4 of 100+;
* the 96 gaps of 20 or more hold 4,045 of the 6,370 unsolved goals;
* 83 of those 96 reach the original's top goal.

**Gap heads (exp12, [notes/2026-11-18-gap-heads.md](notes/2026-11-18-gap-heads.md)).** These are the first goals of the 96 long gaps, with the
chain at 80 s.
* Stage A: **1 of 96, 6.3 CPU h.** Most runs used the full 160,000 pairs.
* But the one proof paid. aK2_eq_aK3_b 421 heads a gap of 40 and was merged at 12:12. Production then proved 422,
  426, 425 and 435 in 3.3-4.9 s each, then 423 and 424 (UL rows 45,504-45,514), all within about an hour. That is
  **7 proofs for the one deep proof**, and 6 of production's first 20 under ul45.
* Stage B (320 s on the other 95) started at 13:31.

**Where production's proofs come from (ul45, its first 1,774 runs, 12:03-13:26).** 20 proofs in about 13 worker
hours, about 1.5 per worker hour. "Position" uses UL's state at 13:26: whether the sibling directly below is
proven (B), and whether one of the three above is (A).

| level | position | runs | proved | worker h | proofs per worker h |
|---|---|---:|---:|---:|---:|
| L0 (5 s) | B, A | 204 | 3 | 0.5 | 6.6 |
| L0 | B only | 97 | 1 | 0.2 | 4.6 |
| L0 | A only | 343 | 5 | 0.8 | 6.5 |
| L0 | neither | 1,001 | 3 | 2.3 | 1.3 |
| L1 (80 s chain) | B, A | 97 | 6 | 5.1 | 1.2 |
| L1 | B only | 32 | 2 | 1.9 | 1.1 |

The cheap retries next to a proof pay best. The 80 s chain level pays about as little as the retries inside
gaps. Some of the L0 proofs are the chain behind 421 above.

**Throughput at depth (measured 16:15, the user's question).** In pairs considered per CPU second (run.py's CPU and
pairs columns), whole runs:

| runs | n | median | p10 | p90 | CPU-capped |
|---|---:|---:|---:|---:|---:|
| 80 s, walls, folded chain (exp11) | 107 | 969 | 677 | 1,540 | 0 |
| 80 s, gap heads (exp12 A) | 95 | 842 | 417 | 1,223 | 4 |
| 80 s, walls, unfolded (exp15, first 36) | 36 | 256 | 148 | 458 | 10 |
| 320 s, gap heads (exp12 B, first 20) | 20 | 458 | 160 | 861 | 2 |
| 320 s, late goals (exp3, 4 arms) | 181 | 553 | 259 | 978 | 0 |
| 640 s, late goals (exp5) | 15 | 612 | 393 | 1,006 | 0 |

The same command at two budgets shows how much slower the later part of a run is, because twee is deterministic in
abstract time:
* **80 s → 320 s** (17 gap heads that ran to the limit in both stages): 901 pairs/s for the first 160,000 pairs and
  491 for the next 480,000. That is 1.9 times slower (the median of the per-goal ratios). So 4 times the budget
  costs 6.7 times the CPU. Peak memory goes from 677 MB to 2,282 MB.
* **320 s → 640 s** (exp5's 15 goals against their exp3 C runs): 739 pairs/s, then 528. 2 times the budget costs
  2.4 times the CPU.
* Outliers are much worse: down to 24-40 pairs/s (Ka_eq_aK3 403 hit the 3,200 s cap at 128,524 pairs).
* Unfolded problems run at a quarter of the folded speed.

So the 9-fold slowdown of 14 Nov (2v: 3.0 → 26 CPU s per abstract s by 130 abstract s, fixed by the overlap index
and the interreduction filter) is gone. But the population is not flat, as the single goal in 2v suggested: the
later pairs of a 320 s run cost about twice the early ones. Candidates: queue renormalisation (2v: about +25%),
GC on a heap 3-4 times larger, and per-pair costs that grow with the rule set (rule model, PG, hint lookups). A
`--progress` profile of one 320 s head would tell them apart.

**The wall study (16:50).** Settings for deep runs on hard holes, all on exp11's 107 walls with exp11's
commands, so exp11 is an exact control (twee is deterministic in abstract time: exp14's 7 unchanged walls
reproduced exactly).

| variant (80 s unless noted) | proved | against exp11 | new to UL | CPU h | note |
|---|---:|---|---:|---:|---|
| exp11: below-only chain (control) | 15 | | 15 | 4.8 | |
| exp14: two-sided chain | 16 | +4 −3 | 4 | 5.7 | −15% pairs where both prove |
| exp18: subsumption matching (the user's point) | 13 | +3 −5 | 2 | 7.9 | −21% pairs where both prove (−0.6% at 20 s, exp7), +63% CPU |
| exp16: Prover9 + chain, 60 s | 4 | 3 twee failed | 3 | 1.8 | Prover9 + pool: 2 (1 new) |
| exp15: unfolded definitions | running | | 1 so far | | about 4 times slower per pair |
| exp17: 60 kNN lemmas | running | | | | |
| exp19: --set-join (Waldmeister 4.3) | running | | | | |

* No variant so far beats the control in count.
* But each proves 2-4 walls that every other run failed. Twee's search is chaotic, so a change of setting
  re-randomises which hard goals fall. As a **portfolio on stalled holes** that is worth about 0.5-1 new proof
  per CPU hour, and **Prover9 with the chain is the cheapest member (2.3 per CPU hour)**. *(20 Nov: void. 9 of P9C's
  10 proofs and all 6 of exp16's used a false axiom from p9twee.py's negation bug;
  [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md).)*
* So from 16:46 a Prover9 side worker with chain hints (abs/p9c.sh, 2 workers) runs on twee's stalled goals,
  writing its proofs into UL.
* The Waldmeister paper (the user, 16:24; [notes/2026-11-18-waldmeister-paper.md](notes/2026-11-18-waldmeister-paper.md)): twee already has most of its
  techniques. The one it lacks (ground-joined equations kept for rewriting) cannot matter here: 29 ground-joined
  equations against 20,751 rules in an 80 s run. --set-join is exp19.

**Running (13:32):**
* chain size (exp13);
* two-sided chains on the walls (exp14);
* unfolded definitions with chain hints on the walls (exp15, from about 14:30);
* exp12 stage B.

## 2az. Portfolios: complementary methods kept, not dropped (user's request, 18 Nov 17:00)

*Notes: [notes/2026-11-22-cp-weights.md](notes/2026-11-22-cp-weights.md).*

*Notes: [notes/2026-11-22-knn-drift.md](notes/2026-11-22-knn-drift.md).*

*Notes: [notes/2026-11-22-ul75.md](notes/2026-11-22-ul75.md).*

*Notes: [notes/2026-11-22-late-ab.md](notes/2026-11-22-late-ab.md).*

*Notes: [notes/2026-11-22-z8.md](notes/2026-11-22-z8.md).*

*Notes: [notes/2026-11-21-renorm-zero.md](notes/2026-11-21-renorm-zero.md).*

*Notes: [notes/2026-11-21-floor-ratio.md](notes/2026-11-21-floor-ratio.md).*

*Notes: [notes/2026-11-21-z7-pair.md](notes/2026-11-21-z7-pair.md).*

*Notes: [notes/2026-11-21-head-time.md](notes/2026-11-21-head-time.md).*

*Notes: [notes/2026-11-21-retry-time.md](notes/2026-11-21-retry-time.md).*

*Notes: [notes/2026-11-21-quick-first.md](notes/2026-11-21-quick-first.md).*

*Notes: [notes/2026-11-21-late-combo.md](notes/2026-11-21-late-combo.md).*

*Notes: [notes/2026-11-21-head-class.md](notes/2026-11-21-head-class.md).*

*Notes: [notes/2026-11-21-knn-ctx.md](notes/2026-11-21-knn-ctx.md).*

*Notes: [notes/2026-11-21-roots.md](notes/2026-11-21-roots.md).*

*Notes: [notes/2026-11-20-yield-discount.md](notes/2026-11-20-yield-discount.md).*

*Notes: [notes/2026-11-20-retry-class.md](notes/2026-11-20-retry-class.md).*

*Notes: [notes/2026-11-20-sweep20.md](notes/2026-11-20-sweep20.md), [notes/2026-11-20-z6.md](notes/2026-11-20-z6.md).*

*Notes: [notes/2026-11-20-given-nowait.md](notes/2026-11-20-given-nowait.md).*

*Notes: [notes/2026-11-20-given-cap.md](notes/2026-11-20-given-cap.md).*

*Notes: [notes/2026-11-20-model-audit.md](notes/2026-11-20-model-audit.md).*

*Notes: [notes/2026-11-20-step-join.md](notes/2026-11-20-step-join.md).*

*Notes: [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md).*

*Notes: [notes/2026-11-20-half2-given.md](notes/2026-11-20-half2-given.md).*

*Notes: [notes/2026-11-20-from-zero-given.md](notes/2026-11-20-from-zero-given.md).*

*Notes: [notes/2026-11-19-climber-member.md](notes/2026-11-19-climber-member.md).*

*Notes: [notes/2026-11-19-enigmawatch.md](notes/2026-11-19-enigmawatch.md).*

*Notes: [notes/2026-11-19-half2-replication.md](notes/2026-11-19-half2-replication.md).*

*Notes: [notes/2026-11-18-no-pg-no-model-walls.md](notes/2026-11-18-no-pg-no-model-walls.md), [notes/2026-11-19-far-goals-deep.md](notes/2026-11-19-far-goals-deep.md), [notes/2026-11-19-from-zero-explore.md](notes/2026-11-19-from-zero-explore.md), [notes/2026-11-19-queue-renorm-ab.md](notes/2026-11-19-queue-renorm-ab.md).*

The user: when a method loses 2 of the best method's proofs but adds 3 of its own, running both for a share of the
time usually beats running the best one all the time. **The record agrees.** Since 12 Nov I decided almost every A/B by
the better arm's count and called the second arm's unique proofs noise. Notes:
[notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md) (the full table), [notes/2026-11-18-time-matched-control.md](notes/2026-11-18-time-matched-control.md) (exp20), [notes/2026-11-18-l0-portfolio.md](notes/2026-11-18-l0-portfolio.md) (exp21).

**Dropped methods with a measured unique share** (best arm's count, the dropped arm's, its gains and losses
against the best, the union):

| setting | best | dropped arm | +/− | union |
|---|---:|---:|---|---:|
| rule-model settings, 345 at 8 s (2b) | 69 | 65-67 | | 93 |
| rm4b, 4 times the model (2f) | 61-63 | 65 | +9 −7 | about 72 |
| 45 frequent hints as axioms (2s) | 76 | 73 | +3 −6 | 79 |
| kNN lemma selections (2am) | 6 | 7 / 5 | +3 −2 / +1 −2 | 10 |
| 60 kNN lemmas, two tests (2am) | 19 of 450 | 17 | +4 −1, +1 −3 | 24 |
| expansion hints at 20 s (2aw) | 86 | 90 | +7 −3 | 93 |
| subsumption matching at 20 s (2ax) | 87 | 87 | +2 −2 | 89 |
| pool against chain at 80 s (exp8) | 9 | 5 | +2 | 11 |
| two-sided chain, 107 walls (exp14) | 15 | 16 | +4 −3 | 19 |
| subsumption matching, walls (exp18) | 15 | 13 | +3 −5 | 18 |
| Prover9 + chain, walls (exp16) | 15 | 4 | +3 | 18 |

Genuine negatives, where the variant proved nothing the others did not:
* the 20 s portfolio on stalled goals (2ac);
* the tail-head probes (2ag);
* `--hint-goal` (2aj);
* chain hints at 5 s on stalled goals (exp9).

**On the walls** (the 92 that exp11's 80 s chain run failed), each 80 s variant proves 3-6 of them. Per CPU hour:

| variant | new | new per CPU h |
|---|---:|---:|
| 60 kNN lemmas (exp17) | 6 | 1.27 |
| two-sided chain (exp14) | 4 | 0.76 |
| unfolded (exp15, 58 so far) | 6 | 0.61 |
| subsumption (exp18) | 3 | 0.42 |

Greedily by new proofs per CPU hour, the union grows:
* the twee chain: 15 at 4.8 CPU h;
* then Prover9 + chain: 18 at 6.6 h;
* then Prover9 + pool: 19 at 8.3 h;
* then the two-sided chain: 22 at 14.0 h;
* then subsumption: 24 at 21.9 h;
* then unfolded and 60 kNN lemmas: about 30.

The time-matched control is pending: exp20, exp11's command at 160 s on the 92.

**Production at 17:12** (UL r5 since 12:02):
* the 5 s fresh level made 11.3 proofs per CPU hour;
* the 80 s chain level 1.16;
* the 320 s level never ran (the deep class had about one worker).

So a variant competes with the far retries and the chain level (about 1 per worker-hour each), not with a deeper
level.

**Deployed (17:13): variant levels.**
* loop.py `--variants` inserts levels of the chain level's budget after it. Each is a fresh run in the same context
  with one change, keeps no state, and is labelled V<name> in results.tsv.
* The deep queue goes breadth first: every waiting goal gets the first variant before any gets the second.
* Production **ul47** = ul46 + `--variants k60,two,unf,sub`, in the order of the wall yields. The Prover9 + chain
  side worker (P9C) keeps running beside it.

**The cheap level (exp21, 18:25).** 9 arms at 5 s on 300 goals whose 5 s fresh run had failed:

| arm | proved of 300 | new per CPU h |
|---|---:|---:|
| **unfolded definitions** | **4** | **3.8** |
| 60 kNN lemmas | 1 | 1.9 |
| control, rule threshold 0.2, no rule model, no PG, subsumption, chain hints, Prover9 at 8 s | 0 each | |

* Changing the search does nothing at 5 s where the same problem just failed. Changing the problem (unfolding)
  does, at three times the 80 s chain level's yield.

**The ratio rule.**
* Independent attempts are best tried in decreasing order of success chance over cost. Here that is each member's
  new proofs per CPU hour on the goals every earlier member failed in the same context.
* Measured order:
  * fresh retry in a new context: 11.3;
  * unfolded at 5 s: 3.8;
  * Prover9 + chain: 2.0 (on the walls; 1.44 live);
  * 60 kNN lemmas at 5 s: 1.9;
  * 60 kNN lemmas at 80 s: 1.24;
  * the 80 s chain: 1.16;
  * two-sided chain: 0.76;
  * unfolded at 80 s: 0.49;
  * subsumption: 0.42;
  * set-join: 0.31;
  * 320 s on gap heads: 0.21.
* Extending the chain run from 80 to 160 s (exp20, on the increment) is about 1.4 on its first 22 walls.

**ul48 (18:30)**, on 6 workers:
* `--variants unf@0,k60@0,k60,two,unf,sub --ratio-order`.
* Every goal whose fresh run failed, near the frontier or not, gets the unfolded and the 60-lemma 5 s runs.
* The deep queue is ordered by each goal's next level's yield: measured priors, updated online.
* Weak members were paused to make room: exp12's 320 s heads (0.21) and exp19's set-join (0.31). Prover9 + chain
  went from 2 to 4 workers.

**The time-matched control (exp20, complete 20:13).** Each of the 92 failed walls got the 80 s chain resumed to 160 s.
* **12 new, at 1.77 per CPU hour on the increment.** That is more than any 80 s variant gives from the same CPU: the
  best, 60 kNN lemmas, gives 6 at 1.24.
* **The variants stay complementary to it.** Their yields conditional on the 160 s run failing, in this order:

| member after the 160 s run | runs | new | conditional per CPU h |
|---|---:|---:|---:|
| 60 kNN lemmas | 80 | 5 | 1.19 |
| two-sided chain | 75 | 1 | 0.23 |
| unfolded | 74 | 6 | 0.47 |
| subsumption | 68 | 0 | 0 |
| no PG (exp22) | 68 | 0 | 0 |

* The union is 24 of 92 at 37 CPU h, twice the 160 s run alone. After the longer run, subsumption and no PG prove
  nothing new in this sample. That makes them real negatives in this position, though not alone: subsumption 3 new,
  no PG 2.
* exp22's no-PG arm alone: 2 new of 92 at 0.43 per CPU hour, 1 after the 80 s variants.

**Production.**
* **ul49 (18:53)**: an 80 -> 160 s resume level right after the chain run, then the 80 s variants
  (`--variants-after 2`, loop.py baa52c7), and `--pass-every 1`. new=8 in 43 min on 6 workers.
* **ul50 (19:38)**: 10 workers, with no PG as the last 80 s variant. Prover9 + chain stopped: 1 proof in 217 runs on
  4 workers since 18:26, 0.28 per CPU hour. Its nearest-first order took the best candidates early. new=7 in 36 min.
* **ul51 (20:15)**: 16 workers, using exp20's 4 CPUs. The 80 s variants are k60, unf, two; sub and nopg are
  dropped. The priors are the conditional yields above.
* **The unfolded 5 s level, live:** 3 of 390 runs from 18:30 to 19:20, 2.15 per CPU hour. All 3 came in the first
  142 runs, because the queue takes the goals nearest a proof first. Its online estimate follows the decline.

**A throughput bug (20:25).**
* ul51 had 15 runs in flight on 16 workers but only 1-3 twee processes.
* Each unfolded run unfolded its 20-30k hints in Python, 5-6 s a run, and the worker threads did that serially under
  the GIL. ul48-ul50 had the same limit on fewer workers.
* Unfolded hints are now memoised per definition set (loop.py a5949d1). A second goal of an original takes 0.02 s
  instead of 3.5 s.
* **ul53 (20:34-21:35, 16 workers) then made 56 new in an hour**, against 10-14 an hour before. 53 of them came in
  the first 46 minutes, mostly from the 5 s levels' backlog:
  * L0: 24 in 1476 runs, 6.1 per CPU hour;
  * unfolded 5 s: 29 in 2057 runs, 4.0 per CPU hour.

**Prover9 + chain back in, as a cascade level (20:38).**
* I had stopped the P9C side worker at 19:38 on its last 217 runs (1 proof): a drop of the kind under review.
* Split by what the goals had failed in production, its 487 live runs gave:
  * 4 proofs in 350 runs on goals that had failed the 160 or 320 s level, about 0.7 per CPU hour;
  * 6 proofs in 121 runs on goals that had failed only 80 s.
* Its decline came from an exhausted nearest-first list. It is now `--variants p9` (loop.py bc450f8): Prover9 at 60 s
  with the level's chain hints and 6 siblings either side, once per goal and context, after k60.

**No rule model (exp22 N80):** 4 new of the 92 walls alone (0.72 per CPU hour), and 1 after the rest. Conditional
yields on the walls in production's order:

| member | runs | new | conditional per CPU h |
|---|---:|---:|---:|
| chain to 160 s | 92 | 12 | 1.77 |
| 60 kNN lemmas | 80 | 5 | 1.19 |
| Prover9 + chain | 75 | 2 | 1.62 |
| unfolded | 73 | 5 | 0.40 |
| two-sided chain | 68 | 1 | 0.25 |
| no PG | 67 | 0 | 0 |
| no model | 67 | 1 | 0.23 |

The union is 26 of 92. **ul54 (21:35)** has 19 workers and adds `nom` as the last 80 s variant before 320 s.

**The order within a goal (22:38).**
* The ratio rule picked which goal ran next, but each goal's levels came in a fixed order.
* By ul54's first hour, the unfolded 5 s level was used up (4 in 3064 runs, 0.39 per CPU hour). The 60-lemma 5 s
  level behind it was paying 5.5 (14 in 1588). Every goal still had to pass the first to reach the second.
* **Now the variants after one cascade level form a tier** (loop.py a0a4486). A goal tries them by current yield,
  each once per context, and the restart replay records which it has tried.
* That is the decreasing-p/c order within each goal as well as across goals. ul55 (22:39) started on the 60-lemma
  5 s level, with 4 new in its first minute.
* ul54 made 37 new in 63 minutes.
* **ul55's first hour made 146 new** (23:40), the best production hour so far. L0 paid 17.5 per CPU hour, mostly
  on goals reopened by new sibling proofs. The 60-lemma 5 s level fell from 5.5 to 1.3, and the unfolded one rose
  from 0.4 to 6.2 on the goals that reach it now. The tiers followed both changes.

**Optional attempts and context-exact restarts (19 Nov 00:00, loop.py 119c3d1, production ul56).**
* Tiers still made a goal try every variant after a level before its next level. Now a goal's next attempt is its
  eligible option of highest live yield: the next cascade level, or any untried variant after a level it ran. Only the
  resume chain is ordered.
* Results rows record their run's context (`c=`). A restart replays only rows of the current context, and starts a
  goal's attempts over at each fresh run. Before this, 892 unsolved goals reopened by new proofs had lost their deeper
  levels at each restart.
* No 5 s search-setting variants were added. exp21 found 0 of 300 for each on unchanged contexts; only the
  problem-changing ones (unfolding, more lemmas) pay at 5 s.
* ul55 ended at new=184 in 80 minutes.
* **ul56 made 233 new in its first 3 h 50 min** (to 03:50 on 19 Nov). After the first hour the 5 s levels
  paid little and the 80 s chain level ran on most workers at **1.61 per CPU hour** (40 of 380, above its 1.16
  prior). One deep proof reopens its neighbours, and their 5 s runs prove more (a burst of 31 in a few minutes at
  about 03:15).

**Two restart bugs and the far goals (19 Nov 03:50-04:08; loop.py 2b5d7d8, 5f8fd4a).**
* At a restart `--retry-hints` compared a goal's last fresh run with its original's latest run, which could be a deep
  run whose hints= counts its chain, not the pool. The pool then looked grown, and the goal repeated its fresh run,
  5 s variants and deep levels in an unchanged context, failing them again identically. ul45-ul48 flagged 265 to
  3,142 goals this way; a restart now would have flagged 2,553 of 5,583. Fixed: both sizes from fresh rows only.
* Deep runs dispatched in the first moment after a start got the original's pool, as the chain records were still
  loading. Fixed: they wait for the records.
* 4,176 of the 5,588 unsolved goals are far from the frontier, and production never deepens them (3,683 never had
  a run over 30 CPU s). By the portfolio rule that member has to be measured before it is left out: exp24 runs
  production's 80 s chain level on 40 of them. `--far-deep K` lets far goals take levels 1..K with their own
  yield (`L1f`), for the ratio rule to rank.
* Prover9 with Veroff's own AIM settings (KBO, no back-demodulation, restrict_denials, para_from_small,
  max_weight 5) and chain hints proved 0 of the 107 walls (exp23), where the defaults prove 4. Strict hint
  following needs the goal's own earlier hints, as in Veroff's loops, not its siblings'.
* **exp24: far goals do not pay at 80 s.** 0 of 40 in 2.9 CPU hours, against about 4.7 due at the near goals' rate
  (1.61). `--far-deep` stays off; a far goal is reached when its neighbour below is proved.

**Where a deep run's CPU goes (19 Nov 05:11-05:49; [notes/2026-11-19-hint-cost.md](notes/2026-11-19-hint-cost.md)).**
* The same 20 abstract s cost 36.1 CPU s with 7,668 chain hints and 19.3 s without. A cost-centre profile puts the
  hints' own bookkeeping at about 7%. The rest is the search: the hinted run makes twice the critical pairs for the
  same pairs considered, and renormalising the queue takes 27% of it.
* Under `--abstract-time` queue renormalisation is free in abstract time, so its 5% budget never binds. At 20 s
  turning it off changed nothing in the output. At 80 s (exp25, 6 walls) it saved 25% of the CPU (613 against
  823 s) with no higher peak memory, but the search differs (it kept 2 of the 3 proofs).
* **exp26** is an A/B test of that in production (ul57, from 05:52, loop.py `--ab-args`). Half the goals, by a hash
  of the name, run their deep levels without renormalisation. The measure is each arm's proofs per CPU hour at L1.

**A 40 s chain level (19 Nov 06:02, ul58).** ul56's 81 proofs at the 80 s chain level came at a median abstract time of
29 s: 50 within 40 s and 28 within 20 s. Twee is deterministic in abstract time, so a 40 s first level proves exactly
those 50 at about half the CPU: 1.73 per CPU hour against 1.45. The resume to 80 s then makes about 1.1 and competes
with the variants. Production now runs `--cascade 5,40,80,160,320`. Old results rows map to the levels of the same budget
(`--relabel`), and the variants stay at 80 s.
* ul58's first hour (to 07:05): the 40 s level made 1.98 proofs per CPU hour (10 in 5.06 CPU h), above the
  predicted 1.73. ul58 made 177 new in 74 minutes.
* exp26 at that point: arm A 6 of 114 at 95 CPU s a run, arm B (no renormalisation) 4 of 97 at 76 s. B is 20%
  cheaper; the proof rates are within noise (Fisher p 0.76).
* At 5 s, renormalisation never triggers. With and without it, a 5 s hinted run allocates the same bytes and gives
  the same output. Only the deep levels can gain from B.

**Two negatives on the way (19 Nov 07:00-07:30).**
* Veroff's Prover9 settings (exp23, [notes/2026-11-19-veroff-p9-settings.md](notes/2026-11-19-veroff-p9-settings.md)). With max_weight 40 they proved 0 of
  the 107 walls at 6,437 CPU s, so did max_weight 5 (3,484 s). The default settings prove 4.
* A per-goal predictor for the deep runs. The failed 5 s run's HINTSTATS (matched share, lastmatch, maxgap,
  deferred) and the goal's distance to the nearest proof below separate L1 successes from failures with AUC
  0.4-0.7, not consistently across ul56 and ul58. Within the near goals, 0 and 1 places away both prove about 10%.
  The deep order stays by level yield.

**The system from zero (exp27, from 07:18; [notes/2026-11-19-from-zero-portfolio.md](notes/2026-11-19-from-zero-portfolio.md)).** Everything since 17 Nov was
measured on production's tail. PGC runs half1 from zero for 2 hours on 6 workers with today's deep portfolio:
* the chain levels;
* the variants;
* the ratio order;
* twee-pg61.
It is compared with PGA (17 Nov, the same script: 18,987).
* **At 2 hours: 18,917 against 18,987, neutral** (−70; identical runs differ by about 185). PGC led in the first
  hour (+237 at 10 minutes) and trailed slightly in the second.
* Its deep worker ran unfolded 5 s runs at 28 per CPU hour. PGA's ran the 20 s pool level at 30. The 40 s chain
  level ran 4 times, proving all 4, starved by the ratio order's priors.
* The tail portfolio neither helps nor hurts the first 2 hours from zero. The starvation it shows is the same
  exploration gap as production's new variants.

**From zero with exploration: +392 at 2 hours on half1, not replicated on half2 (exp29, 19 Nov 10:38-12:39;
[notes/2026-11-19-from-zero-explore.md](notes/2026-11-19-from-zero-explore.md)).** PGD is PGC plus the 5 s
lemma-count members (k100@0, k200@0, k400@0, kd@0) and `--explore 0.2` for them and the 40 s chain level.

| minutes | 10 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|
| PGA (17 Nov system) | 11,467 | 16,913 | 18,529 | 18,875 | 18,987 |
| PGC (exp27) | 11,704 | 16,980 | 18,545 | 18,834 | 18,917 |
| **PGD** | 10,314 | 16,540 | 18,713 | 19,216 | **19,309** |

* +392 against PGC and +322 against PGA, about twice the difference between identical runs (185). Early on, a
  runaway LightGBM fit (all cores, minutes 6-15) cost PGD about 1,100 runs, so the early points are biased against it.
* Only PGD proved 652 goals, only PGC 251. 485 goals were proved by neither control.
* The deep members proved 86 goals themselves: L1 10 of 17 runs, Vk100@0 17, Vk200@0 10, Vk400@0 4, Vunf@0 43. 534
  of the 652 PGD-only goals fell to fresh 5 s runs, and 429 of those 534 used a lemma (sibling or kNN) that only
  PGD had proved: cascades from PGD's extra proofs.
* **solve_new.sh's defaults are now PGD's setting** (`DEEP`, 19 Nov 12:41).
* **The half2 replication does not hold** (exp30, 12:45-14:46, both arms at once;
  [notes/2026-11-19-half2-replication.md](notes/2026-11-19-half2-replication.md)).

  | minutes | 10 | 30 | 60 | 90 | 120 |
  |---|---:|---:|---:|---:|---:|
  | P2A (17 Nov system) | 11,489 | 17,345 | 19,041 | 19,442 | **19,501** |
  | P2D (new defaults) | 11,369 | 17,397 | 18,963 | 19,323 | **19,383** |

  * −118, within the noise. Only P2D proved 295 goals, only P2A 414; the union is 19,798.
  * Deep work is about equal in both arms. P2A's 20 s pool resume made 82 proofs at 35.8 per CPU hour, 47 of them
    goals only P2A proved. P2D's 5 s members made 89 at 34 per CPU hour, 37 of them only P2D's.
  * The rest of the one-arm goals are 5 s runs that differ by chance, both ways. So half1's +392 was mostly
    5 s luck: pooled over both halves, +137 a half, below the noise of one pair.
  * The defaults stay, since they do not lose, but there is no from-zero gain to claim. The 20 s pool resume is a
    member the new defaults lack. Joining it to the 5 s members is the portfolio follow-up, with the union (+297)
    as the target.

**From zero with the derived-rule transfer: +282 at 2 hours on half1 (exp40, 20 Nov 07:06-09:06;
[notes/2026-11-20-from-zero-given.md](notes/2026-11-20-from-zero-given.md)).** PGE is PGD plus 2al's transfer:
loop.py `--given-scan` (each failed run's given rules against the unsolved goals) and givenmatch.py live (each hit,
once the loop has failed on its goal, run with the rule's ancestry as hints at 20 s, then the log's prefix at 40 s;
at most 60 goals per cycle; and the same statement proven in a stronger theory).

| minutes | 10 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|
| PGC (exp27) | 11,704 | 16,980 | 18,545 | 18,834 | 18,917 |
| PGD (control, exp29) | 10,314 | 16,540 | 18,713 | 19,216 | 19,309 |
| **PGE** | 11,695 | 17,003 | 18,849 | 19,425 | **19,591** |

* +282 against PGD, 1.5 times the noise between identical runs; exp29's +392 on half1 did not replicate on half2.
* The live loop added 2.97 CPU h of twee time to the loop's 12 and proved 614 of 901 runs. Its ancestry runs proved
  434 of 478 at 790 per CPU hour, the same-statement runs 154 of 379 at 80, the prefix runs 26 of 44 at 53.
* Its proofs add to the loop's. In the last half hour PGE's loop proved 92 (PGD 93) and the live loop 74 more on
  about 0.85 CPU h. At equal CPU (PGE near 96 minutes) the gain is about +150.
* Only PGE proved 643 goals, only PGD 368 (union 19,961). 308 of the 643 are live proofs; the rest are cascades.
* **solve_new.sh now runs it by default** (`GIVEN=1`; `GIVEN=0` gives the 19 Nov system). exp41 replicates on half2
  against P2D.

**It replicates on half2, more strongly: +769 (exp41, 20 Nov 09:16-11:17;
[notes/2026-11-20-half2-given.md](notes/2026-11-20-half2-given.md)).** P2E is solve_new.sh's new default on half2
from zero, against exp30's P2D.

| minutes | 10 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|
| P2A (exp30) | 11,489 | 17,345 | 19,041 | 19,442 | 19,501 |
| P2D (control, exp30) | 11,369 | 17,397 | 18,963 | 19,323 | 19,383 |
| **P2E (GIVEN=1)** | 11,190 | 17,182 | 19,198 | 19,977 | **20,152** |

* **Only P2E proved 941 goals, only P2D 172** (union 20,325). The live loop proved 501 in 3.05 CPU h, 352 of them
  goals P2D never proved. At P2D's last-half-hour rate (about 15 per CPU h), 3 more CPU h would give P2D about 45.
* By kind: the rule's ancestry runs made 339 proofs in 0.63 CPU h (541 per CPU h), the same-statement runs 143 in
  1.79 (80), and the prefix runs 19 in 0.63 (30).
* The 60-goal cap per cycle, shared with the same-statement runs, starved the ancestry runs: 145-192 hits were still
  pending at the end. givenmatch.py now has `--same-cap` (solve_new.sh `GIVENARGS`).

**Lifting the cap does not help: +22 (exp42, 20 Nov 11:27-13:28;
[notes/2026-11-20-given-cap.md](notes/2026-11-20-given-cap.md)).** P2F is P2E with `--cap 200 --same-cap 20`.

| minutes | 10 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|
| P2E (control) | 11,190 | 17,182 | 19,198 | 19,977 | 20,152 |
| P2F (cap 200, same 20) | 11,266 | 17,357 | 19,307 | 19,991 | 20,174 |

* Ahead by 175 at 30 minutes, within noise at 2 hours. Only P2F proved 301, only P2E 272 (union 20,454).
* The live loop proved 559 in 2.83 CPU h: ancestry 421 of 470 (612 per CPU h), same-statement 110 of 255 (76),
  prefix 28 of 49 (40).
* The cap of 200 was never reached (0-86 goals a cycle). The limit is the wait: a hit runs only after the loop has
  failed on its goal, and the extra ancestry proofs were mostly goals the loop proves anyway.

**Not waiting is worse: −180 (exp43, 20 Nov 13:28-15:29;
[notes/2026-11-20-given-nowait.md](notes/2026-11-20-given-nowait.md)).** P2G runs each hit as soon as it is found
(`--no-wait`).
* P2G had 19,994 at 2 hours, against P2F's 20,174 and P2E's 20,152. Level until 60 minutes, behind after.
* Only P2G proved 254 goals, only P2F 438.
* Its live loop proved 1,494 goals (P2F's 559), mostly ones the loop would have proved on its own soon after.
* The wait for the loop's own failure is what makes the live loop add proofs. It stays.

**The half tests understate the system (20 Nov 13:43; [notes/2026-11-20-half-gap.md](notes/2026-11-20-half-gap.md)).**
* Of the half2 goals production has and the from-zero arms lack (3,768), 2,155 fell to production's 5 s level. Their
  median goal number is 403, against 170 for the arms' goals.
* 1,363 of the 1,714 such proofs with a record used a kNN lemma from the other half. A half run cannot have it.
  Half1: 1,281 of 1,688. Only 11 (half1: 14) used lemmas all of which the arm had proved.
* So the A/B tests on halves stay fair (both arms have the same handicap), but they understate what the system
  does on the whole benchmark, and changes that act through cross-original lemmas show less on a half.
* The long from-zero run goes on all 51,784 (Z6, after exp43), against Z4's curve (37,713 at 2 h).

**Z6: today's system from zero on the whole benchmark (20 Nov from 15:31; [notes/2026-11-20-z6.md](notes/2026-11-20-z6.md)).**
12 workers, 8 hours, solve_new.sh's defaults with `--knn-refresh 600`, proofs kept.

| minutes | 10 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|
| Z4 (17 Nov system) | 15,398 | 29,765 | 35,511 | 37,328 | 37,713 |
| **Z6** | 15,802 | 31,133 | 37,378 | 39,661 | **40,238** |

| hours | 3 | 4 | 6 | 8 |
|---|---:|---:|---:|---:|
| Z4 (ended at 4) | 37,962 | 38,044 | – | – |
| **Z6** | 41,789 | 42,920 | 43,782 | **44,095** |

* +6.7% at 2 hours. Z6 reaches Z4's 2-hour count in about 62 minutes.
* It is also above the two half arms of the same system together (39,743 on 2 × 6 workers).
* **44,095 of 51,784 (85.2%) from zero in 8 hours on 12 workers**, against Z4's 38,044. Its third hour had a burst:
  goals that had failed once got a new context and proved 47% on their retry.
* Hours 4-8 added 1,175.
  * The deeper class ran only 5 s variants (unfolded, then 100 kNN lemmas).
  * The 40 s chain level ran 16 times, all in the first hour. Its cumulative yield estimate stayed below those of
    variants measured in the burst.
* **Production-only: 4,113 goals**, the far ends of the chains: production's first proofs at L0 2,068, variants
  743, L1 590, side loops about 400.
  * 1,914 of those L0 proofs used a lemma Z6 had not proved.
  * Z6 proved 2 goals production had not; both merged and trusted.
* Next (from 23:34): three half2 arms of 5 hours, a control and the two late-phase changes. The failed-before goals
  get their own class (exp44, `--retry-class`). A discounted yield estimate with re-exploration lets L1 come back
  (exp45, `--yield-discount`).

**The late phase from zero: retries, latency and heads (21 Nov, result at 5 hours 04:35; [notes/2026-11-20-retry-class.md](notes/2026-11-20-retry-class.md),
[notes/2026-11-20-yield-discount.md](notes/2026-11-20-yield-discount.md), [notes/2026-11-21-roots.md](notes/2026-11-21-roots.md),
[notes/2026-11-21-knn-ctx.md](notes/2026-11-21-knn-ctx.md), [notes/2026-11-21-head-class.md](notes/2026-11-21-head-class.md),
[notes/2026-11-21-late-combo.md](notes/2026-11-21-late-combo.md)).**
* **exp44/45:** three half2 arms from zero, 6 workers, 5 hours, 23:34-04:35 (identical runs differ by about 185 at
  2 hours).

  | arm | 60 min | 120 min | 180 min | 240 min | 300 min |
  |---|---:|---:|---:|---:|---:|
  | P2K, the control | 19,009 | 20,004 | 20,224 | 20,828 | 21,147 |
  | **P2H, `--retry-class`** | 18,745 | 20,611 | 21,355 | 21,525 | **21,597** |
  | **P2J, `--yield-discount 2000 --reexplore 12:0.25`** | 19,161 | 20,124 | 20,770 | 21,624 | **21,706** |

  * **Both options pass the +185 rule at 5 hours:** P2H +450 (+642 / −192), P2J +559 (+726 / −167). P2H against
    P2J +218 / −327; union P2H ∪ P2J 21,924, all three 21,988.
  * P2H's failed-before goals with a new context have their own --mix class. It costs 264 at 1 hour (retries at 21%
    take workers from first runs at 93%) and leads by 1,128 at 3 hours: the control's context-change retries wait
    until all first runs end, at about 150 minutes. The control catches up later (+697 at 4 hours, +450 at 5).
  * P2J's discounted estimates keep the deeper variants close, so its deep work spreads over Vk100@0, Vk200@0,
    Vk400@0, Vkd@0 and L1 (31 runs, 14 proved; the control and P2H ran L1 0 times after the first hour and spent
    their deep work on Vunf@0). Those proofs give new contexts, which its L0 retries use (414 and 402 proved in the
    half hours 150-210 minutes). It proves 425 and 328 goals from lemmas of hours 2 and 3 (P2H 307 and 40).
* **exp48:** two more half2 arms, 04:36-09:38: P2N with both options, P2O with both plus `--knn-ctx 10 --head-class`.

  | arm | 60 min | 120 min | 180 min | 240 min | 300 min |
  |---|---:|---:|---:|---:|---:|
  | P2N, both | 19,214 | 20,872 | 21,271 | 21,370 | 21,698 |
  | **P2O, both + --knn-ctx 10 --head-class** | 18,792 | 20,934 | 21,524 | 21,686 | **21,939** |

  * **Side by side, P2O +241 over P2N** (+384 / −146): the two options add to the pair.
  * **Wall minutes are not comparable across nights.** Failed plain 5 s L0 runs took 5.6-6.0 CPU s in exp44/45 and
    4.7-5.0 s in exp48. exp/abscurve.py converts each run's CPU into abstract seconds with its window's rate (the
    median failed 5 s run) and compares arms at equal abstract work. At P2J's 5 hours of work (25.1 abstract worker
    hours, reached by exp48's arms at 255 minutes): P2J 21,706, P2H 21,597, P2N 21,381, **P2O 21,706**. So the pair
    alone is 325 behind P2J, and P2O ties it.
  * P2O's lead comes from its head class: 301 L1 runs over 5 hours (P2N 34 L1 runs by 3 hours). By 3 hours, its 34
    heads proved after the first 30 minutes were followed within 30 minutes by 123 proofs of the goals after them.
    The kNN-only retries proved 48 of 274, nearly all in the first hour.
  * Default: P2O's set, the best side by side and tied at equal work. Z7 on all goals decides the late phase, since
    half2 lacks the other half's lemmas.
* **exp49/50 (09:45-12:47, on P2O's set; [notes/2026-11-21-quick-first.md](notes/2026-11-21-quick-first.md),
  [notes/2026-11-21-retry-time.md](notes/2026-11-21-retry-time.md)): both rejected, stopped at 3 hours.**
  * `--quick 1` (each goal's first run at 1 s): +975 at 15 minutes, −719 at 3 hours. A goal that failed its quick run
    waited behind every far goal's quick run.
  * `--retry-time 3` (L0 retries at 3 s): −166 at 3 hours. The retries proved 114 per CPU hour against 137.
  * With abstract time both runs are prefixes of the 5 s run, so neither can add proofs, only move them in time. No
    one-arm goal of either is new to the collection.
* **The Z7 pair (12:48-, all 51,784 goals from zero, 6 workers each; [notes/2026-11-21-z7-pair.md](notes/2026-11-21-z7-pair.md)):
  the late-phase set (solve_new.sh's LATE, default since 12:19) against the 20 Nov system, side by side.**

  | arm | 30 min | 60 min | 120 min | 180 min | 240 min |
  |---|---:|---:|---:|---:|---:|
  | Z7C, the 20 Nov system | 26,757 | 34,522 | 38,957 | 40,479 | 41,237 |
  | **Z7, LATE** | 24,561 | 32,154 | 37,195 | 40,786 | **42,478** |

  * **+1,241 at 4 hours; LATE confirmed on the whole benchmark.** Z7C was stopped at 16:49, when it proved 114 a
    half hour against Z7's 506.
  * The early cost: up to −2,368 at 1 hour. The floors of the retry and head classes held about half a worker of six
    at about 1% of a first run's yield. exp52 (`--floor-ratio`, [notes/2026-11-21-floor-ratio.md](notes/2026-11-21-floor-ratio.md))
    tests floors that wait until those classes can compete.
  * Z7 ran on alone to 8 hours: 43,767, against Z6's 44,092 on 12 workers (cross-time). It proved one goal
    production never had, merged into production.
* **exp52, floors that wait (21 Nov 20:49-23:50; [notes/2026-11-21-floor-ratio.md](notes/2026-11-21-floor-ratio.md)):
  loop.py `--floor-ratio 20` keeps the retry and head classes' one-worker floor only while 20 times their yield
  reaches the best class's.** half2 from zero, 4 workers each, side by side:

  | arm | 30 min | 60 min | 120 min | 180 min |
  |---|---:|---:|---:|---:|
  | P2T, LATE | 14,568 | 16,786 | 18,618 | 20,087 |
  | **P2U, LATE + `--floor-ratio 20`** | 15,574 | 17,696 | 19,658 | **20,876** |

  * **+789 at 3 hours (+1,040 at 2); accepted into LATE (21 Nov 23:51).** P2U spent half the control's CPU on deep
    runs for the same proofs. The floors come back by themselves when the first runs' yield falls.
  * The lead narrowed by 251 in the third hour, as P2U ran out of easy goals first; the next 8-hour run checks it.
  * Z7's late first runs prove 65% against Z7C's 20%: they come later, in a fuller context.
  * A pair, not Z7 against Z6: on a replica pair (P2R against P2O), exp/abscurve.py left 167-426 of the gap.
* **exp53, deep runs without queue renormalisation (21 Nov 23:51 to 22 Nov 02:53; [notes/2026-11-21-renorm-zero.md](notes/2026-11-21-renorm-zero.md)):
  `--cp-renormalise-threshold 1000` from zero, beside a control with the current defaults (half2, 4 workers each).**
  P2W 20,154 against P2V 20,974 at 3 hours (**−820**; −76 at 1 hour, −467 at 2). Rejected; renormalisation stays.
  * Only the 40 s runs got cheaper (11%); the 5-10 s runs, where most of the CPU goes, cost the same.
  * The loss is in first runs after the first hour, goals whose hints come from proofs found earlier.
  * P2W-only 113 for its 12 worker-hours: not a portfolio member. The control matched exp52's P2U within 105.
* **Z8, the defaults with `--floor-ratio 20` from zero on all goals (22 Nov 02:53-08:55, 6 workers;
  [notes/2026-11-22-z8.md](notes/2026-11-22-z8.md)), against Z7's curve (LATE without it, 21 Nov; cross-time).**

  | min | 30 | 60 | 120 | 180 | 240 | 360 |
  |---|---:|---:|---:|---:|---:|---:|
  | Z8 | 26,836 | 33,974 | 38,179 | 40,739 | 42,007 | **42,917** |
  | Z7 | 24,561 | 32,154 | 37,195 | 40,786 | 42,478 | 43,350 |
  | Z6 (20 Nov system, 12 workers) | 31,133 | 37,378 | 40,238 | 41,789 | 42,920 | 43,782 |

  * The floors that wait remove Z7's early cost (+2,275 at 30 minutes, +1,820 at 1 hour), but the lead is gone by 3
    hours and Z8 trails by 408-471 from 4 to 6 hours (−406 at equal abstract work at 5 hours). Stopped at 6 hours:
    by the rule set at its start, the option needs a side-by-side test either way (exp55, planned).
  * Z8's own runs were ahead at 4 hours (+347); the gap was in proofs synced from the statement transfer (−818).
    exp/armdiff.py: of the 798 goals only Z7 had at 4 hours, 387 fell at Z7's first run. For the 206 of them Z8 had
    run, Z7's first run came at a median of 187 minutes and Z8's failed one at 162: later, in a fuller context.
  * Caveat: exp52's side-by-side on half2 still had +789 at 3 hours, where Z8 against Z7 was already level. Part of
    the late gap may be the cross-time comparison (noise up to about 400).
* **ul75: production with the head class (22 Nov 07:13; [notes/2026-11-22-ul75.md](notes/2026-11-22-ul75.md)).** In
  ul74's 14.3 hours the 40 s chain level proved 17 in 23.8 CPU hours (0.71 per CPU hour), the 5 s variants 8 in
  52.7, and 253 of the 1,026 heads had no L1 run: with `--ratio-order` a head's L1 entry queued behind the variants.
  ul75 adds `--head-class` (exp47/48). First hour: 153 L1 runs (ul74: 67 an hour), 4 proved; new=4 (ul74: 2.2 an
  hour). One hour without a control: a direction only.
* **What Z6 lacked (exp/roots.py, trust.py --dump-rec).** Of the 4,117 goals production has and Z6 lacks, 190 have
  recorded lemmas that Z6 all proved (104 first proved at L1); their reach is 363. The rest rest on lemmas Z6
  never proved. The gap is mostly depth.
  * The 190 at 40 s in Z6's final context, fresh, without hints: 121 proved (64%; heads 85 of 138).
* **Latency (exp/latency.py).** Once its last lemma was proved, a goal Z6 proved waited a median of 4-51 minutes
  in hours 1-5 (p75 26-81), and almost always fell at its first run after that.
  * Goals whose last lemma was a near sibling came at once. Those whose last lemma was a kNN lemma did not: 56%
    came over 10 minutes late.
  * With `--fail-order`, a kNN change never triggered a retry; only the learned scheduler's path checked it.
  * exp46: `--knn-ctx K`, a goal that a new proof would enter the top K of its kNN lemmas has a new context.
* **Heads.** At Z6's end 1,120 of its 7,689 unsolved goals were heads (right after a proven sibling); production has
  proved 875 of them. Z6 ran L1 16 times in 8 hours. With --ratio-order, L1's estimate stays near its prior, so a
  head runs every 5 s variant first and L1 entries come last.
  * exp47: `--head-class`, heads whose next own level is L1 are a mix class.

**Step joins: unsolved goals closed by rewriting with other theories' proof steps (20 Nov 10:40;
[notes/2026-11-20-step-join.md](notes/2026-11-20-step-join.md)).**
* exp/joincheck.py asks whether an unsolved goal's ground equation rewrites to one normal form with the union of
  the proof steps of proven unit goals in theories within the goal's. It uses ordered ground rewriting with a
  discrimination tree. For a conditional goal, the hypothesis is a ground rule for that goal only.
* exp/stepjoin.py gives twee those steps as lemma axioms named after their source proof (`skax_<i>_<goal>`), with
  production's options, and keeps the output as the proof's record.
* **All 3,684 unsolved goals: 23 joins, and 23 proofs** (21 unit, 2 conditional), for about 0.25 CPU h.
  * Example: nil3_23_32_to_26__goal_507 from three steps of Ka1_eq_Ka2 proofs.
  * Production never put these together: its lemmas are other goals, not steps of other proofs.
* Live from 10:50 (abs/stepjlive.sh), every 30 minutes over everything unsolved.
* Each step axiom is first checked in Mace4 models of the theory (2ba): hints files also hold printed goal terms
  that are not theorems.

**E as a member (exp28; [notes/2026-11-19-eprover-watchlist.md](notes/2026-11-19-eprover-watchlist.md)): a genuine negative.** E 3.5.9 was built from
ext/eprover and given the chain hints as a static watchlist (`-xUseWatchlist`).
* It proved 0 of the 107 walls at 60 CPU s each (1.79 CPU h). Prover9 with the same hints proved 4 (exp16).
* E processes about 500 clauses a second on these problems. It stays out of the portfolio.

**ENIGMAWatch (exp31, the user's paper of 13:30; [notes/2026-11-19-enigmawatch.md](notes/2026-11-19-enigmawatch.md)):
the model part is a negative; ProofWatch becomes a member.** Goertzel, Jakubův and Urban (TABLEAUX 2019) add the
completion ratios of 512 globally fixed proofs, the proof-state vector, to ENIGMA's features. The selections were
Mean, Var, Rand and Corr; Mean was best, +8.8% over ENIGMA in loop 0 on Mizar40.
* **Offline, on twee's rule model** (exp/ew_offline.py):
  * watchlists: 32,127 proofs of the 86 training originals;
  * a rule matches a step if their canonical keys are equal;
  * training on 1,000 problems, testing on 300 of the 43 held-out originals.
  * The trees use the vector heavily (Rand: 406 of 512 features, a third of the gain).
  * But held-out AUC moves only from 0.900 to 0.901-0.902 (+0.0008 Mean, +0.0012 Var, +0.0015 Rand), with problems
    split about 50/50 better and worse.
  * Mean degenerates on AIM: almost every proof is partly matched in almost every run, so the 512 highest-mean proofs
    are tiny and complete early.
* **No online test.** The lift is negligible, and a near-oracle model already gained nothing through the
  defer-once filter (2ad, 2af).
* **ProofWatch's own part acts on hints, which pay here.** As `--variants pw` (loop.py 3362943), each pool hint
  lists the solved siblings whose proofs contain it, and twee's `--eqhint-watch 0.05` moves its boost toward the
  default 0.01 as its best source proof completes. The 13 Nov test (+2 −4) was complementary, so `pw@0` joins ul65
  as an explored member.

**The deep tail starved from 06:00 to 16:24, and is now explored (portfolio notes, 19 Nov 16:20).** exp32's
climber ([notes/2026-11-19-climber-member.md](notes/2026-11-19-climber-member.md)) proved 4 stuck heads by 16:19. Production had run 22-24 fresh 5 s runs on each, but nothing beyond 40 s.
(Corrected 17:50: I first wrote that its "plain 160 s control runs" proved 3 of them. Those `direct` runs come after a
successful final run, with that run's own proof steps among the hints, so they are no control. exp36,
[notes/2026-11-19-climb-ablation.md](notes/2026-11-19-climb-ablation.md), is the real ablation.)
**exp36 result (20:05): the sketch hints caused 3 of 54 climber proofs.** Each climber proof was rerun twice at its
final budget, in production's context as of the proof: the pool only, and the sketch steps saved before the proof
first. Both arms prove 35, neither 16, the sketch arm alone 3 (all CLU at 20 s), the pool alone 0, at equal speed on
the shared ones. Today's binary and context prove 35 of the 54 without any climb. The 16 that neither proves need
what the arms lack: fill lemmas, assumptions, or the old binary's search.
* Since ul58 (06:02), L2-L4 and the 80 s variants k60, p9, unf, two and nom never ran. Their hand-set priors (L2 1.1)
  sat below the live 5 s members (1-3 per CPU hour), and a label that never runs is never re-measured.
* ul67/ul68 add fresh pool runs at 40 and 80 s right after the 5 s level (`pool@1:0`, `pool@2:0`; new syntax
  NAME@B:F) and explore every label, not a hand-picked list. Each label under 1 CPU h is now measured.

**Periodic re-exploration (ul69, 16:33; loop.py 25804f0).** `--reexplore 150:0.25`: a label that had its
explore hour, but got under 0.25 CPU h among the last 150 CPU h of all runs, is explored again until it has 0.25 in
that window. At 16:32 this picked L2 and Vk60 at once ([notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md)).

**The climber's outputs (exp34, user's question 16:55; [notes/2026-11-19-climber-outputs.md](notes/2026-11-19-climber-outputs.md)).**
* Production takes every real proof a climber made (0 of them missing over 29 climb directories).
* Production takes none of the rest:
  * sketch steps: 64,564 over 108 originals, 46% new to the pools, about 4% of a pool;
  * fill lemmas;
  * conditional proofs.
* Three earlier tests of sketch steps as hints for their own target gained nothing (2g, exp4).
* **Fill lemmas' statements were never written to disk.** Nor were the kNN assumptions' identities or a proof's
  lemma premises.
* exp34 replayed the 4 conditional proofs ("T from proven sibling U") that used no fill lemma: 0 of 4, with U as
  lemmas and the sketch steps as hints, at 20 s. The lemmas those proofs used were not recorded.
* climb.py now writes true.tsv, fillhints/, assume.tsv and used.tsv, and reloads them on start. The data repo has
  every climb directory under climbs/.

**The dropped lemma selections as 5 s members (ul60, 08:05; loop.py 92d60c4).** exp21 found that at 5 s only the
variants that change the problem pay, and the 60-lemma 5 s variant makes 5-20 per CPU hour live. 16 Nov dropped
three lemma selections that each proved goals plain similarity did not (150 unsolved at 20 s: 6 plain; use counts 7,
+3 −2; proof dependencies 5, +1 −2; 100 lemmas 5, +1 −2). They are now variants:
* `kp@0` (use counts), `kd@0` (proof dependencies) and `k100@0`, at prior 3 each, measured live by the ratio rule;
* their indexes are built in a background thread, 37 s on UL.

**Restart bursts are cascades, not a scheduler defect** (portfolio review, 19 Nov). ul58 made 40 new in its first
57 minutes and 129 in its last 16, and ul59 went on with it. Ruled out:
* stale scores;
* proofs synced from other processes;
* the threshold.
The cascade was spread over many originals of the same axiom families (aK2_eq_aK3_*, nil3_*). 392 of 401 proofs
since ul58 used a kNN lemma of another original, and for 171 the youngest was under 30 minutes old. So the kNN
index is now rebuilt every 10 minutes, not 30 (about 1 s a rebuild).

**Exploration, and 5 s members measured one after another (19 Nov 09:20-10:20; loop.py 3f95f59, e2986e3, 5fc6b48,
4d3baca).**
* **The gap.** The deep queue is one global sort by each goal's best option. So a member whose prior is below the
  best live member never runs, and is never measured. At prior 3, ul60's new lemma selections ran 7-9 times in 45
  minutes. In exp27 the 40 s chain level ran 4 times in an hour from zero, behind unfolded 5 s runs, and proved all 4.
* **`--explore H`.** A label with less than H CPU hours of runs in the round is estimated at no less than the best
  label that has H. ul62 (10:05) and ul63 (10:17) use `--explore 1` for the new members, with no hand-set priors.
* **Measured, each conditional on the members before it in the same context** (`exp/condvar.py`):

| member (5 s) | where | runs | proved | CPU h | per CPU h | proved after |
|---|---|---:|---:|---:|---:|---|
| k100@0: 100 kNN lemmas | ul60 | 1,726 | 42 | 2.95 | 14.2 | 32 after k60@0 failed |
| kd@0: proof-dependency lemmas | ul61 | 1,050 | 9 | 1.83 | 4.9 | all 10 after k100@0 failed |
| kp@0: use-count lemmas | ul61-62 | 523 | 0 | 0.93 | 0 | |
| k200@0 | ul62 | 463 | 14 | 1.01 | 13.8 | all 14 after k100@0, 12 after k60@0 |
| s12@0: 12 sibling lemmas | ul62 | 539 | 5 | 1.02 | 4.9 | all 5 after k100@0 and kd@0 |

* So each lemma selection, and each lemma count, is its own problem. Three of these four were dropped on 16 Nov on
  count (+1 −2 each against 30 kNN lemmas). As members after one another they pay at about the rate of a fresh 5 s
  run in a new context (L0, 3-13 per CPU hour on the tail).
* A 5 s run with 400 kNN lemmas costs no more than with 60 (4 goals, 1.2-6.4 CPU s). One proved an unsolved goal.
* Twee normalises its input: a permuted problem gives byte-identical output, so there are no cheap random restarts.
* **ul63** explores 13 members at 5 s:
  * lemma sets: k100, k200, k400, kp, kd, s12, k200s12;
  * hl: the pool plus the kNN lemmas' proof steps as hints at factor 0.1 (2ap's dropped `--hint-lemma-proofs`), 114-591
    hints more a run;
  * search settings: the rule models rm7t and rm4b (`mX`, each with goal files in its own vocabulary), threshold 0.2,
    no parental guidance, no rule model.
* **Twee's critical-pair weights (exp57, 22 Nov; the user: "have we played with different weights for the default
  twee weighting functions?"; [notes/2026-11-22-cp-weights.md](notes/2026-11-22-cp-weights.md)).** No run before
  had changed them. One fresh 20 s run per goal on 300 late heads (Z7's context), one value either side of each
  default:

  | arm | proved of 300 | +/− vs default | union with default | vs default at 40 s (116) |
  |---|---:|---|---:|---:|
  | default 20 s | 98 | | | |
  | `--lhs-weight 2` / `8` | 89 / 89 | +2 −11 / +4 −13 | 100 / 102 | −16 / −14 |
  | `--depth-weight 0` / `5` | 76 / 95 | +3 −25 / +6 −9 | 101 / 104 | −15 / −12 |
  | `--var-weight 0.5` / `1.5` | 91 / 87 | +5 −12 / +5 −16 | 103 / 103 | −13 / −13 |
  | `--dup-factor 1` | 91 | +0 −7 | 98 | −18 |

  All nine arms together proved 119 in 19.3 CPU h, the 40 s default alone 116 in 4.1. So the weights are not
  complementary members: on these goals a second setting is worth less than twice the time. loop.py
  `--flag-variants NAME=FLAGS` (any twee flag as a variant) stays for later tests.

## 2ba. Soundness: the Prover9 negation bug, re-verification, and a model audit (20 Nov)

*Notes: [notes/2026-11-20-semantic-guidance.md](notes/2026-11-20-semantic-guidance.md).*

*Notes: [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md),
[notes/2026-11-20-model-audit.md](notes/2026-11-20-model-audit.md).*

**The bug.** p9twee.py, which turns twee's problems into Prover9's input, wrote TPTP `~ a = b` as LADR `- a = b`.
* In TPTP, `=` binds tighter than `~`. In LADR, prefix `-` binds tighter than `=`, so `- a = b` is the equation
  (-a) = b with `-` a new function symbol.
* Every conditional sibling lemma given to Prover9 was a false axiom. From one, Prover9 derived that the loop has at
  most 2 elements, and proved goals from that.
* Fixed 09:45 (`-(a = b)`). All 9,052 conditional conjectures convert to a negated atom, and Prover9 prints them as
  `!=` literals.

**Found by an independent check.** joincheck (step joins, 2az) "joined" aK2_eq_aK3_s__goal_497 using commutativity
and `ld(X0,e) = X0`, both false in that theory. They came from the hints of a P9C proof.

**Scope.**
* Prover9 ran only through p9twee.py: P9T (15 Nov), P9L (from 15 Nov 08:56), exp16 and P9C (18 Nov), and
  production's `p9` variant (28 runs, 0 proofs). The from-zero arms never ran it.
* 16 goals in production rested on a Prover9 proof that used a false clause: P9C 9 of 10, P9L 3 of 9, P9T 1 of 1,
  exp16 all 6 proofs (3 more goals).
* **Void claims:** 2ad's "first hit" (aK2_eq_aK3_r__goal_241), 2az's "Prover9 with the chain is the cheapest member
  (2.3 per CPU hour)", exp16's walls, and the p9 member's yields.
* The goals' statements are true. They are steps of real Prover9 proofs in AIM60k. Our proofs of them are void,
  and so are, until re-proved, the proofs that used them as lemma axioms.

**Re-verification.**
* **Trust** (exp/trust.py), a fixpoint over the lemma records. Since twee-e31 (14 Nov) each kept output's
  `USEDAXIOMS` line names its lemma axioms after their goals. A proof is trusted if it is older than the first
  unsound one (15 Nov 08:56), or if its record names every lemma it used and each is a trusted proven goal.
* **Exposed theories.** Every lemma mechanism takes lemmas from theories within the target's. So only 43 of the 129
  originals, those whose axioms contain a bad goal's, can hold a dependent proof. The other 86 are trusted
  outright.
* **The quarantine** (10:07): 1,130 goals: the closure, plus every proof after 15 Nov 08:56 without a record. 84 of
  them, outside the exposed theories, went back at 10:36.
* **Re-proofs** (exp/rever2.py): each pass re-proves the untrusted proofs without a complete record, and the
  quarantined goals, with trusted lemmas only. Outputs are kept, so the new proofs carry records. Passes repeat
  until one proves nothing new.
  * Pass 1 (10:37-11:13): 161 of 221.
  * trust.py then missed rever2's own nested outputs, and kept old records through the side loops' symlinked hints
    dirs. After the fix (11:21): 230 untrusted of 48,168.
  * Continuing in loops/REVER3. Whatever stays untrusted at the end leaves the solved list.
* All side loops now keep their outputs, and every lemma axiom they add carries its goal's name.

**A model audit finds no other unsoundness** (exp/modelcheck.py).
* Mace4 finds up to 40 models (sizes 2-8) of each of the 68 theories, 2,504 models in all.
* Each step of every solved unit goal's proof is evaluated in its theory's models: 2.4M checks.
* Self-test: no AIM60k goal statement fails.
* **217 false steps in 71 goals, all with different variables on the two sides**, such as `X0 = X1` and
  `X0 = m(k(X1,X2),...)`. These are printed goal terms, not derived equations. Harmless as hints, since twee
  matches by variant; stepjoin now rejects them as axioms.
* No step with the same variables on both sides is false. That is the shape of a wrong derived equation.
* **Positive control:** 13 of the 16 unsound Prover9 proofs show such a step, e.g. `ld(X0,e) = X0`.

**The models as guidance: a weak negative** ([notes/2026-11-20-semantic-guidance.md](notes/2026-11-20-semantic-guidance.md)).
* Semantic guidance in the style of Slaney's SCOTT: a rule false in a model of the base axioms where an extra axiom
  fails depends on the extras.
* Mace4 has such models for 62 of the 116 originals with extras.
* In 10 production logs per original, proof steps are false there 32.4% of the time and the other given rules 30.4%
  (lift 1.09; clearly enriched in 18 originals, depleted in 11). Most of what a run derives depends on the extras
  too.
* Not worth evaluating models per rule inside twee.

**Lesson.** Hints may be wrong; axioms may not. Every path that turns text into an axiom (a second prover's input,
hints as lemmas, given rules as `.ax`) is part of the trusted base. Each needs a check, and each proof should record
its lemmas when it is written.

## 2c. Long runs: stall cutoff and checkpoints

*Notes: [notes/2026-11-12-long-runs-checkpoints.md](notes/2026-11-12-long-runs-checkpoints.md).*

* `--eqhint-stall N` gives up when no new rule has matched a hint for N
  rules. This is Veroff's practice of stopping lost jobs. `HINTSTATS` now
  reports `lastmatch` and `maxgap`, the largest gap between matches, to
  calibrate N on solved runs.
* `--load-state F` resumes a run saved with `--dump-state`, with the hints
  given now. On the new state it re-normalises the hints and re-scores the
  queue. A 1 s run dumped (1.5 MB) and resumed solves in 1.4 s, against
  2.3 s from scratch. Long runs can be continued with new hints instead of
  being restarted, as with Prover9-new's checkpoints.

### Long runs on hard problems (60 s)

The set has 59 dev10 goals, 6 per original, that no 2 s or 8 s setting
solved. Each has solved goals shortly before it in the original proof, so
relevant hints exist. Model rm3 never saw these problems, but it was
trained on the easier, solved goals of the same originals (dev10 is part
of its training data).

| setting (60 s) | solved | CPU total |
|---|---|---|
| plain | 26 | 2682 s |
| kNN hints (100) | 28 | 2623 s |
| hints = statements of solved earlier goals of the same original (50–213) | 26 | 2494 s |
| hints = all earlier goal statements, solved or not | 29 | 2403 s |
| rule model | 36 | 2110 s |
| rule model + kNN hints | 36 | 2116 s |
| rule model + earlier-goal hints + kNN hints | **37** | 1920 s |
| rule model + kNN hints + `--eqhint-stall 2000` | 18 | 777 s |

* In long runs the rule model gives +10. Hints give +2 to +3 without the
  model and +0 to +1 with it.
* Earlier goal statements are the lines of the original Prover9 proof,
  close to Veroff's sketches. They help a little (+3), mostly when unsolved
  goals are included as hints too.
* A stall cutoff of 2000 rules is far too aggressive for 60 s runs, which
  reach about 20k rules: it loses half the solutions. It is about 35% more
  CPU-efficient, so it would suit a loop with many problems only with a
  much larger N.

### Checkpoints: hints arriving late

On the same 59 hard problems:

* Plain twee runs 30 s and dumps its state (19 solved; about 16 MB per
  state).
* The 40 unsolved are resumed for 30 s more:
  * without hints: +8, giving 27 (one plain 60 s run gives 26), so resume
    is a true continuation;
  * with the kNN hints: +9, giving 28, the same as hints from the start
    for 60 s.

Hints that arrive late do as well as hints from the start here.
`loop.py --resume` builds a checkpointed Veroff loop on this. Unsolved runs
dump their state, and the next round resumes them with the current hints,
so search time accumulates across rounds instead of being redone. Cost: a
19 MB state loads in about 1 s and dumps in about 2 s. That is fine for
rounds of 30 s or more, but about 40% overhead for 8 s rounds.

## 2d. Prover9-new branches: what was ported

| branch | what it does | decision |
|---|---|---|
| packed-fast, better-packed, faster-packed-fallback, adaptive-hint-mask-filter, lazy-hash-gate | fast matching against very large hint banks (millions of hints, Josef runs): packed matchers, 64-bit checklists, bit tables | not ported. With ≤ 10^3 hints per run, matching costs about 7% of twee's throughput after the fingerprint prefilter, which plays the same role. |
| experimental-generalized-hint-hash | subsumption matching by hashing precomputed hint generalisations | ported in a simple form as `--eqhint-generalise` (one-step generalisations of each hint go into the hint map). Neutral on the hard dev set (68 vs 69, section 2f). |
| proof-parent-guidance, proof-recipe-replay | replay a known proof's parent graph | covered by self-replay with own-proof hints (15× faster). Not useful for new problems. |
| target-directed-inference | hash-guided inference toward targets | the branch reports a no-go; not ported. |
| long-run-scalability, ancestor store, compact indexing, checkpoints | memory and restart for runs with 10^5+ given clauses | checkpoints ported as `--load-state` (twee already had `--dump-state`). Twee's AIM runs are far from those memory limits. |
| (master) back_demod_hints, sos back-demodulation | re-simplify hints and queued clauses | ported as `--eqhint-normalise` and `--eqhint-requeue`. |
| long-run-scalability, mature-back-index-cpu, adaptive-back-index-crossover (indexing side) | paramodulation and back-demodulation indexes that stay cheap as the clause set grows | ported in twee's terms (2v): a fingerprint index for overlap partners (exact, 1.8× on long runs) and a backward-demodulation filter for interreduction. |

## 3. Assessment

*22 Nov, 12:52 (`date` checked). The 22 Nov 03:58 assessment follows it.*

* **Where it stands.** **48,329 solved (+55.6% over plain twee at 4 s), holdout 5,359 (+67.3%)**, all trusted (12:41).
  3,455 are left. That is 69 more than at 00:26.
* **Where the new proofs come from.** Of the 49 since 07:21:
  * production's own runs 23 (ul75, 6 workers; 24 new in its first 5.7 hours, against about 1.6 an hour for ul74
    before it, a comparison across times);
  * the given-rule retry 18 (exp56), the live given-rule loop 7, the proof-step transfer 1.
* **A defect found and fixed: given rules lacked their lemma axioms (exp56).**
  * When a failed run derives an unsolved goal's equation, its rules are replayed as a sketch for that goal. The
    source run's lemma axioms (proven sibling and kNN lemmas) reached the sketch only as hints, because loop.py's
    scan marks only the original's axioms.
  * Named after the proven goals they state, so trust.py resolves them, they made 13 of the 25 given-up goals fall
    at 27 per CPU hour (12 at 20 s, where the old sketches proved 0 of 30).
  * The live loop also used to try a goal once and never again; it now retries every 3 hours on newer hits. Both
    changes have been live since 12:06.
  * Production's runs therefore pay twice: in their own proofs, and in the hits they supply. Since 07:13, L1 supplied
    the first hit of 18 goals and the 5 s variants of 5. The ratio order counts only the first kind.
* **From zero.** Z8 (`--floor-ratio 20`, 6 workers) ended at 42,917 at 6 hours, against Z7's 43,350 the day before.
  That is within the cross-time noise, and the floors were kept on exp52's side-by-side +789. The lemma-axiom fix
  should matter more from zero: in Z8's live loop 682 goals failed, and Z8 solved 265 of them later by other routes.
  That is the next from-zero test after exp55 (exp58).
* **Not adopted today:** the head class's 40 s runs cut to 20 s (exp54, +8 at 3 hours, within its ±50 band).
* **Portfolio: twee's own critical-pair weights (exp57, the user's question at 11:08).** Seven weight settings at 20 s
  on 300 heads, against the control at 20 s (98 proved) and 40 s (116). Every setting proved fewer than the default
  (76-95), and each one's union with the default stayed 12-18 below the default at twice the time. No member; twee's
  default weights are the best single setting on these goals.
* **What is weak in the evidence:**
  * The given-rule figures are on goals selected for having hits from many runs. Their rate will not hold for goals
    with a single hit.
  * The late A/B's noise is still not measured (its replica pair is deferred), so its ±50 band is a guess.
  * Production's rates are compared across times and contexts.

*22 Nov, 03:58 (`date` checked). The 20 Nov assessment follows it.*

* **Where it stands.** All 51,784 public problems: **48,260 solved (+55.4% over plain twee at 4 s)**, holdout
  **5,347 (+66.9%)**, all trusted (22 Nov 00:26). 3,524 are left. Production's own loop now proves about 1.6 an hour
  on 6 workers (17 in the 10.5 hours after its 21 Nov 16:50 restart, 59 CPU hours), and its side loops a few more.
* **From zero, the measure that matters most.** The system as of 21 Nov evening (solve_new.sh's LATE set) had
  43,767 at 8 hours on 6 workers (Z7), against 44,092 for the 20 Nov system on 12 workers (Z6).
  * Z8 (LATE + `--floor-ratio 20`, 6 workers, from 02:53) is level with the 20 Nov system in the first hour, where
    Z7 was 2,368 behind it. At 1 hour Z8 had 33,987, against Z7's 32,154. Its 4-hour reading comes at about 06:53.
* **What moved the from-zero curve in the last 1.5 days** (half2 from zero, side by side; the same setup run twice,
  3 hours apart, differed by at most 105 at any reading (P2U, P2V), earlier identical pairs by about 185):
  * failed-before goals as their own mix class, `--retry-class`: +450 at 5 hours (exp44);
  * member yields over the last 2,000 runs with re-exploration: +559 at 5 hours (exp45);
  * both, plus kNN-context retries and a head class (P2O): +241 over the pair (exp48);
  * floors that wait for the class to compete, `--floor-ratio 20`: +789 at 3 hours (exp52).
* **Rejected, each side by side:** 1 s quick first runs (−719, exp49), 3 s retries (−166, exp50), and deep runs
  without queue renormalisation (−820, exp53).
* **The late curve is limited by hard goals, not by CPU.** Twice the workers gave 325 more at 8 hours (Z6 against
  Z7). The unsolved goals sit at the ends of the proof chains: 2,379 of the 3,524 are in the last tenth of their
  original's goals, none in the first four tenths, and 1,029 come right after a solved goal. Runs of 640 s proved
  none of 15 late goals that failed at 320 s (17 Nov).
* **What is weak in the evidence:**
  * The 3-hour half2 tests hardly reach the deep and head classes: the control of exp53 ran the 40 s chain level 31
    times in 3 hours. Methods for those classes need another design. The late A/B
    ([notes/2026-11-22-late-ab.md](notes/2026-11-22-late-ab.md)) starts on the 3,817 half2 goals Z7 left unsolved,
    with Z7's proofs as the context. Its noise is not known yet. Its first test, exp54 (`--head-time 20`: the head
    class's 40 s runs cut to 20 s), ended at +8 in 3 hours (360 against 352 new goals; union 376). That is within its
    ±50 band, so the setting is not adopted.
  * From-zero runs at different times differ by up to about 400 from the machine's load alone. exp/abscurve.py
    corrects only part of that.
* **Proofs.** Search runs use `--no-proof`, and exp/proofq.py reruns every proved run with the proof printed. But
  twee reads the flag only after the search has succeeded: printing costs nothing (61.1 against 61.2 CPU s on 42
  jobs). So the reruns spend about 3 CPUs repeating proved runs, and they fall behind: 123,342 jobs were queued at
  03:58. loop.py `--proof-in-search` would keep the same proofs without reruns. It is ready, and waits for the
  user's decision. (07:08: 69,073 queued, and 20,203 rerun in the hour from 06:00, so the queue is now
  shrinking: most jobs are runs of under a second.)

*20 Nov, 13:40 (`date` checked). After the soundness re-verification. The 19 Nov assessment follows it.*

* **Where it stands.** All 51,784 public problems: **48,172 solved (+55.1% over plain twee at 4 s)**, holdout
  **5,336 (+66.6%)**. Every proof is trusted by the fixpoint of 2ba. 3,612 goals are left.
* **The day's main event was a soundness bug, not a gain** (2ba).
  * p9twee.py turned conditional sibling lemmas into false axioms. 16 Prover9 proofs were void, and 143 more rested
    on them.
  * Claims that fell: the Prover9 member's yields (2az), exp16's walls, and 2ad's first Prover9 hit. The solved list
    was re-verified and the totals corrected. 5 of the 16 statements are still unproved (true, but not proved by us).
  * What guards it now:
    * every lemma path records its lemmas by name;
    * exp/trust.py checks the records as a fixpoint;
    * a model audit runs every 6 hours. On the 16 known-bad proofs it caught 13.
  * What still rests on argument, not a check:
    * Proofs outside the 43 exposed originals are trusted because every lemma mechanism stays within the target's
      theory.
    * Conditional goals' proofs are not model-checked.
    * The audit misses false steps that hold in all models up to size 8.
* **From zero, the one clear gain this week is the derived-rule transfer** (solve_new.sh `GIVEN=1`): +282 on half1
  (exp40) and +769 on half2 (exp41), against a noise of about 185 between identical runs.
  * Lifting its per-cycle cap did nothing (exp42, +22). The limit is that a hit waits for the loop's own failure.
    Running hits at once does not help either (exp43, −180).
* **Measured negatives today** (each closed, each recorded):
  * semantic guidance from Mace4 relevance models (lift 1.09);
  * cross-run joining with the goal's own failed run's rules (0 of 30);
  * the from-zero arms' proof steps as a bigger join bank (0 of 1,557).
* **Step joins are cheap but nearly exhausted.** 24 proofs in about 0.3 CPU h, then about 1 a cycle. New joins come
  only as new proofs enter the bank.
* **What is weak in the evidence:**
  * Each from-zero comparison is one run per arm on one half. The two halves gave +282 and +769 for the same change.
  * Two-hour curves converge. exp42 led by 175 at 30 minutes and by 22 at 2 hours. So the 2-hour totals hide speed
    differences, and the 6-8 hour from-zero run that would show long-run effects is still not done.
  * The rule model rm4t was trained on public proofs, so "from zero" is not fully clean (2aq).
  * Production's rate has no control. The quarantine, the re-proofs and the experiments' CPU share make its hourly
    counts today uninterpretable as a measure of any setting.
* **The limit now.** It is as on 19 Nov. Most of the 3,612 are far from any proof. They fall in cascades when a
  neighbour below falls, or through cross-original lemmas. Joins and model-based guidance do not reach them.

*19 Nov, 09:26 (`date` checked). An independent look at where things stand. The 16 Nov assessment follows it.*

* **Where it stands.** All 51,784 public problems: **47,041 solved (+51.5% over plain twee at 4 s)**, holdout
  **5,188 (+62.0%)**. That is about 5 days of loops on 10–19 workers. 4,743 public goals are left.
* **From zero on a new half of the benchmark** (half1, 25,937 goals, 6 workers, no outside proofs):
  * 11,500 in 10 minutes, 18,500 in an hour, 19,000 in 2 hours (PGA 18,987; today's system 18,917).
  * The curve is front-loaded: the second hour adds 2.5%.
  * *With the explored lemma portfolio: half1 19,309 in 2 hours (+392, exp29), but half2 −118 (exp30, 14:46).
    Pooled, the difference is within noise.*
* **Where the gain comes from now:**
  1. Proven siblings as lemmas, online: the chain along each original's proof.
  2. **Cross-original kNN lemmas.** 392 of the 401 production proofs from 06:02 to 08:05 used one, often proved
     minutes earlier. Cascades run through families of originals with the same axioms (aK2_eq_aK3_*, nil3_*).
  3. In short runs, the rule model with parental guidance (+577 on half1 at 2 hours).
  4. On the tail: chain hints for the deep runs (the 40 s chain level, about 1.4–1.9 proofs per CPU hour on near
     goals), and a portfolio of cheap 5 s variants that change the problem:
     * unfolded definitions (2–3 per CPU hour);
     * 60 kNN lemmas (4–8);
     * 100 kNN lemmas (14, complementary to 60: 32 proofs after 60 had failed).
* **Genuine negatives, measured** (nothing proved that others did not):
  * Veroff's Prover9 settings at max_weight 5, 40 and 100 (0 of 107 walls each);
  * deep runs on far goals (0 of 40 at 80 s);
  * chain hints at 5 s;
  * a per-goal success predictor for the deep runs (AUC 0.4–0.7, inconsistent).
* **What is weak in the evidence:**
  * Production's tail measures have no controls. Proof cascades swing a window's rate from 40 to 300 an hour, so
    before/after comparisons of settings are unreliable. Only the per-member yields of the ratio rule, measured
    side by side, are comparable.
  * The tail portfolio is unproven from zero. In 2 hours on half1 it is neutral, and longer from-zero runs (6–8
    hours, where its gains would show) have not been done.
  * The ratio rule left members unmeasured whose priors were below the best live member (fixed by `--explore`,
    19 Nov). Several priors come from the walls, a different population from production's goals.
  * The rule model rm4t was trained on public proofs, so "from zero" is not fully clean (2aq).
* **The limit now.** Of the 4,743 unsolved goals, most are far from the frontier, where deep runs do not pay. They
  fall only as their neighbours below are proved, or through new cross-original lemmas. Near goals' deep runs prove
  5–10% each.

*16 Nov, 15:15. The text after this update is from 13–14 Nov.*

* **Where it stands:**
  * All 51,784 public problems: 44,710 solved, +43.9% over plain twee
    at 4 s. The holdout has 4,898, +52.9%. This took about 3.5 days of
    loops on 10–16 workers.
  * **Unseen originals:** on the 11 whole holdout originals, from
    scratch with a clean context, the system reaches 71.7% in 1 hour
    per batch, against 61.2% for plain twee (2aq).
  * **From zero**, with no other originals' proofs, on the 3 replay
    originals: 890 of 1,320 in 1 hour on 4 workers, against 731 for
    plain twee and 942 with the public context (2aq).
* **Where the gain comes from**, by today's evidence:
  1. **The sibling chain:** proven goals of the same original as lemma
     axioms, online (below).
  2. **Exact reuse across originals.** A proven goal of the same or a
     weaker theory proves a goal that states it, or of which it is an
     instance.
     * kNN lemmas from such theories: 10 → 30 lemmas helped. A filter
       that dropped goals identical to the target had hidden many of
       them since 13 Nov; fixed 16 Nov, 2al.
     * The proof-step transfer (2al): a goal that is a step of another
       proof gets that proof as hints and its goal as a lemma.
     * On new originals the transfer proves 30–40% of the goals in
       seconds. From zero, with no other originals' proofs, the loop
       proves 890 of 1,320 replay goals in 1 hour. The 13 Nov context
       adds 5–6% (942), today's filtered one 22% (1,085, against
       production's 1,111 after 3.5 days; 2aq).
  3. **Hints from all of the original's proofs**, and the ENIGMA rule
     filter in the short runs.
* **What did not help** (16 Nov additions to the list below; *18 Nov correction: several of these, and of the
  list below, are complementary, with unique proofs, and belong in a portfolio rather than out; 2az*):
  * more than 30 kNN lemmas;
  * use-count or MaSh-style dependency selection of lemmas (2am);
  * similar proofs' steps as hints from other originals (2ap);
  * the rule model ordering the queue (2ao);
  * learned climbing moves and theory sampling (2ak);
  * extra CPU for heads (2an).
* **The limit now:** the remaining 7,074 public goals need long
  derivations. Fresh retries in new contexts are used up: 0 of 281
  since 11:05. The 320 s level makes about 1 proof per CPU hour, the
  climbers 0.5–1.2.

*Rewritten 13 Nov evening, updated 14 Nov morning; earlier conclusions are corrected where noted.*

* **Overall.** On all 51,784 public problems at 4 s per problem, the
  first loop (rule model + kNN hints, then lemma import) solves 33,249
  against 31,060 for plain twee (+7.0%), with 13% less CPU (holdout 3417
  vs 3203). The Veroff-style online loop then runs everything left in goal
  order: its first round (5 abstract s) brings the total to 36,057 (+16.1%
  over plain; holdout 3,747), its second (20 s) to 39,008 (+25.6%;
  holdout 4,196), and a cascade round is running (2o, 2p). On the
  hardest goals of two families, long runs with whole-original pools
  solve 64 of 68 over four rounds (2m).
* **Where the gain comes from**, largest first:
  1. **The sibling chain: lemma import, run online.** Proven sibling
     goals become axioms (sound, CASC LTB-style, reported separately). In
     goal order, each proof feeds the next runs at once (+25% over fixed
     pools). Success depends on how near the last proof is: 58% at a gap
     of 1 goal at 20 s, 26% at 4–10, 0 of 5 beyond (2p). The loop advances
     along each original's proof.
  2. **The ENIGMA-style rule filter** (+5–6% at 2 s, +36% on hard dev
     goals at 8 s, +11 of 300 hard holdout goals at 60 s). In the 20 s
     ablation (2q) it is the strongest single guide: 42 of 189 against
     37 for hints and 28 for plain twee, at about 60% of plain's time.
     Without lemmas, ENIGMA and hints add up (49). With lemmas they
     overlap, and either one alone gives the full gain (58–59).
  3. **Hints from all of an original's proofs.** At 20 s and longer, the
     whole-original pool beats kNN-selected hints (60 vs 55 of 189 online;
     48 vs 40 of 68 at 300 s, against 36 without hints).
* **Hints in long runs: corrected.** The earlier negative result came
  from small hint lists (kNN, 100 hints): those runs stop matching after a
  few seconds because the list is used up. With pools of 2,000–6,000 hints
  the runs keep matching until late, and the pool adds 12 of 68 over no
  hints at 300 s. A hint's precision rises with the number of sibling
  proofs it comes from (0.8% from one proof, 51% from 20 or more), but
  weaker boosts for rare hints do not help (60 = 60).
* **What did not help** (each within noise or worse; *18 Nov: within noise in count, but several had unique
  proofs, 2az*): sketches and
  chained sketches; kNN/goal-statement/ProofWatch hints on top of the
  model; more model data or capacity (rm5, rm4b); portfolios; P9 SFDF
  reorientation (2n); multi-goal search, which lacks the restart with the
  new lemma (2p); a stall rule at short limits (hint signals at 5 s do not
  predict 20 s success, 2o).
* **Engineering.**
  * Abstract time (critical pairs) makes runs deterministic and
    comparable. Real CP rates fall to 50–300 per CPU second on runs with
    40k–110k rules, so long runs cost far more than their abstract time.
  * Checkpoints: resuming now takes new lemmas (the signature bug fixed in
    twee-e20). A resume of a big state costs minutes, mostly re-scoring the
    saved queue against new hints (2m).
  * Giving an original up after 30 failures in a row lost no proofs in
    replays of the sets/u3 runs. In the full 5 s round, which used it,
    giving up after 10 would have kept 84.5% of the proofs for 46% of the
    time.

## 4. Next steps

*20 Nov, 11:56 (2az, 2ba):*

* **Soundness first.** The re-verification (2ba) ends with the untrusted proofs out of the solved list, and the
  totals corrected (exp/quarantine2.py).
  * Every lemma path now records its lemmas by name.
  * The model audit (exp/modelcheck.py, about 15 minutes on 3 CPUs) is cheap enough to run every day, and after
    any new lemma or axiom path.
* **The derived-rule transfer is the from-zero gain** (exp40 +282 on half1, exp41 +769 on half2). Its ancestry runs
  make about 540-790 proofs per CPU h. A higher per-cycle cap does not help (exp42, +22), nor does running hits
  without waiting for the loop's failure (exp43, −180).
* **Step joins** (23 of 23) are a live member.
  * Next, cross-run joining: the goal's own failed run's given rules together with the other theories' proof steps
    (loop.py `--given-keep`, joincheck `--own-given`; pilot running).
  * Then the non-joined goals' normalising steps as lemmas.
* **Open:**
  * the climber (CLHL2), restarted after the re-verification;
  * a 6-8 hour from-zero run with GIVEN=1, where the tail starts.

*19 Nov, 11:11 (2az; [notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md)):*

* **Production (ul63, then ul64 at about 12:40)** is a portfolio of 5 s problem changes, explored and then ordered
  by the ratio rule. The deep levels (the 40 s chain, then 80 and 160 s) and the 80 s variants come after them.
  * Lemma counts pay most: each larger kNN set proves goals the smaller ones failed in the same context (400 lemmas
    at 11.5 per CPU hour). ul64 adds k1000@0, k2000@0, 40 and 200 sibling lemmas, and 400 lemmas at 80 s.
  * Search-setting changes (other rule models, no PG, threshold 0.2, no model) make 0-2 per CPU hour. They are kept,
    ordered below.
* **From zero:** exp29 (half1) gave +392 at 2 hours, and solve_new.sh's defaults became its setting. exp30 did not
  replicate it on half2 (−118, within noise): no from-zero gain is established. Both arms' deep work tied. The
  one-arm goals (295 and 414; union +297) are the target of a combined portfolio.
* **Measured and closed:**
  * E with watchlists (0 of 107 walls);
  * Prover9 with Veroff's settings (0 of 107 at max_weight 5, 40, 100);
  * deep runs on far goals (0 of 40);
  * a learned lemma ranker (a modest lift, from popularity; the lemma-count members reach the same lemmas);
  * recency-weighted yield estimates (they rank members worse than the cumulative one).
* **Open:**
  * the exp26 A/B on queue renormalisation in deep runs (stalled: L1 runs rarely now);
  * a 6-8 hour from-zero run, where the tail starts;
  * lemma sets by other criteria (the proof dependencies, kd@0, make 4.9 per CPU hour).

*18 Nov, 18:49 (the portfolio, 2az):*

* Production is a **portfolio ordered by the ratio rule**: each member is ranked by its new proofs per CPU hour on
  the goals every earlier member failed in the same context.
  * ul48: unfolded and 60-lemma 5 s runs on every goal whose fresh run failed;
  * after a failed 80 s chain run: 60 kNN lemmas, two-sided chain, unfolded, subsumption;
  * then 320 s;
  * the deep queue is ordered by each member's yield, from measured priors updated online;
  * Prover9 + chain as a 4-worker side worker.
* **Open:**
  * an 80 → 160 s resume level (exp20, about 1.4 per CPU hour on the increment so far);
  * no-PG and no-model 80 s members (exp22);
  * `--pass-every 1` at the next restart (the full pass now takes 0.5 s a run).
* **Rule from now on:** every A/B reports +/−, the union, and the second arm's unique proofs per CPU hour. A
  method is dropped only when it proves nothing the others don't. Otherwise it becomes a portfolio member at
  the share its yield earns.

*17 Nov, 15:20:*

* **Since 23:55:**
  * From zero on the whole benchmark, the dispatcher was the
    bottleneck. Then repeats of failed goals were (2as, 2at).
    `--mix` and `--fail-order` fixed both. Z4 reached 35,511 in 1 hour,
    37,713 in 2 hours and 38,044 at 3 h 56 min. Production has 44,858.
  * 70% of production's extra goals needed runs longer than 5 s (2au).
  * Ordering by an original's recent rate gained nothing, and neither
    did `--fail-reset`. On the 2-hour half1 test, identical runs
    differ by 1% (185).
  * Speed, the same search for less time (2au):
    * twee-e43 writes no state for a proved goal, so proved runs are a
      third faster: +700–1,000 proofs at 10 minutes.
    * twee-e44 renormalises hints incrementally: −11% CPU, same
      proofs.
    * `--no-fresh-states` drops the state dump of first runs, which
      was 22% of a failing run and 3.7× its memory.
  * Neither larger GC allocation areas (slower) nor hint lookups (1%)
    are worth more work.
  * The 20 s level leans positive (+48 at 2 h).
  * Z4's saved states (123 GB) are deleted, with the user's OK.
* **Next:**
  * ORG against ORH (ends 16:20) decides on `--no-fresh-states`.
  * Then `solve_new.sh` defaults: e44, 5, 20, 80, 320 s, and that
    flag if it holds.
  * Z5 (`abs/z5_test.sh`): the whole benchmark from zero with them, to
    set against Z4's curve.
  * Production restarts on e44 (`abs/ul40.sh`, 4 workers). It keeps
    its states, since it resumes them across rounds.
* Open for the user: proof steps as lemma axioms (2al), worth at most
  about 39 proofs.

*16 Nov, 23:55:*

* **Since 19:00:**
  * The learned scheduler's +30 on the replay was noise. Two runs with
    the same settings gave 971 and 919. `--sweep-first` (needed from
    zero) gave 940 with context (2aq).
  * The 4-hour replays leveled off near 950 because loops/ALL is the
    13 Nov context. Production's proofs of the missing goals use kNN
    lemmas from later proofs of other originals.
  * With today's proofs, filtered for known leaks (`abs/freshctx.py`):
    1,085 of 1,320 in 1 hour (production 1,111). On the other 8
    holdout originals 3,021 of 3,400 (production 3,092), but 37% of
    the checkable newer proofs there used those originals' goals, so
    that is an upper bound. The 13 Nov context with today's defaults
    gives 2,573.
* **Running overnight:**
  * Z0, from 23:49: the final system from zero on all 51,784 public
    problems (`abs/z0_test.sh`): 12 workers plus the transfer, 10
    hours, without the scheduler (at this size `--sweep-first` would
    run every goal once before any retry). It gives the curve over
    time to set against the totals table above, and any proofs it
    finds that production lacks.
  * Production at 4 workers once LZ4's last runs end.
* Open for the user: proof steps as lemma axioms (2al), worth at most
  about 39 proofs.

*16 Nov, 19:00:*

* **Since 15:15:**
  * From zero, with no other originals' proofs, the loop reaches 890
    of 1,320 replay goals in 1 hour (plain twee 731). The public
    context adds 5–6% (942) (2aq).
  * Two from-scratch knobs failed: 60 kNN lemmas (920) and a 20 s
    level. A 2-minute transfer cycle gave 942 and became the default.
  * Same statement in another theory (2ar): 13 of 323 filtered
    candidates. The source proofs mostly use the axiom that differs.
  * `solve_new.sh` now keeps the new goals' public siblings by default
    (EXCLUDE=goals). That matters for the 1,156 secret goals moved
    out of public originals.
  * Production at 8 workers from 17:20, 4 from 19:50: its 320 s level
    made 0.3 proofs per CPU hour. The instance batch (2.3 an hour) has
    the rest.
* **Next:**
  * A learned-scheduler arm on the replay (LVS, to 19:50).
  * Then 4-hour from-scratch curves, with context (LV4) and from zero
    (LZ4). Production has 1,111 of these 1,320, after 3.5 days of
    loops. 127 of the 158 gap goals with recorded runs took it under
    30 s, so they need context, not long runs.
  * Open for the user: proof steps as lemma axioms (2al), worth at
    most about 39 proofs.

*16 Nov, 15:15:*

* Make the first hour on new problems faster, testing on the replay
  (2aq): budget levels (a 20 s level is running), the transfer's
  cadence, the context.
* For the secret part: `solve_new.sh` with the full public context.
* Production goes on at 12–16 workers, at about 16 proofs an hour.
* Open for the user: proof steps as lemma axioms (2al). It is worth at
  most about 39 proofs now (2an).

*Updated 15 Nov, 12:10.*

* **Since 09:05:**
  * The cascade's retry gate now sees kNN lemma changes (2ae): about
    +160 proofs in 30 minutes, then the rate fell back to 40–60 an hour.
  * Model quality cannot pay online. The oracle model gains nothing,
    with defer-once or with deferral repeated 3 times (2ad, 2af). The
    GNN reaches AUC 0.887 offline and stays there.
  * Twee folds AIM's definitions and Prover9 unfolds them (2af).
    * Unfolded twee proves 7 of Prover9's 9 proofs, and 3 of 10 goals
      Prover9 failed. On random frontier goals it gains nothing.
    * It now runs as the side worker, instead of Prover9.
  * Controls in the same snapshot matter: without them, fresh context
    looks like a method's gain (the folded lemma instances, 2af).
* **Next:**
  * Watch the side worker's rate as it moves away from the nearest
    targets.
  * Tail heads (92 originals, 58% of the unsolved goals behind them):
    folded 0 of 30 at 20 s.
  * Production and side worker use 14 CPUs. The rest is for tests.

*Earlier (15 Nov, 09:05):*

* **Since 04:35:**
  * The learned scheduler with a 10 s first level is in production
    (2ac).
  * Stalled goals resist every twee variant: settings, cross-original
    pools, rm7t, the climber, heads at 320 s.
  * Retraining on the late, long proofs raises offline AUC (0.846 to
    0.894–0.897) but not online results, even with a stricter filter.
    The GNN plateaued at AUC 0.80 (2ad).
  * Prover9, given twee's pools and the sibling lemmas, proves stalled
    goals twee cannot, at about 0.8 per CPU-hour. It now runs as a live
    side worker.
* **Next:**
  * Measure the side worker over a few hours: its proofs, and twee's
    follow-up proofs on goals whose context it changed.
  * If it holds up, try Prover9 settings (max_weight, hint ratios) on
    the P9L failures. Try twee with the Prover9 proofs as hints on their
    neighbours.

*Earlier (15 Nov, 04:35):*

* **Since 14 Nov 22:30:** sketch climbing (2ab) works but is beaten 3× by
  fresh runs on its own targets. The cause was stale round-start
  semantics, fixed by `--fresh-first`. The retry line gap went from 21 to
  80, worth about 2.5× (UL14: 610 proofs an hour). A learned scheduler
  (2ac) orders the fresh runs by predicted success; in an A/B from one
  snapshot it led 60 to 12 after 8.5 minutes.
* **Next:** put the scheduler into production if the hour-long A/B holds.
  Then test a 10 s first level against 20 s with it (77% of fresh proofs
  come within 10 s, 59% within 5 s). Stop the climber, which makes under
  8 proofs per CPU-hour against about 47 for the learned loop.

*Earlier (14 Nov, 22:30):*

* **Done since the last update:** 6 sibling lemmas won (2r) and run in
  the full loop's cascade round 4. rm6t and rm7t brought no online gain
  (2r); the planned rm7t online test was cancelled because its training
  data held proofs of the test goals. Long runs are 1.8–2.0× cheaper in
  CPU (2v).
* **P9loop / Bigloop against resume** (2w, test 2): resume wins on the
  frontier (27 against 18–19 at equal time), and resuming without
  re-scoring the queue beats re-scoring (27 against 23). The full loop
  now resumes without re-scoring. Orderings are kept in reserve for goals
  whose resume has stalled.
* **A resume bug** grew one run to 100 GB; it is fixed, and every run now
  has a 6 GB heap limit (2x).
* **Consider-emulation off** (2y): about 30% less CPU, 76 against 77 on
  u3n150. The full loop runs without it from 20:15.
* **Proof-line distance** (2z): it predicts success (32% within 13 lines
  against 12% beyond 34; by goal gap 22% / 12%). The cascade orders its
  work by it from 20:58.
* **Stalled goals** (2aa): a fresh run with the current hints beats a
  longer resume (20 s fresh 14 proofs per CPU-hour, resume to 320 s 0 of
  13). The cascade retries goals whose hint pool has grown 25%
  (`--retry-hints 1.25`, from 22:28).
* **Sketch climbing** (2ab): `climb.py`. Laws alone add nothing; gap filling (`--fill`) plus true assumptions (siblings, `--knn`) matches fresh 80 s per CPU-hour and reaches other goals. A 64-goal test is running.
* **In-loop retraining** adds nothing online (2u): with the model kept
  fixed, FHL solves 970 after round 1, against 963 for EHL, which
  retrains. The full loop keeps rm4t fixed.
* **Next:** watch the full loop's deepening (round 5, 80 s by resume,
  without re-scoring the queue). For goals whose resume stalls at
  320–960 s, try a restart with a new ordering plus matcher lemmas
  instead of a longer resume. Also look at the hardest originals,
  where the frontier is far from any proof (gap > 3).

## 5. How to run the best system

Build twee from this branch (`cabal build exe:twee`). The commands below
are run in `/project/hintwork`, with `venv` holding lightgbm.

1. **Training data.** Given-rule logs of solved training problems:
   `given.py NAMES OUTDIR --twee BIN --timeout 2`. Rows are label, index,
   rule, and parents.
2. **Rule model.**
   `rulemodel.py DIR1,DIR2 --all --save M.txt --vocab M.vocab`, then
   `lgb2bin.py M.txt M.bin`.
3. **The loop** (round 0: model + kNN hints from training proofs; later
   rounds: hints and 3 proven sibling lemmas from the loop's own proofs):

       loop.py NAMES LOOPDIR --rounds 2 --timeout 2,2 -j 12 --twee BIN \
         --pool knn:30:100 --args= --model --model-fixed M.bin,M.vocab \
         --model-args "--rule-threshold 0.1 --rule-penalty 2" \
         --hints-extra hints/train_pool,hints/tr30_g1_pool --hints-from-start \
         --lemmas 3

   Leave out `--lemmas` for hints only. `summary.py LABEL=LOOPDIR ...`
   counts solved problems per part.
4. **Single long runs:**

       twee P.p --max-time 60 --rule-model M.bin --rule-vocab M.vocab \
         --rule-goal G --hints-file H

   `G` comes from `rulemodel.py goalfiles`, `H` from
   `hintsel.py knnfiles`, and `P.p` with lemmas from `lemmas.py`.
5. **The production loop as of 15 Nov 17:31** (`abs/ul31.sh` in
   /project/hintwork). It is a cascade of fresh 5 s runs ordered by the
   learned scheduler (2ac), with resumes to 80 and 320 s. Proofs that
   other processes append are synced in. Since 07:36 it has gained
   `--retry-knn` (2ae) and unit forms of conditional lemmas (2ae). It
   now uses `--cascade 5,80,320 --sched-pmin 0.011 --sched-pmin-auto
   400` (2ag) on 14 workers. The command below is the 12:17 version
   (`abs/ul28.sh`); `abs/ul31.sh` has the current one:

       loop.py sets/all loops/UL --start 5 --cascade 10,80,320 --cascade-start 0 \
         --cascade-continue --fresh-first --far-retry --retry-gap 3 \
         --sched-model sched/m4.json --sched-max-lgap 320 --sched-retrain 200 \
         --line-gaps 80,80 --retry-hints 1.25 --sync 60 \
         --model --model-fixed rm4t.bin,rm4t.vocab --model-theory \
         --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after \
         --twee twee-e22 -j 12 --reserve 0 --pool original --wall-factor 15 \
         --sched-pmin 0.025 --retry-knn \
         --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider"

   Beside it ran the unfolded-twee side worker (2af, `abs/uflive.sh`),
   stopped at 15:17 when it fell to 0–1 proofs per 24-goal cycle:

       uflive.py loops/UL loops/UFL -j 4 --batch 24 --loop-args "--pool original \
         --wall-factor 15 --model --model-fixed rm4t.bin,rm4t.vocab --model-theory \
         --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee twee-e22 --timeout 20" \
         --twee-args "--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider"

   The model comes from `schedfeats.py loops/UL sets/all F.tsv` and
   `schedmodel.py train F.tsv M.json --drop hints,ofrac,ggap,nfail_c6`.
   The live climber (`climb.py --live`, 2ab) was stopped at 05:10.
   For a new round, use `--cascade-start -1`, so that every goal gets a
   fresh run in the new context first (2ab). Watch memory with
   `abs/memwatch.py 7 45`; twee itself stops at 6 GB (`-M6g`).
   A/B arms (reflink copies of UL) go back with `abs/merge_ab.sh`.
   `merge.py UL DIR...` adds proofs from probe dirs.
6. **Hint generator** (2ah, CPU torch in `venv`):

       venv/bin/python3 hints/gencopy.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
         --test-names sets/ultest --save models/gc1.pt --init-enc models/gen2_3000.pt \
         --novel loops/UL/hints --steps 6000 --threads 4 --batch 8     (abs/gc1.sh)
       venv/bin/python3 hints/gencopy.py eval GIVENDIRS --test-names NAMES --load models/gc1.pt \
         --n 400 --temp 0.7 --pool-dir loops/UL/hints

   In a loop, `loop.py --gen-model models/gc1.pt --gen-script
   gencopy.py --gen-n 400 --gen-temp 0.7` with `--twee twee-e39` (or
   later) and `--resume-requeue` in the twee arguments. A failed level
   saves its context, and the resumed level gets the generated hints.
   `abs/gen_test.sh` is the paired online test.

6. **New problems, from scratch** (16 Nov, `hints/solve_new.sh`; the
   setting of 2aq):

       solve_new.sh NAMES CONTEXT OUT [J [HOURS]]

   * It runs the cascade (5, 80, 320 s, 30 kNN lemmas, 6 siblings, rm4t,
     the learned scheduler) on the goals in NAMES, with J workers for
     HOURS.
   * Beside it, the live proof-step transfer runs on 2 workers every 2
     minutes (XEVERY, 2aq).
   * CONTEXT's proofs are the round-0 context: lemma sources, hint
     pools and transfer sources.
     * By default (`EXCLUDE=goals`) only proofs of the NAMES themselves
       are left out. So the 1,156 secret goals moved out of public
       originals (README) keep their public siblings as lemmas.
     * `EXCLUDE=originals` leaves out every proof of the new goals'
       originals. The replays (2aq) use it to simulate unseen
       originals.
   * Run order (`ORDER`, default `--mix 0.1 --fail-order`, 2at): every
     goal's first fresh run before any repeat, near goals before far
     ones, and a share of the workers for the deeper levels. On the
     whole benchmark from zero it made 37,713 in 2 hours, against
     36,552 without it. On the rp3 replay with today's context it made
     1,095, against 1,085 with the learned scheduler.
   * `SCHED` (default empty) takes the learned scheduler's options, for
     example production's (the comment in `solve_new.sh` has them).
     With it, `--fail-order` is idle. `LOOPARGS` passes other loop.py
     options.
   * The full scheduling pass runs at most once a second
     (`PASS_EVERY`, default 1, 2as). With 0 it runs after every run,
     and on 51,784 goals that left most workers idle.
   * For the secret part, use a snapshot of loops/UL as CONTEXT (all
     public proofs). For replays on public originals,
     `abs/freshctx.py SET OUT` makes a context of today's proofs minus
     those known to use SET's goals, but it cannot catch every leak
     (2aq).
   * The whole public benchmark from zero: `abs/z4_test.sh` (2at; Z1,
     `abs/z1_test.sh`, is the run without the new order, 2as).
   * `AIM_PROB` sets the problem directory. For new problems, use one
     with links to both the public and the new `.p` files.
   * A 2-minute test on 20 lra2aa goals with the clean context proved
     20 of 20.

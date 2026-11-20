# Working record: hint guidance for twee (internal)

Written 17 Nov 2026, 18:08, from the whole session transcript (12 Nov 19:30 to now: 68 user messages,
32 more sent mid-turn, 940 replies, 4,974 tool calls, 24 context compactions), the 334 commits on
branch `hints`, and REPORT.md. REPORT.md is the outward report, with results and numbers. This file is for
resuming the work. It says why each thread was started, how it was done, what came out, where the
pieces are, and what went wrong.

**This file is the map, not the journal.** Each experiment gets its own report in hints/notes/ (user, 17 Nov
18:30: this file read as "a compressed version of REPORT.md"; "write a short report about every experiment we
do"). Those reports carry the detail: the question and who asked, the exact setup, how the goal sets were
chosen, the numbers, the noise, and what the numbers do not show. The index is section 9.

**When resuming:** read sections 1, 2 and 8 first. Before designing anything, grep this file and REPORT.md for
the topic (section 7 lists the mistakes this rule prevents). Add to the log in section 6 when a thread
starts, changes or ends.

The transcript is `~/.claude/projects/-project/06816eaa-f48d-4d65-80b0-498c3b54febf.jsonl` (86 MB).
`~/.config/fc1dev/scratch/twee-record/digest.py JSONL OUT` turns it into a readable digest: user messages,
my replies, tool-call descriptions and the compaction summaries. That directory also holds `user.txt`
(the user's messages), `midturn.txt` (messages sent while I worked), `gitlog.txt`, `sum01..24.txt`
(the compaction summaries) and `errs.txt` (their errors and results sections).

---------------------------------------------------------------------------------------------------------

## 1. The goal, and what the user has asked for along the way

**Goal (12 Nov 19:30, re-set 13 Nov 09:39 as a /goal):** hint guidance for twee on AIM60k. The model is
Veroff-style hint loops: easy problems give hints that guide harder ones, so as to solve as many problems as
possible in the least time.
* Learn from the Prover9-new branches.
* Iterate on small subsets: the about 150 hard originals and the goals derived from them.
* Own branch, frequent commits, interim reports, critical self-review.
* About 20 CPUs and 60 GB RAM.
* One agent: no worker agents. Many twee processes in parallel are fine.

**The user's directions, in order** (what each led to is in brackets):

* 12 Nov 20:35: look at the latest ENIGMA featurizers. [Twee.Enigma, the rule model rm*: REPORT 2b]
* 12 Nov 20:51: hints matter in long hard runs. Veroff stops a run when no hint has matched for many given
  clauses. [--eqhint-stall, later HINTLOG/stallsim: 2c, 2m]
* mid-turn, 12–13 Nov:
  * "doesn't P9 also demodulate hints during the run?" [hints are kept normalised by the oriented rules]
  * "knn because too many hints slow things down? what knn, on what?" [explained: kNN over goal statements]
  * checkpointing as in recent P9 [--dump-state/--load-state, loop.py --resume]
  * ENIGMA and ENIGMAWatch guidance [rule model; ProofWatch hint boosting, neutral]
  * control: Prover9 hint loops on a couple of families [p9loop.py: 2i]
  * the "harder" evaluation: how long runs stay on hints, gaps up to about a minute, let such runs go
    longer [HINTLOG, stallsim, V2 rounds: 2m]
* 13 Nov 09:03: Veroff reorients proofs into SFDF runs (strictly forward, demodulation-free), so hints carry
  no skolems. Did we? Reorientation can be expensive.
  [p9loop --convert/--sfdf: no gain (2n); skolem-free hints from conditional goals (2j)]
* 13 Nov 09:28: **compare runs by abstract time** (inferences, given clauses), never CPU or wall time,
  because the machine load varies. [--abstract-time 2000 everywhere since then: 2k]
* mid-turn, 13–14 Nov:
  * "a twee process took 100 GB, I killed it. 1. prevent that at all cost (kill before, RAM limit),
    2. look into it and fix the growth in twee". [-M6g default heap limit, memwatch.py, the stale-id
    resume bug fixed at the root: 2x]
  * Nigma guidance combined with hints; "we already use enigma-style clause ranking?" [yes: rule model]
  * sketches: extra assumptions, a lattice of assumption sets, climb from easy to the original
    [climb.py: 2ab]
  * the numbers at the top of the REPORT should be totals by time [the summary table]
* 14 Nov 10:05: ENIGMA-style looping (retrain on new, shorter proofs; Mizar60 paper; Deepire), and the
  dynamic GNN of Chvalovsky et al. LPAR 2023; CPU GNNs as in Deepire. [EL/EHL/FHL loops, deepire.py,
  gnn.py: 2u, 2ad]
* 14 Nov 13:14: do long runs slow down? Use the Prover9 branches' indexing. [fingerprint overlap index,
  interreduction filter, 1.8–2x: 2v]
* 14 Nov 14:03: implement Veroff's p9loop and bigloop (AITP 2026 slides BV.pdf, ai4reason.eu/veroff-aim-proof).
  14:37: they also vary the settings, such as orderings. [--p9loop, --p9-orders, --p9-parallel: 2w]
* 14 Nov 20:53: "isn't the name encoding the real goal?" (AIM60k goal files name the line of the
  original Prover9 proof). [--line-gaps, distance in proof lines: 2z]
* 14 Nov 22:39: Veroff adds frequent extra axioms such as commutativity to the lattice pool. [climb.py --laws, --freq]
* mid-turn, 14–15 Nov:
  * retrain the ENIGMA guidance now and then; later long proofs are worth more for training than easy ones
    [rm7t/rm8h on hard proofs: offline +0.05 AUC, online nothing: 2ad]
  * enough data for the dynamic GNN [gnn.py v1]
  * **GNN v2:** symbol-aware (the signature is tiny), mark the conjecture terms, expand the goal constants
    from flattening, dynamic data as Chvalovsky 2023, prefer harder proofs [gnn.py v2: AUC 0.887 offline]
  * BliStr uses abstract proof-search length as a proxy metric for unsolved problems, but don't overdo it
  * a GNN2Seq hint generator after JUrban/E_conj_dev1 (branch vampire4, IWIL paper), dreaming up hints from
    the clause situation [gen.py, gencopy.py: 2ah]
  * "what's our production loop now, and what helps?"
  * add axioms from other problems (Bol loop instead of loop), mathematically relevant, not trivialising;
    dream up axioms with the generator [climb.py --theories, --gen-assume: 2aj]
  * when the strengthened theory is still too hard, strengthen more or weaken the goal; climb up and down,
    as in Korovin's abstraction-refinement paper (978-3-319-94205-6_43.pdf) [--updown]
  * "shouldn't we learn the up/down steps?" [latticedata.py, latticepolicy.py, Thompson sampling: 2ak]
* 15 Nov 09:37: Chvalovsky's GNNs balance positives and negatives in the loss. [pos_weight in gnn.py]
* 15 Nov 18:24: try the conjecture cuts of the IWIL 2026 paper (it helped on Mizar). 18:31: generate cuts in the
  middle of the search from the proof state, like the hints. [--gen-cuts: no gain, 2ai]
* 15 Nov 18:59: "by sketches you mean extra axioms like commutativity, then hints from those runs guide the
  original?" (yes)
* 15 Nov 21:49: "are you keeping notes how the experiments were done in the repo?" [hints/exp/: every
  launch script and goal set is copied there and committed]
* 15 Nov 21:52–21:54: what's a climb without theories; the up step could also add one axiom. [--up-single]
* 16 Nov 10:28: update the report numbers.
* 17 Nov 08:40: "what's the last day's work about?"
* 17 Nov 14:54: **delete Z4's states** (done).
* 17 Nov 15:17–15:22: the user set kernel.perf_event_paranoid=-1 and installed ghc-prof. Profiling works:
  `cabal build exe:twee --builddir=dist-prof --constraint='twee-lib +profile'`. perf still records nothing
  in the sandbox (no /sys).
* 17 Nov 15:52: Veroff limits generated clauses by weight; in E there is **parental guidance** (FroCoS
  2021), a smarter quick prefilter. 15:54: go ahead with it.
* 17 Nov 16:14–16:16: "otter or discount loop?" (DISCOUNT). "We did the freezer for E. Have you read the
  FroCoS paper?"
* 17 Nov (mid-turn): "every new rule is scored against all candidate partners, roughly 840k evaluations
  sounds silly. In E we score only partners that produce an offspring. Did you read the paper?" Then:
  "tell me exactly how the paper does these things".
* 17 Nov 17:30: **try ENIGMA features in Pcat, as in the paper.** 17:40: hashing to a small base, not sparse
  features. 17:44: E's fast hash? 17:54: FNV-1a is fine if fast. Mizar needed hashing for its many symbols
  and paths. 17:56: anonymous features worry me, because AIM has few symbols and they matter.
  "Didn't we discuss all this before?" (yes: the GNN v2 and goal-constant conventions).
* 17 Nov 17:58 and 18:00: keep a more detailed record for internal use; go over the whole session. [this file]

**Decisions waiting for the user:** proof steps of other proofs as lemma axioms (REPORT 2an: worth at most about
39 goals now). Do not do it without approval.

---------------------------------------------------------------------------------------------------------

## 2. Standing rules (the user's, and my own lessons)

Resources and processes:
* About 20 CPUs and at most 60 GB RAM. Twee binaries run with `-M6g` by default (twee.cabal rtsopts).
  Use `abs/memwatch.py 7 45` for loops, and pywatch guards for big trainings: rm6t reached 55 GB, so use
  negmax 150–200.
* **Never `pkill -f` or `pgrep -f | kill`.** Patterns match my own shell, whose command line contains the
  pattern (exit 144, at least six times). Kill by exact PID trees:
  `desc() { for c in $(ps -o pid= --ppid $1); do desc $c; done; echo $1; }`. Find PIDs with
  `ps -eo pid,args | awk` on exact fields.
* No foreground sleeps or sleep chains (the harness blocks them). Wait with an until-loop in
  run_in_background and end the turn. Never start a second waiter for the same thing. Waiters with
  timeouts over 600 s get backgrounded automatically, and "timeout reached" is not completion: check the files.
* **Never edit a running bash script.** Bash reads it by offset (queue3.sh died; solve_new.sh had to be
  restored in place with `git show HEAD~1:... >`). `sed -i` makes a new inode and is safe, but avoid it
  anyway. Tests run private copies: `sed "s|^H=.*|H=/project/twee/hints|" solve_new.sh > PRIVATE`.
* Install loop.py edits atomically: test on a scratch copy with production's exact options, then `.tmp`,
  py_compile, mv. A shadowed variable name crashed production three times: `k`, the `heads` set, and `nf`
  (UL40 died at 16:24 on 17 Nov).
* **No `rm -rf` on variable paths** (memory, 15 Nov; I broke it once on 17 Nov). Remove only literal paths,
  and refresh into new empty directories.
* Every new script gets `chmod +x` (z4_test.sh did not).
* The session scratchpad (/tmp/claude-1001/...) is wiped when the session ends, and every process the
  session started dies with it. Keep anything needed later in /project/hintwork or
  ~/.config/fc1dev/scratch. On 17 Nov 18:05 the PG testbed was copied to pg/tb, its scripts to pg/tm, and the
  paper's text to pg/paper.
* Run Python with `-I` in the scratchpad: a stray copy.py there shadows the standard library.

Method:
* Compare by abstract time (`--abstract-time 2000`: 2,000 critical pairs considered = 1 s; deterministic,
  6/6 identical). Report CPU separately, measured as user + sys of the twee processes. Wall time on this
  shared machine varies by about 15% (load 35–45).
* **Noise:** identical whole-set runs differ by about 1% (half1 2 h: 185 of about 18,400). The rp3 replay
  repeats to within 1, but scheduler runs vary by about 25 to 50 (971 against 919 with the same settings).
  r1sim varies by ±3. Replicate before claiming a gain. Three of my claims were noise:
  * the scheduler's +30;
  * KN60's 9/150 (the replication gave 8/300 against 10/300);
  * Thompson sampling at 0 against 8, p = 0.007 (an artefact of assigning arms per target).
* **Controls:** every new mechanism gets the cheapest obvious control at the same cost. The live climber looked
  good until a plain fresh-retry control made 3x its proofs per CPU hour (2ab).
* **Leaks:** check that test goals' proofs are not in training data, pools or contexts.
  * rm7t was trained on the test goals' proofs: cancelled.
  * 10 ho3_unsolved problems were in all_r0_hard.
  * HO8U's context leaked 37% (reported as an upper bound).
  * `loop.py --init` imports only round-0 rows, so snapshots need column 2 set to 0. ULsM's probes were
    invalid because of this.
* **New twee flags must be off by default, with identical output when off.** Check results, WORK
  (considered, rules) and hints on 150–200 captured runs before using a binary.
* Install binaries under new names: /project/bin/twee-eNN, never overwritten (a running binary gives "text
  file busy", and old results must stay reproducible). Wrappers such as twee-pg add `$TWEE_PG_ARGS`.
* Experiment launch scripts live in /project/hintwork/abs and pg. Copy them and the goal sets into
  /project/twee/hints/exp/{abs,pg,sets} and commit them with each REPORT section. The header comment holds
  the real start time (check `date`; I wrote wrong times at least six times) and the reason.
* Commit often on branch `hints`. Messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
* Report in plain words, never by internal labels alone. Never put the user's email or name into outside requests.
* Before designing a feature, read the paper it comes from (section 7.1). If a paper is cited, read the relevant
  sections fully, then write down its exact method here before implementing.
* Reuse conventions that already exist (section 4.4). Grep REPORT.md and this file first.

---------------------------------------------------------------------------------------------------------

## 3. Where things are

Repositories and directories:
* `/project/twee`: twee, branch `hints` (my branch, 334 commits since 12 Nov). The source is in src/Twee.hs
  (main loop, hints, PG), src/Twee/Enigma.hs (forest evaluator, ENIGMA features), src/Twee/Index (FPIndex),
  executable/SequentialMain.hs (flags) and hints/ (all Python and REPORT.md).
* `/project/hintwork`: working directory, not versioned; scripts are copied to hints/exp. Python venv:
  `venv/bin/python3` (lightgbm, torch 2.15 CPU; install with uv, the venv has no pip).
  * `loops/<NAME>/`: one loop each, holding solved.tsv, hints/, given/, states/, goals/, results per round,
    config.json, and NAME.log.
  * `loops/UL` is the production loop. Its states take 208 GB (17 Nov). Z4's states were deleted on the
    user's word.
  * `sets/` (101 goal sets), `models/` (rm*, gnn*, gen*, gc*, lattice*), `sched/` (scheduler models),
    `given/` (given-rule logs), `abs/` (launch scripts, memwatch.py, curve.py, setcurve.py, zstat.py, merge_ab.sh),
    `pg/` (parental guidance).
* `/project/AIM60k`: the benchmark. 51,784 public goal problems in about 129 originals; holdout.names has
  5,880. Goal files name the line of the original Prover9 proof (abs/goal_lines.tsv).
* `/project/Prover9-new`: branches studied in REPORT 2d; built serially (make -j4 races).
* `/project/bin`: the binaries.

**Twee binaries** (each adds to the one before; off-by-default flags):

| binary | date | what it added |
|---|---|---|
| h1–h9 | 12 Nov | first hint matching versions |
| e1–e13 | 12–13 Nov | rule model, given log, stall, state resume, ProofWatch, binary forest, FNV-hashed rule features, generalisation matching |
| e14 | 13 Nov 09:15 | HINTS-HYP: no generalised lemmas that depend on a conditional goal's hypothesis |
| e15 | 13 Nov 09:31 | --abstract-time |
| e16 | 13 Nov 10:10 | HINTLOG, --eqhint-stall-cps |
| e17 | 13 Nov 10:58 | resume counts old matches silently |
| e18 | 13 Nov 11:18 | --max-cpu (CPULIMIT with full output) |
| e19 | 13 Nov 12:50 | task costs in abstract time (newTaskCost) |
| e20 | 13 Nov 16:17 | resume signature fix |
| e21 | 13 Nov 17:47 | --multi-goal |
| e22 | 13 Nov 18:33 | RESUMETIME, --no-resume-requeue. **The file /project/bin/twee-e22 was overwritten in place** so running loops picked up new code with an identical search: e27's code at 14 Nov 13:39, e31's at 16:15, and the 100 GB resume fix at 18:44. The original e22 is twee-e22.orig. Production's binary until 17 Nov |
| e23–e29 | 14 Nov 13:18–14:05 | e23 --progress; e24 fingerprint overlap index (Twee/FPIndex.hs); e26 interreduction filter; e27 --queue-cost (so e27 has all three) |
| e30–e36 | 14 Nov 18:07–19:45 | e30 --print-hint-matchers (P9loop); e31 USEDAXIOMS; debug and profile builds (e32prof uses twee's own stamp profiler, not GHC -prof); the 100 GB resume fix; --eqhint-consider-open |
| e37 | 14 Nov 22:49 | HINTS-ASSUMED (sketch gap filling) |
| e38 | 15 Nov 10:16 | --rule-defer-max |
| e39 | 15 Nov 14:34 | --print-given-unsolved |
| e40, e41 | 15 Nov 15:25–15:33 | --eqhint-instances (negative) |
| e42 | 16 Nov 11:01 | --cp-model-factor (negative) |
| e43 | 17 Nov 11:10 | no state dump for a solved problem |
| e44 | 17 Nov 14:47 | incremental hint normalisation (−11% CPU) |
| e45 | | slower, deleted |
| e46–e49 | 17 Nov 16:20–16:57 | parental guidance and freezer (--pg-threshold, --pg-log); e48 is the sum-filter binary of the A/B |
| e50 | 17 Nov 17:00 | --pg-model, additive forest, pgRuleFeatures |
| e51 | 17 Nov 17:26 | the PG check after unification and before simplifyOverlap, as in E |
| e52 | 17 Nov 17:32 | Pcat on the rule model's ENIGMA vocabulary |
| e53 | 17 Nov 17:43 | hashed ENIGMA keys, --pg-enigma B, --pg-anon |
| e54 | 17 Nov 17:59 | ENIGMA keys on the goal-constant-expanded rule with real names; --pg-anon removed; PGR field `E<keys>` |
| e55 | 17 Nov | additive Pcat ENIGMA parental model (PGEnigmaAdd) |
| e56 | 17 Nov 21:59 | e55 + --print-goal-nf N: on failure, the N smallest normal forms of each goal side (GOALNF L/R lines); use with --no-flatten-goal (exp4 nf.py) |
| e57 | 18 Nov 05:20 | e56 + --ground-joining-branch-limit B: assume not ground joinable once the case split has more than B branches (exp6, runs that never end) |
| e58 | 18 Nov 06:11 | e57 + --eqhint-subsume: a critical pair or rule that subsumes a hint matches it (Prover9's semantics; exp7) |
| e59 | 18 Nov 06:17 | e58 with the subsumption index in an IntMap of hashed keys and a size check before matching: same results on 3 goals, CPU over flag-off +15% instead of +30% |
| e60 | 18 Nov 07:06 | e59 + the parental filter judged before unification again unless it is a full forest (e51 had moved it after unification for all filters: +10% CPU, +8% memory for the same pairs with the sum filter). On aa1_45_c 292 at 80 s: e48 83.0 s, e60 86.5 s, e59 96.6 s; output identical to e48 |
| e61 | 18 Nov 07:25 | e60 with e50's strict rejected set for the early parental check (e60's lazy memo cost 6-8%): e50's speed; output byte-identical to e50 on 8 goals; resumes e50 states. **Production since 18 Nov 07:30** (twee-pg61) |
| e62 | 19 Nov 17:07 | e61 plus `--pg-order F` (exp35): a new pair's score × F ** sigmoid(q1 + q2), from the parents' stored rule-model scores, two lookups per pair; F = 1 (default) byte-identical to e61 on 3 goals. Wrapper `twee-pg62` (e62 with $TWEE_PG_ARGS) |

Wrappers: `twee-pg` (e48 with $TWEE_PG_ARGS), `twee-pg50` (e50 with $TWEE_PG_ARGS; production until 18 Nov 07:30), `twee-pg61` (e61 with $TWEE_PG_ARGS; production since 18 Nov 07:30).

Models:
* `models/rm4t.bin/.vocab`: the rule model in production. It is a LightGBM ENIGMA model on given-rule logs,
  with a theory block, and runs with `--rule-threshold 0.1 --rule-penalty 2`: a new rule predicted useless
  is deferred once, re-queued at its score times 2.
* rm7t and rm8h are better offline but not online (2ad). gnn2.pt is GNN v2 (0.887 offline, never online,
  because model quality does not pay online, 2af).
* gc1.pt is the hint generator (copy model).

Main scripts in hints/:
* run.py: parallel runner.
* loop.py: the loop, the cascade and every scheduling flag.
* Hints: hintlib.py, hintsel.py (kNN hints).
* Lemmas: lemmas.py (sibling, kNN and subset lemmas, LemmaIndex).
* Rule model: given.py, rulemodel.py, lgb2bin.py.
* Scheduler: schedfeats.py, schedmodel.py.
* Other tracks: climb.py (sketches and the lattice), latticedata.py, latticepolicy.py, climbab.py,
  transfer.py (proof steps of other proofs), merge.py, p9loop.py, p9twee.py, uflive.py and unfold.py,
  gnn.py, gen.py and gencopy.py, deepire.py, stallsim.py, summary.py, timecurve.py.
* solve_new.sh: the system for new problems.
* PG: pgdata.py, pgtrain.py, pgdata_enigma.py, pgtrain_enigma.py.

---------------------------------------------------------------------------------------------------------

## 4. The system as it stands

### 4.1 What a run is
Each goal is one twee run on the goal's problem.
* **Lemmas:** the 6 nearest proven sibling goals of the same original, on either side by goal order, as
  axioms. Plus the 30 kNN proven goals of originals with the same axioms or a subset of them (lemmas.py
  LemmaIndex: idf-weighted Jaccard on term-shape features). Conditional goals with a definitional hypothesis
  enter as unit forms.
* **Hints:** the pool of all proof lemmas of the original's solved goals (`--pool original`), as equations
  with goal constants expanded and skolems as variables. They are kept normalised by the current rules. A
  critical pair matching a hint gets its score scaled down.
* **Rule model:** rm4t with a goal block (`--rule-goal`).
* **Settings:** `--abstract-time 2000 --no-resume-requeue --no-eqhint-consider --max-cpu ...`. `--wall-factor 15`
  sets the wall-clock safety limit.

### 4.2 The cascade (loop.py)
* Levels 5, 20, 80 and 320 abstract s. The first is a fresh run; deeper levels resume the saved state, or run
  fresh when the hint pool grew 25% (`--retry-hints 1.25`) or the kNN lemmas changed (`--retry-knn`).
* A goal becomes eligible when its context changes: a nearer proven goal below it (line gap at most 80
  proof lines, `--line-gaps 80,80`), new hints, or new kNN lemmas.
* Order: `--mix 0.1 --fail-order`. Each kind (near retries, far goals, deeper levels) keeps a share of the
  workers, and the rest go to the best yield over the last 300 runs. Fresh runs go fewest failures first,
  then near before far.
* `--sync 60` takes in proofs that side workers append. `--pass-every 1` limits the full scheduling pass,
  with an adaptive 8x interval.
* `--no-fresh-states`: no state dump for fresh runs, which saves 22% of a failing run.
* The learned scheduler (`--sched-model`) is off by default, because at scale its gain was noise.

### 4.3 Production
* No side workers. Prover9 with chain hints (the P9C side worker, abs/p9c.sh and p9c4.sh, 16:46–19:38) is now the
  cascade's `p9` level.
* `abs/ul63.sh` since 19 Nov 10:16:50 (UL63.log): ul62 plus k400@0, k200s12@0, hl@0 (loop.py 5fc6b48), m7t@0, m4b@0
  (4d3baca), r2@0, nopg@0 and nom@0, all explored. ul62 ended at new=17+ in 11 minutes: in its first 10 minutes
  Vk200@0 proved 14 in 1.01 CPU h (13.8 per CPU hour), all after Vk100@0 had failed in the same context, and Vs12@0
  5 in 1.02.
* `abs/ul62.sh` 19 Nov 10:05:50 - 10:16 (UL62.log): ul61 plus k200@0 and s12@0 (loop.py e2986e3), with `--explore 1`
  (3f95f59) for the lemma-set variants in place of hand-set priors. ul61 ended at new=49 in 46 minutes, after the
  cascade. Its yields: Vkd@0 9 in 1.83 CPU h (4.9 per CPU hour), Vk100@0 28 in 7.73 (3.6), Vkp@0 0 in 0.54, L0 3.4.
* `abs/ul61.sh` 19 Nov 09:19:05 - 10:05 (UL61.log): ul60 on 19 workers with the priors Vkp@0 = Vkd@0 = Vk100@0 = 9.
  ul60 ended at new=209 in 74 minutes on 12 workers.
* `abs/ul60.sh` 19 Nov 08:04:50 - 09:19 (UL60.log; `J=12` while exp27 runs, then a restart with the default 19): ul59
  plus three lemma-set variants at 5 s, kp@0 (use counts), kd@0 (proof dependencies) and k100@0 (loop.py 92d60c4,
  priors 3 each), and `--knn-refresh 600` (portfolio review, 19 Nov). ul59 ended at new=224 in 47 minutes.
* `abs/ul59.sh` 19 Nov 07:17:30 - 08:04 (UL59.log): ul58 on 12 workers, with `--relabel-until 103427` hardcoded.
  ul58 ended at new=177 in 74 minutes.
* `abs/ul58.sh` 19 Nov 06:02:46 - 07:17 (UL58.log; its first results row is 103428, 1-based, and `--relabel-until`
  103427, 0-based). A **restart must keep `--relabel-until 103427` fixed**: the script computes it from the file's
  length, so a later script must hardcode it. ul57 with the cascade 5,40,80,160,320 (loop.py 1bb0a0f). The 40 s
  chain level is the old 80 s run's first half: ul56's L1 proofs came at a median of 29 abstract s, 50 of 81 within
  40 s, so 1.73 per CPU hour against 1.45. The variants stay at 80 s after the 160 s level. Old rows are relabelled
  by budget (L1=L2, L2=L3, L3=L4). The A/B test exp26 goes on.
* `abs/ul57.sh` 19 Nov 05:52:34 - 06:02 (UL57.log, first results row 102781): ul56 restarted for loop.py 516f416,
  with the A/B test exp26 (`--ab-args="--cp-renormalise-threshold 1000"`: half the goals' deep runs never renormalise
  the queue; rows ab=1; [notes/2026-11-19-queue-renorm-ab.md](notes/2026-11-19-queue-renorm-ab.md)). The restart flagged 1 goal as pool-grown (the fixed
  check). ul56 ended at new=289 in 5 h 52 min.
* `abs/ul56.sh` 18 Nov 23:59:50 - 19 Nov 05:52 (UL56.log): ul55 restarted for loop.py 119c3d1.
  * Variant levels are optional attempts. A goal's next attempt is its eligible option of highest live yield: its
    next cascade level, or any untried variant after a level it ran. Goals far from the frontier choose among the
    fresh level's variants only.
  * Results rows carry the run's context (`c=` hash, column 7). Replay skips rows of other contexts and starts a goal's
    attempts over at each fresh run. The old replay kept the round's highest level, so 892 unsolved goals reopened by
    new proofs had lost their deeper levels at each restart.
  * Smoke test: hints/exp/optvar_smoke.sh on 3 nil3_15 goals at cascade 1,2,4,8.
  * First hour (01:05): 8300 runs, new=90. L0 11.4 per CPU hour, 60 lemmas at 5 s 3.2, unfolded 5 s 1.2. Then the
    80 s chain runs took over, using about 2 GB each.
* `abs/ul55.sh` from 18 Nov 22:39:20 to 23:59 (UL55.log, 10,350 runs, **new=184 in 80 min** on 19 workers): ul54 with
  variant tiers (loop.py a0a4486). The variants after a cascade level are taken by current yield, each once per
  context, and replay records the tried ones.
  First hour (23:40): 8350 runs, **new=146**. L0 17.5 per CPU hour (mostly reopened goals), 60
  kNN lemmas at 5 s 1.3, unfolded 5 s 6.2; no 80 s runs yet. Solved 45,901 (holdout 5043).
* `abs/ul54.sh` from 18 Nov 21:35:49 to 22:39 (UL54.log, 7050 runs, new=37 in 63 min on 19 workers): ul53 on **19 workers** with `nom` (no rule model, 80 s) as the last
  variant before 320 s. exp22 is done; the only other job is transfer.py live (xfrlive2, -j 2, about 0.2 CPU on average).
* `abs/ul53.sh` from 18 Nov 20:34:50 to 21:35 (UL53.log, 4600 runs, **new=56** in 60 min on 16 workers; 53 in its
  first 46 min, while the 5 s levels had untried goals): ul52 with Prover9 + chain as the cascade level `p9` after k60 (loop.py
  bc450f8). Proofs and inputs go to loops/UL/p9var. Levels: L0, Vunf@0, Vk60@0, L1 80, L2 160, Vk60, Vp9 (60 s
  Prover9), Vunf, Vtwo, L3 320.
* `abs/ul52.sh` from 18 Nov 20:27:05 to 20:34 (UL52.log, 400 runs, new=5 in 6.6 min): ul51 restarted for memoised hint unfolding (loop.py a5949d1).
  ul51 was prep-bound: the threads unfolded 20-30k hints a run in Python, 5-6 s each, under the GIL, so 1-3 of its
  16 workers ran twee.
* `abs/ul51.sh` from 18 Nov 20:15:19 to 20:27 (UL51.log): ul50 on **16 workers** (exp20 done). The 80 s variants after the
  160 s level are k60, unf, two; sub and nopg are dropped (0 of 68 each after the 160 s run, exp20). Priors are the
  conditional yields (loop.py fc74100).
* `abs/ul50.sh` from 18 Nov 19:38:58 to 20:15 (UL50.log, new=7 in 36 min on 10 workers): ul49 on **10 workers** with `nopg` as the last 80 s variant. P9C was
  stopped at 19:38 (1 proof in 217 runs on 4 workers, 0.28 per CPU hour), and its CPUs moved here.
* `abs/ul49.sh` from 18 Nov 18:53:40 to 19:38 (UL49.log, new=8 in 43 min on 6 workers): ul48 plus an 80 -> 160 s resume level right after the 80 s chain run
  (`--cascade 5,80,160,320 --variants-after 2`), `--pass-every 1`, and conditional priors (loop.py baa52c7). Levels:
  L0 5, Vunf@0, Vk60@0, L1 80 (chain, fresh), L2 160 (resume), Vk60, Vtwo, Vunf, Vsub (80 s each), L3 320 (resume).
* `abs/ul48.sh` from 18 Nov 18:30:32 to 18:53 (UL48.log, new=5 in 22 min on 6 workers, deep class 6 per worker-hour): ul47 on **6 workers** with `--variants unf@0,k60@0,k60,two,unf,sub
  --ratio-order` (loop.py b67d828). Every goal whose fresh run failed, near the frontier or not, gets an unfolded and a
  60-lemma 5 s run (exp21: unfolding 4 of 300 at 3.8 per CPU hour). The deep queue is ordered by the next level's
  estimated yield, heads first. The 2 extra workers come from exp19, paused.
* `abs/p9c4.sh` from 18:25:55 to 19:38 (P9C4.log): P9C on 4 workers; 1 proof in 217 runs, stopped.
* `abs/ul47.sh` from 18 Nov 17:13:49 to 18:30 (UL47.log, new=14 in 76 min on 4 workers): ul46 plus `--variants k60,two,unf,sub` (loop.py 551f563): after a
  failed 80 s chain run, four more 80 s fresh runs in the same context (60 kNN lemmas, the two-sided chain,
  definitions unfolded, subsumption matching) before the 320 s level; results rows Vk60/Vtwo/Vunf/Vsub. The portfolio
  task: [notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md). P9C keeps running beside it.
* `abs/ul46.sh` from 18 Nov 14:46 to 17:13 (UL46.log, new=12; its header says 14:50, written before the start): ul45 on 4 workers
  with chain_records2.tsv (+40 records of merged experiment proofs, 39,884 in all). ul45 had proved nothing from
  13:20 to 14:37 (its 5 s classes had no candidates; all 8 workers on 80 s chain runs), then 2 by 14:46; new=22 in all. The other 4
  workers run exp18.
* `abs/ul45.sh` from 18 Nov 12:02 to 14:46 (UL45.log): ul44 with loop.py running the chain level (80 s) **fresh** with the
  chain, and `--chain-since-row 47530`, so goals whose deep runs all predate the chain (3,845 rows capped) get a
  fresh 80 s chain run.
* `abs/ul44.sh` from 18 Nov 09:47 (UL44.log): ul43 on 8 workers instead of 4 (load had fallen to 13.5). Its first
  start (09:23) died at 09:29 (log loops/UL44a.log): loop.py could send a goal deep and then fresh in the same
  pass. The two runs shared tmp/<goal>.hints (the fresh run read the chain), and the second unlink failed.
  Fixed in loop.py at 09:47, so production was down 09:29-09:47.
* `abs/ul43.sh` from 18 Nov 08:28 (UL43.log; 90 new in 50 min on 4 workers): ul42 with `--chain-level 1 --chain-records
  /project/hintwork/chain_records.tsv`. The 80 s level (which resumes the 5 s run's state, so the chain reached only new pairs; corrected 11:55, fixed in ul45) takes the
  goal's chain (hints/sibchain.py: the proofs of its 10 nearest proven siblings below, expanded through the
  proven goals they used) instead of the pool ([notes/2026-11-18-chain-hints-unsolved.md](notes/2026-11-18-chain-hints-unsolved.md), exp3's K arm).
  The records file is read at start; rebuild it after merges (merge.py copies hint files, not outputs):
  `python3 hints/sibchain.py --build chain_records.tsv.new --extra exp3/out_K@320,...` then mv (08:31: 39,643
  records, 12 of them from the merged exp3/exp8 outputs).
* `abs/ul42.sh` from 18 Nov 07:30 (UL42.log): ul41 with `--twee /project/bin/twee-pg61` (twee-e61) and
  `TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"`, on 4 workers. The branch limit stops
  one-step hangs in ground joining ([notes/2026-11-18-ground-joining-hangs.md](notes/2026-11-18-ground-joining-hangs.md)); the search is otherwise identical.
* Before that, `abs/ul41.sh` from 17 Nov 17:25 (UL41.log): ul40 (e44, the 17 Nov defaults) plus the PG sum filter,
  via `twee-pg50`.
* Solved: 44,870 of 51,784 at 18:05 on 17 Nov (holdout about 4,900; count the distinct goals in
  loops/UL/solved.tsv). Plain twee at 4 s gets 31,060.
* The production lineage is in the headers of abs/ul3.sh … ul41.sh, each with its reason and time:
  * ul3–ul10: rounds 3–5, adding --no-resume-requeue, --no-eqhint-consider, line gaps, retry-hints and sync.
  * ul12–ul14: fresh-first, far-retry, line gaps 80.
  * ul15–ul31: the learned scheduler, heads-first (reverted), a 5 s first level, retry-knn.
  * ul32–ul38: CPU shares for side batches, 30 kNN lemmas.
  * ul39: --mix. ul40: e44. ul41: PG. ul42: e61 and the ground-joining branch limit. ul43: chain hints at 80 s. ul44: -j 8. ul45: fresh chain level, --chain-since-row.
* For new problems, `hints/solve_new.sh NAMES CONTEXT OUT [J [HOURS]]` runs the same cascade. The live
  proof-step transfer runs beside it every 2 minutes. Its defaults are TWEE twee-e44, CASCADE
  5,20,80,320, STATES --no-fresh-states, and ORDER `--mix 0.1 --fail-order`. REPORT section 5 explains
  EXCLUDE, SCHED, LOOPARGS and AIM_PROB. **REPORT section 5 item 5 still shows the 15 Nov production
  command; the current one is ul45.**
* From zero on the whole benchmark (Z4, abs/z4_test.sh): 15,398 at 10 min, 35,511 at 1 h, 37,713 at 2 h,
  38,044 at about 4 h.

### 4.4 Conventions to reuse (do not re-decide)
* **Goal constants:** twee flattens goals (e.g. `ld(x0,e)` becomes a constant `ld2`).
  * Before matching anything, flattening constants become their definitions and skolems become variables:
    `expandGoalConsts st_eqhints`, with cycles and size capped by setEqHintGoalConsts.
  * Hints, given logs, rule-model features and GNN v2 all use this expanded form.
  * Every feature of a rule or clause is computed on the expanded rule, with real symbol names. The AIM
    signature is tiny (about 9 symbols) and the symbols matter, so no anonymous features (user, 15 Nov 09:05
    for the GNN; again 17 Nov 17:56). Since e54, PG's ENIGMA features follow this rule.
* ENIGMA features are keyed by FNV-1a hashes of the feature names (twee ff4c1c6, 12 Nov). The rule model maps
  them through its vocabulary. PG folds them to bucket `key mod B`.
* Hints from conditional goals that depend on the hypothesis go to HINTS-HYP and never into pools
  (false when generalised).
* The proof-line distance between goals, not goal-number distance, predicts transfer.
* A pool's hints count from proofs of unconditional goals only. Old conditional-goal pools carry false
  hints such as X0 = X1.

---------------------------------------------------------------------------------------------------------

## 5. What helped, and what did not (one line each; numbers in REPORT)

Helped, in rough order of size:
* the online loop with lemmas from proven siblings: the largest effect (2g, 2o; the ablation in 2q: lemmas
  49, plain 28);
* the rule model rm4 and rm4t (2b, 2q);
* kNN lemmas from same-axiom and subset theories (2l), and 30 rather than 10 (2am);
* hints (2q: +9–10 over lemmas alone, overlapping ENIGMA);
* the cascade (90 against 69) with fresh retries when the context changes (2p, 2aa, 2ab, 2ae);
* the speed work: fingerprint overlap index and interreduction filter 1.8–2x on long runs (2v), consider-emulation
  off (−25% CPU, 2y), e43, e44, --no-fresh-states (2au);
* the scheduling order: line gaps (2z); --mix and --fail-order from zero (2at);
* proof-step transfer, 43 proofs per CPU hour on its first batch (2al);
* PG with the sum filter: 52 against 29 on the 200 hard goals, and +900 at 50 minutes on half1 (2av; the A/B
  is still running).

Neutral or negative *in count* (18 Nov, the user: many of these are complementary, with unique solutions, and belong in
a portfolio; [notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md) lists each one's share):
* ProofWatch boosting; parent features; generalisation matching; hint reranking; frequency-weighted boosts;
* hint axioms; multi-goal search; SFDF reorientation; the stall cutoff at short limits;
* retraining on hard proofs and the oracle rule model online;
* GNN online (never deployed); Deepire;
* repeated deferral; the rule model ordering the queue (--cp-model-factor);
* hint instances; the hint generator (it reproduces pool lemmas); conjecture cuts;
* sketches and climbing as production (about 1–2% of climbs prove; useful only as a filler);
* learned lattice moves (underpowered); heads-first at 320 s;
* more than 30 kNN lemmas; MaSh-style lemma dependencies; lemma-pop; hints from kNN lemmas' proofs;
* a 20 s level from scratch; --orig-rate; --fail-reset;
* the learned scheduler at scale (noise);
* the additive PG model in twee (37–39 against the sum's 52);
* GC flags; the simplify pre-scan; --max-term-size.

Why things fail online when they win offline: twee's search is chaotic, so any change re-randomises which
hard goals fall. Model quality beyond rm4t buys nothing, even with an oracle (2ad, 2af). What pays is
context (lemmas, hints from nearby proofs), cost (faster runs mean more runs), and order (first runs before
repeats).

---------------------------------------------------------------------------------------------------------

## 6. Log by day (why, how, outcome)

### 12 Nov (19:30–24:00): hints in twee, the loop, the rule model
* Why: the goal. How:
  * **st_eqhints:** canonical hint variants in both orientations, normalised by oriented rules, with all
    forms remembered.
  * **CP matching:** a match gives score × eqhint-factor + weight.
  * **Fingerprint prefilter:** matching overhead fell from 30% to 7%.
  * **Goal-constant expansion:** generalised hints never matched under flattening without it.
  * **--eqhint-requeue:** re-simplifies the queue on new matches, like P9 back-demodulating sos.
    Self-replay: 2,283 rules fell to 334.
  * **Scripts:** loop.py, run.py, hintsel.py (kNN by goal statement).
* The user pointed at the ENIGMA featurizers. So: Twee.Enigma (a LightGBM evaluator, enigmatic features
  matching hints/enigfeats.py), the rule model with a one-time deferral, given logs, the stall cutoff, state
  resume, ProofWatch, and the binary forest format (load 0.07 s against 0.39 s). Deferral is keyed by the
  canonical equation, and features by FNV hashes.
* Outcome: the rule model is the big gain (holdout at 2 s: 3,049 → 3,177); hint selection recall is capped
  near 0.84.

### 13 Nov: lemmas, the full benchmark, controls, abstract time, harder eval
* Lemma import (proven siblings as axioms) and the first full benchmark: plain 31,060; loop + lemmas 33,249.
* Prover9 control on 2 families: P9 is a good hint user, but twee without hints is far ahead (2i).
* Hint soundness check: 807/814 sampled hints are theorems. The 6 false ones came from conditional goals,
  and HINTS-HYP fixes them (e14).
* User: abstract time → --abstract-time (e15), task costs (e19).
* User: harder eval → HINTLOG, stallsim, the V2 rounds (whole-pool hints on 68 hard goals: 48 → 64 over 4
  rounds). Runs stay on hints, and failures die on the CPU cap while still on hints.
* Axiom groups and subsets: the 129 originals use 68 axiom sets, and 66 have strict subsets among the
  others. So kNN lemmas from same or weaker theories are sound: r1sim 92 → 176 (2l).
* SFDF (user): LADR prooftrans expand/directproof is linear; the search-based conversion converts few. No gain
  either way (2n).
* Resume fixes (e17, e20); online pools (+25%); the full-benchmark online loop UL started. Multi-goal search lost.

### 14 Nov: cascade, ablation, speed, P9loop/Bigloop, RAM, sketches
* Cascade 90 against 69; 6 sibling lemmas beat 3; 2x2x2 ablation (2q).
* ENIGMA loop (user): retraining adds +0.03 AUC offline and nothing online; fixed model + hints beats in-loop
  retraining (2u). Deepire-style model weak.
* Slowdown (user): fingerprint index, the interreduction filter, queue cost (2v).
* P9loop/Bigloop (user, with orderings): resume beats them on the frontier; no requeue wins (2w).
* 100 GB (user): stale symbol-id tables on resume made goal-constant expansion cyclic. Fixed at the root;
  -M6g by default (2x).
* Consider-emulation off (2y). Line distances (user's remark on goal names, 2z). Stalled goals: fresh runs
  with new hints beat resumes (2aa).
* Sketch climbing (user): climb.py with laws (user: commutativity), frequent equations, gap filling, sync and
  live side workers (2ab).

### 15 Nov: scheduling, GNN, generator, cuts, theories, lattice learning
* Self-correction: the climber's gain was the missing fresh-retry control, which led to --fresh-first and
  --far-retry.
* The learned scheduler: A/B 69 against 22 at the time (2ac); later found to be noise at scale.
* Tail heads analysed; heads-first negative.
* GNN (user: Chvalovsky, balancing; v2 symbol-aware): 0.887 offline, not deployed (2ad).
* The stall was an artefact of a frozen kNN index; --retry-knn gave about +160 in 30 minutes (2ae).
* Unfolding definitions (twee folds them; Prover9's proofs unfold): a side worker for a while (2af).
* The 5 s first level beat 10 s: 33 against 20 (2ag).
* Hint generator (user: GNN2Seq): pointer/copy decoders on CPU. It reproduces pool lemmas, and the novel
  recall plateaus at 1–2% (2ah).
* Conjecture cuts (user: IWIL 2026): no gain. AIM's sibling chain already supplies the oracle cuts (2ai).
* Stronger theories and up/down climbing (user: Bol loops, Korovin): family results 3 against 3, but on
  different goals (2aj). Learned lattice moves and Thompson sampling: underpowered (2ak).
* hints/exp created (user asked about notes in the repo).

### 16 Nov: transfer, lemmas, replays, from scratch
* Goals that are steps of existing proofs get those proofs' steps as hints: 32/101 at 43 per CPU hour (2al).
  The live transfer worker followed.
* An identical-goal bug fixed in LemmaIndex; 30 kNN lemmas in production (2am).
* Where proofs come from (2an). A proved tail head raises its original's later rate only from 0.43 to 0.53
  goals an hour, so the head climber was stopped.
* Replays of unseen originals from scratch (2aq): the context is worth 5–6%. solve_new.sh was born.
* The scheduler from scratch starved originals without proofs, so --sweep-first. Its "+30" was noise.
* The same statement proven in another theory: 13/323 (2ar).
* Z0 (the whole benchmark from zero) was dispatcher-bound: the ctx cache, the select memo and --pass-every (2as).

### 17 Nov: order, speed, parental guidance
* --mix and --fail-order (2at): Z4 reached 37,713 at 2 h against 36,552. --fail-reset and --orig-rate gave no gain.
* The tail needs longer runs; hint statistics do not predict which runs succeed (2au).
* Speed: e43 (no dump for solved), --lean-states and then --no-fresh-states, e44 (incremental normalisation),
  and a profile with ghc-prof: pair generation and normalisation take about 55%.
* ORG/ORH (2 h, half1): --no-fresh-states 18,476 against 18,374, and 4,792 runs an hour against 4,268.
  Adopted, with CASCADE 5,20,80,320.
* **Parental guidance** (user, 15:52). See 6.1 for the full thread.

### 6.1 Parental guidance, in detail (17 Nov 15:50 onwards)

**What the paper does** (FroCoS 2021, "Fast and Slow Enigmas and Parental Guidance", arXiv 2107.06750; text
in /project/hintwork/pg/paper/pg.txt). I should have read this first:
* **Placement:** the model is called after a clause is generated (an inference found by indexing) and before
  it is simplified. It judges real inferences only, of two-parent rules (paramodulation; in E that covers
  resolution).
* **Freezer:** rejected clauses are generated and then frozen. The freezer is revived when the unprocessed
  set empties.
* **Features:** ENIGMA Anonymous vectors, fixed length by feature hashing. E uses sdbm on 64-bit unsigned
  integers, modulo the base, summing collisions. ENIGMA-NG tried bases 1k–32k; with trees, 8k matched no hashing.
* **Pair representation:** Pfuse (the sum of the two parents' vectors) or Pcat (their concatenation). Pcat wins.
* **Labels:** P_proof (parents of proof clauses positive, every other generated clause negative) beats
  P_given. Negatives are sampled down per problem to ρ, best ρ = 4 for Pfuse and 8 for Pcat.
* **Models:** the best Pcat models have 100–200 trees and 1,024–8,192 leaves, at threshold 0.05 for large
  models and 0.2 for small ones.
* **Result:** holdout +11.7% (Table 8: 1,553 against 1,390; with the GNN 1,623; 3-phase 1,632).

**Twee's version:**
* Twee runs a DISCOUNT loop: passives hold only parent ids, position and score, and each pair is
  normalised once at generation, just to score it. Abstract time counts pairs considered, so PG changes
  which pairs get selected, and the CPU saving comes on top.
* `--pg-threshold P` keeps a pair when sigmoid(q1 + q2) ≥ P, where q is the rule-model raw score of the
  critical pair each rule came from. Unscored rules (axioms, interreduced rules, a loaded state) are always paired.
* **Freezer:** a decision depends only on the two stored scores, so nothing needs storing. When the queue
  empties, thawPG regenerates every skipped pair (each active with itself and older ones) and turns the
  filter off; a second empty queue is saturation.
* **Placement since e51:** indexedOverlaps finds the overlap (overlapAt'), then checks `pgOK` once per
  partner (lazy memo), then simplifyOverlap.
* **Logging:** `--pg-log` prints PGR (id, parents, raw score, 10 dense features, `E<keys>`, canonical rule),
  PGN (a new rule's pairs per partner) and, on success, PGPROOF lines.

**Results so far:**
* **Sum filter on the 200 hard goals** (base 29, testbed pg/tb):

  | P | proved |
  |---|---:|
  | 0.047 | 40 |
  | 0.119 | 43 |
  | 0.269 | **52** |
  | 0.4 | 49 |
  | 0.6 | 48 |
  | 0.8 | 45 |
  | 0.95 | 45 |

  At 0.269 CPU is about equal.
* **Half1 A/B,** filter at 0.25 (PGA) against the new defaults (PGB):

  | | PGA | PGB |
  |---|---:|---:|
  | 10 min | 11,467 | 10,061 |
  | 20 min | 15,106 | 14,219 |
  | 30 min | 16,913 | 15,886 |
  | about 50 min | 18,150 | 17,248 |

  Noise is about 185. The A/B ends about 18:54. Production ul41 already runs the filter.
* **Learned models:**
  * Additive model (pga1: interaction constraints, 10 features per rule): offline at 90% proof-pair
    retention it keeps 11% of overlaps against the sum's 36%. In twee it proves only 37–39.
  * At pruning matched to the sum's (35.5% of overlaps kept, pgtest5):

    | model | proved | CPU s |
    |---|---:|---:|
    | pga1 | 39 | 819 |
    | pga2 (no queue score) | 39 | 795 |
    | pgq (q only) | 49 | 1,040 |
    | pgqh (q and hint) | 45 | 966 |
    | sum | 52 | 993 |
    | base | 29 | 933 |

  * Reading: offline proof-pair retention does not predict online proofs. The features copy the selection
    order (queue score, size), and the plain sum of the rule model's scores is the best signal so far.
  * The full 21-feature forest costs about 25 µs per evaluation: 3 s on a 2.3 s run.
* **Next:** Pcat on hashed ENIGMA keys, as in the paper.
  * e52 used the rule model's vocabulary; e53 hashed the keys (named and anonymous).
  * e54 takes the keys from the goal-constant-expanded rule with real names (section 4.4; the user objected
    to anonymous).
  * In one run: 794 distinct features, 37 per rule. Collisions: 36.6% at base 1k, 14.2% at 4k, 9.9% at 8k.
    Anonymous features had only 112 distinct.
  * The 1,500 late goals were re-logged with e54 into pg/d3 (pg/relog5.sh, 18:00–18:09): 1,482 proved,
    551,947 scored rules, the same as d2. The keys are signed 64-bit integers, often negative, so grep for
    `E-?[0-9]`. With the flags off, e54 matches e44 on 24 testbed goals (exp/pg/eqchk54.sh). Then train Pcat
    (ENIGMA only, and with the 20 dense features) at bases 1k/4k/8k, ρ = 8, about 100 trees and 255+ leaves.
    Test at matched pruning on the 200 goals, reporting proofs and CPU separately.
  * Cost is the risk (25 µs per evaluation); then a faster evaluator or a smaller forest.
  * **Pcat offline** (pg/pc1.sh, 17 Nov 18:15): 1,440 training runs with ρ = 8 (32,144 rows, 3,105
    positive), 60 held-out runs with all negatives (1.18M rows, 276 positive), 100 trees, 255 leaves.
    When each model prunes as hard as the sum filter (38.1% of overlaps kept), the share of proof-parent
    pairs kept is:

    | model | 1k | 4k | 8k |
    |---|---:|---:|---:|
    | ENIGMA vectors only (pce_B) | 93.5% | 93.8% | 91.7% |
    | ENIGMA + 20 dense numbers (pcd_B) | 97.5% | 96.7% | 97.1% |
    | sum filter | 84.1% | 84.1% | 84.1% |

    The base does not matter.
  * **Cost in twee:** one 5 s run took 35.5 s of CPU with pce_1024, 4.5 s base, 5.0 s with the sum filter.
    That is about 30 µs per judged pair for a 100 × 255 forest. A twee pair costs a few µs to make, so a
    full Pcat forest cannot pay in CPU. Its quality is tested at a fixed abstract budget anyway
    (pg/tm/pgtest6.sh, from 18:17).
  * Cheap variant (from 18:18): an **additive Pcat** model. Interaction constraints put each tree on the new
    rule's side (its ENIGMA vector and 10 numbers) or the partner's (`pgtrain_enigma.py --additive`). Twee
    splits the forest at load (splitPGModelE) into PGEnigmaAdd, scores each rule once in both roles
    (pgPartsE), and a pair costs two lookups. It loses pair interactions; pgtest6 shows what those are worth.
    Offline at matched pruning: pca_1024 (ENIGMA only) keeps 87.0% of proof-parent pairs, pcad_1024 (with the
    numbers) 96.4%; the full models keep 93.5% and 97.5%. In twee-e55, CPU on one goal: pca 5.65 s, pcad 4.87 s,
    sum 5.03 s. With the flags off, e55 matches e44 on 24 goals. The online test (pg/tm/pgtest7.sh, 6 workers)
    starts when the half1 A/B ends.

---------------------------------------------------------------------------------------------------------

## 7. Mistakes, and what to do instead

7.1 **Designing before reading the source** (17 Nov, PG). I built PG from the paper's title idea and
"improved" it.
* I scored candidate partners before unification. E scores only real inferences.
* I used sparse vocabulary features where the paper uses hashing to a small base.
* I used anonymous features where this project had decided on named, expanded ones.
* The user had to ask "did you read the paper?" three times.
* **Instead:** when a method comes from a paper, read the method sections fully, write the exact recipe
  into section 6 or REPORT, and implement that first. Variants come after, as named variants.

7.2 **Re-deciding settled conventions.** The goal-constant expansion and symbol-awareness were settled for
the rule model (12 Nov) and the GNN (15 Nov), and I reopened them for PG. **Instead:** grep REPORT.md and
this file before any feature design.

7.3 **Unmeasured numbers stated as facts.** "Roughly 840k evaluations" was an estimate. **Instead:** say
"estimate" or measure first.

7.4 **Noise claimed as gains:** the scheduler +30, KN60, Thompson sampling, a time-based A/B of 20 against 18.
**Instead:** state the noise floor beside every comparison, and replicate when the gain is under about 2x the
floor.

7.5 **Missing controls and leaks** (section 2). Every probe of stalled goals before 15 Nov 09:40 ran in a
stale context (--init round 0, a frozen kNN index), so they were invalid.

7.6 **Shell self-kills** with `pkill -f`, `pgrep -f` and `ps | grep` patterns contained in my own command
(about six times, 12–15 Nov). **Instead:** use exact PIDs and the `desc` function.

7.7 **Production crashes from loop.py edits** (shadowed names, three times). **Instead:** test every loop.py
change on a copy of a loop directory with production's full option list before restarting production.

7.8 **Wrong times** in REPORT, script headers and memory (at least six times). **Instead:** run `date`
before writing any time.

7.9 **Misreading a listing:** I reported 6 proofs when there were 3, because three names came from `ls given/`.
**Instead:** count from the results file.

7.10 **Editing a running script** (queue3.sh; solve_new.sh during LVZ). **Instead:** use private copies.

7.11 **rm -rf on a variable path** (17 Nov, `$S/RTt/states`). **Instead:** use literal paths only.

7.12 **Losing track** of what had already been discussed, which is why this file exists. The compaction
summaries keep results but lose the reasons and the user's exact words. Keep section 1 current.

---------------------------------------------------------------------------------------------------------

## 8. Open threads (19 Nov 12:56; `date` checked)

**The portfolio task** (the user, 18 Nov 17:00: keep complementary methods;
[notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md), REPORT 2az). The principle is the ratio
rule: rank each member by its new proofs per CPU hour on the goals every earlier member failed in the same context.
Production orders members online (`--ratio-order`), and new members get measured first (`--explore H`).

Running:
* **exp30** (12:43 - about 14:45, loops/P2A and loops/P2D,
  [notes/2026-11-19-half2-replication.md](notes/2026-11-19-half2-replication.md)): half2 from zero, the 17 Nov
  system against solve_new.sh's new defaults, both at once (2 × 6 workers + transfers). Crash watcher on PIDs
  2796889 (P2D) and 2796890 (P2A). Read it with `abs/setcurve.py sets/half2 P2A P2D` and exp29/ana.py, adapted.
* **production ul64** on 4 workers since 12:42:51 (abs/ul64.sh with J=4, loops/UL64.log; the 19-worker start
  12:40:20 is in UL64a.log; first rows 145787 and 145962). Crash watcher on PID 2796866. Back to 19 workers when
  exp30 ends (`bash abs/ul64.sh`, J defaults to 19).
  * 18 explored 5 s members (`--explore 1`, `--prior-weight 0.5`):
    * lemma counts: k100, k200, k400, k1000, k2000;
    * lemma selections: kp, kd, s12, s40, s200, k200s12;
    * hl, the kNN lemmas' proof steps as hints;
    * search settings: m7t, m4b, r2, nopg, nom.
  * Also k400 at 80 s. Watch `levyield.py loops/UL/r5/results.tsv 145787` and `exp/condvar.py ...`.
  * The exp26 A/B (`--ab-args`, [notes/2026-11-19-queue-renorm-ab.md](notes/2026-11-19-queue-renorm-ab.md)) is
    still on the deep runs. L1 runs rarely now, so it is stalled. Read L1 against L1/B from row 103428.

Ended today:
* hintdata (16:12; user, 15:20): the durable data is now its own git repo, /project/hintwork/hintdata (branch main,
  275 small commits, 445 MB, no file above 10 MB): proofs per original, the solved list, run logs, chain records,
  models, sets, the from-zero runs, and the rule logs as one .tar.xz per original. exp/hintdata_build.py adds new
  data in further small commits. The README gives the formats.
* exp30 14:46: the half2 replication, P2D 19,383 against P2A 19,501 (−118, within noise). Half1's +392 does not
  hold. Both arms' deep work tied, and the union is 19,798. The defaults stay, with no claim.
* exp31 14:09: ENIGMAWatch offline (the user's paper). 512 completion ratios lift held-out AUC by +0.001: not built.
  The ProofWatch member pw@0 joins production (ul65, 14:46).
* exp29 12:39: half1 from zero with the explored portfolio, 19,309 at 2 hours, against 18,917 and 18,987 (+392).
  solve_new.sh's defaults are now its setting (`DEEP`).
* exp28 10:38: E with chain-hint watchlists, 0 of 107 walls. A genuine negative.
* exp27 09:18: today's tail system from zero without exploration, neutral (18,917 against 18,987).
* exp23 08:50: Veroff's Prover9 settings, 0 of 107 at max_weight 5, 40 and 100. A genuine negative.
* exp24 and exp25 (05:29, 05:49): far goals 0 of 40 at 80 s; 80 s runs without queue renormalisation cost 25% less.
* Offline (portfolio review):
  * the cumulative yield estimate ranks members best (discounted, time-normalised and per-original estimates
    are worse);
  * a learned lemma ranker gives a modest lift, from popularity, and is not built.

Paused:
* exp12 stage B: 320 s on gap heads, 34 of 95 done, 0.21 per CPU hour (run.py skips done ids).
* exp19: set-join on the walls, 37 of 107 done, 0.31 per CPU hour (run.py skips done ids).

Next:
0. exp37 (19:50): retrained rule models (rm9*) on today's data with the papers' sampling tricks; offline on the 400
   newest proofs, then a paired test (control loops/MR_rm4t_20), then members `m9*@0`
   ([notes/2026-11-19-retrained-models.md](notes/2026-11-19-retrained-models.md)). exp35 stopped at 19:43 (no unique proof).
   ul71 (20:30, J=10) = ul70 + member m9a@0 (rm9a: AUC 0.876 on the 400, rm4t 0.835). exp36 ended: sketch hints +3 −0 of 54.
   ul72 (23:30, J=8) = ul71 + m9f@0, m9h@0, m9i@0: Suda's per-log weighting (AUC 0.892-0.900); replayed at 20 s rm9f +9 −5, rm9h +5 −1 against rm4t (202 of 400).
   exp37 final (20 Nov 02:12): rm4t 202, rm9f 204, rm9h 203, rm9i 204, rm9a 184, rm9e 181, rm9g 187; union 226; cover rm9f, rm4t +14, rm9e +5, rm9h +2, rm9a +1. ul73 (02:17, J=12) = ul72 − m9i@0 + m9e@0. Time-matched control rm4t at 40 s running. Production's 19-20 Nov burst (783 proofs 22:20-02:13) came from the transfer loop: one L1 proof's steps solved 22 goals of other originals, which started sibling chains.
1. ul70 (17:58, 15 workers while exp36 runs; ul69 + the climbs' hints as members sk@0 and sk@1:0,
   [notes/2026-11-19-climber-outputs.md](notes/2026-11-19-climber-outputs.md)). Before it, ul69 (16:33, 17 workers beside exp32's climber): the deep tail had not run since 06:00 (portfolio notes). Fresh
   pool runs at 40 and 80 s, every label explored, and `--reexplore 150:0.25` (periodic re-measuring). Read the
   new labels after about 1 CPU h each.
1. ul65 (19 workers from 14:46): the new members after 1 CPU hour each, namely pw@0 (ProofWatch), k1000@0, k2000@0,
   s40@0, s200@0 and Vk400 at 80 s.
2. From zero: a combined portfolio, the 20 s pool resume beside the 5 s lemma members, aiming at exp30's union.
3. A longer from-zero run (4-6 hours) where the tail starts.
4. CPU: about 20 in use at 14:47 (ul65 19, transfer 2 at times).

---------------------------------------------------------------------------------------------------------

## 9. Experiment reports (hints/notes/)

Conventions for a report: [notes/README.md](notes/README.md).

One report per experiment: the question and who asked, the exact setup (scripts, sets and how they were chosen,
snapshots, binaries), the numbers, the noise, and what the numbers do not show. Reports for 12–17 Nov 15:50 were
reconstructed on 17 Nov from REPORT.md, the commits, and the session's commands (exp/findcmd.py). Those say so at
the top, and corrections found while reconstructing went into REPORT.md as well (2e, 2m). From 17 Nov 18:30 on,
reports are written as the experiments run.

| report | title |
|---|---|
| [notes/2026-11-12-hint-selection.md](notes/2026-11-12-hint-selection.md) | Which hints to give: pools, kNN, and a learned ranking (transfer benchmark T1) |
| [notes/2026-11-12-hints-dev10.md](notes/2026-11-12-hints-dev10.md) | First hints in twee: baselines, self-replay, and the first hint loops on dev10 |
| [notes/2026-11-12-holdout.md](notes/2026-11-12-holdout.md) | The AIM60k holdout: plain twee, the rule model, and the hint loop |
| [notes/2026-11-12-long-runs-checkpoints.md](notes/2026-11-12-long-runs-checkpoints.md) | Long runs on hard dev goals: the stall cutoff and checkpoints; what was ported from Prover9-new |
| [notes/2026-11-12-rule-model.md](notes/2026-11-12-rule-model.md) | ENIGMA in twee: a learned filter on new rules |
| [notes/2026-11-13-axiom-groups.md](notes/2026-11-13-axiom-groups.md) | Lemmas and hints across originals with the same or weaker axioms |
| [notes/2026-11-13-enigma-loop.md](notes/2026-11-13-enigma-loop.md) | The ENIGMA loop (rm4, rm5, rm4b) and generalisation matching |
| [notes/2026-11-13-full-benchmark.md](notes/2026-11-13-full-benchmark.md) | The whole public benchmark at 4 s per problem, long runs on hard holdout, and a Prover9 control |
| [notes/2026-11-13-hyp-hints-abstract-time.md](notes/2026-11-13-hyp-hints-abstract-time.md) | False hints from conditional goals, and abstract time |
| [notes/2026-11-13-lemma-import.md](notes/2026-11-13-lemma-import.md) | Proven sibling goals as axioms, resumed runs with lemmas, and sketches |
| [notes/2026-11-13-long-runs-stall.md](notes/2026-11-13-long-runs-stall.md) | Long runs: how long runs stay on hints, the whole-pool advantage, and resumed rounds |
| [notes/2026-11-13-online-pools-cascade.md](notes/2026-11-13-online-pools-cascade.md) | Online pools, multi-goal search, the gap to the nearest proof, and the cascade |
| [notes/2026-11-13-p9-sfdf.md](notes/2026-11-13-p9-sfdf.md) | Prover9: SFDF reorientation of proofs before they become hints |
| [notes/2026-11-14-ablation-lemma-count.md](notes/2026-11-14-ablation-lemma-count.md) | Ablation of ENIGMA, hints and lemmas; how many sibling lemmas; which lemmas proofs use |
| [notes/2026-11-14-enigma-looping-deepire.md](notes/2026-11-14-enigma-looping-deepire.md) | ENIGMA-style looping, a Deepire-style model, and retraining online |
| [notes/2026-11-14-hint-axioms-profile.md](notes/2026-11-14-hint-axioms-profile.md) | Frequent hints as axioms, a false hint in old pools, where twee's time goes, and the rule penalty |
| [notes/2026-11-14-line-gaps-stalled.md](notes/2026-11-14-line-gaps-stalled.md) | Distance in proof lines, and stalled goals: run fresh with new hints rather than resume |
| [notes/2026-11-14-long-run-speed.md](notes/2026-11-14-long-run-speed.md) | Long runs slow down: the overlap index and the interreduction filter |
| [notes/2026-11-14-p9loop-bigloop.md](notes/2026-11-14-p9loop-bigloop.md) | Veroff's P9loop and Bigloop in twee, against resuming the saved search |
| [notes/2026-11-14-resume-bug-consider-cost.md](notes/2026-11-14-resume-bug-consider-cost.md) | A resume bug that grew one run to 100 GB; consider-emulation costs a quarter of the CPU |
| [notes/2026-11-14-sketch-climbing.md](notes/2026-11-14-sketch-climbing.md) | Sketch climbing, gap filling, and the control that undid it |
| [notes/2026-11-15-conjecture-cuts.md](notes/2026-11-15-conjecture-cuts.md) | Conjecture cuts, generated and oracle |
| [notes/2026-11-15-heads-fresh-vs-resume.md](notes/2026-11-15-heads-fresh-vs-resume.md) | Tail heads, the cutoff between fresh runs and resumes, and a 5 s first level |
| [notes/2026-11-15-hint-generator.md](notes/2026-11-15-hint-generator.md) | A hint generator (GNN2Seq) and instance matching of hints |
| [notes/2026-11-15-learned-scheduler.md](notes/2026-11-15-learned-scheduler.md) | A learned scheduler for the cascade, stalled goals, and tail heads |
| [notes/2026-11-15-retrain-gnn-p9side.md](notes/2026-11-15-retrain-gnn-p9side.md) | Retraining the rule model on hard proofs, a GNN, the oracle test, and Prover9 as a side worker |
| [notes/2026-11-15-retrain-stall-artefact.md](notes/2026-11-15-retrain-stall-artefact.md) | The stall was partly an artefact; unit forms of conditional lemmas; repeated deferral; folding |
| [notes/2026-11-15-sketches-stronger.md](notes/2026-11-15-sketches-stronger.md) | Sketches in stronger theories, climbing up and down |
| [notes/2026-11-16-from-zero-dispatcher.md](notes/2026-11-16-from-zero-dispatcher.md) | The whole benchmark from zero, and a faster dispatcher |
| [notes/2026-11-16-knn-lemma-count.md](notes/2026-11-16-knn-lemma-count.md) | How many kNN lemmas, and which; where production's proofs come from; what a head is worth |
| [notes/2026-11-16-lattice-moves.md](notes/2026-11-16-lattice-moves.md) | Learning the lattice moves of the climber |
| [notes/2026-11-16-queue-model-lemma-proof-hints.md](notes/2026-11-16-queue-model-lemma-proof-hints.md) | The rule model ordering the queue; hints from the kNN lemmas' proofs |
| [notes/2026-11-16-replay-unseen.md](notes/2026-11-16-replay-unseen.md) | From scratch on unseen originals: the replays (rp3, ho8), contexts, the scheduler, and leaks |
| [notes/2026-11-16-same-statement-other-theory.md](notes/2026-11-16-same-statement-other-theory.md) | The same statement proven in another theory |
| [notes/2026-11-16-step-transfer.md](notes/2026-11-16-step-transfer.md) | Goals that are steps of existing proofs: transfer, source lemmas, and a kNN filter bug |
| [notes/2026-11-17-expanded-proofs.md](notes/2026-11-17-expanded-proofs.md) | Expanding lemma-based proofs back to the axioms (Veroff style) |
| [notes/2026-11-17-deep-runs-expanded-chains.md](notes/2026-11-17-deep-runs-expanded-chains.md) | Deep runs on late unsolved goals, guided by expanded proof chains (Veroff's question) |
| [notes/2026-11-17-lattice-construction.md](notes/2026-11-17-lattice-construction.md) | Building a lattice with reasonable steps: strengthenings, weaker goals and conjectures (design and stage 1) |
| [notes/2026-11-17-long-runs-late-goals.md](notes/2026-11-17-long-runs-late-goals.md) | Long runs (640 s) on the late goals no deep run proved, and the hint-match signal (exp5) |
| [notes/2026-11-18-ground-joining-hangs.md](notes/2026-11-18-ground-joining-hangs.md) | Runs that never end: unbounded ground joinability, and a limit for it (exp6) |
| [notes/2026-11-18-subsumption-matching.md](notes/2026-11-18-subsumption-matching.md) | Hint matching by subsumption, as in Prover9 (exp7, twee-e58 --eqhint-subsume) |
| [notes/2026-11-18-chain-hints-unsolved.md](notes/2026-11-18-chain-hints-unsolved.md) | Chain hints (expanded proofs of the nearest proven siblings) against the pool on 78 unsolved goals at 80 s (exp8) |
| [notes/2026-11-18-chain-hints-short.md](notes/2026-11-18-chain-hints-short.md) | Chain hints against the pool at 5 s and 20 s on 200 frontier goals (exp9) |
| [notes/2026-11-18-chain-transfer-records.md](notes/2026-11-18-chain-transfer-records.md) | Chains whose holes are filled with transfer sources, against exp8's chains, 78 goals at 80 s (exp10) |
| [notes/2026-11-18-wall-breaking.md](notes/2026-11-18-wall-breaking.md) | The 107 walls (first unsolved goal of each original; 6,263 of the 6,370 unsolved are behind them) with chain hints at 80 s and 320 s (exp11) |
| [notes/2026-11-18-gap-heads.md](notes/2026-11-18-gap-heads.md) | The heads of the 96 gaps of >= 20 unsolved goals (4,045 goals) with chain hints at 80 s and 320 s (exp12) |
| [notes/2026-11-18-chain-size.md](notes/2026-11-18-chain-size.md) | Smaller chains: 5 siblings (S5) and the siblings' own proofs without expansion (D) against the 10-sibling chain, exp8's 78 goals at 80 s (exp13) |
| [notes/2026-11-18-two-sided-chain.md](notes/2026-11-18-two-sided-chain.md) | Two-sided chains (the 10 nearest proven siblings above or below) against the below-only chain, exp11's 107 walls at 80 s (exp14) |
| [notes/2026-11-18-unfolded-walls.md](notes/2026-11-18-unfolded-walls.md) | Unfolded definitions with chain hints against the folded chain, exp11's 107 walls at 80 s (exp15) |
| [notes/2026-11-18-prover9-chain-walls.md](notes/2026-11-18-prover9-chain-walls.md) | Prover9 with chain hints against Prover9 with the pool, exp11's 107 walls at 60 s (exp16) |
| [notes/2026-11-18-knn60-walls.md](notes/2026-11-18-knn60-walls.md) | 60 kNN lemmas against 30 at 80 s with exp11's chain hints, the 107 walls (exp17) |
| [notes/2026-11-18-subsumption-deep.md](notes/2026-11-18-subsumption-deep.md) | Subsumption hint matching (--eqhint-subsume) at 80 s with chain hints, the 107 walls (exp18; the user's remark) |
| [notes/2026-11-18-waldmeister-paper.md](notes/2026-11-18-waldmeister-paper.md) | Reading: Hillenbrand's Waldmeister lessons, technique by technique against twee; candidates (ground-joined equations as simplifiers) and a 320 s profile |
| [notes/2026-11-18-set-join-walls.md](notes/2026-11-18-set-join-walls.md) | Successor sets for critical pairs (--set-join, Waldmeister 4.3) at 80 s on the 107 walls (exp19) |
| [notes/2026-11-18-portfolio-review.md](notes/2026-11-18-portfolio-review.md) | Complementary methods: every dropped variant's unique share, the missing time-matched comparison, and portfolio approaches (the user's request, 17:00) |
| [notes/2026-11-18-time-matched-control.md](notes/2026-11-18-time-matched-control.md) | exp11's chain at 160 s on the 92 failed walls: the time-matched control for 80 s + 80 s portfolios (exp20) |
| [notes/2026-11-18-l0-portfolio.md](notes/2026-11-18-l0-portfolio.md) | 8 arms at 5 s (control, 60 kNN lemmas, unfolded, subsumption, rule threshold 0.2, no rule model, no PG, chain hints) on 300 goals that failed their 5 s fresh run (exp21) |
| [notes/2026-11-18-no-pg-no-model-walls.md](notes/2026-11-18-no-pg-no-model-walls.md) | No PG / no rule model at 80 s on the 107 walls as portfolio members (exp22, queued after exp21) |
| [notes/2026-11-19-veroff-p9-settings.md](notes/2026-11-19-veroff-p9-settings.md) | Prover9 with Veroff's AIM settings and chain hints on the 107 walls (exp23, from 02:15, 1 worker): max_weight 5 0 of 107; 40 paused at 0 of 39 (03:54); 100 to do |
| [notes/2026-11-19-far-goals-deep.md](notes/2026-11-19-far-goals-deep.md) | production's 80 s chain level on 40 far goals, which production never deepens (exp24, 03:58-05:29): 0 of 40 at 2.9 CPU h; found the chain-records race at loop start |
| [notes/2026-11-19-hint-cost.md](notes/2026-11-19-hint-cost.md) | what chain hints cost per abstract second; the profile; queue renormalisation under the abstract clock (exp25) |
| [notes/2026-11-19-queue-renorm-ab.md](notes/2026-11-19-queue-renorm-ab.md) | deep runs without queue renormalisation, an A/B test in production ul57 (exp26, from 05:52) |
| [notes/2026-11-19-eprover-watchlist.md](notes/2026-11-19-eprover-watchlist.md) | E 3.5.9 with chain hints as a static watchlist on the 107 walls, 60 s (exp28): 0 of 107, a genuine negative |
| [notes/2026-11-19-from-zero-explore.md](notes/2026-11-19-from-zero-explore.md) | exp29: half1 from zero with the explored 5 s lemma members: 19,309 at 2 hours against PGC 18,917, PGA 18,987; solve_new.sh's new defaults |
| [notes/2026-11-19-half2-replication.md](notes/2026-11-19-half2-replication.md) | exp30: the explored portfolio from zero on half2, both arms at once (12:45 - about 14:45) |
| [notes/2026-11-19-enigmawatch.md](notes/2026-11-19-enigmawatch.md) | exp31: ENIGMAWatch (user, 13:30): the paper's recipe and the oracle ceiling. Offline, 512 completion ratios (Mean, Var, Rand) lift held-out AUC by +0.001 (0.900 to 0.902), not built. The ProofWatch member pw@0 joins ul65 |
| [notes/2026-11-19-climber-member.md](notes/2026-11-19-climber-member.md) | exp32: the live head climber measured again as a deep member (user's message, 15:20), 2 climbs beside ul66 (17 workers) from 15:39 |
| [notes/2026-11-19-oracle-pg.md](notes/2026-11-19-oracle-pg.md) | exp33: the near-oracle rmO through parental guidance (user, 16:40), paired against rm4t on the 400 ultest goals at 20 s |
| [notes/2026-11-19-climber-outputs.md](notes/2026-11-19-climber-outputs.md) | exp34 and the climber's records (user, 16:55): what production uses from the climber; conditional-proof replay 0 of 4; climb.py persists fill lemmas, assumptions, used premises; climbs/ in the data repo |
| [notes/2026-11-19-pg-order.md](notes/2026-11-19-pg-order.md) | exp35: the parents' stored rule-model scores ordering the queue (twee-e62 `--pg-order` 0.5 and 0.1), paired against exp33's rm4t arm on the 400 ultest goals |
| [notes/2026-11-19-climb-ablation.md](notes/2026-11-19-climb-ablation.md) | exp36: the climbs' sketch hints ablated on 55 climber proofs (pool vs pool + sketch steps, context as of the proof; user, 17:20); production on 15 workers meanwhile |
| [notes/2026-11-19-retrained-models.md](notes/2026-11-19-retrained-models.md) | exp37: retrained rule models as members (user, 19:35): the ENIGMA/Mizar60/Suda papers' training tricks, given logs of every loop indexed (several proofs per goal), rm9* models held out of the 400 newest production proofs, paired test from snapshot ULsN19 |
| [notes/2026-11-19-from-zero-portfolio.md](notes/2026-11-19-from-zero-portfolio.md) | half1 from zero in 2 hours with today's deep portfolio (PGC), against PGA's 18,987 (exp27, from 07:18) |
| [notes/2026-11-17-lemma-circularity.md](notes/2026-11-17-lemma-circularity.md) | Are lemma chains circular? A check of the used lemmas |
| [notes/2026-11-17-mix-fail-order.md](notes/2026-11-17-mix-fail-order.md) | Repeats cost most of the time: `--mix` and `--fail-order` |
| [notes/2026-11-17-pg-ab-half1.md](notes/2026-11-17-pg-ab-half1.md) | Parental guidance at scale: half1 from zero, 2 hours, sum filter 0.25 against the defaults |
| [notes/2026-11-17-pg-learned-dense.md](notes/2026-11-17-pg-learned-dense.md) | Learned parental models on 10 numbers per rule |
| [notes/2026-11-17-pg-pcat-enigma.md](notes/2026-11-17-pg-pcat-enigma.md) | Pcat parental models on hashed ENIGMA features, as in the paper |
| [notes/2026-11-17-pg-sum-filter.md](notes/2026-11-17-pg-sum-filter.md) | Parental guidance with the sum filter, on 200 hard goals |
| [notes/2026-11-17-tail-states-e44.md](notes/2026-11-17-tail-states-e44.md) | The tail: which goals get longer runs; original rates; saved states; noise at scale; e43/e44 |

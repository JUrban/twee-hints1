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

**Keep the proofs (user, 20 Nov 15:03).** Every new experiment keeps the printed Twee proof of each proved run.
Search runs stay `--quiet --no-proof`. A proved run is rerun with the proof printed: loop.py run_one queues it in
DIR/proofq/ (`proof_job`, on by default), and exp/proofq.py `--follow -j 2` (loops/PROOFQ.pid) writes
DIR/proofs/<goal> and the live destination's proofs/ (loops/UL/proofs). Keep the worker running; past experiments
are not rerun. The proofs collected so far: /project/THM_proofs.tar.gz and /project/THMR5k_proofs.tar.gz
(exp/collect_proofs.py).

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
| e63 | 23 Nov 15:59 | e62 plus `--lazy-lemmas`: axioms named lemma_* wait in a list by critical-pair score (times `--lazy-lemma-factor`, default 1) and become active when at most the best queued pair's score; startup at 1,575 axioms 8.1 s -> 1.2 s. Off: byte-identical to e62 on 3 goals. Not kept in --dump-state |

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
**Current production: REPORT.md, section "Production now"** (main loop, members, side loops, PIDs; kept current at every
restart). **Every version's options, members, workers, dates and reason, ul3 to now: [notes/production-history.md](notes/production-history.md)**
(exp/prodhistory.py, from the scripts in exp/prod/; rerun after every restart). Below: the older prose history, newest first (it stops at ul63).
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

7.13 **Appending by `open(p, 'w').write(open(p).read() + x)`** (23 Nov): the 'w' open runs first and empties the file,
so two notes lost all but their newest section, four times, and commits 56d49d8 and 2216deb carried it. Rebuilt from
9caa5fa plus each appended section. **Instead:** `open(p, 'a')`, or read into a variable on its own line; check `wc -l`
or `git diff --stat` before a commit. Same day: the Z9-gap pre-checks had no sibling lemmas at all (condprove.py's
sibling pool is --set, here the 500 unproved gap goals), and a note said "40 siblings changed nothing". **Instead:**
look at one generated problem of each arm before reading an arm's numbers.

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

**Printed proofs in hintdata (21 Nov 11:50; user: "pack these new proofs also into hintwork/hintdata/realproofs"):**
188,561 kept proofs (44,475 goals) in hintdata/realproofs/<family>/<family>_NN.tar.xz, 10 parts of at most 10 MB
(45 MB), index.tsv.gz and README.md; `exp/hintdata_build.py --realproofs` adds the rest once proofq has caught up.
(22 Nov 15:33-16:02) `--realproofs --skip=P2X,P2Z` packed 578,449 printed proofs in 24 families (new: Z7, Z7C, Z8, P2Q-P2W,
exp54/56/57/59, profile; 23 commits in hintdata, parts at most 9.9 MB, realproofs/ 121 MB). exp55's arms come later.
(20:29-20:58) `--realproofs --skip=P3A,P3B,P3C` added P2X 26,444 and P2Z 26,555 (with their side loops), exp61 9, smoke
KDA/KDB, production to 369: 632,292 proofs in 27 families, realproofs/ 133 MB, every part under 10 MB. exp60 later.
(23 Nov 02:39-03:08) `--realproofs --skip=Z9` added exp60's arms (P3A 26,645, P3B 26,633, P3C 26,761 with their side
loops), production to 383, smoke with KDC (RST, started later, comes next time): 712,749 proofs in 30 families, realproofs/ 151 MB, every part under 10 MB.

**Totals (23 Nov 12:56, trust.py loops/TRUSTNOW/t1256): 48,512 of 51,784 solved (holdout 5,410 of 5,880), 3,272 unsolved, 0 untrusted.** Since 09:33 (10): loops/CI3 5 (the queue's last sweeps and the ranked PLL1), loops/CI2 1 (the live loop's c5W), production 4.

**Totals (23 Nov 09:33, trust.py loops/TRUSTNOW/t0933): 48,502 of 51,784 solved (holdout 5,405 of 5,880), 3,282 unsolved, 0 untrusted.** Since 06:41: the plain sweeps (PLN2, PLW1, PLK1), the live plain loop, the hint bed's proof and production.

**Totals (23 Nov 06:41, trust.py loops/TRUSTNOW/t0641): 48,466 of 51,784 solved (holdout 5,393 of 5,880), 3,318 unsolved, 0 untrusted.** Since 21:39: production's own streaks (com_Ralt, lra2aa, ns_to_aa1_*) and PLN1's 22 plain proofs (merged 06:16 and 06:40).

**Totals (22 Nov 21:39, all trusted, trust.py -j 2 --exposed loops/UNSOUND/exposed.txt, loops/TRUSTNOW/t2139, run
21:39-21:43): 48,372 of 51,784 solved (holdout 5,365 of 5,880), 3,412 unsolved.** 15 new since 18:02: gmlive4 9,
ul75 5, XFL 1. REPORT's totals table
has the history (user, 20 Nov: "update the total numbers in the report etc every now and then").

Next:
000000000000000000000000000000000000000000000000000000000000000000000. **exp81 (longer plain runs on the local heads, [notes/2026-11-24-plain-time.md](notes/2026-11-24-plain-time.md)):** HLW1's
   60 s plain proofs on local heads came within 27 s; CC67D's long hinted runs on first heads mostly after 150 s. 60 of HLW1's
   failed local heads (seed 81), the same context: P81A 60 s (control) and P81B 300 s, plain, 100+30 siblings, 400 kNN, 2 threads
   each; waits for exp76's end. Decision: B beyond A at 0.5 per CPU h or better gives a 300 s pass over the local heads.
   (05:06) Arm P81C after P81A: 60 s with every earlier sibling (--sibs 1000) and 100 later: no plain 60 s run had more than 100+30.
00000000000000000000000000000000000000000000000000000000000000000000. **exp80 (what runs with hundreds of lemma axioms cost, [notes/2026-11-24-lemma-cost.md](notes/2026-11-24-lemma-cost.md)):**
   tonight's winning setting at the frontier is runs with 30-130 siblings and 400 kNN lemma axioms (exp67, HLW1), and those
   get slow as they lengthen: exp74's 1,200 abstract s took about 3 CPU s per abstract s. One plain 505-lemma problem (aa1_45_c 355)
   at 5-300 abstract s with +RTS -s, and a cost-centre profile at 120 s (dist-prof2). 120 s: 1.95 CPU s per abstract s.
   **Result: 0.9 (5 s) to 2.4 (300 s) CPU s per abstract s. makePassives is 80%: 10.3M pairs made (350 per new rule), 1.3% considered;
   simplify 56%, mostly index lookups. e64 (skip the no-change rewriting pass, same normal forms, byte-identical trace) was 11% slower:
   reverted and deleted. No free speed-up; the remaining levers change the search. Closed.**
0000000000000000000000000000000000000000000000000000000000000000000. **exp79 (CC67D's run as a production member, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp79"):**
   **ul81** (02:56) = ul80 plus k400s30@3:0: a fresh 160 s run after L0 with 30 siblings and 400 kNN, the run that proved 9 of
   91 heads in exp67's control (0.66 per CPU h; production's last 6,000 runs 0.48). Explored and ordered by live yield.
000000000000000000000000000000000000000000000000000000000000000000. **exp67 arm B against its CPU-matched control ([notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md)):**
   on all 91 frozen heads the climber CLB67 proved 8 and one long run per head with the same lemma lists (CC67D, 552 CPU s each)
   proved 9, +0 −1, at 14.90 against 13.58 CPU h. Climbing added nothing beyond the long lemma lists. Arm A's pair still runs.
   **(03:23) Arm A agrees: CLA67 2, CC67C 5 (+0 −3) on 88 heads. Controls: 30+400 lemmas 9, 6+30 lemmas 5 (+6 −2, union 11).**
   **(03:46) exp67 done, all 91 heads in every dir: arms 2 / 8, CLA67 vs CC67C 2 / 5, CLB67 vs CC67D 8 / 9; 11 heads in all. Closed.**
00000000000000000000000000000000000000000000000000000000000000000. **exp78 (production retries climbed goals, [notes/2026-11-24-cond-replay.md](notes/2026-11-24-cond-replay.md), "exp78"):**
   loop.py --retry-climb: a goal whose climb sketches are newer than its last fresh run gets one fresh run (then the sk members).
   Before, 127 of CLS71's first 149 climbed targets had no production run after their climb. **ul79** (01:15) = ul78 plus
   --retry-climb --retry-climb-hours 6; 212 goals marked at the start; retries in loops/UL/climbretry.tsv.
   **(02:18) Negative: 1,312 runs in 63 minutes, 0 proofs; 1,304 on 287 retried goals (5.9 CPU h, 0 proved). ul80 (02:19) = ul78's setting.**
0000000000000000000000000000000000000000000000000000000000000000. **exp77 (twee's CASC strategies on local heads, [notes/2026-11-24-cond-replay.md](notes/2026-11-24-cond-replay.md), "exp77"):**
   every run so far used twee's default queue. Four of twee's UEQ portfolio strategies (lhs-weight 1 or 9 with flip-ordering,
   ground connectedness, kbo-weight0) as plain 60 s runs on 120 local heads; HLW1 is the control. --complete-subsets and
   --depth-weight 60 are out: 5-10 times the CPU per critical pair with 529 lemma axioms (abstract time counts pairs).
   **Stopped (03:49): not new. exp57 ([notes/2026-11-22-cp-weights.md](notes/2026-11-22-cp-weights.md)) found every queue weight below the defaults, and 15 Nov's
   var_test flip-ordering and kbo-weight0 0 at 5-20 s. A2's one proof (aK2_eq_aK3_gen 594, merged) the defaults find in 11 s.**
000000000000000000000000000000000000000000000000000000000000000. **exp76 (CLS71's finals at 160 s, [notes/2026-11-24-cond-replay.md](notes/2026-11-24-cond-replay.md), "exp76"):**
   CLS71's 20 s finals: 0 real proofs in 119 (1,174 sketch proofs). 30 of its failed targets get one 160 s final with its
   climb hints (F76S) and without (F76C), after exp67's arms end. Also: condprove.py capped every run at 600 s wall, so
   exp74's first run stopped early (rerun since 00:19).
00000000000000000000000000000000000000000000000000000000000000. **exp75 (replaying conditional climber proofs, [notes/2026-11-24-cond-replay.md](notes/2026-11-24-cond-replay.md)):**
   0 ready now. A first scan found 25 sketch proofs of unsolved targets whose assumptions production had proved; 21 were
   proofs of weakened goals (climb.py --weaken: `goal=` in the sketch header), the 4 others rest on a kNN label one of
   whose 2 candidate goals is unproved. climb.py's used.tsv now records each label's goal and the weakened flag; abs/crploop.sh
   replays ready proofs hourly. keylemmas.py (exp69's key goals) counted weakened sketches too; recounted in the notes.
0000000000000000000000000000000000000000000000000000000000000. **exp74 (long plain runs on the cluster heads, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp74"):**
   **exp70 ended 01:14: 0 of 9 in both arms (K70F 30 s fills 44% of gaps, K70R 40%); closed.**
   exp70 so far: 30 s fills prove 39% of the gaps they try, 3 s fills 40% (CLK69 42%): fill time is not the limit. The 7
   cluster originals' first heads (166 unsolved goals behind them) never had more than production's 320 s cascade. One plain
   1200 s run each, H's lemma lists, 2 threads (exp/exp74.sh, 23:49).
   **(04:34) Ended: 1 of 7, TLRproperties_2 367, which exp67 had proved meanwhile; 6 failed at 1,200 abstract s (2,909-4,393 s each). Closed.**
000000000000000000000000000000000000000000000000000000000000. **exp73 (sk with long lemma lists, [notes/2026-11-23-tail-allocation.md](notes/2026-11-23-tail-allocation.md), "exp73"):**
   loop.py members skkNsM; **ul78** (23:43) adds skk400s30@1:0: production's top member sk@1:0 (2 of ul76's 5 proofs, 60% of
   its CPU) with exp67 arm B's 30 siblings and 400 kNN in place of 6 and 30. Explored and ordered by live yield.
00000000000000000000000000000000000000000000000000000000000. **exp72 (tail allocation, [notes/2026-11-23-tail-allocation.md](notes/2026-11-23-tail-allocation.md)):** the tail's side loops by
   proofs per CPU h from their records: the plain live loop's L (400 lr2-ranked kNN, 5 s) 0.22 per h, N 0.88, H (heads, 60 s)
   about 2; CLHL3/CLHL4 0. plainlive5 (23:39) drops L. HLW1: H's setting as a sweep on the 940 local heads (unsolved, the
   goal before proved), after exp67's arms end; CLS71 excludes them (restarted 23:33). exp67: arm B 7, arm A 2 (+6 −1, 54
   common heads, 8.2 and 9.1 CPU h); its proofs now merged every 10 minutes (exp/exp67merge.sh).
   **(24 Nov 04:50-04:57) HLW1 resumed with 5 threads (4 new in 123 runs, 1.32 per CPU h); ul82 = ul81 with 4 workers: the variant
   members took 76% of production's CPU at 0.26 per CPU h (last 30,000 runs), the fresh levels 1.86, plain side loops 0.88-1.8.
   plainlive6 (W: the local heads, rerun on sibling changes only) starts after HLW1.**
0000000000000000000000000000000000000000000000000000000000. **exp71 (the live climber on stalled goals, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp71"):**
   all 10 of production's recent sk proofs (climb hints as hints) were in originals with many sketches of CLU (16 Nov,
   stalled goals: 22 real proofs at 0.79 per CPU h, 7,302 sketch files over 108 originals); today's head climbers cover
   14-15 originals each, and 2,700 of the 3,229 unsolved are holes. CLS71 (exp/prod/side/cls71.sh, 23:22): CLU's cheap
   climb with today's binary and arm B's lemmas, -j 6. **ul77** (23:24): ul76 plus CLS71, CLK69, K70F, K70R in --climb-hints.
000000000000000000000000000000000000000000000000000000000. **exp70 (a second round on the key goals, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp70"):**
   the 9 key goals again from CLK69's sketches and fill hints and t2300. K70F: gap filling 30 s per fill run (CLK69: 3 s);
   K70R: CLK69's setting (the round-2 control). -j 1 each, merged into loops/UL every 10 minutes (exp/exp70.sh, 23:04).
   climb.py now records each fill lemma's premises (fillprem.tsv, from twee's USEDAXIOMS), so trust.py can check fill
   lemmas: the 6 untrusted goals at t2300 are production sk@1 proofs with CLHL2's fill lemmas (or use those goals).
   (23:14) trust.py checks fill lemmas (fill nodes from fillprem.tsv; production's lemma_fill_N matched by formula through
   the printed proof); exp/fillcheck.py re-proved 20 of the 22 old fill lemmas behind them. t2314: 48,555 trusted, 3 untrusted.
00000000000000000000000000000000000000000000000000000000. **exp69 (climb the assumptions, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp69"):**
   most climbed heads have a 5 s sketch proof from a single assumption, nearly always an unsolved goal X of another
   original. exp/keylemmas.py ranks the X by the unsolved targets they unlock: Kproperties_1 332 and nil4_19K 394 4 each,
   7 more 2 each; 7 of the 9 are not heads (1-9 goals behind one), so nothing climbed them. CLK69 (exp/exp69.sh): a set-mode
   climb of the 9 from t2120, CLHL4's setting, 1 climb at a time, real proofs merged into loops/UL every 10 minutes (21:22).
   **Ended 22:55: 0 of 9 in 1.51 CPU h. The 9 and their own sketches' assumptions are one cluster of 7 originals: each
   follows from another unsolved one; fills (3 s) proved 93 of 219 gaps.**
0000000000000000000000000000000000000000000000000000000. **exp68 (live climber, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp68"):** CLHL3 (arm A's
   setting) stopped at 21:07, 0 real proofs in 4.1 CPU h. CLHL4 (abs/clhl4.sh, loops/CLHL4): arm B's lemmas (30 siblings, 400 kNN)
   and --weaken 12 (all weakened goals; the hints of 3 of exp67's 4 proofs came from weakened-goal sketches). Two changes:
   the production climber, not an A/B; read per CPU h against CLB67 and plainlive4's H runs.
   (21:14) **ul76**: ul75 plus today's climb dirs (CLHL3, CLHL4, CLA67, CLB67) in --climb-hints. In ul75's last 6,000 runs
   member sk@1:0 (40 s with the climb hints) made 8 of 19 proofs, but its dirs were all from 15-20 Nov (exp/memberyield.py).
   **(23:30) CLHL4 stopped: 21 heads, 0 real proofs in 4.7 CPU h; its heads were exp67's (arms and controls) at the same time.**
000000000000000000000000000000000000000000000000000000. **exp67 ([notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md), "exp67"):** two climber settings,
   paired, on the 91 heads of t1854 frozen (exp/sets/heads67): CLA67 = clhl3's setting (6+30 lemmas), CLB67 = 30 sibling and
   400 kNN lemmas (the plain sweeps' size finding). Set mode with the new climb.py --targets, the trusted context and a copy of
   its hints, 2 climbs each (exp/exp67.sh), from 19:01.
   Control CC67 (exp/exp67c.sh, after exp65): the same heads and context, one run per head of CLA67's CPU per target, no sketches
   (climb.py --runs 0): does climbing beat a long run (the 14 Nov lesson)?
   **(21:05) 2 h: CLB67 3 real proofs, CLA67 1, CLHL3 0, at about 4 CPU h each (exp/climbread.py).** Plain 60 s head runs
   had failed on all four; in three the hints came from weakened-goal sketches. Merged into production. Control CC67B
   (exp/exp67d.sh) for arm B at its CPU per target, beside CC67 after exp65.
   (21:05) trust.py counted every sketch run's assume_* as premises of a climber's proof: no climber proof in an exposed
   original was trusted (aa1_14 533). Now the target's last used.tsv row (the run that made the real proof); 3 -> 2 untrusted.
   (23:27) The controls CC67/CC67B (22:56) were over budget: CPU/1.07 as abstract time, but these heads run 2.3-3.6 CPU s
   per abstract s, so about 2.3 times the arm's CPU per head. Stopped (kept as .v1; CC67.v1's proof of aa3_12 487 merged);
   CC67C and CC67D (exp/exp67e.sh, 23:28) cap each run by CPU (climb.py --final-cpu, 608 and 552 s).
00000000000000000000000000000000000000000000000000000. **exp66 (climber restart, [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md)):** the live head
   climber back beside production (abs/clhl3.sh, loops/CLHL3; clhl2.sh's setting, a fresh record). clhl2 made 69 proofs in
   66 CPU h (1.04 per CPU h) and stopped 20 Nov 10:04, never restarted. The user: "you should remember to use the climber and
   experiment with it as it's veroff's main weapon for solving open problems". Launched with CPUS=28 (more CPUs allowed for
   a limited time); read per CPU h against plainlive4's H setting on the same heads.
   (19:47) Restarted with per-run proof names (d79c82e): every climb run wrote proofs/<target> over the last, sketch proofs
   (assume_* axioms) included; now <target>.<tag>, sketch proofs kept, finals safe. No sketch proof was in loops/UL/proofs.
0000000000000000000000000000000000000000000000000000. **exp65 (redesigned 15:47, [notes/2026-11-23-plain-sizes.md](notes/2026-11-23-plain-sizes.md)):** larger kNN lists in the plain levels
   from zero. Q5A: P4B's DEEP exactly, on P4B's CPU set (also a cross-time replica of P4B); Q5B: plain levels plk400s40@0 and
   plk1600s130@0 in place of plk100s40@0 and plk400s130@0, on P4A's set. sets/half2, 4 workers, 6 hours (abs/exp65.sh), after
   exp64 ends, if P4B still leads at 6 hours. Why: on 235 held-out Z9 gap goals, plain 5 s, kNN only, 100+400 prove 39 and
   400+1,600 prove 46. The ranker design (--lemma-ranker-all) dropped. Frontier sweep PLG1 (1,600 kNN, W's siblings) from 15:45.
   (16:36) With siblings (exp/z9gap9.sh; the earlier pre-checks had none): P4B's plain levels 40, Q5B's 45 (+8 −3, union 48) on the 235 gap goals; exp65 stands.
   (16:36) twee-e63 `--lazy-lemmas` (lemma axioms enter by score, like SOS): startup 8.1 -> 1.2 s at 1,575 axioms, but factor 1 lost 17 proofs and factor 0.5 tied eager (40 and 40, +3 −3) at the same wall time: not used.
   Started 23 16:55:36 (loops/EXP65.pids); loop.py Q5A 3439513, Q5B 3439516; ends about 22:55.
   1 h (17:56): Q5A 17,367, Q5B 17,495; at equal work +192. Replica Q5A against P4B at 60 min -235.
   (17:01) PLG1 stopped at 1,453 goals, 1 proof (merged; it used a kNN lemma ranked 1,420). The frontier is 92 heads (each original's first unsolved goal, all earlier siblings proved; the other 3,176 sit behind them): plain 60 s sweeps HDW1 (400 kNN) and HDG1 (1,600) on sets/heads92.
   **(17:49) HDW1: 4 of 92 heads proved by plain 60 s runs (400 kNN, 100+30 siblings) in 2.25 CPU h, 1.8 per CPU h; all merged into production (its own loop: about 5 in 6 hours). Next: HDG1 (1,600 kNN), then the live loop with a heads setting (abs/plainlive4.sh).**
   HDG1 (18:52): 1,600 kNN lemmas on the 88 other heads at 60 s, 1 proof (aK1_nil3_b 177) in 3.02 CPU h (0.33 per CPU h) against HDW1's 4 in 2.25 (400 lemmas, 1.78); H keeps 400.
   2 h: Q5A 19,244, Q5B 19,523 (+279; +336 at equal work), P4B (Q5A's setting) 19,669: replica spread 425, so no signal yet.
   4 h (20:56): Q5A 21,316, Q5B 21,283 (-33; -31 at equal work), P4B 21,547: Q5B's early lead is gone; no gain from the bigger lists so far.
   **6 h (22:56): Q5A 21,749, Q5B 21,747 (-2; -2 at equal work), P4B 21,803; +151 −149, union 21,898. Rule not met: closed, production keeps 100+400.**
000000000000000000000000000000000000000000000000000. **Lemma ranker (08:59, [notes/2026-11-23-lemma-ranker.md](notes/2026-11-23-lemma-ranker.md)):** the used kNN lemmas of plain
   proofs are spread evenly over ranks 0-400; a learned ranker could bring needed lemmas into the list. Data sweep
   RKD1 (abs/rkd1.sh): 800 solved goals near the frontier, 1,000 kNN lemmas, 5 s, 2 threads; then LightGBM, recall at
   100/400 against similarity, and a frontier sweep with it if recall rises.
   First CV (09:04, 213 frontier proofs): recall of used kNN lemmas in the top 50 of 400-lists 0.18 -> 0.44 (PLW1), top 100 0.34 -> 0.63. Frontier test PLL1 armed (abs/lrab.sh): lr1 after RKD1, the context of cycle c5, control c5W.
   **lr1 (09:59; 770 problems): in RKD1's 1,000-lists the top 400 by the model hold 0.94 of the used lemmas (similarity 0.78), all of them in 0.74 of the problems (0.52). PLL1 (lr1, W's sizes, context c5) started; control c5W.**
   **Frontier (same context c5): PLL1 3 proofs (1.2 per CPU h) against W's 1 (0.3), W's among them; each PLL1 proof used lemmas beyond similarity rank 400. loop.py --variants plr[kN][sM] --lemma-ranker (dc2c652). Live loop: plainlive3.sh (N and L) from 11:24.**
   Packed (12:34, exp/hintdata_build.py --realproofs --skip=P4A,P4B): smoke part 1 (9967 printed twee proofs, 1.4 MB xz); production part 1 (543 printed twee proofs, 2.5 MB xz); Z9 part 2 (26259 printed twee proofs, 4.6 MB xz); Z9 part 1 (32283 printed twee proofs, 6.6 MB xz).
   (13:06) loop.py `--lemma-ranker-all`; exp65 now tests it (one change). Offline pre-check exp/z9gap.sh: 500 of Z9's gap goals in Z9's context, 30 kNN lemmas by similarity (cond/ZGS) or lr2 (cond/ZGR).
   (13:37) Pre-check at 30 lemmas on 235 held-out half2 gap goals: similarity 11, lr2h 6 (+0 −5), mixed 9 (+1 −3): similarity wins; exp65 (--lemma-ranker-all) not run. Next: the same at 100 lemmas.
   (13:37) The live loop's first lr2 cycle c8L (400 lemmas, the frontier): ran 3002, 4 proved, 4 merged into UL; lr1's c7L before it: ran 2982, 0.
   (14:55) Half1 at 30 lemmas: similarity 13, lr2h1 8 (+0 −5). 100 lemmas on half2: similarity 20, lr2h 14 (+3 −9): the ranker loses at 30 and 100, and the list's size matters more than its order. Next: 200 and 400 (exp/z9gap6.sh), similarity against lr2h.
   (15:10) **Size, not order.** 235 half2 gap goals, plain 5 s, similarity / lr2h by kNN lemma count: 30: 11 / 6, 100: 20 / 14, 200: 22 / 24, 400: 35 / 30. The ranker is dropped for from-zero runs (it keeps the frontier live loop); exp65 tests list size instead. Next: 800 and 1,600 lemmas, 400 with 40 siblings (exp/z9gap8.sh).
   **Totals (14:57, loops/TRUSTNOW/t1457): 48,516 trusted, holdout 5,410; the 4 new since 12:56 are c8L's (lr2), production's own loop proved none in those 2 hours.**
00000000000000000000000000000000000000000000000000. **exp64 (07:10, [notes/2026-11-23-plain-level.md](notes/2026-11-23-plain-level.md)):** a plain level from zero: P4A (control) and P4B
   (DEEP with `plk100s40@0`, prior 3), sets/half2, 4 workers each, 6 hours, CPU sets as exp60's (abs/exp64.sh,
   abs/or_test3.sh). Starts 5 minutes after Z9 ends, in Z9C's place (loops/Z9C.skip). PLZ8 (Z8's context): 160 of 2,000,
   85 per CPU h.
   Changed 07:57 (before the start): P4B has two plain levels, plk100s40@0 and plk400s130@0 (N and W), prior 3 each.
   Started 10:52:03 (loops/EXP64.pids); loop.py P4A 3128645, P4B 3128644; ends about 16:52.
   1 h (11:53): P4A 17,562, P4B 17,602 (+40); at equal work −46. Plain runs 124, 25 proved.
   2 h (12:53): P4A 19,434, P4B 19,669 (+235); at equal work +85. Plain levels 50 of 353 runs proved.
   4 h (14:55): P4A 21,146, P4B 21,547; at equal work +397. One-arm goals P4A 87, P4B 488 (the plain level proved 80 of P4B's itself); P4B ran the unfiltered member 227 times, P4A 939: the plain runs take goals Vunf would have run, and L0 gets the time.
   **6 h (16:53): P4A 21,697, P4B 21,803; at equal work +113 (under the +200 rule). One-arm goals P4A 114, P4B 220. The plain levels make the loop faster (P4B's 240-minute count came about an hour later in P4A), not stronger at 6 h; solve_new.sh unchanged. exp65 follows with P4B as the control.**
0000000000000000000000000000000000000000000000000. **Plain live loop (06:55, [notes/2026-11-23-conditional.md](notes/2026-11-23-conditional.md), "Plain live loop"):** PLN1's
   plain sweep as a side loop of production: each cycle (30 min or more, 3 threads) takes loops/UL's solved goals as
   context, reruns only goals whose problem changed (condprove.py --prev), imports the proofs into loops/CI2 and merges
   them into loops/UL. abs/plainlive_start.sh (PID in cond/PLNL.pid) starts it after PLN2. Log cond/PLNL/log; stop with
   cond/PLNL.stop.
   Wide sweep PLW1 (armed 07:13, abs/plw1.sh): after PLN2, 100 earlier and 30 later siblings, 400 kNN; proofs into loops/CI3 and loops/UL.
   PLN2 (06:54-07:17): 1,540 changed problems run (1,778 SAME), 5 proved, 4.5 per CPU h; merged. The live loop started 07:17 (c1).
   Hint bed (07:20, abs/hintbed.sh): 600 goals plain failed, PLN2's problems with 200 or 2,000 hints from the lemma goals' proofs, against a perturbation control. Smoke: with 2,000 hints 2 of PLN2's 5 plain proofs.
   Two settings (07:48): PLW1 so far 14 proofs in 1,541 goals, 11 not PLN2's; abs/plainlive2.sh runs N and W each cycle with their own --prev chains, from PLW1's end (starter cond/PLNL2.starter).
   Sweep queue (07:49, abs/sweepq.sh after the hint bed): PLK1, PLS1, PLM1, PLT1: kNN alone, siblings alone, between, 20 s; proofs into loops/CI3 and loops/UL.
   **Hint bed (07:20-07:54): on 600 plain-failed frontier goals, 200 lemma-proof hints 0, 2,000 hints 1 (2x CPU), control 0: the lemma set proves these goals, not hints.**
   **PLW1 (07:17-08:24): 23 proofs, 7.0 per CPU h, 18 beyond PLN2 (which it contains); 16 merged. plainlive2.sh (N and W) since 08:27.**
000000000000000000000000000000000000000000000000. **COND1 (05:00, [notes/2026-11-23-conditional.md](notes/2026-11-23-conditional.md)):** conditional proofs of the 3,412
   unsolved goals: each with its 10 nearest earlier siblings assumed (proved or not) and 30 kNN trusted lemmas, one
   plain 5 s twee run (exp/condprove.py, abs/cond1.sh, 6 threads, cond/COND1 outside loops/). Hard steps against
   blocked goals, and the blockers' reach.
   **Result (05:26; ran 05:00-05:23): 2,826 hard, 585 blocked, 1 unconditional of 3,412; no single goal frees more than 10
   (reach: hard >=1 184, >=5 5, >=20 0). The hard steps are the long ones (every unsolved goal is 8+ Prover9 lines after
   the previous goal). No keystones: no change. The one unconditional proof (nil3_30__goal_473) is not reproduced by
   loop.py in the trusted context (CU2, with its 8,504 hints) and is not entered.**
   Step test bed (05:28): sets/hardstep300 (300 of the hard goals), abs/stepbed1.sh: arms KNN29 (perturbation control),
   SIB30, AFT10, KNN100, SIB3 (5 s each) and T20 (20 s), 6 threads, one at a time, cond/STEP_<arm>.
   **Batch 1 (05:56): KNN29 1, SIB30 41, AFT10 51, KNN100 12, SIB3 4, T20 47 of 300; siblings matter most (SIB30, AFT10). One more unconditional
   proof (aK2_eq_aK3_c__goal_479, KNN100). COND2 (30 earlier siblings, all unsolved goals) runs from 05:56, then batch 2
   on SIB30's problems (abs/stepbed2.sh).**
   PLN1 (05:58): plain 5 s runs (no model, no hints) on all unsolved goals with only trusted siblings (30 earlier, 10
   later) and 100 kNN lemmas: real attempts (abs/pln1.sh, condprove.py --proved, 4 threads, cond/PLN1).
   **Result (05:58-06:40): 24 proofs in 3,412 runs (2.71 CPU h of twee runs, 8.8 per CPU h); production had proved 2
   of them itself since 21:39 (nslm_to_aa1__goal_981, _1078), so 22 new, merged into loops/UL through loops/CI1
   (10 at 06:16, 12 at 06:40). COND2 (30 earlier siblings assumed): 2,484 hard, 925 blocked; still no keystones.**
   **So far (06:15): 10 new proofs in 1,366 runs (1.10 CPU h of twee runs, 9.1 per CPU h; production makes 0.35 per CPU h on
   these goals), none in any production loop. loop.py `--variants pl[kN][sM]` (f79acac; smoke PLS2: Vplk100s40@0 proved
   PLN1's first goal where L0 failed). exp/condimport.py makes the loop record for merge.py (test: loops/CI1).**
   **Merged (06:16, the hints files' mtime): merge.py loops/UL loops/CI1, 10 new proofs (PLN1's first 10); production synced them (synced 56 -> 66).**
00000000000000000000000000000000000000000000000. **Readiness (04:54, [notes/2026-11-23-readiness.md](notes/2026-11-23-readiness.md)):** offline on Z8's rows (exp/triglag.py,
   exp/fresh_ready.py). Late retries are prompt: of 593 proofs that used a lemma proved after the goal's last failure, the
   proving run came 3/8/16/30/50 min after it (deciles 10/25/50/75/90), always the first run after it. First runs wait longer
   (6/16/40/98/147 min after their latest lemma), but no kNN signal orders them better than the gap order: its AUC is
   the highest in every hour (0.730 over all, n30 0.658, s1 0.575). **No change.**
0000000000000000000000000000000000000000000000. **Z9C (03:01, [notes/2026-11-23-z9.md](notes/2026-11-23-z9.md), "Continuation"):** Z9 continued after its 8 hours
   for 16 more (abs/z9cont.sh: Z9's saved loop.py command with `--cascade-continue --cascade-hours 16`, its side
   loops again, config.json's mtime set back, loops/Z9.toffset for t=). Starts 5 minutes after loops/Z9.done unless
   loops/Z9C.skip (waiter PID 2816917). Smoke test abs/rst_smoke.sh (02:53-02:59): 365 -> 400 of 487, no solved goal
   run again.
   **Not run (07:11): abs/z9cont.sh stopped, loops/Z9C.skip; the slot after Z9 goes to exp64 (a plain level from zero).**
000000000000000000000000000000000000000000000. **Model audit 2 (23 Nov, [notes/2026-11-23-model-audit2.md](notes/2026-11-23-model-audit2.md)):** exp/modelcheck.py
   again on all of production's proved unit goals (loops/MODELCHECK2, the first audit's models cached), -j 2, after
   the realproofs packing. Reading: false goals (must be 0), false steps against 217 in 71, alarms.
   **Result (03:31): 0 false goals, 0 alarms, 217 false steps in 71 goals (the same set as 20 Nov's); none in
   production's 378 proofs since then.**
00000000000000000000000000000000000000000000. **Z9 (23 Nov 02:46, [notes/2026-11-23-z9.md](notes/2026-11-23-z9.md)):** the system from zero on all
   51,784 goals, 6 workers, 8 hours, CPUs 0-20,28-48 (production keeps 21-27,49-55): solve_new.sh's defaults with
   exp55's `--knn-drift 5` and the GIVENARGS `--lemma-ax`. A measurement against Z8 (42,917 at 6 hours) and Z7, not an
   A/B. abs/after_exp60.sh (PID 2665589) starts it 10 minutes after exp60 ends unless loops/Z9.skip.
   **Started 02:46:34 (loop.py 2737443, transfer 2737562, givenmatch 2737566; loops/Z9.solve_new.sh = solve_new.sh,
   checked 02:47; affinity 0-20,28-48). Ends about 10:46. Crash watcher on production and Z9's three loops.**
   30 min (03:17): Z9 27,339, Z8 26,777 (+562), Z7 24,561 by wall; at equal abstract work (Z8's 28 min) Z9 25,481 at 26 min against Z8's 26,147 (−666).
   The machine is faster tonight (Z9 0.97 CPU s per abstract s, Z8 1.01 in its first hour). Cross-time and early: noise.
   60 min (03:47): Z9 34,436, Z8 33,971 (+465), Z7 32,154 by wall; at equal abstract work (Z8's 58 min) Z9 33,347 at 52 min (−451).
   2 h (04:47): Z9 39,248, Z8 38,169 (+1,079), Z7 37,195 by wall; at equal abstract work (Z8's 115 min) Z9 37,992 at 100 min (−35). The wall lead is the faster machine; at equal work Z9 has caught up.
   4 h (06:48): Z9 42,861, Z8 41,984 (+877), Z7 42,478 by wall; at equal abstract work (Z8's 235 min) Z9 42,488 at 206 min (+571; Z7 +29). Beyond the noise against Z8, level with Z7: Z8 may have been the weak run.
   6 h (08:48): Z9 43,667, Z8 42,894 (+773), Z7 43,350 (+317) by wall; at equal work (Z8's 355 min) +598 over Z8, +155 over Z7. Holdout Z9 4,725, Z8 4,605.
   8 h, end (10:47): Z9 44,161, Z7 43,767 (+394) by wall; at equal work (Z7's 475 min) +338. Holdout Z9 4,800, Z7 4,734.
0000000000000000000000000000000000000000000. **exp63 (16:48, [notes/2026-11-22-frontier-orderings.md](notes/2026-11-22-frontier-orderings.md)):** another
   term ordering on production's frontier. Production yields about 0.5 proofs per CPU h now (698 CPU h spent on the
   3,432 unsolved, median 47 runs), all under twee's default precedence. 120 unsolved unit goals (sets/ulu120, seed
   63) in production's context (loops/ULF.ctx), 20 s fresh: OD default vs OO1 ordering 1. abs/ordtest.sh.
   **Result (18:01): 0/120 both (1.15 and 1.22 CPU h). Not adopted; no 80 s version (too few expected proofs).**
000000000000000000000000000000000000000000. **exp62 (16:33, [notes/2026-11-22-o2-build.md](notes/2026-11-22-o2-build.md)):** twee-e61 built with -O2
   (all binaries so far: cabal's default -O1; Prover9-new's josef01-cpu-next audits build flags). Worktree
   /project/hintwork/tw61o2; abs/o2bench.sh runs exp61's command with both binaries at once (loops/OB1, OB2).
   Adopt if the outputs match and the CPU saving is at least 5%.
   **Result (16:44): not adopted. exp/rawbench.py, 30 goals x 3 binaries, identical outputs: -O2 median CPU ratio
   1.035 (124.6 against 118.6 s), -O1 + -fspecialise-aggressively 1.002. The loop benchmark was not run.**
00000000000000000000000000000000000000000. **exp61 (15:40, [notes/2026-11-22-retry-deficit.md](notes/2026-11-22-retry-deficit.md)):** the retry
   deficit: 300 random unit goals Z8 left (sets/z8u300, seed 60), one 5 s run each in Z8's final context
   (abs/rd5.sh, after the packer; loops/RD5). How much would perfect retries add at 6 h?
   **Result (16:29): 9 of 300 (3.0%, 1.1-4.9%) -> about 260 of 8,642. Perfect late 5 s retries add little; exp55's +200
   bar is likely out of reach from retries alone. Z8 never ran 4,475 of its unsolved goals (by design; those prove
   1.3% at 5 s in the final context, the others 4.7%).**
0000000000000000000000000000000000000000. **exp60 (15:34, [notes/2026-11-22-floor-ratio-until.md](notes/2026-11-22-floor-ratio-until.md)):** the
   floor-ratio pair. P3A control vs P3B `--floor-ratio-until 120`, half2 from zero, 4 workers each, 6 h. Why: Z8 led
   Z7 by 1,820 at 1 h and trailed by 408-471 from 4 h (cross-time); in Z8 the head class got 171 runs in 6 h.
   abs/after_exp55.sh (PID 2235753) starts it 10 min after exp55 ends unless loops/EXP60.skip. Decision +200 at 6 h.
   (18:29) Third arm P3C `--knn-drift 5 --knn-drift-after 60` (new loop.py option, 1b4d930: the drift count admits
   goals only after MIN minutes; exp55 lost 216 at 30 min, then +109 to +122). Same control, same rule.
   **Started 20:35:22: loop.py P3A 2354007, P3B 2354010, P3C 2354012, each on the old solve_new.sh (copies checked
   20:35:30; `--knn-drift 5` went into LATE at 20:35, 8ce5e8c). Ends about 02:35. Crash watcher on production and
   the three loops. Read: abs/setcurve.py sets/half2 P3A P3B P3C --at 30,60,120,180,240,300,360.**
   30 min: P3A 15,203, P3B 14,838, P3C 14,981. P3B is P3A's twin until minute 120, so −365 is noise (throughput:
   13,154 runs against 12,530 at equal run seconds); exp55's early −216 is within it.
   60 min: P3A 17,541, P3B 17,196, P3C 17,312 by wall time; at equal abstract work P3B −115, P3C +40 (P3A ran at
   1.07 CPU s per abstract s in the second half hour, the others 1.18-1.20). Decision read both ways at 6 h.
   120 min: P3A 19,520, P3B 19,061 (−459 by wall; −27 at equal abstract work at P3A's 90 min), P3C 19,299 (+148
   at equal work). Cause: P3A ran on socket 0, P3B, P3C and production on socket 1. 22:37-22:39 CPU affinity: each arm
   and production 14 whole cores, 7 per socket (abs/pin_exp60b.sh). The decision is read at equal abstract work.
   New A/Bs: abs/or_test3.sh with CPUSET per arm (exp/or_test3.sh); Z9 pinned to 0-20,28-48. Production keeps
   21-27,49-55 until its next restart (the set is lost then; pin it again).
   180 min: P3A 20,510, P3B 20,028, P3C 20,809 by wall; at equal abstract work P3B −259, P3C +528.
   **Result (done 02:36:26, read 02:39): 360 min P3A 21,670, P3B 21,532 (−138; −101 at equal work, P3A's 340), P3C 21,682 (+12; +54).
   P3B not adopted: the twins were −305 apart at equal work at 120, more than the end gap. P3C: exp55's
   +204 does not replicate (one-arm 166 against 154); +390 at equal work at 180. `--knn-drift 5` kept,
   lower claim. The 4-hour reading was lost: its waiter took a bare clock time, which after midnight is the evening.**
000000000000000000000000000000000000000. **exp59 (14:39, [notes/2026-11-22-hub-roots.md](notes/2026-11-22-hub-roots.md)):** 4,355 goals only
   production has (not Z7, not Z8); 2,082 fell at production's 5 s L0. exp/hubroots.py: 502 roots (first proof uses
   no other such goal), a few with reach 1,200-1,980 (aK2rev 349, Kproperties_1 314, aKperms_1 342, ...); the top
   10 first fell to production's L2 4, L1 3, L0 2, not its own runs 1; Z7/Z8 ran them mostly at 5 s. Test: the top 24, one 80 s run each in Z8's context
   (loops/Z8F.ctx), 1 worker (abs/hub80.sh, loops/HUB80).
   **Result (15:24): 15 of 24 proved in Z8's context (7 under 10 s: context drift; 8 at 11-175 s: Z8 never
   gave any more than 8 s). Next: a kNN-centrality signal for hubs, checked on these roots, then a from-zero pair.**
   kNN centrality (exp/hubcent.py, 15:26): Spearman 0.20 with reach over 437 roots; the 9 hubs with reach > 1,000 rank
   247-1,144 of 8,642; the top 500 hold 49.6% later-production goals vs 42.4% base. Weak; not pursued for now.
   (15:30) Z8's head class ran 171 times in 6 h (floor withheld while r out-yielded it), so hub heads never got L1.
   But within Z8, L1 proofs were used as lemmas less than L0 proofs (0.93 vs 2.21 per proof; same hours 0.33 vs 1.35):
   the hubs' reach is a multi-day effect. No from-zero change from this thread.
00000000000000000000000000000000000000. **exp58b (13:32, [notes/2026-11-22-src-used.md](notes/2026-11-22-src-used.md)):** the same gap in transfer
   runs: a proof's hint file lacks the lemma axioms it used, and same-statement runs get no source lemmas at all.
   transfer.py `--src-used` adds the source proofs' used lemma axioms (from their proof texts), named by goal.
   exp/soreplay.py on 100 of the 525 goals Z8's live loop failed in same-statement runs (20 controls), each in Z8's
   context at the time (PID 2066925, loops/SORP). If +10 over control: production's GML and XFL get it.
   **Result (14:31): used 6 of 100 (4 of the 55 that got lemmas; median 1 lemma added), ctl 0 of 20, paired 0 vs 0.
   Not adopted; the option stays off by default.**
0000000000000000000000000000000000000. **exp58a (12:57, [notes/2026-11-22-lemma-ax-replay.md](notes/2026-11-22-lemma-ax-replay.md)):** the
   lemma-axiom fix replayed on Z8's live loop. Only 59 goals failed there with an ancestry run (most of the 682
   failures were same-statement runs), so the fix can change at most 59 from zero: the 6-hour pair (exp58) is
   dropped. exp/gmreplay.py: lax on all 59 and ctl on 15, each in Z8's context at the time of its run, 20 s, 1
   worker (PID 2059788, loops/GMRP). If lax beats the control rate by 10+, `--lemma-ax` goes into solve_new.sh's
   GIVENARGS before exp55 (~15:20).
   **Result (13:26): lax 46 of 59, ctl 0 of 15 (paired 12 vs 0); 27 of the 36 Z8 never solved; all 597
   axiom lines of the proofs resolve. solve_new.sh GIVENARGS default += `--lemma-ax` (13:26).**
000000000000000000000000000000000000. **exp57 (11:12, [notes/2026-11-22-cp-weights.md](notes/2026-11-22-cp-weights.md)):** twee's
   **Result (14:14; ended 14:13:40): every weight arm below the default at 20 s (CW0 98; arms 76-95); each union with
   CW0 12-18 below CW9 (116 at 40 s); all nine arms 119. No member. Twee's default weights stay.**
   critical-pair weights as members (user, 11:08: "have we played with different weights for the default twee
   weighting functions?" No: no run in the records changed them). sets/wheads300: 300 heads of late2 (previous goal
   proven in Z7's context; seed 57), loops/LAA.ctx, one fresh 20 s run per goal and arm. CW0 control; CW1/CW2
   lhs-weight 2/8; CW3/CW4 depth-weight 0/5; CW5/CW6 var-weight 0.5/1.5; CW7 dup-factor 1; CW9 the control at 40 s
   (time-matched for control + one variant). Smoke clean (11:10). **abs/after_exp54w.sh (PID 2026476) starts it when
   exp54 ends (EXP55.skip for after_exp54.sh), then exp55.** exp54's replica pair is deferred. Decision: a union with
   CW0 that beats CW9 by 5+.
   loop.py `--flag-variants NAME=FLAGS;...` (d825cae), so a winner can be a production variant: smoke FVS (11:17-11:23,
   `lw2=--lhs-weight=2`, --variants lw2@0,unf@0) built level Vlw2@0 and ran it with `--lhs-weight 2`; no traceback.
00000000000000000000000000000000000. **exp56 (11:05, [notes/2026-11-22-gm-retry.md](notes/2026-11-22-gm-retry.md)):** the given-rule
   hits the live loop gave up on. givenmatch.py live runs a hit goal once and lists it in loops/GML/tried.tsv for
   good. 30 of the 273 tried goals are still unsolved and all have hit rows; ns_to_aa1_b 673 has 229 from 32 source
   runs (newest 10:15 today), tried once on 20 Nov 04:57. The live loop's sort by ancestry size sees 0 on every
   failed-run hit, so it took the oldest logs. exp/gmretry.py runs the same two passes (20 s ancestry, 40 s prefix)
   on the newest 3 hits of distinct sources, 1 worker, into production. Started 11:05:27 (PID 2023224, loops/GMR).
   Ancestry pass 0 of 30 (937 s). Likely cause (11:21): loop.py given_scan labels only the original's axioms as −1,
   so a failed run's lemma axioms (proven goals) reach the sketch as hints, not in `.ax`. exp56b (`--lemma-ax`): the
   parentless source rules that are statements of proven goals within the target's axioms go into `.ax` named by goal
   (skax_<i>_<goal>, resolved by trust.py); goal_673's 3 sketches get 300. abs/gmr2.sh (PID 2032897) runs it after GMR.
   **exp56 result (11:59): prefix pass 5 of 30 (goal_673 among them), about 5.6 per CPU h; all trusted-resolvable.**
   GMR2 (--lemma-ax) on the 25 left from 11:59:25.
   **GMR2: 7 of its first 12 at the 20 s ancestry pass (GMR 0 of 30 there); 105 of 105 named skax axioms match
   their goal. Production's GML restarted 12:06:46 as gmlive3.sh (`--retry-tried 3 --lemma-ax`, PID 2047685,
   loops/GML3.log).**
   **exp56b final (12:39): 13 of 25 (12 at 20 s), 0.48 CPU h; 18 of the 30 given-up goals proved in all. GML3 4 of 4
   in its first 30 minutes. Production 48,329.**
   exp56c (12:59): the 11 left, `--times 60,160` (their hits come at given rule 2,000-18,000 of the source runs);
   abs/gmr3.sh starts GMR3 after the exp58a replay.
   **GMR3 (14:15): 8 of 11 (5 at 60 s, 3 more at 160 s), 0.70 CPU h; 26 of the 30 given-up goals proved in all.**
   Production's GML restarted 14:17:28 as gmlive4.sh (+ `--retry-times 60,160`; PID 2074661, loops/GML4.log).
   Candidate for from zero (exp58, after exp55): solve_new.sh's GIVENARGS + `--lemma-ax --retry-tried 1`. In Z8's live
   loop (loops/Z8_GML) the ancestry pass proved 665 of 765, the prefix pass 40 of 95, and 682 goals failed there
   (same-statement runs included), of which Z8 later solved 265. A half2 pair, 6 h, as exp55.
0000000000000000000000000000000000. **exp55 (09:33, [notes/2026-11-22-knn-drift.md](notes/2026-11-22-knn-drift.md)):**
   loop.py `--knn-drift M`: retry goals whose kNN lemma sets drifted (M or more new since the last fresh run), and
   the retry class goes by that count. Why: LAA's first runs on Z7's unsolved goals prove 40% with 5+ new kNN
   lemmas against 8% with fewer (exp/knndrift.py); Z7 had last run them at a median of minute 193. Smoke KDS
   (09:32:56, sets/half2s2000, 2 workers, 15 min). exp55 = P2X control vs P2Z `--knn-drift 5`, half2, 4 workers,
   6 h; abs/after_exp54.sh (PID 1942249) starts it after exp54 only with loops/EXP55.go. Decision +200 at 6 h.
   (The floor-ratio pair moves after it.)
   Smoke KDS clean (09:48): no traceback, 7 rebuilds counted in 0.0 s, 7 goals flagged by the count only, rows kd=.
   **Started 14:23:40 by abs/after_exp54w.sh (after exp57): P2X loop.py 2075027 (knn_drift 0), P2Z 2075029 (5);
   both live loops with `--lemma-ax` (solve_new.sh's new default). Ends about 20:24. Readings at 30-360 min.**
   Interim: 30 min −216, 60 min −149, 120 min +109, 180 min +122, **240 min +117** (P2Z 21,324, P2X 21,207).
   **Result (done 20:25:02): 360 min +204 (P2Z 21,796, P2X 21,592); P2Z-only 297, P2X-only 93, union 21,889.
   Adopted: `--knn-drift 5` into solve_new.sh's LATE after exp60's arms copied solve_new.sh (P3C = replica).**
000000000000000000000000000000000. **ul75 (07:13, [notes/2026-11-22-ul75.md](notes/2026-11-22-ul75.md)):** production with
   `--head-class`. Since ul74's start (14.3 h) L1 proved 17 in 23.8 CPU h (0.71/h), the 5 s variants 8 in 52.7, and
   253 of the 1,026 heads had no L1 run. **ul74 stopped 07:13:18; ul75 started 07:13:25 (loop.py 1846757, J=6, first
   row 257,905); class h ran 5 L1 runs in its first 197 s.** Read: L1 runs and proofs per hour from row 257,905,
   against ul74's 2.2 new per hour.
   First hour (08:14): L1 153 runs (ul74 67/h), 4 proved in 3.15 CPU h; new=4, synced=2 (ul74 2.2 new/h).
   At 3.7 h (11:00): new=18 (4.8 an hour); L1 17/503 in 10.64 CPU h (1.60/h, ul74 0.71), 53% of the CPU; the 5 s
   variants and L0 1 of 3,805 runs.
   (11:15) Is there a better use of the variants' CPU? Over each label's own last 5 CPU h only L1 (1.39/h), L0 (1.20)
   and Vs40@0 (0.40) prove anything; L2 0 in 3.1 CPU h since the relabel, L3 1 in 2.0, L4 0 in 4.2. So no: it needs
   new members on heads (exp57).
   (12:41, correction) The runs also feed the given-rule loop: since 07:13 the first hits of 25 goals came from L1 18,
   L0 2, Vk100@0 2, Vk60@0 2, Vk200@0 1 (21 solved now). Since 21 Nov 16:50, 35 of production's 94 new goals came by
   that route (GML 17, exp56 18), 55 from its own runs.
00000000000000000000000000000000. **Late A/B (03:00, [notes/2026-11-22-late-ab.md](notes/2026-11-22-late-ab.md)):** the 3-hour half2 tests
   from zero hardly reach the head and deep classes (P2V: 31 runs at the 40 s level in 3 hours). sets/late2: the 3,817
   half2 goals Z7 left unsolved (production has 2,234), with loops/Z7's proofs as the context (solve_new.sh CONTEXT),
   abs/late_test.sh. Smoke LSM (200 goals, 2 workers, 10 minutes, --head-time 20) at 03:00:20. Planned exp54 when Z8
   ends (about 10:53): LAA control and LAB --head-time 20 (exp51), 4 workers each, 3 hours; decision +50, a replica
   pair first if within ±50.
   Smoke clean (12 of 200 in 10 minutes, no errors). **abs/after_z8.sh (PID 1622999, 03:11) starts abs/exp54.sh when
   loops/Z8.done appears, after up to 20 minutes for loops/EXP54.go or EXP54.skip.**
   **Started 08:55:22 (Z8 stopped at 6 h): LAA loop.py 1903363, LAB 1903360; head_time 0 / 20.0. Ends about 11:57.**
   At 30 min (09:27): LAA 162, LAB 163; L1 LAA 13/35, LAB 12/64 (ht=1), 0.49 CPU h each.
   At 1 h (09:57): LAA 234, LAB 244 (+10); L1 16/58 against 23/125 in 0.99 CPU h each; LAB-only 17, LAA-only 7.
   At 2 h (10:57): LAA 315, LAB 327 (+12, flat since 1 h); L1 30/115 against 34/240 in 2 CPU h each; LAB-only 20,
   LAA-only 8.
   (11:12) The replica pair (abs/exp54r.sh) is deferred for exp57 (the user's weights question): +12 is far below
   the +50 bar, so LAB stays undecided and is not adopted.
   **Final (11:57): LAA 352, LAB 360 (+8, within ±50: not adopted, undecided); L1 43/194 in 3.44 CPU h against
   49/398 in 3.40; LAB-only 24, LAA-only 16, union 376 new (15.7 per worker-hour; LAB alone 30.0).**
   Candidate from production (07:10, loops/UL/r5 since the restart at row 233,804, 14.3 h): its own runs proved 32,
   L1 (the 40 s chain level) 17 in 23.8 CPU h (0.71/h), L0 7, the 5 s variants (V*@0) 8 in 52.7 CPU h. 773 of the
   1,026 heads had an L1 run since the restart, 253 none; 16 of the 17 L1 proofs were heads whose previous goal was
   proved 35-188 h earlier, not fresh chain steps. So heads wait for L1 CPU that the 5 s variants take: a late-A/B
   arm (or production) with L1 on every head before the variants.
0000000000000000000000000000000. **Z8 (planned 00:23, [notes/2026-11-22-z8.md](notes/2026-11-22-z8.md)):** the defaults as they stand
   (LATE + --floor-ratio 20) from zero on all goals, 6 workers, 8 hours, one arm against Z7's curve. abs/after_exp53.sh
   (PID 1485120) starts abs/z8.sh when exp53 ends (about 02:52), after up to 20 minutes for loops/Z8.go or Z8.skip.
   **Started 02:53:28 by the go file, made at once when exp53 was rejected (loop.py 1572206, transfer 1572319,
   givenmatch 1572323); config.json floor_ratio 20.0, no renormalisation argument. Ends about 10:53.**
   At 30 min (03:24): Z8 26,836, Z7 24,561 (+2,275; +1,828 at equal abstract work), Z7C 26,757: the early cost is gone.
   At 1 h (03:54): Z8 33,987, Z7 32,154 (+1,833; +1,607 at equal abstract work), Z7C 34,522 (Z8 −535).
   At 2 h (04:54): Z8 38,179, Z7 37,195 (+984; +2,216/+1,820/+1,346 at 30/60/90 min: narrowing), Z7C 38,955.
   At 3 h (05:54): Z8 40,740, Z7 40,786 (−46; −338 at equal abstract work), Z7C 40,479: the early lead is used up.
   At 4 h (06:54): Z8 42,007, Z7 42,478 (−471; −503 at equal abstract work), Z7C 41,237. Z8's own runs +347 (new
   32,751 against 32,404), synced −818 (9,256 against 10,074); Z8-only 327, Z7-only 798 (exp/armdiff.py). Over the
   400 rule: a side-by-side pair for `--floor-ratio 20` after exp54, unless Z8 is within 400 at 8 h.
   At 6 h (08:54): Z8 42,917, Z7 43,350 (−433; −408 at 5 h; −406 at equal abstract work at 5 h); union 43,604.
   **Stopped at 6 h (08:55:04, 42,920 in solved.tsv): the gap is steady and the pair is needed anyway; exp54 starts early (EXP54.go).**
   Plan (08:58): exp55 after exp54 (or after exp54's replica pair, if exp54 lands within ±50): `--floor-ratio 20`
   side by side on all goals from zero, LATE as it is against LATE without it (Z7's setting), 6 workers each, 6 h,
   production paused or at J=2 meanwhile. Note: exp52 on half2 (4 workers) still had +789 at 3 h, where Z8 against
   Z7 was already −46: the cross-time comparison may be part of the gap.
   Plan (03:26): at 4 hours, if Z8 leads Z7 by more than about 400 at equal abstract work, stop Z8 (its hours 4-8
   would only give a cross-time difference inside the noise) and start exp54 then instead of at 10:53.
000000000000000000000000000000. **Proof cost (23:58, [notes/2026-11-21-proof-cost.md](notes/2026-11-21-proof-cost.md)):** twee's `proof` flag is read only
   after a successful search (SequentialMain.hs:1618). exp/proofcost.py, 42 queued proof jobs from six dirs, each
   with and without `--no-proof`: 61.1 against 61.2 CPU s, the same output outside the proof block in all 42. So
   proofq's rerun is a full second run per proved job; printing the proof in the search run is free. **For the
   user to decide** (their method); until then search `--no-proof` and proofq stay.
   Prepared: loop.py `--proof-in-search` (0ae814a, off by default; transfer.py loops take it too). Smoke PIS
   (smoke487, 00:54-01:00): 387 proved, 387 proofs kept, 0 proofq jobs.
00000000000000000000000000000. **exp53 (22:25, DONE 02:53, REJECTED, [notes/2026-11-21-renorm-zero.md](notes/2026-11-21-renorm-zero.md)):** abs/after_exp52.sh (exp/ copy, PID 1287489) waits for
   P2T.done and P2U.done, then up to 20 minutes for loops/EXP53.go or loops/EXP53.skip, then runs abs/exp53.sh:
   P2V (control) and P2W (`PG="--cp-renormalise-threshold 1000"`), half2 from zero, 4 workers each, 3 hours
   (to about 03:10). Decision +185 at 3 h. Smoke: twee-e61 takes the option (a 5 s proof, byte-identical output).
   **Started 23:51:52 by the go file (P2V loop.py 1400531, P2W 1400534); both arms have the new LATE with
   --floor-ratio 20 (config.json floor_ratio 20.0), P2W's args end with --cp-renormalise-threshold 1000. Ends
   about 02:52.** **Result: P2W 20,154 against P2V 20,974 at 3 h (−820; −77 at 30 min, −76 at 1 h, −467 at 2 h).
   Union 21,087 (P2W-only 113 for 12 worker-hours). The loss is in first runs after the first hour; L1 runs are 11%
   cheaper. Renormalisation stays on.**
0000000000000000000000000000. **exp53 candidate (16:58, run as exp53 above, rejected): deep runs without queue renormalisation, from zero.** Under
   --abstract-time renormalising the queue is 27% of a hinted run's CPU but free in abstract time; off, 80 s runs cost
   25% less with a different search (exp25: 2 of 3 proofs kept); exp26 in production was too thin to tell (7/209 vs
   5/186, [notes/2026-11-19-queue-renorm-ab.md](notes/2026-11-19-queue-renorm-ab.md)). In Z7 the retry and deep
   classes take about half the CPU after 2 hours, so a from-zero A/B has the volume: `PG="--cp-renormalise-threshold
   1000"` (solve_new.sh passes $PG into twee's arguments; empty for twee-pg61) against the control. After exp52.
000000000000000000000000000. **After the Z7 pair (plan agreed with the user, 14:34):** split the CPU instead of
   speed tests only. About 10 CPUs: exp52's A/B on half2 (LATE against LATE + `--floor-ratio 20`, 4 workers each, 3 h),
   judged also by the h and q classes' proofs and the union per worker-hour. About 10 CPUs: the unsolved 3,550:
   production restarted as ul74 at J=8 (its last 3.3 h: 62 new on 17 workers; the yield discount scored worse on its
   rows), the 20 s sweep at -j 1, the live transfer loops. User, 14:34: no E or Vampire; the work is on Twee.
   **Started early, with Z7C's CPU: production restarted 16:50 (abs/ul74.sh, J=6 while Z7 runs; loop.py 995541),
   the sweep 16:50 (995832, -j 1 from SW20/J). exp52 starts when Z7 ends.** exp52 started 20:49 (P2T loop.py
   1115326, P2U 1115327). The 20 s sweep ended at 20:58; its CPU went to the proof worker (-j 3, PID 1177545,
   21:02; 121,512 jobs queued, most from Z7 and Z7C). At -j 3 it reruns about 4,100 jobs an hour (3,468 in 21:03-21:54,
   from the proofq.log rows), and each half2 arm from zero queues about 25,000: 131,363 queued at 21:51. It needs
   more CPU in a gap between A/B tests to catch up.
00000000000000000000000000. **exp52 (13:30, DONE 23:50, ACCEPTED, [notes/2026-11-21-floor-ratio.md](notes/2026-11-21-floor-ratio.md)):
   P2U 20,876 against P2T 20,087 at 3 h (+789; +1,006 at 30 min, +910 at 1 h, +1,040 at 2 h). `--floor-ratio 20` is in
   solve_new.sh's LATE since 23:51 (0e6996b). Union 21,164 on 8 workers, 882 a worker-hour against P2U's 1,740.
   Watch the narrowing in hour 3 (−251) in the next 8-hour run.** Z7 at 30 minutes was 2,196
   behind Z7C: the q and h floors held half a worker of six at 77 and 12 proofs per run-hour against the first runs'
   6,885. loop.py `--floor-ratio K` (classes `--floor-classes`, default qh) keeps a floor only while K × its yield
   reaches the best class's. Smoke FRT fine. **abs/after_z7.sh (16:52) starts P2T (control) and P2U (+ --floor-ratio
   20) when Z7 ends: half2, 4 workers each, 3 hours (the user's CPU split); decision +185 at 3 h.**
0000000000000000000000000. **Z7 pair (12:48, [notes/2026-11-21-z7-pair.md](notes/2026-11-21-z7-pair.md)):** today's late-phase default
   (solve_new.sh LATE, P2O's set) against `LATE=` (the 20 Nov system), side by side on all goals from zero, 6 workers
   each, 8 hours (abs/z7pair.sh): Z7 vs Z7C. A pair because abscurve leaves 167-426 of a replica's gap. Decision: Z7 ≥
   Z7C + 260. Proof worker on again beside it.
   **At 4 hours (16:49) Z7 42,478, Z7C 41,237 (+1,241; −2,368 at 1 h, even at about 2 h 50 min): LATE confirmed on
   all goals. Z7C stopped at 16:49 (it proved 114 in the last half hour against Z7's 506); Z7 runs to 8 h (~20:50).**
   **At 8 h (20:49): Z7 43,767 on 6 workers, Z6 44,092 on 12 (cross-time; Z7 +1,289 from 4 to 8 h, Z6 +1,172).
   Z7 ∪ Z6 44,505. One goal new to the collection (mbol_asqr__goal_420) merged into production at 20:52.**
000000000000000000000000. **exp51 candidate (08:40, [notes/2026-11-21-head-time.md](notes/2026-11-21-head-time.md)):** P2O's failed L1
   head runs took 86.6 CPU s each (2.55 of class h's 2.86 CPU h); production's L1 proofs replayed at 20 s kept 73% for
   45% of the CPU. loop.py `--head-time S`: class h's chain-level runs at S (rows ht=1); a resume runs the rest of its
   level. Smoke HTT2 (6 workers) fine. A/B after exp49/50 and Z7.
00000000000000000000000. **Dispatch profile (07:20, [notes/2026-11-21-dispatch-profile.md](notes/2026-11-21-dispatch-profile.md)):** exp/stacksample.py
   samples loop.py's threads. At 6 workers workers are twee-bound (80%); the main thread spent 90 s (all goals) writing
   every rule-model goal file before the first run: now written at first use (loop.py goalfile, smoke GFT identical).
   Z6 at 12 workers had the main thread 76% busy early (about 20 ms a run): profile at 12 workers between exp48 and exp49.
0000000000000000000000. **exp50 (06:50, [notes/2026-11-21-retry-time.md](notes/2026-11-21-retry-time.md)):** L0 retries of failed-before goals
   took 30.8 of Z6's 96 CPU hours for 2,149 proofs (late: 5% proved); 78-84% of retry proofs come within 3 s. loop.py
   `--retry-time T` runs them at T s (rows r=1); a replay gives 1.2-1.4x proofs per CPU hour at T=3. Smoke loops/RTT;
   arm P2S = exp49's base + `--retry-time 3`, started with P2Q/P2R by abs/after48b.sh, against P2R. stepjlive3 stopped
   06:45 (no joins in 3 cycles).
   **P2S started 09:45:47 (loop.py 403368), against P2R.**
   **Stopped at 3 hours (12:47): P2S 21,098, P2R 21,264 (−166); its 3 s retries 114 proofs per CPU h against 137.
   Rejected.**
000000000000000000000. **exp49 (04:47, [notes/2026-11-21-quick-first.md](notes/2026-11-21-quick-first.md)):** in P2J the failed first runs took 10.3 of
   the first pass's 13.1 CPU hours, and 86% of first-run proofs came within 1 s. loop.py `--quick Q`: a goal's first
   fresh run at Q seconds; a goal that fails it gets its T0 run after the goals never run. Smoke tests loops/QKT
   (`--quick 1`) and QKC (control), smoke487, 2 workers, 12 minutes. A/B on half2 after exp48, on its winner's base.
   **Started 09:45:32 on P2O's set: P2Q (+ --quick 1, loop.py 401107), P2R (control, 401110); to about 14:50.**
   At 1 hour P2Q +975 at 15 min but −734 at 60: quick-failed near goals waited behind the far tail's quick runs (the
   key put quick-failed before near/far). `--quick-near` (smoke QKN) reorders; the second try if P2Q loses.
   **Stopped at 3 hours (12:47): P2Q 20,545, P2R 21,264 (−719; +225/−959). Rejected; `--quick-near` is a later,
   short A/B.**
00000000000000000000. **exp48 (03:37, [notes/2026-11-21-late-combo.md](notes/2026-11-21-late-combo.md)):** at 4 hours P2H (--retry-class) +697 and P2J
   (--yield-discount 2000 --reexplore 12:0.25) +796 over P2K. P2N = both; P2O = P2N + --knn-ctx 10 --head-class
   (exp46/47 in one arm, to stay near 24 CPUs). half2, 5 h, when exp44/45 end; abs/after4445e.sh waits for
   loops/GO48. Production stays paused. **At 5 hours (04:35) P2K 21,147, P2H 21,597 (+450), P2J 21,706 (+559):
   both options become defaults; union P2H ∪ P2J 21,924. P2N and P2O started 04:36** (loops/AFTERZ6.pids), to
   about 09:40. Decision: P2N ≥ P2J + 185 makes the pair the default; P2O ≥ P2N + 185 adds the two options.
   **DONE 09:38: P2O 21,939, P2N 21,698 (P2O +241 side by side). At equal abstract work (exp/abscurve.py; the machine
   was ~15% faster than in exp44/45) P2O ties P2J (21,706) and P2N trails it by 325. Default: P2O's set; exp49/50 on it.**
0000000000000000000. **exp47 (01:40, [notes/2026-11-21-head-class.md](notes/2026-11-21-head-class.md)):** Z6 ended with 1,120 unsolved heads,
   875 of them proved by production, and ran L1 16 times in 8 hours (3 on those heads): with --ratio-order L1's
   estimate stays near its prior and its entries come last. loop.py `--head-class`: heads whose next own level is
   L1 are a mix class (h). Smoke test loops/HCT; A/B P2M on half2 beside P2L. The roots at 40 s in Z6's context:
   38 of 61 at 01:38.
000000000000000000. **exp46 (00:55, [notes/2026-11-21-knn-ctx.md](notes/2026-11-21-knn-ctx.md)):** Z6 waited long to use new kNN
   lemmas: after hour 1, 56% of the proofs whose last lemma was a kNN lemma came over 10 minutes after it (siblings:
   at once). With --fail-order a kNN change never made a retry (only the learned scheduler looked). loop.py
   `--knn-ctx K`: after each kNN rebuild, a goal for which a new proof enters its top K kNN lemmas has a new context. Smoke
   tests loops/KCT, KCT2, KCT3; A/B P2L (K=10) on half2 after exp44/45 (abs/after4445b.sh).
00000000000000000. **Roots (00:44; latency 00:48, [notes/2026-11-21-roots.md](notes/2026-11-21-roots.md)):** of the 4,117 goals production has and Z6
   lacks, 190 have recorded lemmas that Z6 all proved (L1 104, L0 46, L2 26); their reach is 363. The rest rest on
   lemmas Z6 lacks (2,981 through goals without a record). The gap is mostly depth. Test: the 190 at 40 s in Z6's
   context, loops/ROOTS/t40, 1 worker (abs/roots_t40.sh).
0000000000000000. **exp45 (written 19:38, starts with exp44 when Z6 ends, [notes/2026-11-20-yield-discount.md](notes/2026-11-20-yield-discount.md)):**
   Z6 after 4 hours ran only Vunf@0 (2 of its last 291) and L0 retries: its cumulative estimate (23 per CPU h) kept
   L1 (9 of 16, only in the first hour) from ever running again. estcmp on Z6's rows: cumulative -791, flat -616,
   discounted over 1,000 rows -557; production's rows keep cumulative best. loop.py `--yield-discount N`; P2J =
   defaults + `--yield-discount 2000 --reexplore 12:0.25` against P2K, half2, 5 h. exp44 changed to 5 h against P2K
   too (abs/exp4445.sh); production and stepjlive3 start when the three arms end (abs/afterz6.sh, 19:38; from 21 Nov 00:56 abs/after4445.sh, production at J=6 beside exp46). **DONE 04:35: P2J 21,706, P2K 21,147 (+559).**
000000000000000. **exp44 (written 18:44, starts when Z6 ends, [notes/2026-11-20-retry-class.md](notes/2026-11-20-retry-class.md)):** Z6's first runs ended at
   about 150 min, then retries of goals with a new context proved 47% (1,096 of 2,331 in half an hour), the last
   first runs 3%. loop.py `--retry-class`: failed-before goals as their own --mix class. P2H on half2 against P2E/P2F.
   (Design changed 19:37: 5 hours against P2K, see exp45.) **DONE 04:35: P2H 21,597, P2K 21,147 (+450).**
00000000000000. **20 s sweep (15:32, [notes/2026-11-20-sweep20.md](notes/2026-11-20-sweep20.md)):** 2,895 unsolved goals never had a production run
   above 5 s; the non-joined test proved 4 of 100 such at 20 s. exp/sweep20.py loops/SW20, chunks of 300 with a
   fresh trusted lemma context, 2 workers, proofs into UL (and kept). Production's own loop is stopped (2 proofs in
   its last 2,000 runs). Chunk 0 (16:47): 2 of 300, 0.8 per CPU h (the pilot's sample was nearer); kept running.
   **Done 21 Nov 20:58: 30 of 2,874, 25.1 h of run time, 1.2 per CPU h (production's own loop meanwhile about 0.45).**
0000000000000. **Z6 (15:30, DONE 23:33, [notes/2026-11-20-z6.md](notes/2026-11-20-z6.md)): 44,095 at 8 hours, Z4 38,044; 4,113 production-only, 2 Z6-only merged.** today's from-zero system on all 51,784, 12 workers, 8 hours
   (to about 23:30), `--knn-refresh 600`, against Z4 (37,713 at 2 h). abs/z6_test.sh; read with
   `abs/setcurve.py sets/all Z4 Z6 --at 10,30,60,120,180,240,360,480`. Production's own loop stopped meanwhile.
000000000000. **The half gap (13:43, [notes/2026-11-20-half-gap.md](notes/2026-11-20-half-gap.md)):** of the goals production has and the from-zero
   half arms lack, most fell to production's 5 s level, and 80% (half2) / 76% (half1) of those proofs used a kNN
   lemma from the other half, which a half run cannot have. Half tests stay for A/B; the long from-zero run goes on
   the whole benchmark (Z6 after exp43: today's defaults, 12 workers, 8 hours, against Z4).
00000000000. **exp43 (13:28, [notes/2026-11-20-given-nowait.md](notes/2026-11-20-given-nowait.md)):** P2G = P2F + givenmatch `--no-wait`
   (hits run as soon as found), half2 from zero, 2 hours, against P2F. abs/exp43.sh.
   Done 15:29: **P2G 19,994 vs P2F 20,174 (−180, edge of noise)**; +254/−438. The live loop made 1,494 proofs
   (P2F 559), mostly goals the loop proves anyway. The wait stays.
0000000000. **Semantic guidance offline (12:14, [notes/2026-11-20-semantic-guidance.md](notes/2026-11-20-semantic-guidance.md)):** are proof steps false in
   Mace4 models of the base axioms where an extra axiom fails (SCOTT-style relevance) more often than other given
   rules? exp/semguide.py over 10 logs per original. Done 12:36: 62 originals with models; 32.4% vs 30.4%, lift
   1.09 (18 originals clearly enriched, 11 depleted). Closed as a weak negative.
000000000. **exp42 (11:27, [notes/2026-11-20-given-cap.md](notes/2026-11-20-given-cap.md)):** half2 from zero, P2F = P2E (solve_new.sh defaults)
   with the live loop at `--cap 200 --same-cap 20` (ancestry runs no longer starved by the same-statement runs),
   against exp41's P2E (20,152 at 2 h). abs/exp42.sh; production at J=6, rever at 2 meanwhile.
   Done 13:28: **P2F 20,174 vs P2E 20,152 (+22, noise)**; +301/−272. Ahead early (+175 at 30 min), caught up by
   2 h. The cap was never reached (0-86 goals a cycle); the wait for the loop's failure limited the ancestry runs,
   and their extra proofs were goals the loop proves anyway. Default stays.
00000000. **Model audit (10:54, [notes/2026-11-20-model-audit.md](notes/2026-11-20-model-audit.md)):** exp/modelcheck.py evaluates every proof step
   of every solved unit goal in up to 40 Mace4 models (sizes 2-8) of its theory; a step false in a model is not a
   theorem. Self-test: all goal statements must hold. Done 11:17: 2.4M step checks in 2,504 models of 68 theories;
   0 false goals; 217 false steps in 71 goals, all printed goal terms (different variables on the two sides, e.g.
   X0 = X1), none a wrong derived equation. Positive control: 13 of the 16 unsound Prover9 proofs have one
   (ld(X0,e) = X0). stepjoin now model-checks its step axioms.
0000000. **Step joins (10:43, [notes/2026-11-20-step-join.md](notes/2026-11-20-step-join.md)):** exp/joincheck.py over all 3,170 unsolved
   unit goals with trusted proof steps of weaker theories; exp/stepjoin.py proves each join with the steps as named
   lemma axioms. All 3,684 (3,170 unit, 514 conditional with the hypothesis as a ground rule): 23 joins, 23 proved.
   Live from 10:50 (abs/stepjlive.sh, every 30 min); cycle 1 of stepjlive2 (11:57): +1, 24 of 24.
   Cross-run pilot (the goal's own failed run's given rules in the bank, exp/owng_pilot.py): 0 of 30; closed.
   Bigger bank (12:38-13:31): the from-zero arms' proofs of the same goals (joincheck `--banks`), 43% more
   equations, 0 of 1,557 joined (shard 0/2); 2,264 false printed goal lines dropped by the new model filter. Closed.
   Non-joined steps (13:33): 100 non-joined goals with their normalising steps as lemmas (loops/STEPN) vs without
   (STEPN0), 20 s, 1 worker each. Done 14:22: 4 = 4 (the same goals): closed. Production had run those 4 only at 5 s.
000000. **Soundness (10:00, [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md)):** p9twee.ladr wrote TPTP `~ a = b` as
   LADR `- a = b` (the equation (-a) = b): conditional sibling lemmas became false axioms, and 16 Prover9 proofs in
   production used one (P9C, P9L, P9T, exp16). Fixed 09:45. Quarantine of 1,130 goals at 10:07 (closure + proofs
   without lemma records); exp/trust.py (trusted = before 15 Nov 08:56, or every recorded lemma trusted) and
   exp/rever2.py (re-proves the roots with a trusted context, --keep-out) running from 10:32. The side loops now keep
   outputs (abs/xfrlive2k.sh, gmlive2k.sh); transfer.py names source lemmas by goal.
00000. **exp41 done (11:20, [notes/2026-11-20-half2-given.md](notes/2026-11-20-half2-given.md)):** half2 from zero, P2E (GIVEN=1) 20,152 at
   2 hours against P2D's 19,383: +941/−172, net +769 (half1 exp40: +282). Replicates; GIVEN=1 stays. The live loop's
   ancestry runs made 541 proofs per CPU h, same-statement runs 80, and the 60-goal cap starved the former (145-192
   pending). Next: exp42 with --cap 200 --same-cap 20 on half1 against PGE, after the re-verification.
0000. exp40 ([notes/2026-11-20-from-zero-given.md](notes/2026-11-20-from-zero-given.md)): half1 from zero as exp29's PGD (19,309 at 2 h)
   plus `--given-scan` and givenmatch.py live on the loop (abs/exp40.sh); production at J=4 meanwhile.
   Done 09:06: **PGE 19,591, +282** (+150 at equal CPU); the live loop 614 of 901 in 2.97 CPU h (ancestry runs 434
   of 478 at 790 per CPU h); one-arm 643 vs 368. solve_new.sh GIVEN=1 by default (09:13); givenmatch live --loops.
000. exp39 (05:39, [notes/2026-11-20-base-saturation.md](notes/2026-11-20-base-saturation.md)): base-theory runs (13 originals share the 17 base
   axioms, within nearly every theory) as rule generators for 3,001 unsolved goals; pilot exp/gensat.py, 120 runs of 30 s,
   3 workers, hits to loops/GSAT for the live loop. Production's base runs gave about 16 goals per CPU h.
   Done 07:24: three settings, 4.96 CPU h, 20 new hits, 8 + 1 direct proved (about 1.8 per CPU h); exp39b (hypotheses
   dropped) 0 = 0 of 60. Production's failed-run hits fell from 19 to 17 to 1 an hour (an accumulated harvest).
   Time-matched control final: rm4t 40 s 225 of 400 vs rm4t|rm9f at 20 s 218, union 232.
00. exp38 ([notes/2026-11-20-given-transfer.md](notes/2026-11-20-given-transfer.md)): unsolved goals that other runs derived and did not use. Full scan 19 hits, 13
   proved; live loop loops/GML (abs/gmlive.sh, every 20 min) 3 of 5 in cycle 1. Next: `--given-scan` in loop.py
   (failed runs' given rules), ancestries fixed at 04:08 (parents are numbers). ul74 (04:15, J=12) = ul73 +
   `--given-scan loops/GFAIL` + m10f@0 (rm9f's recipe on all data) in place of m9f@0.
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
| [notes/2026-11-20-from-zero-given.md](notes/2026-11-20-from-zero-given.md) | exp40: half1 from zero with the derived-rule transfer (--given-scan + givenmatch live) |
| [notes/2026-11-20-half2-given.md](notes/2026-11-20-half2-given.md) | exp41: exp40 replicated on half2 (solve_new.sh GIVEN=1 against P2D) |
| [notes/2026-11-20-p9-negation-bug.md](notes/2026-11-20-p9-negation-bug.md) | Unsound Prover9 proofs (p9twee negation bug), the quarantine and the trust re-verification |
| [notes/2026-11-20-step-join.md](notes/2026-11-20-step-join.md) | Step joins: unsolved goals closed by rewriting with proof steps of weaker theories |
| [notes/2026-11-20-model-audit.md](notes/2026-11-20-model-audit.md) | Soundness audit: every proof step evaluated in finite models of its theory |
| [notes/2026-11-20-given-cap.md](notes/2026-11-20-given-cap.md) | exp42: the derived-rule transfer with the ancestry runs uncapped (P2F against P2E) |
| [notes/2026-11-20-semantic-guidance.md](notes/2026-11-20-semantic-guidance.md) | Semantic guidance offline: proof steps vs other given rules in relevance models |
| [notes/2026-11-20-given-nowait.md](notes/2026-11-20-given-nowait.md) | exp43: derived-rule hits run without waiting for the loop's failure (P2G against P2F) |
| [notes/2026-11-20-half-gap.md](notes/2026-11-20-half-gap.md) | Why a from-zero half run stops short of production: the other half's kNN lemmas |
| [notes/2026-11-20-z6.md](notes/2026-11-20-z6.md) | Z6: today's from-zero system on the whole benchmark, 8 hours |
| [notes/2026-11-20-sweep20.md](notes/2026-11-20-sweep20.md) | One 20 s run for each unsolved goal that never had more than 5 s |
| [notes/2026-11-20-retry-class.md](notes/2026-11-20-retry-class.md) | exp44: failed-before goals as their own cascade class (P2H against P2K, 5 h) |
| [notes/2026-11-20-yield-discount.md](notes/2026-11-20-yield-discount.md) | exp45: a discounted yield estimate for the deeper levels from zero (P2J against P2K, 5 h) |
| [notes/2026-11-21-roots.md](notes/2026-11-21-roots.md) | Roots: which of production's proofs Z6 was one proof away from, and a 40 s test of them |
| [notes/2026-11-21-knn-ctx.md](notes/2026-11-21-knn-ctx.md) | exp46: a new kNN lemma counts as a new context (`--knn-ctx`) |
| [notes/2026-11-21-head-class.md](notes/2026-11-21-head-class.md) | exp47: heads at L1 as a class of their own (`--head-class`) |
| [notes/2026-11-21-late-combo.md](notes/2026-11-21-late-combo.md) | exp48: the late-phase winners together, and with exp46/47 |
| [notes/2026-11-21-quick-first.md](notes/2026-11-21-quick-first.md) | exp49: a quick first run for every goal (`--quick Q`) |
| [notes/2026-11-21-retry-time.md](notes/2026-11-21-retry-time.md) | exp50: shorter L0 retries (`--retry-time T`) |
| [notes/2026-11-21-dispatch-profile.md](notes/2026-11-21-dispatch-profile.md) | Where a from-zero start spends its time: loop.py's threads; goal files at first use |
| [notes/2026-11-21-head-time.md](notes/2026-11-21-head-time.md) | exp51 (candidate): shorter first runs for heads at the chain level (`--head-time S`) |
| [notes/2026-11-21-z7-pair.md](notes/2026-11-21-z7-pair.md) | Z7 pair: today's late-phase default against the 20 Nov system, on all goals |
| [notes/2026-11-21-floor-ratio.md](notes/2026-11-21-floor-ratio.md) | exp52: floors for the late classes only when they can compete (`--floor-ratio K`); accepted |
| [notes/2026-11-21-renorm-zero.md](notes/2026-11-21-renorm-zero.md) | exp53: deep runs without queue renormalisation, from zero (`--cp-renormalise-threshold 1000`) |
| [notes/2026-11-21-proof-cost.md](notes/2026-11-21-proof-cost.md) | What `--no-proof` saves in a search run: nothing measurable (42 proved runs) |
| [notes/2026-11-22-z8.md](notes/2026-11-22-z8.md) | Z8: the system as it stands, from zero on all goals (after exp52) |
| [notes/2026-11-22-late-ab.md](notes/2026-11-22-late-ab.md) | A late-phase A/B: the goals Z7 left, with Z7's proofs as the context; exp54 (`--head-time 20`) |
| [notes/2026-11-22-ul75.md](notes/2026-11-22-ul75.md) | ul75: production with the head class |
| [notes/2026-11-22-knn-drift.md](notes/2026-11-22-knn-drift.md) | exp55: retry the goals whose kNN lemmas drifted (`--knn-drift`) |
| [notes/2026-11-22-gm-retry.md](notes/2026-11-22-gm-retry.md) | exp56: retry the given-rule hits the live loop gave up on (exp/gmretry.py) |
| [notes/2026-11-22-cp-weights.md](notes/2026-11-22-cp-weights.md) | exp57: twee's critical-pair weights as portfolio members |
| [notes/2026-11-22-lemma-ax-replay.md](notes/2026-11-22-lemma-ax-replay.md) | exp58a: the lemma-axiom fix replayed on a from-zero live loop (exp/gmreplay.py) |
| [notes/2026-11-22-src-used.md](notes/2026-11-22-src-used.md) | exp58b: the source proofs' used lemma axioms in transfer runs (transfer.py --src-used, exp/soreplay.py) |
| [notes/2026-11-22-hub-roots.md](notes/2026-11-22-hub-roots.md) | exp59: the goals only production has, their lemma roots, and the hubs run long in Z8's context |
| [notes/2026-11-22-floor-ratio-until.md](notes/2026-11-22-floor-ratio-until.md) | exp60: `--floor-ratio-until 120` from zero against the control |
| [notes/2026-11-22-retry-deficit.md](notes/2026-11-22-retry-deficit.md) | exp61: what Z8's final context proves in 5 s (the retry deficit) |
| [notes/2026-11-22-o2-build.md](notes/2026-11-22-o2-build.md) | exp62: twee built with -O2 against the -O1 production binary |
| [notes/2026-11-22-frontier-orderings.md](notes/2026-11-22-frontier-orderings.md) | exp63: another term ordering on production's frontier |
| [notes/2026-11-23-z9.md](notes/2026-11-23-z9.md) | Z9: the system from zero on all goals after exp55 and exp60 (6 workers, 8 hours) |
| [notes/2026-11-23-model-audit2.md](notes/2026-11-23-model-audit2.md) | The finite-model audit again on production's proofs since 20 Nov |
| [notes/2026-11-23-readiness.md](notes/2026-11-23-readiness.md) | How long ready goals wait (Z8), and kNN readiness against the gap order for first runs |
| [notes/2026-11-23-conditional.md](notes/2026-11-23-conditional.md) | COND1: the unsolved goals with their earlier siblings assumed: hard steps or blocked |
| [notes/2026-11-23-plain-level.md](notes/2026-11-23-plain-level.md) | exp64: a plain level (no hints, no model) from zero |
| [notes/2026-11-23-lemma-ranker.md](notes/2026-11-23-lemma-ranker.md) | a learned ranker for the plain runs' kNN lemmas |
| [notes/2026-11-23-plain-sizes.md](notes/2026-11-23-plain-sizes.md) | exp65: plain levels with 400 and 1,600 kNN lemmas from zero; the frontier sweep PLG1 |
| [notes/production-history.md](notes/production-history.md) | Production's history: every ulNN version's options, members, workers, dates and reason, and the side loops (generated) |
| [notes/2026-11-23-climber-restart.md](notes/2026-11-23-climber-restart.md) | exp66: the live head climber restarted beside production (stopped 20 Nov, 1.04 per CPU h then); per CPU h against the plain head runs |
| [notes/2026-11-23-tail-allocation.md](notes/2026-11-23-tail-allocation.md) | exp72: the tail's side loops by proofs per CPU h; the plain live loop without L, a plain 60 s sweep on the 940 local heads, the climber on the other holes |
| [notes/2026-11-24-cond-replay.md](notes/2026-11-24-cond-replay.md) | exp75: replaying the climbers' conditional proofs once their assumptions are proved (exp/condreplay.py, abs/crploop.sh); weakened-goal sketches; exact assumption records in used.tsv |
| [notes/2026-11-24-lemma-cost.md](notes/2026-11-24-lemma-cost.md) | exp80: what twee's runs with hundreds of lemma axioms cost per abstract second, and where the time goes |
| [notes/2026-11-24-plain-time.md](notes/2026-11-24-plain-time.md) | exp81: plain 300 s against 60 s on local heads that failed at 60 s |
| [notes/2026-11-20-base-saturation.md](notes/2026-11-20-base-saturation.md) | exp39: base-theory runs as rule generators for the unsolved goals of the stronger theories |
| [notes/2026-11-20-given-transfer.md](notes/2026-11-20-given-transfer.md) | exp38: unsolved goals that are variants of rules other runs derived and did not use (379 M in the given logs; transfer.py only matches proof steps); their ancestry as hints |
| [notes/2026-11-19-from-zero-portfolio.md](notes/2026-11-19-from-zero-portfolio.md) | half1 from zero in 2 hours with today's deep portfolio (PGC), against PGA's 18,987 (exp27, from 07:18) |
| [notes/2026-11-17-lemma-circularity.md](notes/2026-11-17-lemma-circularity.md) | Are lemma chains circular? A check of the used lemmas |
| [notes/2026-11-17-mix-fail-order.md](notes/2026-11-17-mix-fail-order.md) | Repeats cost most of the time: `--mix` and `--fail-order` |
| [notes/2026-11-17-pg-ab-half1.md](notes/2026-11-17-pg-ab-half1.md) | Parental guidance at scale: half1 from zero, 2 hours, sum filter 0.25 against the defaults |
| [notes/2026-11-17-pg-learned-dense.md](notes/2026-11-17-pg-learned-dense.md) | Learned parental models on 10 numbers per rule |
| [notes/2026-11-17-pg-pcat-enigma.md](notes/2026-11-17-pg-pcat-enigma.md) | Pcat parental models on hashed ENIGMA features, as in the paper |
| [notes/2026-11-17-pg-sum-filter.md](notes/2026-11-17-pg-sum-filter.md) | Parental guidance with the sum filter, on 200 hard goals |
| [notes/2026-11-17-tail-states-e44.md](notes/2026-11-17-tail-states-e44.md) | The tail: which goals get longer runs; original rates; saved states; noise at scale; e43/e44 |

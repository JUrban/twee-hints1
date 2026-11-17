# Are lemma chains circular? A check of the used lemmas

**Question.** The user, 17 Nov ~18:30, reading "the 6 nearest proven sibling goals of the same original, on
either side by goal order, as axioms": "if we prove a lemma A from lemma B which follows it, and lemma B from
lemma A which precedes it, we can get some very simple and circular proofs?"

**The argument.** A cycle cannot form when four things hold:
1. A run gets as lemmas only goals already proven when its problem is written (loop.py `lemma_src` grows
   only in `add_proof`).
2. A solved goal is not run again (production's `rerun_solved` is False).
3. merge.py appends an arm's rows in their order and skips goals already present.
4. Side workers take lemmas from their copy of the loop's proven goals.

Then along solved.tsv each proof uses only earlier proofs. Inlining the lemmas' proofs recursively ends,
because each step goes back in time, so each goal has a proof from its own axioms. Whichever of A and B is
proven first was proven without the other.

The kNN lemmas from other originals rest on a separate assumption: the source's axioms are the same as the
target's or a subset of them.

**Setup.** hints/depcheck.py DIR reads the kept outputs (`--keep-out`: DIR/r*/out/<goal>, twee's USEDAXIOMS
line, printed since 14 Nov 16:13). It maps lemma names to goals: `lemma_goal_<j>` is goal j of the same
original, and `lemma_knn_<i>_<goal>` names its goal. Then it checks:
* each used lemma's goal has its first solved.tsv row before the proof's own row;
* the graph of recorded proofs has no cycle;
* each used lemma's own problem file has a subset of the target's axioms (clause bodies without
  whitespace). This reads the files directly, not lemmas.axiom_set, which assumes all goals of an original
  share axioms.

One subtlety. A goal can have two rows: a live-transfer proof (time 0) is synced only every 60 s, so the loop
can prove the goal again in between. The kept output is then the later run's, so its row is the goal's last
row. The first version of the check compared against the first row and reported 3–13 false violations per
loop. One case: Z4's goal nil3_23_32_to_27__goal_30 had the transfer's row 14871, then the loop's run at row
15258 used goal 29 from row 14983.

**Results** (17 Nov 18:30):

| loop | recorded proofs | later-lemma violations | cycles | lemmas from a non-weaker theory | no lemma used |
|---|---:|---:|---:|---:|---:|
| UL (production, kept outputs since 14 Nov) | 3,112 | 0 | 0 | 0 of 20,448 | 0.3% |
| Z4 (whole benchmark from zero, 4 h) | 31,452 | 0 | 0 | 0 of 68,189 | 13.7% |
| PGA (half1 A/B arm) | 16,541 | 0 | 0 | | 14.0% |
| ORH (half1, 2 h) | 15,955 | 0 | 0 | | 14.3% |

* Use of a later sibling as a lemma (the user's scenario, valid when that sibling was proven first): 41.3%
  of UL's recorded proofs, 2.3% of Z4's. An earlier sibling: 68.8% and 22.8%. A kNN goal of another
  original: 85.5% and 79.7%. Script: exp/depcheck_above.py.
* Lemma-chain depth within UL's recorded proofs reaches 36; the full chains are longer.
* 4,465 of Z4's goals have two rows: the loop proved them again before the transfer's row was synced. That
  is wasted work.

**Reading.**
* No circular proofs, and the cross-theory lemmas are sound, on every recorded proof.
* For UL that covers only 7% of the solved goals (3,112 of 44,876). The earlier ones have no kept output with
  the line, and rest on the argument above.
* The user's other point stands. Our "solved" counts are proofs with lemmas: most of production's late
  proofs need proven siblings or kNN goals, and 41% use a later sibling. These proofs are valid, and each
  goal is a theorem of its axioms. But they are a different, easier measure than proving each problem alone;
  plain twee alone at 4 s gets 31,060.

**Decision and next.**
* Run depcheck.py on every loop before quoting its totals, and keep `--keep-out` on.
* Measure how much worker time the double proofs cost (Z4: 4,465), and sync side-worker rows before
  dispatching a goal.
* Consider reporting a standalone count beside the totals.

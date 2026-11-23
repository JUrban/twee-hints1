# (19 Nov, the user: "it might be good to have in the REPORT.md and JOURNAL.md links to the more detailed reports in
# notes/") Turns every plain notes/<file>.md (or hints/notes/<file>.md) in REPORT.md and JOURNAL.md into a markdown
# link, expands abbreviated names (", -chain-hints-short.md"), and under each REPORT section adds a "Notes:" line for
# the notes of that section it does not name yet. Idempotent: existing links are left alone.
import re, os, sys, collections
NOTES = sorted(f for f in os.listdir('notes') if f.endswith('.md'))
MAP = {  # note -> REPORT section, for notes the section does not name (checked by hand, 19 Nov)
    '2026-11-12-hints-dev10.md': '2', '2026-11-12-hint-selection.md': '2', '2026-11-12-long-runs-checkpoints.md': '2c',
    '2026-11-12-rule-model.md': '2b', '2026-11-13-axiom-groups.md': '2l', '2026-11-13-enigma-loop.md': '2f',
    '2026-11-13-full-benchmark.md': '2h', '2026-11-13-hyp-hints-abstract-time.md': '2j', '2026-11-13-lemma-import.md': '2g',
    '2026-11-13-long-runs-stall.md': '2m', '2026-11-13-online-pools-cascade.md': '2o', '2026-11-13-p9-sfdf.md': '2n',
    '2026-11-14-ablation-lemma-count.md': '2q', '2026-11-14-enigma-looping-deepire.md': '2u',
    '2026-11-14-hint-axioms-profile.md': '2s', '2026-11-14-line-gaps-stalled.md': '2z', '2026-11-14-long-run-speed.md': '2v',
    '2026-11-14-p9loop-bigloop.md': '2w', '2026-11-14-resume-bug-consider-cost.md': '2x', '2026-11-14-sketch-climbing.md': '2ab',
    '2026-11-15-conjecture-cuts.md': '2ai', '2026-11-15-heads-fresh-vs-resume.md': '2ag', '2026-11-15-hint-generator.md': '2ah',
    '2026-11-15-learned-scheduler.md': '2ac', '2026-11-15-retrain-gnn-p9side.md': '2ad', '2026-11-15-retrain-stall-artefact.md': '2ae',
    '2026-11-15-sketches-stronger.md': '2aj', '2026-11-16-from-zero-dispatcher.md': '2as', '2026-11-16-knn-lemma-count.md': '2am',
    '2026-11-16-lattice-moves.md': '2ak', '2026-11-16-queue-model-lemma-proof-hints.md': '2ao', '2026-11-16-replay-unseen.md': '2aq',
    '2026-11-16-same-statement-other-theory.md': '2ar', '2026-11-16-step-transfer.md': '2al',
    '2026-11-17-lemma-circularity.md': '2g', '2026-11-17-mix-fail-order.md': '2at', '2026-11-17-pg-learned-dense.md': '2av',
    '2026-11-17-pg-sum-filter.md': '2av', '2026-11-17-tail-states-e44.md': '2au', '2026-11-18-chain-size.md': '2ay',
    '2026-11-18-chain-transfer-records.md': '2ax', '2026-11-18-knn60-walls.md': '2ay', '2026-11-18-no-pg-no-model-walls.md': '2az',
    '2026-11-18-prover9-chain-walls.md': '2ay', '2026-11-18-set-join-walls.md': '2ay', '2026-11-18-subsumption-deep.md': '2ay',
    '2026-11-18-two-sided-chain.md': '2ay', '2026-11-18-unfolded-walls.md': '2ay', '2026-11-19-far-goals-deep.md': '2az',
    '2026-11-19-from-zero-explore.md': '2az', '2026-11-19-half2-replication.md': '2az', '2026-11-19-enigmawatch.md': '2az', '2026-11-19-climber-member.md': '2az', '2026-11-19-oracle-pg.md': '2av', '2026-11-19-climber-outputs.md': '2az', '2026-11-19-pg-order.md': '2ao', '2026-11-19-climb-ablation.md': '2az', '2026-11-19-retrained-models.md': '2av', '2026-11-20-given-transfer.md': '2al', '2026-11-20-base-saturation.md': '2al', '2026-11-20-from-zero-given.md': '2az', '2026-11-20-half2-given.md': '2az', '2026-11-20-p9-negation-bug.md': '2ba', '2026-11-20-step-join.md': '2az', '2026-11-20-given-cap.md': '2az', '2026-11-20-given-nowait.md': '2az', '2026-11-20-half-gap.md': '2az', '2026-11-20-z6.md': '2az', '2026-11-20-retry-class.md': '2az', '2026-11-20-yield-discount.md': '2az', '2026-11-20-sweep20.md': '2az', '2026-11-21-roots.md': '2az', '2026-11-21-knn-ctx.md': '2az', '2026-11-21-head-class.md': '2az', '2026-11-21-late-combo.md': '2az', '2026-11-21-quick-first.md': '2az', '2026-11-21-retry-time.md': '2az', '2026-11-21-dispatch-profile.md': '2as', '2026-11-21-head-time.md': '2az', '2026-11-21-z7-pair.md': '2az', '2026-11-21-floor-ratio.md': '2az', '2026-11-21-renorm-zero.md': '2az', '2026-11-21-proof-cost.md': '1', '2026-11-22-z8.md': '2az', '2026-11-22-late-ab.md': '2az', '2026-11-22-ul75.md': '2az', '2026-11-22-knn-drift.md': '2az', '2026-11-22-gm-retry.md': '2al', '2026-11-22-cp-weights.md': '2az', '2026-11-22-lemma-ax-replay.md': '2al', '2026-11-22-src-used.md': '2al', '2026-11-22-hub-roots.md': '2az', '2026-11-22-floor-ratio-until.md': '2az', '2026-11-22-retry-deficit.md': '2az', '2026-11-22-o2-build.md': '2d', '2026-11-22-frontier-orderings.md': '2az', '2026-11-23-z9.md': '2az', '2026-11-23-model-audit2.md': '2ba', '2026-11-23-readiness.md': '2az', '2026-11-23-conditional.md': '2az', '2026-11-23-plain-level.md': '2az', '2026-11-20-semantic-guidance.md': '2ba', '2026-11-20-model-audit.md': '2ba', '2026-11-19-queue-renorm-ab.md': '2az', '2026-11-16-knn-lemma-count.md': '2am',
}
def expand(s):
    """', -name.md' after a full notes/DATE-... name -> notes/<the unique notes file DATE-name.md>"""
    def f(m):
        c = [n for n in NOTES if re.fullmatch(r'2026-\d\d-\d\d-' + re.escape(m.group(2)), n)]
        return m.group(1) + 'notes/' + c[0] if len(c) == 1 else m.group(0)
    return re.sub(r'([\s(])-([a-z0-9][a-z0-9-]*\.md)', f, s)
def linkify(s):
    out = []; i = 0
    for m in re.finditer(r'(?:hints/)?notes/((?:2026-[\w.-]+?|README)\.md)', s):
        a, b = m.span()
        pre = s[max(0, a - 2):a]
        if pre.endswith('[') or pre == '](' or (a > 0 and s[a - 1] in '/`'):
            continue
        if m.group(1) not in NOTES:
            print('NO SUCH NOTE', m.group(0), file=sys.stderr); continue
        out.append(s[i:a]); out.append(f'[notes/{m.group(1)}](notes/{m.group(1)})'); i = b
    out.append(s[i:])
    return ''.join(out)
r = open('REPORT.md').read()
r = linkify(expand(r))
# per-section Notes lines
lines = r.split('\n')
secpos = {}
for i, l in enumerate(lines):
    m = re.match(r'## (2[a-z]{0,2}|\d+)\.? ', l)
    if m: secpos.setdefault(m.group(1), i)
order = sorted(secpos.items(), key=lambda x: x[1])
def sec_text(k):
    i = secpos[k]; j = min([p for _, p in order if p > i] or [len(lines)])
    return '\n'.join(lines[i:j])
add = collections.defaultdict(list)
for n, k in MAP.items():
    if k not in secpos:
        print('NO SECTION', k, n, file=sys.stderr); continue
    if f'](notes/{n})' not in sec_text(k):
        add[k].append(n)
for k, ns in sorted(add.items(), key=lambda x: -secpos[x[0]]):
    i = secpos[k]
    lines[i + 1:i + 1] = ['', '*Notes: ' + ', '.join(f'[notes/{n}](notes/{n})' for n in sorted(set(ns))) + '.*']
r = '\n'.join(lines)
ptr = ("**Detailed reports.** Each experiment has its own report in [notes/](notes/): the question and who asked, "
       "the exact setup, the numbers, the noise, and what they do not show. The index is "
       "[JOURNAL.md section 9](JOURNAL.md#9-experiment-reports-hintsnotes). Each section below links the notes it "
       "rests on.\n\n")
key = '**Summary.** On all 51,784 public AIM60k problems'
if '**Detailed reports.**' not in r:
    assert key in r; r = r.replace(key, ptr + key, 1)
open('REPORT.md', 'w').write(r)
j = open('JOURNAL.md').read()
j = linkify(expand(j))
old = "## 9. Experiment reports (hints/notes/)\n"
if '[notes/README.md](notes/README.md)' not in j:
    assert old in j
    j = j.replace(old, old + "\nConventions for a report: [notes/README.md](notes/README.md).\n", 1)
open('JOURNAL.md', 'w').write(j)
# check: every link target exists
for f in ('REPORT.md', 'JOURNAL.md'):
    t = open(f).read()
    tg = re.findall(r'\]\((notes/[^)#]*)\)', t)
    bad = [x for x in tg if not os.path.exists(x)]
    plain = re.findall(r'(?<![\[(/`])notes/2026-[\w.-]+?\.md', re.sub(r'\[notes/[^\]]*\]\(notes/[^)]*\)', '', t))
    print(f, 'links', len(tg), 'distinct', len(set(tg)), 'broken', bad, 'plain left', plain[:5])
t = open('REPORT.md').read() + open('JOURNAL.md').read()
print('notes not linked from either:', [n for n in NOTES if f'](notes/{n})' not in t])

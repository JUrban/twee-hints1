#!/usr/bin/env python3
"""Where a fresh-context replay's extra proofs get their help (16 Nov 22:30).

  leakcheck.py SET ARM BASE [--ctx loops/UL]

For ARM's proofs of SET that BASE (the same replay on loops/ALL) lacks: the kNN lemma sources named in ARM's kept
outputs and the transfer sources in ARM.xfer/transfer.tsv. Each source of another original is 'old' (in loops/ALL,
13 Nov, before any loop ran on SET's originals), 'checked' (newer, and a kept output or transfer row names its own
sources, none of SET's originals) or 'unchecked' (newer, provenance unknown: could carry SET's goals).
"""
import collections, glob, os, re, sys
args = sys.argv[1:]
ctx = 'loops/UL'
if '--ctx' in args:
    i = args.index('--ctx'); ctx = args[i + 1]; del args[i:i + 2]
S, arm, base = args
o_ = lambda g: g.rsplit('__goal_', 1)[0]
G = {l.strip() for l in open(S) if l.strip()}
O = {o_(g) for g in G}
def solved(d):
    return {l.split('\t')[0] for l in open(f'loops/{d}/solved.tsv')
            if l.split('\t')[0] in G and os.path.exists(f'loops/{d}/hints/' + l.split('\t')[0])}
A, B = solved(arm), solved(base)
extra = A - B
ALL = {l.split('\t')[0] for l in open('loops/ALL/solved.tsv')}
checked = set()
for d in glob.glob(f'{ctx}/r*/out'):
    for g in os.listdir(d):
        for x in open(os.path.join(d, g), errors='replace'):
            if x.startswith('USEDAXIOMS'):
                if re.search(r'lemma_knn_\d+_\S', x) and not any(
                        o_(s) in O for s in re.findall(r'lemma_knn_\d+_(\S+__goal_\d+)', x)):
                    checked.add(g)
                break
for f in glob.glob('loops/*/transfer.tsv') + glob.glob('loops/*.xfer/transfer.tsv'):
    for l in open(f, errors='replace'):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 5 and w[1] == 'THM' and not any(o_(s) in O for s in w[4].split(',') if s):
            checked.add(w[0])
srcs = collections.defaultdict(set)
for f in glob.glob(f'loops/{arm}/r*/out/*'):
    g = os.path.basename(f)
    if g not in extra:
        continue
    for x in open(f, errors='replace'):
        if x.startswith('USEDAXIOMS'):
            srcs[g] |= set(re.findall(r'lemma_knn_\d+_(\S+__goal_\d+)', x))
            break
for l in open(f'loops/{arm}.xfer/transfer.tsv'):
    w = l.rstrip('\n').split('\t')
    if w[0] in extra and w[1] == 'THM' and len(w) >= 5:
        srcs[w[0]] |= {s for s in w[4].split(',') if s}
def cls(s):
    return 'same3' if o_(s) in O else 'old' if s in ALL else 'checked' if s in checked else 'unchecked'
c = collections.Counter(); per = collections.Counter()
for g in extra:
    k = {cls(s) for s in srcs.get(g, ())}
    for s in srcs.get(g, ()):
        c[cls(s)] += 1
    per['no named source' if not k else 'some unchecked source' if 'unchecked' in k else 'only old/checked/own'] += 1
print(f'{arm} {len(A)}, {base} {len(B)}, extra {len(extra)}; sources {dict(c)}; proofs {dict(per)}')

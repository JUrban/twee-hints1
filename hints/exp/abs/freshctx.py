#!/usr/bin/env python3
"""Today's production proofs as a replay context (16 Nov 22:00).

  freshctx.py SET OUTDIR [--from loops/UL]

Writes OUTDIR/solved.tsv: the source loop's proofs, minus those known to use a goal of SET's originals (a kNN
lemma named in a kept output's USEDAXIOMS, or a source in a transfer.tsv row); OUTDIR/hints links to the source's
hints and OUTDIR/excluded.tsv lists what was left out. solve_new.sh with EXCLUDE=originals then leaves out the
originals' own proofs. Outputs that were not kept cannot be checked (on rp3 1.6% of the checked newer proofs used
an rp3 goal), so a replay on such a context can be slightly optimistic.
"""
import collections, glob, os, re, sys
args = sys.argv[1:]
src = 'loops/UL'
if '--from' in args:
    i = args.index('--from'); src = args[i + 1]; del args[i:i + 2]
S, out = args
o_ = lambda g: g.rsplit('__goal_', 1)[0]
O = {o_(l.strip()) for l in open(S) if l.strip()}
rows = collections.OrderedDict()
for l in open(f'{src}/solved.tsv'):
    w = l.rstrip('\n').split('\t')
    rows.setdefault(w[0], l if l.endswith('\n') else l + '\n')
cand = {g for g in rows if o_(g) not in O}
bad = {}
for d in glob.glob(f'{src}/r*/out'):
    for g in os.listdir(d):
        if g not in cand or g in bad:
            continue
        for x in open(os.path.join(d, g), errors='replace'):
            if x.startswith('USEDAXIOMS'):
                if any(o_(s) in O for s in re.findall(r'lemma_knn_\d+_(\S+__goal_\d+)', x)):
                    bad[g] = 'knn ' + d
                break
for f in glob.glob('loops/*/transfer.tsv') + glob.glob('loops/*.xfer/transfer.tsv'):
    for l in open(f, errors='replace'):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 5 and w[1] == 'THM' and w[0] in cand and w[0] not in bad \
                and any(o_(s) in O for s in w[4].split(',') if s):
            bad[w[0]] = 'transfer ' + f
os.makedirs(out)
with open(f'{out}/solved.tsv', 'w') as f:
    f.writelines(l for g, l in rows.items() if g not in bad)
with open(f'{out}/excluded.tsv', 'w') as f:
    f.writelines(f'{g}\t{v}\n' for g, v in sorted(bad.items()))
os.symlink(os.path.abspath(f'{src}/hints'), f'{out}/hints')
print(f'{out}: {len(rows) - len(bad)} of {len(rows)} proofs ({len(bad)} left out: '
      f'{dict(collections.Counter(v.split()[0] for v in bad.values()))}); {len(O)} originals in {S}')

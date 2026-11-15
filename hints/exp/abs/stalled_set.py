"""Pick goals stalled in their context: unsolved, at most MAXLG proof lines above a proof, and
their last fresh run failed with the same nearest proven goal below (nfail_ctx >= 1).

  python3 abs/stalled_set.py LOOPDIR OUT N [--seed S] [--max-lgap 80]
"""
import argparse, os, random, sys
sys.path.insert(0, '/project/twee/hints')
import schedfeats

ap = argparse.ArgumentParser()
ap.add_argument('dir'); ap.add_argument('out'); ap.add_argument('n', type=int)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--max-lgap', type=int, default=80)
a = ap.parse_args()
names = [l.strip() for l in open('/project/hintwork/sets/all') if l.strip()]
gl = {l.split()[0]: int(l.split()[1]) for l in open('/project/hintwork/abs/goal_lines.tsv')}
H = schedfeats.History(names, gl, c6=False)
H.replay(a.dir)
cand = []
for n in names:
    if n in H.R.solved:
        continue
    x, _ = H.feats(n)
    if x['lgap'] <= a.max_lgap and x['nfail_ctx'] >= 1:
        cand.append(n)
random.Random(a.seed).shuffle(cand)
sel = sorted(cand[:a.n])
open(a.out, 'w').write(''.join(n + '\n' for n in sel))
print(f'{len(cand)} stalled goals within {a.max_lgap} lines; {len(sel)} -> {a.out}')

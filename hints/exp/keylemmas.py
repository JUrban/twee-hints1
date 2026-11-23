"""keylemmas.py CLIMBDIR... [--solved loops/UL/solved.tsv] [--min 2] [--out FILE]: the key unsolved goals of the
climbers' conditional proofs (23 Nov, notes/2026-11-23-climber-restart.md "exp69").

A climb's sketch run that proved target T with a single assumption assume_X (used.tsv; X's goal from assume.tsv:
an unproved sibling, an unsolved kNN goal of another original) says: T follows from X in a few seconds. Over the
dirs, each unsolved X with the targets it unlocks, most first (Veroff's sketches: prove the assumption, then the
target). Prints: X, solved?, head?, the number of targets, the targets; --out writes the X's with at least --min
unsolved targets, one per line (climb.py --targets)."""
import collections, os, subprocess, sys

L = '/project/hintwork/loops'
a = sys.argv[1:]
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
SOL = opt('--solved', f'{L}/UL/solved.tsv'); MIN = int(opt('--min', '2')); OUT = opt('--out', '')
S = {l.split()[0] for l in open(SOL) if l.strip()}
hp = subprocess.run(['python3', '/project/twee/hints/exp/heads.py', '/dev/stdin'], input='\n'.join(sorted(S)) + '\n',
                    capture_output=True, text=True).stdout.split()
heads = {x for x in hp if '__goal_' in x}
X = collections.defaultdict(set)
for d in a:
    p = d if '/' in d else os.path.join(L, d)
    A = {}
    for l in open(os.path.join(p, 'assume.tsv')):
        w = l.rstrip('\n').split('\t')
        if len(w) >= 4:
            A[(w[0], w[2])] = w[3]
    for l in open(os.path.join(p, 'used.tsv')):
        w = l.rstrip('\n').split('\t')
        if len(w) < 3:
            continue
        U = [x for x in w[2].split(',') if x.startswith('assume_')]
        if len(U) == 1 and A.get((w[0], U[0]), '-') not in ('-', ''):
            X[A[(w[0], U[0])]].add(w[0])
rank = sorted(X, key=lambda x: (-len(X[x] - S), x))
keep = []
for x in rank:
    ts = sorted(X[x] - S)
    print(f'{x}\tsolved={int(x in S)}\thead={int(x in heads)}\t{len(ts)}\t{",".join(ts)}')
    if x not in S and len(ts) >= MIN:
        keep.append(x)
if OUT:
    open(OUT, 'w').writelines(x + '\n' for x in keep)
    print(f'{OUT}: {len(keep)} unsolved goals that unlock at least {MIN} unsolved targets', file=sys.stderr)

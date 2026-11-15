"""Features of a loop's fresh runs, replayed in order, for a learned scheduler.

  python3 schedfeats.py LOOPDIR SET OUT.tsv [--rounds 3,4,5]

Each L0 row of LOOPDIR/r*/results.tsv (rounds without a level column count as
L0) becomes one line: round, name, label (1 = THM), then features as they were
when the run started. The solved set is replayed: a round starts with the
solved.tsv rows of earlier rounds, and the round's own THM rows join in order
(rows other processes appended in the round join at its end).
"""
import argparse, collections, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib, lemmas

FEATS = ['lgap', 'ggap', 'agap', 'nfail', 'nfail_ctx', 'grow', 'orate', 'ofrac',
         'size', 'nvars', 'hints', 'nolow', 'nfail_c6', 'dctx']


def orig_of(n):
    return n.rsplit('__goal_', 1)[0]


def goal_size(name, cache={}):
    if name not in cache:
        s = v = 0
        for l in open(os.path.join(hintlib.PROB, name + '.p')):
            if ',conjecture,' in l:
                body = l.split(',conjecture,', 1)[1]
                s = len(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', body))
                v = len(set(re.findall(r'\bX\d+\b', body)))
        cache[name] = (s, v)
    return cache[name]


class Replay:
    def __init__(self, names, goal_lines):
        self.names = set(names)
        self.gl = goal_lines
        self.byo = collections.defaultdict(list)
        self.solved = set()

    def set_solved(self, solved):
        self.solved = set(solved)
        byo = collections.defaultdict(set)
        for n in self.names | self.solved:
            byo[orig_of(n)].add(n)
        self.byo = {o: sorted(L, key=lambda n: lemmas.split(n)[1]) for o, L in byo.items()}
        self.pos = {n: (o, i) for o, L in self.byo.items() for i, n in enumerate(L)}
        self.nsol = collections.Counter(orig_of(n) for n in self.solved)

    def add(self, n):
        if n not in self.solved:
            self.solved.add(n); self.nsol[orig_of(n)] += 1

    def ctx6(self, n, k=6):
        """loop.py's ctx(n) with --lemma-after: the k nearest proven siblings by goal number"""
        o, i = self.pos[n]; L = self.byo[o]
        g = lemmas.split(n)[1]
        pr = [lemmas.split(m)[1] for m in L if m in self.solved]
        return tuple(sorted(sorted(pr, key=lambda j: (abs(g - j), j))[:k]))

    def context(self, n):
        """(nearest proven below or None, line gap, index gap, line gap to nearest proven above)"""
        o, i = self.pos[n]; L = self.byo[o]
        below = None
        for j in range(i - 1, -1, -1):
            if L[j] in self.solved:
                below = j; break
        above = None
        for j in range(i + 1, len(L)):
            if L[j] in self.solved:
                above = j; break
        g = self.gl.get(n, 0)
        lg = g - self.gl.get(L[below], 0) if below is not None else 5000
        ig = i - below if below is not None else 1000
        ag = self.gl.get(L[above], 0) - g if above is not None else 5000
        return (L[below] if below is not None else None), lg, ig, ag


class History:
    """The features of every goal, kept up to date: replay a loop dir's rounds (replay()),
    then observe() each finished run and add() each proof, and ask feats(n)."""
    def __init__(self, names, gl, c6=True):
        self.R = Replay(names, gl); self.c6 = c6
        self.fails = collections.Counter()      # name -> failed runs so far (any level)
        self.fail_ctx = collections.Counter()   # (name, nearest proven below) -> failed fresh runs
        self.fail_c6 = collections.Counter()    # (name, loop's ctx) -> failed fresh runs
        self.last_nsol = {}                     # name -> proven goals of its original at its last fresh run
        self.last_lg = {}                       # name -> line gap at its last fresh run
        self.orecent = collections.defaultdict(lambda: collections.deque(maxlen=30))
        self.tot = collections.Counter(orig_of(n) for n in names)

    def feats(self, n, hints=0):
        R = self.R; o = orig_of(n)
        below, lg, ig, ag = R.context(n)
        c6 = R.ctx6(n) if self.c6 else None
        dq = self.orecent[o]
        s, v = goal_size(n)
        x = dict(lgap=lg, ggap=ig, agap=ag, nfail=self.fails[n], nfail_ctx=self.fail_ctx[(n, below)],
                 grow=math.log((R.nsol[o] + 1) / (self.last_nsol.get(n, 0) + 1)),
                 orate=(sum(dq) + 0.5) / (len(dq) + 3), ofrac=R.nsol[o] / max(1, self.tot.get(o, 1)),
                 size=s, nvars=v, hints=hints, nolow=int(below is None),
                 nfail_c6=self.fail_c6[(n, c6)], dctx=self.last_lg.get(n, 5000) - lg)
        return x, (below, c6, lg)

    def observe(self, n, ok, lev, ctx=None):
        """a finished run of n (ctx: feats(n)[1] when it started; default: now)"""
        if lev == 'L0':
            below, c6, lg = ctx if ctx else self.feats(n)[1]
            self.orecent[orig_of(n)].append(int(ok))
            self.last_nsol[n] = self.R.nsol[orig_of(n)]; self.last_lg[n] = lg
            if not ok:
                self.fail_ctx[(n, below)] += 1; self.fail_c6[(n, c6)] += 1
        if ok:
            self.R.add(n)
        else:
            self.fails[n] += 1

    def add(self, n):
        self.R.add(n)

    def replay(self, d, keep=(), out=None):
        """replay loop dir d's rounds; with out, write the rows of fresh runs of rounds in keep"""
        srows = [l.rstrip('\n').split('\t') for l in open(os.path.join(d, 'solved.tsv'))]
        rounds = sorted({int(w[1]) for w in srows} | {int(x[1:]) for x in os.listdir(d)
                                                      if re.fullmatch(r'r\d+', x)})
        nrows = 0
        for r in rounds:
            if r == 0:
                continue
            self.R.set_solved(w[0] for w in srows if int(w[1]) < r)
            p = os.path.join(d, 'r%d' % r, 'results.tsv')
            if not os.path.exists(p):
                continue
            for line in open(p):
                f = line.rstrip('\n').split('\t')
                if len(f) < 4 or f[0] not in self.R.pos:
                    continue
                n, ok = f[0], f[1] == 'THM'
                lev = f[4] if len(f) >= 5 and f[4][:1] == 'L' else 'L0'
                ctx = None
                if lev == 'L0':
                    m = re.search(r'hints=(\d+)', f[3])
                    x, ctx = self.feats(n, int(m.group(1)) if m else 0)
                    if out and r in keep and n not in self.R.solved:
                        out.write(f'{r}\t{n}\t{int(ok)}\t' + '\t'.join(
                            f'{x[h]:.4g}' if isinstance(x[h], float) else str(x[h]) for h in FEATS) + '\n')
                        nrows += 1
                self.observe(n, ok, lev, ctx)
        self.R.set_solved(w[0] for w in srows)
        return nrows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('set'); ap.add_argument('out')
    ap.add_argument('--rounds', default='3,4,5')
    ap.add_argument('--goal-lines', default='/project/hintwork/abs/goal_lines.tsv')
    a = ap.parse_args()
    keep = {int(x) for x in a.rounds.split(',')}
    names = [l.strip() for l in open(a.set) if l.strip()]
    gl = {}
    for l in open(a.goal_lines):
        n, x = l.split(); gl[n] = int(x)
    H = History(names, gl)
    with open(a.out, 'w') as out:
        out.write('round\tname\tlabel\t' + '\t'.join(FEATS) + '\n')
        nrows = H.replay(a.dir, keep, out)
    print(f'{nrows} rows -> {a.out}')


if __name__ == '__main__':
    main()

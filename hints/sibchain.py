#!/usr/bin/env python3
"""Chain hints (18 Nov, exp3/exp8): the expanded proofs of a goal's nearest proven siblings below it.

exp3 (47 late unsolved goals, 320 s) found that a deep run guided by the "chain" proves more than one guided by
the original's whole pool (K 11 against C 9, K a superset, a third less CPU). The chain of goal G is the
expansions (expand.py: a proof's own steps, then recursively the steps of the proven goals it used as lemmas,
by depth) of the N nearest proven siblings below G, nearest first, with duplicates dropped.

Records: goal -> the proven goals its proof used, from the USEDAXIOMS lines of a loop's kept outputs
(depcheck.used_lemmas), plus the records of new proofs added as they come (add_record). Records whose lemma
names map to no goal (assumed or cut conjectures) are left out, as in expand.py.

  python3 sibchain.py LOOPDIR GOAL [N]   prints GOAL's chain (lhs<TAB>rhs) from LOOPDIR's records
  python3 sibchain.py --build OUT.tsv [LOOPS] [--extra DIR,...]   the records of all loops (expand.py's LOOPS; first
      loop with a clean record of a goal and its hint file wins), as rows goal<TAB>loop dir<TAB>source goals
      (comma-separated). --extra: also experiment output dirs (files <goal> or <goal>.out, as exp3/exp6 run.py keep
      them) for goals that have a hint file in the first loop but no record yet: proofs merged with merge.py.
      --transfer: then goals still without a record that a transfer proved (a THM row of BASE/*/transfer.tsv, the
      first file in name order) get the transfer's source goals as their record: the goal is a step or an
      instance of a step of those proofs (transfer.py), so their expansion holds its derivation.
  Chains(LOOPDIR, records=OUT.tsv) starts from such a file (fast) instead of LOOPDIR's own outputs; hint files
  come from the record's loop (as in expand.py), else from LOOPDIR/hints.
"""
import collections, os, re, sys, threading

_LEMMA_KNN = re.compile(r'lemma_knn_\d+_(\S+__goal_\d+)$')
_LEMMA_GOAL = re.compile(r'lemma_goal_(\d+)$')


def parse_used(goal, rest):
    """The source goals named in a USEDAXIOMS line's REST, or None if a name maps to no goal."""
    o = goal.rsplit('__goal_', 1)[0]
    src = set()
    for x in rest.split():
        m = _LEMMA_KNN.match(x)
        if m:
            src.add(m.group(1)); continue
        m = _LEMMA_GOAL.match(x)
        if m:
            src.add(f'{o}__goal_{m.group(1)}'); continue
        if x.startswith(('lemma_', 'cut_', 'true_', 'assume_', 'src_')):
            return None
    return src


class Chains:
    def __init__(self, loop_dir, background=True, records=None):
        self.dir = loop_dir
        self.records = records
        self.where = {}          # goal -> loop dir of its record (records file)
        self.rec = None          # goal -> set of source goals (None until loaded)
        self.new = {}            # records added before the load finished
        self.cache = {}          # goal -> its expansion (list of (lhs, rhs))
        self.lock = threading.Lock()
        if background:
            threading.Thread(target=self._load, daemon=True).start()
        else:
            self._load()

    def _load(self):
        if self.records:
            rec = {}
            for l in open(self.records):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 3:
                    rec[w[0]] = set(x for x in w[2].split(',') if x); self.where[w[0]] = w[1]
        else:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import depcheck
            rec = {g: src for g, (src, unm) in depcheck.used_lemmas(self.dir).items() if not unm}
        with self.lock:
            rec.update(self.new)
            self.rec = rec

    def ready(self):
        return self.rec is not None

    def add_record(self, goal, out):
        """A new proof's output: its USEDAXIOMS line becomes GOAL's record."""
        for line in out.splitlines():
            if line.startswith('USEDAXIOMS'):
                src = parse_used(goal, line[len('USEDAXIOMS'):])
                if src is None:
                    return
                with self.lock:
                    if self.rec is None:
                        self.new[goal] = src
                    else:
                        self.rec[goal] = src
                return

    def expansion(self, g):
        """G's own proof steps, then those of every proven goal its proof used, recursively, by depth."""
        if g in self.cache:
            return self.cache[g]
        rec = self.rec or {}
        depth = {g: 0}; order = [g]; q = collections.deque([g])
        while q:
            x = q.popleft()
            for y in sorted(rec.get(x, ())):
                if y not in depth:
                    depth[y] = depth[x] + 1; order.append(y); q.append(y)
        seen, out = set(), []
        for x in order:
            lines = None
            for d in (self.where.get(x), self.dir):   # (the record's own loop first, as expand.py)
                if d:
                    try:
                        lines = open(os.path.join(d, 'hints', x)).read().splitlines(); break
                    except OSError:
                        pass
            if lines is None:
                continue
            for l in lines:
                w = l.split('\t')
                if len(w) < 2:
                    continue
                k = (w[0], w[1]) if w[0] <= w[1] else (w[1], w[0])
                if k not in seen:
                    seen.add(k); out.append((w[0], w[1]))
        if g in rec:   # (a goal without a record may get one later; then its expansion grows)
            self.cache[g] = out
        return out

    def chain(self, goal, solved_nums, n=10, max_hints=100000, two_sided=False):
        """GOAL's chain: the expansions of its N nearest proven siblings below (SOLVED_NUMS: the goal numbers of
        GOAL's original that are proven), nearest first, duplicates dropped. TWO_SIDED (exp14): the N nearest by
        goal-number distance above or below, ties below first."""
        o, k = goal.rsplit('__goal_', 1); k = int(k)
        if two_sided:
            sibs = sorted((j for j in solved_nums if j != k), key=lambda j: (abs(j - k), j > k))[:n]
        else:
            sibs = sorted((j for j in solved_nums if j < k), reverse=True)[:n]
        seen, out = set(), []
        for j in sibs:
            for h in self.expansion(f'{o}__goal_{j}'):
                if h not in seen:
                    seen.add(h); out.append(h)
                    if len(out) >= max_hints:
                        return out
        return out


def build(out, loops='UL,Z4,Z3,Z2,Z1,Z0,PGA,PGB,ORH,ORG,ORF,ORE,ORD,ORC,ORB,ORA', base='/project/hintwork/loops',
          extra='', transfer=False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import depcheck
    rec = {}
    for x in loops.split(','):
        d = os.path.join(base, x)
        if not os.path.isdir(d):
            continue
        for g, (src, unm) in depcheck.used_lemmas(d).items():
            if g not in rec and not unm and os.path.exists(os.path.join(d, 'hints', g)):
                rec[g] = (d, src)
    first = os.path.join(base, loops.split(',')[0]); nx = 0
    for ed in filter(None, extra.split(',')):
        # (18 Nov) merged experiment proofs: merge.py copies their hint files, not their outputs
        for f in sorted(os.listdir(ed)):
            g = f[:-4] if f.endswith('.out') else f
            if '__goal_' not in g or g in rec or not os.path.exists(os.path.join(first, 'hints', g)):
                continue
            for line in open(os.path.join(ed, f), errors='replace'):
                if line.startswith('USEDAXIOMS'):
                    src = parse_used(g, line[len('USEDAXIOMS'):])
                    if src is not None:
                        rec[g] = (first, src); nx += 1
                    break
    if extra:
        print(nx, 'records from --extra', file=sys.stderr)
    if transfer:
        import glob
        nt = 0
        for f in sorted(glob.glob(os.path.join(base, '*', 'transfer.tsv'))):
            for l in open(f):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 5 and w[1] == 'THM' and w[0] not in rec and os.path.exists(os.path.join(first, 'hints', w[0])):
                    src = set(x for x in w[4].split(',') if '__goal_' in x) - {w[0]}
                    if src:
                        rec[w[0]] = (first, src); nt += 1
        print(nt, 'records from transfer sources', file=sys.stderr)
    with open(out + '.tmp', 'w') as f:
        for g in sorted(rec):
            f.write(f'{g}\t{rec[g][0]}\t{",".join(sorted(rec[g][1]))}\n')
    os.replace(out + '.tmp', out)
    print(len(rec), 'records', file=sys.stderr)


if __name__ == '__main__':
    if sys.argv[1] == '--build':
        ex = ''; tr = '--transfer' in sys.argv
        if tr:
            sys.argv.remove('--transfer')
        if '--extra' in sys.argv:
            i = sys.argv.index('--extra'); ex = sys.argv[i + 1]; del sys.argv[i:i + 2]
        build(sys.argv[2], *sys.argv[3:4], extra=ex, transfer=tr)
        sys.exit()
    recs = None
    if '--records' in sys.argv:
        i = sys.argv.index('--records'); recs = sys.argv[i + 1]; del sys.argv[i:i + 2]
    d, g = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    C = Chains(d, background=False, records=recs)
    o = g.rsplit('__goal_', 1)[0]
    nums = {int(l.split('\t')[0].rsplit('__goal_', 1)[1]) for l in open(os.path.join(d, 'solved.tsv'))
            if l.startswith(o + '__goal_')}
    for l, r in C.chain(g, nums, n):
        print(f'{l}\t{r}')

"""A graph neural network for twee's rules, after Olšák, Kaliszyk and Urban (property-invariant
embeddings, 2020) and Chvalovský, Korovin, Piepenbrock and Urban (iProver, LPAR 2023): "dynamic"
training data, i.e. new rules scored in the context of the rules added so far (the decision twee's
rule model makes), not ENIGMA's one example per proof.

  python3 gnn.py train GIVENDIRS --test-names sets/ultest --save M.pt [--steps N --dim D --layers L]
  python3 gnn.py eval  GIVENDIRS --test-names sets/ultest --load M.pt [--per FILE]

GIVENDIRS: comma-separated dirs of given.py logs (label, index, lhs, rhs, parents...; label -1 =
input axiom, 1 = rule in the proof, 0 = other rule). twee prints these rules with its goal
constants expanded: flattening constants by their definitions, skolem constants by fresh variables
(expandGoalConsts, as the rule model sees them).

A sample is one problem at a cut k in its added rules: equations = axioms + goal + the last --ctx
rules before k (context) + the --query rules from k on (to score). Nodes: one per equation (typed
axiom/goal/context/query), per term (ground terms shared within the sample, terms with variables
only within their equation), per variable (per equation), per symbol and per goal skolem.

Version 2 (15 Nov, user: the signature is small, so be symbol-aware; mark the conjecture terms;
prefer the harder proofs and clauses):
  * symbol nodes have an embedding per symbol name (learned vocabulary) besides their arity type
    (--no-names: arity only, as version 1);
  * the conjecture's variables are skolem nodes, its terms are typed as goal terms, and every rule
    term that is a variant of a conjecture subterm with at least two function symbols (the skolems
    became fresh variables in the logs) is typed as a marked term and linked to that goal term by
    a goal-match edge (--no-goal-marks: off);
  * training problems are drawn with probability proportional to (log size in bytes) ** --hard, and the
    proof rule a sample is anchored on with probability proportional to (index + 1) ** --hard-clauses,
    so long proofs and their late rules weigh more;
  * the query's index in the run (log scale) goes into the scoring layer (--no-idx: off).
Messages are passed along typed edges (equation-lhs, equation-rhs, term-symbol, term-argument i,
goal-match) in both directions with mean aggregation; a query's score combines its equation node
with the mean of the goal nodes. Evaluation: per-problem AUC over all added rules (as
rulemodel.py), scored chunk by chunk with each chunk's preceding rules as context.
"""
import argparse, math, os, random, re, sys, time
import numpy as np
import torch
import torch.nn as nn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintsel

TOK = re.compile(r"[A-Za-z0-9_$']+|[(),]")
MAXARG = 4
# node types
T_AX, T_GOAL, T_CTX, T_QRY, T_TERM, T_VAR, T_GTERM, T_SKO, T_MTERM = 0, 1, 2, 3, 4, 5, 6, 7, 8
T_SYM = 9   # + arity (0..MAXARG)
NTYPES = T_SYM + MAXARG + 1
# relations (each used in both directions)
R_LHS, R_RHS, R_SYM = 0, 1, 2
R_ARG = 3   # + position (0..MAXARG-1)
R_GMATCH = R_ARG + MAXARG
NREL = R_GMATCH + 1
VARNAME = re.compile(r'^[A-Z]')


def parse(s):
    toks = TOK.findall(s); pos = 0
    def term():
        nonlocal pos
        t = toks[pos]; pos += 1
        if pos < len(toks) and toks[pos] == '(':
            pos += 1; args = [term()]
            while toks[pos] == ',':
                pos += 1; args.append(term())
            pos += 1
            return (t, tuple(args))
        return (t, ())
    return term()


def isvar(x):
    return not x[1] and VARNAME.match(x[0]) is not None


def variant_key(x):
    """The term with its variables renamed in order of first occurrence, and its number of
    function symbols."""
    ren = {}; nf = 0; out = []
    def go(t):
        nonlocal nf
        if isvar(t):
            if t[0] not in ren:
                ren[t[0]] = f'_{len(ren)}'
            out.append(ren[t[0]]); return
        nf += 1; out.append(t[0])
        if t[1]:
            out.append('(')
            for i, a in enumerate(t[1]):
                if i:
                    out.append(',')
                go(a)
            out.append(')')
    go(x)
    return ''.join(out), nf


def load_log(path):
    ax, rules = [], []
    for line in open(path):
        f = line.rstrip('\n').split('\t')
        if len(f) < 4:
            continue
        lab = int(f[0])
        (ax if lab < 0 else rules).append((lab, f[2], f[3]))
    return ax, rules


_goals = {}
def goal_eqs(name):
    if name not in _goals:
        try:
            _goals[name] = [(l, r) for _, l, r in hintsel.goal_lits(name)]
        except Exception:
            _goals[name] = []
    return _goals[name]


class Vocab:
    def __init__(self, names=()):
        self.idx = {n: i + 1 for i, n in enumerate(names)}   # 0 = unknown / no name
        self.frozen = False

    def get(self, name):
        i = self.idx.get(name)
        if i is None and not self.frozen:
            i = self.idx[name] = len(self.idx) + 1
        return i or 0


class Graph:
    """A batch of samples as one disjoint graph."""
    def __init__(self, vocab, names=True, marks=True):
        self.vocab, self.names, self.marks = vocab, names, marks
        self.ntype = []; self.nname = []; self.edges = [[] for _ in range(NREL)]   # (src, dst) pairs
        self.qry, self.qlab, self.qsample, self.qidx = [], [], [], []
        self.goal, self.gsample = [], []
        self.ns = 0

    def node(self, t, name=0):
        self.ntype.append(t); self.nname.append(name)
        return len(self.ntype) - 1

    def add_sample(self, eqs):
        """eqs: [(type, lhs, rhs, label, index)]"""
        s = self.ns; self.ns += 1
        shared = {}; syms = {}; gkeys = {}; skolems = {}
        def sym(name, ar):
            k = (name, ar)
            if k not in syms:
                syms[k] = self.node(T_SYM + min(ar, MAXARG), self.vocab.get(f'{name}/{ar}') if self.names else 0)
            return syms[k]
        for t, l, r, lab, idx in eqs:
            local = {}
            goal = t == T_GOAL and self.marks
            def term(x):
                f, args = x
                if isvar(x):
                    if goal:   # the conjecture's variables are its skolem constants (shared by its literals)
                        if f not in skolems:
                            skolems[f] = self.node(T_SKO)
                        return skolems[f], False
                    k = ('v', f)
                    if k not in local:
                        local[k] = self.node(T_VAR)
                    return local[k], True
                kids = [term(a) for a in args]
                hasv = any(v for _, v in kids)
                key = (f, tuple(c for c, _ in kids), goal)
                tab = local if hasv else shared
                if key not in tab:
                    n = self.node(T_GTERM if goal else T_TERM)
                    tab[key] = n
                    self.edges[R_SYM].append((sym(f, len(args)), n))
                    for i, (c, _) in enumerate(kids):
                        self.edges[R_ARG + min(i, MAXARG - 1)].append((c, n))
                    if self.marks and args:
                        vk, nf = variant_key(x)
                        if nf >= 2:
                            if goal:
                                gkeys.setdefault(vk, n)
                            elif vk in gkeys:
                                self.ntype[n] = T_MTERM
                                self.edges[R_GMATCH].append((gkeys[vk], n))
                return tab[key], hasv
            e = self.node(t)
            self.edges[R_LHS].append((term(parse(l))[0], e))
            self.edges[R_RHS].append((term(parse(r))[0], e))
            if t == T_QRY:
                self.qry.append(e); self.qlab.append(lab); self.qsample.append(s); self.qidx.append(idx)
            elif t == T_GOAL:
                self.goal.append(e)
                self.gsample.append(s)
        return s

    def tensors(self):
        E = []
        for r in range(NREL):
            if self.edges[r]:
                a = torch.tensor(self.edges[r], dtype=torch.long)
                E.append((r, a[:, 0], a[:, 1]))
        return (torch.tensor(self.ntype), torch.tensor(self.nname), E, torch.tensor(self.qry),
                torch.tensor(self.qlab, dtype=torch.float32), torch.tensor(self.qsample),
                torch.tensor(self.qidx, dtype=torch.float32), torch.tensor(self.goal, dtype=torch.long),
                torch.tensor(self.gsample, dtype=torch.long), self.ns)


class GNN(nn.Module):
    def __init__(self, d=32, layers=8, nnames=64, idx=True):
        super().__init__()
        self.emb = nn.Embedding(NTYPES, d)
        self.nemb = nn.Embedding(nnames + 1, d, padding_idx=0)
        self.layers = layers; self.use_idx = idx
        # per layer: self map, and per relation a forward (src->dst) and a backward (dst->src) map
        self.selfw = nn.ModuleList([nn.Linear(d, d) for _ in range(layers)])
        self.fw = nn.ModuleList([nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(NREL)]) for _ in range(layers)])
        self.bw = nn.ModuleList([nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(NREL)]) for _ in range(layers)])
        self.norm = nn.ModuleList([nn.LayerNorm(d) for _ in range(layers)])
        self.out = nn.Sequential(nn.Linear(3 * d + (1 if idx else 0), d), nn.ReLU(), nn.Linear(d, 1))

    def forward(self, ntype, nname, E, qry, qsample, qidx, goal, gsample, ns):
        nname = nname.clamp(max=self.nemb.num_embeddings - 1)
        h = self.emb(ntype) + self.nemb(nname)
        N, d = h.shape
        inv = []   # 1/in-degree per (relation, direction, node)
        for r, src, dst in E:
            cf = torch.zeros(N).index_add_(0, dst, torch.ones(len(dst))).clamp(min=1)
            cb = torch.zeros(N).index_add_(0, src, torch.ones(len(src))).clamp(min=1)
            inv.append((1 / cf, 1 / cb))
        for L in range(self.layers):
            m = self.selfw[L](h)
            for (r, src, dst), (icf, icb) in zip(E, inv):
                m = m.index_add(0, dst, self.fw[L][r](h[src]) * icf[dst].unsqueeze(1))
                m = m.index_add(0, src, self.bw[L][r](h[dst]) * icb[src].unsqueeze(1))
            h = self.norm[L](h + torch.relu(m))
        g = torch.zeros(ns, d).index_add_(0, gsample, h[goal])
        gc = torch.zeros(ns).index_add_(0, gsample, torch.ones(len(gsample))).clamp(min=1)
        g = g / gc.unsqueeze(1)
        hq = h[qry]; gq = g[qsample]
        x = [hq, gq, hq * gq]
        if self.use_idx:
            x.append((torch.log1p(qidx) / 8).unsqueeze(1))
        return self.out(torch.cat(x, 1)).squeeze(1)


def sample_eqs(name, ax, rules, k, ctx, query):
    eqs = [(T_AX, l, r, 0, 0) for _, l, r in ax]
    eqs += [(T_GOAL, l, r, 0, 0) for l, r in goal_eqs(name)]
    eqs += [(T_CTX, l, r, 0, i) for i, (_, l, r) in enumerate(rules[max(0, k - ctx):k], max(0, k - ctx))]
    eqs += [(T_QRY, l, r, lab, i) for i, (lab, l, r) in enumerate(rules[k:k + query], k)]
    return eqs


def paths_of(dirs):
    P = {}
    for d in dirs.split(','):
        if os.path.isdir(d):
            for n in os.listdir(d):
                P[n] = os.path.join(d, n)
    return P


def auc(y, s):
    o = np.argsort(s, kind='mergesort'); rk = np.empty(len(s)); rk[o] = np.arange(1, len(s) + 1)
    P = y.sum(); N = len(y) - P
    if P == 0 or N == 0:
        return None
    return (rk[y == 1].sum() - P * (P + 1) / 2) / (P * N)


def run_model(model, G):
    nt, nn_, E, q, ql, qs, qi, g, gs, ns = G.tensors()
    return model(nt, nn_, E, q, qs, qi, g, gs, ns), ql


def evaluate(model, P, names, a, vocab, limit=None, per=None):
    model.eval(); aucs = []
    frozen = vocab.frozen; vocab.frozen = True
    with torch.no_grad():
        for n in names[:limit]:
            ax, rules = load_log(P[n])
            if len(rules) < 20 or not any(l == 1 for l, _, _ in rules):
                continue
            scores = []
            for k in range(0, len(rules), a.eval_chunk):
                G = Graph(vocab, a.names, a.goal_marks); G.add_sample(sample_eqs(n, ax, rules, k, a.ctx, a.eval_chunk))
                scores.append(run_model(model, G)[0].numpy())
            s = np.concatenate(scores); y = np.array([l for l, _, _ in rules])
            v = auc(y, s)
            if v is not None:
                aucs.append(v)
                if per is not None:
                    per.write(f'{n}\t{v:.4f}\n'); per.flush()
    vocab.frozen = frozen
    model.train()
    return float(np.mean(aucs)), len(aucs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('dirs')
    ap.add_argument('--test-names', required=True)
    ap.add_argument('--save'); ap.add_argument('--load')
    ap.add_argument('--dim', type=int, default=32); ap.add_argument('--layers', type=int, default=8)
    ap.add_argument('--ctx', type=int, default=512); ap.add_argument('--query', type=int, default=128)
    ap.add_argument('--eval-chunk', type=int, default=256)
    ap.add_argument('--batch', type=int, default=8)
    ap.add_argument('--steps', type=int, default=20000)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--pos-frac', type=float, default=0.5, help='share of samples whose query holds a proof rule')
    ap.add_argument('--hard', type=float, default=0.5, help='draw training problems with weight (log size in bytes) ** HARD')
    ap.add_argument('--hard-clauses', type=float, default=1.0, help='anchor on proof rule i with weight (i+1) ** H')
    ap.add_argument('--no-names', dest='names', action='store_false', help='symbols typed by arity only (version 1)')
    ap.add_argument('--no-goal-marks', dest='goal_marks', action='store_false')
    ap.add_argument('--no-idx', dest='idx', action='store_false')
    ap.add_argument('--eval-every', type=int, default=2000)
    ap.add_argument('--eval-n', type=int, default=100)
    ap.add_argument('--per', help='eval: write each test problem\'s AUC to this file')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--max-train', type=int, default=0, help='use at most N training problems')
    a = ap.parse_args()
    torch.set_num_threads(a.threads); torch.manual_seed(a.seed); rnd = random.Random(a.seed)
    P = paths_of(a.dirs)
    test = sorted(set(l.split()[0] for l in open(a.test_names)) & set(P))
    rnd.shuffle(test)
    vocab = Vocab()
    if a.load:
        ck = torch.load(a.load)
        for k in ('names', 'goal_marks', 'idx', 'dim', 'layers'):
            if k in ck.get('args', {}):
                setattr(a, k, ck['args'][k])
        vocab = Vocab(ck.get('vocab', []))
        model = GNN(a.dim, a.layers, idx=a.idx); model.load_state_dict(ck['model'])
    else:
        model = GNN(a.dim, a.layers, idx=a.idx)
    if a.cmd == 'eval':
        vocab.frozen = True
        v, k = evaluate(model, P, test, a, vocab, a.eval_n or None, open(a.per, 'w') if a.per else None)
        print(f'AUC {v:.3f} over {k} problems', flush=True)
        return
    train = sorted(set(P) - set(test))
    rnd.shuffle(train)
    if a.max_train:
        train = train[:a.max_train]
    w = [max(1, os.path.getsize(P[n])) ** a.hard for n in train]
    print(f'{len(train)} training problems, {len(test)} test; d={a.dim} layers={a.layers} names={a.names} '
          f'goal_marks={a.goal_marks} idx={a.idx} hard={a.hard} hard_clauses={a.hard_clauses}', flush=True)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    lossf = nn.BCEWithLogitsLoss(reduction='none')
    def save():
        if a.save:
            names = sorted(vocab.idx, key=vocab.idx.get)
            torch.save({'model': model.state_dict(), 'vocab': names,
                        'args': {k: getattr(a, k) for k in ('names', 'goal_marks', 'idx', 'dim', 'layers')}}, a.save)
    t0 = time.time(); run = []; marked = [0, 0]
    for step in range(1, a.steps + 1):
        G = Graph(vocab, a.names, a.goal_marks)
        while G.ns < a.batch:
            n = rnd.choices(train, weights=w)[0] if a.hard else rnd.choice(train)
            try:
                ax, rules = load_log(P[n])
            except Exception:
                continue
            pos = [i for i, (l, _, _) in enumerate(rules) if l == 1]
            if not rules or not pos:
                continue
            if rnd.random() < a.pos_frac:
                p = rnd.choices(pos, weights=[(i + 1) ** a.hard_clauses for i in pos])[0] if a.hard_clauses else rnd.choice(pos)
                k = max(0, p - rnd.randrange(a.query))
            else:
                k = rnd.randrange(len(rules))
            G.add_sample(sample_eqs(n, ax, rules, k, a.ctx, a.query))
        marked[0] += G.ntype.count(T_MTERM); marked[1] += G.ntype.count(T_TERM) + G.ntype.count(T_MTERM)
        out, ql = run_model(model, G)
        npos = ql.sum().clamp(min=1); nneg = (len(ql) - ql.sum()).clamp(min=1)
        wt = torch.where(ql > 0, 0.5 / npos, 0.5 / nneg)   # balanced loss per batch
        loss = (lossf(out, ql) * wt).sum()
        opt.zero_grad(); loss.backward(); opt.step()
        run.append(loss.item())
        if step % 200 == 0:
            print(f'step {step} loss {np.mean(run[-200:]):.4f} {time.time()-t0:.0f}s '
                  f'(marked terms {marked[0] / max(1, marked[1]):.3f}, vocab {len(vocab.idx)})', flush=True)
        if step % a.eval_every == 0 or step == a.steps:
            v, k = evaluate(model, P, test, a, vocab, a.eval_n)
            print(f'  eval step {step}: AUC {v:.3f} over {k} test problems', flush=True)
            save()


if __name__ == '__main__':
    main()

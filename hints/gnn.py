"""A name-independent graph neural network for twee's rules, after Olšák, Kaliszyk and Urban
(property-invariant embeddings, 2020) and Chvalovský, Korovin, Piepenbrock and Urban (iProver,
LPAR 2023): "dynamic" training data, i.e. new rules scored in the context of the rules added so
far, not ENIGMA's one example per proof.

  python3 gnn.py train GIVENDIRS --test-names sets/ultest --save M.pt [--epochs N --dim D --layers L]
  python3 gnn.py eval  GIVENDIRS --test-names sets/ultest --load M.pt

GIVENDIRS: comma-separated dirs of given.py logs (label, index, lhs, rhs, parents...; label -1 =
input axiom, 1 = rule in the proof, 0 = other rule). A sample is one problem at a cut k in its
added rules: equations = axioms + goal + the last --ctx rules before k (context) + the --query
rules from k on (to score). The graph has a node per equation (typed axiom/goal/context/query),
per term (shared within the sample; terms with variables only within their equation), per variable
(per equation) and per symbol (typed by arity only, so names never matter). Messages are passed
along typed edges (equation-lhs, equation-rhs, term-symbol, term-argument i) with mean
aggregation; a query's score combines its equation node with the mean of the goal nodes.
Evaluation: per-problem AUC over all added rules (as rulemodel.py), scored chunk by chunk with
each chunk's preceding rules as context.
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
T_AX, T_GOAL, T_CTX, T_QRY, T_TERM, T_VAR = 0, 1, 2, 3, 4, 5
T_SYM = 6   # + arity (0..MAXARG)
NTYPES = T_SYM + MAXARG + 1
# relations (each used in both directions)
R_LHS, R_RHS, R_SYM = 0, 1, 2
R_ARG = 3   # + position (0..MAXARG-1)
NREL = R_ARG + MAXARG


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


class Graph:
    """A batch of samples as one disjoint graph."""
    def __init__(self):
        self.ntype = []; self.edges = [[] for _ in range(NREL)]   # (src, dst) pairs
        self.sample = []      # node -> sample index (equation nodes only matter)
        self.qry, self.qlab, self.qsample = [], [], []
        self.goal, self.gsample = [], []
        self.ns = 0

    def node(self, t, s):
        self.ntype.append(t); self.sample.append(s)
        return len(self.ntype) - 1

    def add_sample(self, eqs):
        """eqs: [(type, lhs, rhs, label)]"""
        s = self.ns; self.ns += 1
        shared = {}; syms = {}
        def sym(name, ar):
            k = (name, ar)
            if k not in syms:
                syms[k] = self.node(T_SYM + min(ar, MAXARG), s)
            return syms[k]
        for t, l, r, lab in eqs:
            local = {}
            def term(x):
                f, args = x
                if not args and f[:1].isupper():   # a variable (per equation)
                    k = ('v', f)
                    if k not in local:
                        local[k] = self.node(T_VAR, s)
                    return local[k], True
                kids = [term(a) for a in args]
                hasv = any(v for _, v in kids)
                key = (f, tuple(c for c, _ in kids))
                tab = local if hasv else shared
                if key not in tab:
                    n = self.node(T_TERM, s)
                    tab[key] = n
                    self.edges[R_SYM].append((sym(f, len(args)), n))
                    for i, (c, _) in enumerate(kids):
                        self.edges[R_ARG + min(i, MAXARG - 1)].append((c, n))
                return tab[key], hasv
            e = self.node(t, s)
            self.edges[R_LHS].append((term(parse(l))[0], e))
            self.edges[R_RHS].append((term(parse(r))[0], e))
            if t == T_QRY:
                self.qry.append(e); self.qlab.append(lab); self.qsample.append(s)
            elif t == T_GOAL:
                self.goal.append(e); self.gsample.append(s)
        return s

    def tensors(self):
        E = []
        for r in range(NREL):
            if self.edges[r]:
                a = torch.tensor(self.edges[r], dtype=torch.long)
                E.append((r, a[:, 0], a[:, 1]))
        return (torch.tensor(self.ntype), E, torch.tensor(self.qry), torch.tensor(self.qlab, dtype=torch.float32),
                torch.tensor(self.qsample), torch.tensor(self.goal), torch.tensor(self.gsample), self.ns)


class GNN(nn.Module):
    def __init__(self, d=32, layers=8):
        super().__init__()
        self.emb = nn.Embedding(NTYPES, d)
        self.layers = layers
        # per layer: self map, and per relation a forward (src->dst) and a backward (dst->src) map
        self.selfw = nn.ModuleList([nn.Linear(d, d) for _ in range(layers)])
        self.fw = nn.ModuleList([nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(NREL)]) for _ in range(layers)])
        self.bw = nn.ModuleList([nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(NREL)]) for _ in range(layers)])
        self.norm = nn.ModuleList([nn.LayerNorm(d) for _ in range(layers)])
        self.out = nn.Sequential(nn.Linear(3 * d, d), nn.ReLU(), nn.Linear(d, 1))

    def forward(self, ntype, E, qry, qsample, goal, gsample, ns):
        h = self.emb(ntype)
        N, d = h.shape
        # 1/in-degree per (relation, direction, node)
        inv = []
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
        return self.out(torch.cat([hq, gq, hq * gq], 1)).squeeze(1)


def sample_eqs(name, ax, rules, k, ctx, query):
    eqs = [(T_AX, l, r, 0) for _, l, r in ax]
    eqs += [(T_GOAL, l, r, 0) for l, r in goal_eqs(name)]
    eqs += [(T_CTX, l, r, 0) for _, l, r in rules[max(0, k - ctx):k]]
    eqs += [(T_QRY, l, r, lab) for lab, l, r in rules[k:k + query]]
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


def evaluate(model, P, names, a, limit=None):
    model.eval(); aucs = []
    with torch.no_grad():
        for n in names[:limit]:
            ax, rules = load_log(P[n])
            if len(rules) < 20 or not any(l == 1 for l, _, _ in rules):
                continue
            scores = []
            for k in range(0, len(rules), a.eval_chunk):
                G = Graph(); G.add_sample(sample_eqs(n, ax, rules, k, a.ctx, a.eval_chunk))
                nt, E, q, ql, qs, g, gs, ns = G.tensors()
                scores.append(model(nt, E, q, qs, g, gs, ns).numpy())
            s = np.concatenate(scores); y = np.array([l for l, _, _ in rules])
            v = auc(y, s)
            if v is not None:
                aucs.append(v)
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
    ap.add_argument('--eval-every', type=int, default=2000)
    ap.add_argument('--eval-n', type=int, default=100)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--max-train', type=int, default=0, help='use at most N training problems')
    a = ap.parse_args()
    torch.set_num_threads(a.threads); torch.manual_seed(a.seed); rnd = random.Random(a.seed)
    P = paths_of(a.dirs)
    test = sorted(set(l.split()[0] for l in open(a.test_names)) & set(P))
    rnd.shuffle(test)
    model = GNN(a.dim, a.layers)
    if a.load:
        model.load_state_dict(torch.load(a.load))
    if a.cmd == 'eval':
        v, k = evaluate(model, P, test, a)
        print(f'AUC {v:.3f} over {k} problems', flush=True)
        return
    train = sorted(set(P) - set(test))
    rnd.shuffle(train)
    if a.max_train:
        train = train[:a.max_train]
    print(f'{len(train)} training problems, {len(test)} test; d={a.dim} layers={a.layers}', flush=True)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    lossf = nn.BCEWithLogitsLoss(reduction='none')
    t0 = time.time(); run = []
    for step in range(1, a.steps + 1):
        G = Graph()
        while G.ns < a.batch:
            n = rnd.choice(train)
            try:
                ax, rules = load_log(P[n])
            except Exception:
                continue
            pos = [i for i, (l, _, _) in enumerate(rules) if l == 1]
            if not rules or not pos:
                continue
            if rnd.random() < a.pos_frac:
                k = max(0, rnd.choice(pos) - rnd.randrange(a.query))
            else:
                k = rnd.randrange(len(rules))
            G.add_sample(sample_eqs(n, ax, rules, k, a.ctx, a.query))
        nt, E, q, ql, qs, g, gs, ns = G.tensors()
        out = model(nt, E, q, qs, g, gs, ns)
        npos = ql.sum().clamp(min=1); nneg = (len(ql) - ql.sum()).clamp(min=1)
        w = torch.where(ql > 0, 0.5 / npos, 0.5 / nneg)   # balanced loss per batch
        loss = (lossf(out, ql) * w).sum()
        opt.zero_grad(); loss.backward(); opt.step()
        run.append(float(loss))
        if step % 200 == 0:
            print(f'step {step} loss {np.mean(run[-200:]):.4f} {time.time()-t0:.0f}s', flush=True)
        if step % a.eval_every == 0 or step == a.steps:
            v, k = evaluate(model, P, test, a, a.eval_n)
            print(f'  eval step {step}: AUC {v:.3f} over {k} test problems', flush=True)
            if a.save:
                torch.save(model.state_dict(), a.save)


if __name__ == '__main__':
    main()

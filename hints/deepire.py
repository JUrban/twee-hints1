#!/usr/bin/env python3
"""Deepire-style rule model for twee: learn from derivation history only.

Each rule twee adds gets an embedding computed from its parents' embeddings
(Suda 2021, "Improving ENIGMA-style clause selection while learning from
history"): axioms get a learned embedding per equation (if it is frequent in
training) or a generic one; a rule made from the critical pair of rules a and b
gets tanh(W [e_a + e_b ; e_a * e_b] + c) (symmetric in the parents). A small
classifier on the embedding (optionally with a projection of the goal's ENIGMA
features) predicts whether the rule ends up in the proof. No term features:
the cost in twee would be one d x 2d matrix-vector product per new rule.

deepire.py GIVENDIRS --test-origs O1,O2 [--dim 32] [--epochs 5] [--max-problems N]
           [--goal] [--compare-lgb MODEL.txt,MODEL.vocab] [--save M.pt]
Data: given logs (label, idx, lhs, rhs, parent1, parent2; label -1 = axiom).
Reports the mean per-problem AUC on the test originals (and the LightGBM
model's on the same rules with --compare-lgb).
"""
import argparse, collections, math, os, random, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GEN_AX, GEN_ORPHAN, NONE = 0, 1, 2   # reserved embedding rows

def load(path):
    """(labels, keys, parent row indices (-1 = none)) of one given log."""
    lab, keys, par, pos = [], [], [], {}
    for line in open(path):
        f = line.rstrip('\n').split('\t')
        if len(f) < 6:
            continue
        i = len(lab)
        pos[int(f[1])] = i
        lab.append(int(f[0])); keys.append(f[2] + '\t' + f[3])
        par.append((int(f[4]), int(f[5])))
    # parent numbers: the rule logged at position k has number k+1
    pr = [(pos.get(a - 1, -1) if a > 0 else -1, pos.get(b - 1, -1) if b > 0 else -1) for a, b in par]
    return np.array(lab, dtype=np.int8), keys, np.array(pr, dtype=np.int64).reshape(-1, 2)

class Problem:
    __slots__ = ('name', 'lab', 'leaf', 'par', 'level', 'gfeat')

def prepare(name, path, vocab, keep_keys=False):
    lab, keys, par = load(path)
    p = Problem(); p.name = name; p.lab = lab; p.par = par
    n = len(lab)
    leaf = np.full(n, -1, dtype=np.int64)       # embedding row for leaves, -1 for derived rules
    level = np.zeros(n, dtype=np.int64)
    for i in range(n):
        a, b = par[i]
        if a < 0 and b < 0:
            leaf[i] = vocab.get(keys[i], GEN_AX if lab[i] < 0 else GEN_ORPHAN)
        else:
            level[i] = 1 + max(level[a] if a >= 0 else 0, level[b] if b >= 0 else 0)
    p.leaf = leaf; p.level = level
    p.gfeat = None
    return p, (keys if keep_keys else None)

class Deepire(torch.nn.Module):
    def __init__(self, nvocab, dim, ngoal=0):
        super().__init__()
        self.emb = torch.nn.Embedding(nvocab, dim)
        self.comb = torch.nn.Linear(2 * dim, dim)
        self.goal = torch.nn.EmbeddingBag(ngoal, dim, mode='sum') if ngoal else None
        self.out = torch.nn.Sequential(torch.nn.Linear(dim * (2 if ngoal else 1), dim), torch.nn.ReLU(),
                                       torch.nn.Linear(dim, 1))

    def forward(self, probs):
        """Logits for all rules of a list of problems (concatenated)."""
        off, leaf, par, level, gidx = 0, [], [], [], []
        for k, p in enumerate(probs):
            leaf.append(p.leaf)
            pp = p.par.copy(); pp[pp >= 0] += off; par.append(pp)
            level.append(p.level); gidx.append(np.full(len(p.lab), k)); off += len(p.lab)
        leaf = torch.from_numpy(np.concatenate(leaf)); par = torch.from_numpy(np.concatenate(par))
        level = torch.from_numpy(np.concatenate(level))
        n = off; dim = self.emb.embedding_dim
        H = torch.zeros(n, dim)
        is_leaf = leaf >= 0
        H = H.index_put((is_leaf.nonzero().squeeze(1),), torch.tanh(self.emb(leaf[is_leaf])))
        none = torch.tanh(self.emb.weight[NONE])
        for L in range(1, int(level.max()) + 1 if n else 1):
            idx = (level == L).nonzero().squeeze(1)
            if len(idx) == 0:
                continue
            a = par[idx, 0]; b = par[idx, 1]
            ea = torch.where((a >= 0).unsqueeze(1), H[a.clamp(min=0)], none)
            eb = torch.where((b >= 0).unsqueeze(1), H[b.clamp(min=0)], none)
            h = torch.tanh(self.comb(torch.cat([ea + eb, ea * eb], 1)))
            H = H.index_put((idx,), h)
        if self.goal is not None:
            gi = torch.from_numpy(np.concatenate(gidx))
            G = torch.stack([self.goal(torch.tensor(p.gfeat[0], dtype=torch.long).unsqueeze(0),
                                       per_sample_weights=torch.tensor(p.gfeat[1], dtype=torch.float32)).squeeze(0)
                             if len(p.gfeat[0]) else torch.zeros(dim) for p in probs])
            H = torch.cat([H, G[gi]], 1)
        return self.out(H).squeeze(1)

def auc(y, s):
    order = np.argsort(s, kind='mergesort')
    ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    npos = y.sum(); nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return None
    return (ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('givendirs')
    ap.add_argument('--test-origs', default='')
    ap.add_argument('--test-names', help='file: test on these problems (the loop setting: their originals stay in training)')
    ap.add_argument('--dim', type=int, default=32)
    ap.add_argument('--epochs', type=int, default=5)
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--lr', type=float, default=3e-3)
    ap.add_argument('--min-ax', type=int, default=3, help='axiom equations in fewer training problems share one embedding')
    ap.add_argument('--max-problems', type=int, default=0)
    ap.add_argument('--ntest', type=int, default=300)
    ap.add_argument('--goal', action='store_true', help='add a projection of the goal\'s ENIGMA features')
    ap.add_argument('--compare-lgb', help='MODEL.txt,MODEL.vocab: LightGBM rule model to score the same test rules')
    ap.add_argument('--theory', action='store_true', help='--compare-lgb model uses the theory block')
    ap.add_argument('--threads', type=int, default=5)
    ap.add_argument('--save')
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    torch.set_num_threads(a.threads); torch.manual_seed(a.seed); random.seed(a.seed)
    test_o = set(a.test_origs.split(',')) if a.test_origs else set()
    test_n = set(l.split()[0] for l in open(a.test_names)) if a.test_names else set()
    paths = {}
    for d in a.givendirs.split(','):
        for n in os.listdir(d):
            paths[n] = os.path.join(d, n)      # later dirs win
    orig = lambda n: n.split('__goal_')[0]
    train = sorted(n for n in paths if orig(n) not in test_o and n not in test_n)
    test = sorted(n for n in paths if orig(n) in test_o or n in test_n)
    random.shuffle(train); random.shuffle(test)
    if a.max_problems:
        train = train[:a.max_problems]
    test = test[:a.ntest]
    t0 = time.time()
    # axiom vocabulary from the training problems
    cnt = collections.Counter()
    for n in train:
        for line in open(paths[n]):
            if line.startswith('-1\t'):
                f = line.split('\t'); cnt[f[2] + '\t' + f[3]] += 1
    vocab = {k: 3 + i for i, k in enumerate(k for k, c in cnt.most_common() if c >= a.min_ax)}
    gvocab = {}
    def gfeat(n):
        import rulemodel
        g = rulemodel.goal_feats(n)
        ids, ws = [], []
        for k, v in g.items():
            if k not in gvocab:
                gvocab[k] = len(gvocab)
            ids.append(gvocab[k]); ws.append(float(v))
        return ids, ws
    def prep(names):
        out = []
        for n in names:
            p, _ = prepare(n, paths[n], vocab)
            if (p.lab == 1).sum() == 0 or len(p.lab) < 2:
                continue
            if a.goal:
                p.gfeat = gfeat(n)
            out.append(p)
        return out
    tr = prep(train); te = prep(test)
    print(f'train {len(tr)} problems {sum(len(p.lab) for p in tr)} rules, test {len(te)}; '
          f'axiom vocab {len(vocab)}; loaded in {time.time()-t0:.0f}s', flush=True)
    npos = sum(int((p.lab == 1).sum()) for p in tr); nneg = sum(int((p.lab == 0).sum()) for p in tr)
    model = Deepire(3 + len(vocab), a.dim, (len(gvocab) + 1) if a.goal else 0)
    if a.goal:
        gvocab_frozen = dict(gvocab)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    lossf = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(nneg / max(1, npos)))
    def evaluate(probs):
        model.eval(); aucs = []
        with torch.no_grad():
            for i in range(0, len(probs), a.batch):
                bt = probs[i:i + a.batch]
                s = model(bt).numpy(); off = 0
                for p in bt:
                    y = p.lab; sc = s[off:off + len(y)]; off += len(y)
                    m = y >= 0
                    if m.sum() >= 20:
                        v = auc((y[m] == 1).astype(int), sc[m])
                        if v is not None:
                            aucs.append(v)
        model.train()
        return float(np.mean(aucs)) if aucs else float('nan'), len(aucs)
    for ep in range(a.epochs):
        random.shuffle(tr); tot = 0.0; t1 = time.time()
        for i in range(0, len(tr), a.batch):
            bt = tr[i:i + a.batch]
            logit = model(bt)
            y = torch.from_numpy(np.concatenate([p.lab for p in bt]).astype(np.float32))
            m = y >= 0
            loss = lossf(logit[m], y[m])
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss.detach()) * len(bt)
        print(f'epoch {ep+1}: loss {tot/len(tr):.4f} test AUC %.3f over %d problems ({time.time()-t1:.0f}s)'
              % evaluate(te), flush=True)
    if a.compare_lgb:
        import lightgbm as lgb, rulemodel
        rulemodel.THEORY = a.theory
        mt, mv = a.compare_lgb.split(',')
        rm = rulemodel.RuleModel(False)
        for line in open(mv):
            c, k = line.rstrip('\n').split('\t'); rm.vocab.idx[k] = int(c) - rulemodel.NFIX
        rm.vocab.frozen = True
        rm.model = lgb.Booster(model_file=mt); rm.ncol = rm.model.num_feature()
        aucs = []; fused = collections.defaultdict(list)
        model.eval()
        for p in te:
            rows = [x for x in rulemodel.load(paths[p.name]) if x[0] >= 0]
            if len(rows) < 20 or len(rows) != int((p.lab >= 0).sum()):
                continue
            y = np.array([x[0] for x in rows])
            sl = rm.predict(p.name, [x[1:] for x in rows])
            v = auc(y, sl)
            if v is None:
                continue
            aucs.append(v)
            with torch.no_grad():
                sd = model([p]).numpy()[p.lab >= 0]
            # rank fusion: is the derivation signal complementary to the term features?
            rl = np.argsort(np.argsort(sl)) / len(sl); rd = np.argsort(np.argsort(sd)) / len(sd)
            for w in (0.1, 0.25, 0.5, 1.0):
                fused[w].append(auc(y, rl + w * rd))
        print(f'LightGBM {os.path.basename(mt)}: test AUC {np.mean(aucs):.3f} over {len(aucs)} problems')
        for w, L in sorted(fused.items()):
            print(f'  rank fusion LightGBM + {w} x deepire: AUC {np.mean(L):.3f}')
    if a.save:
        torch.save({'model': model.state_dict(), 'vocab': vocab, 'dim': a.dim}, a.save)

if __name__ == '__main__':
    main()

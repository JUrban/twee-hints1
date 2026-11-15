"""Hint generator with a copy action (15 Nov): gen.py's model, plus COPY: point at a term node of
the sample (a subterm of the axioms, the goal or the context rules, size >= 3), then one VAR action
per distinct variable of the copied term (its variables, or the goal's skolems, in first-occurrence
order) maps them to the equation's variable slots.

Why: gen.py learns the common lemmas, which the pool already holds (22 of its 24 hits), and finds 2
of 1,251 steps the pool lacks. Those novel steps are long (median 18 symbols), but on each side the
largest subterm already in the context covers typically 40-70% of the step; written by copying they
take a few decisions instead of ~18.

Targets are encoded greedily top-down: a subterm whose variant occurs among the sample's copyable
terms is copied (the loss sums the probability of all nodes with that variant), else its symbol is
written and its arguments follow.

  python3 gencopy.py train GIVENDIRS --test-names sets/ultest --save C.pt [--novel HINTSDIR]
  python3 gencopy.py eval GIVENDIRS --test-names NAMES --load C.pt --pool-dir HINTSDIR [--n 400 --temp 0.7]
  python3 gencopy.py hints LOG GOALNAME --load C.pt [--n 400]
"""
import argparse, math, os, random, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import (GGraph, Enc, IncDec, _proj, _heads, canon, sample_eqs, rows_from_out, MAXV, TOKV)
from gnn import parse, isvar, Vocab, load_log, paths_of, T_TERM, T_GTERM, T_MTERM, T_GOAL

A_BOS, A_SYM, A_VAR, A_EOS, A_COPY = 0, 1, 2, 3, 4
MINCOPY = 3


def tsize(t):
    return 1 + sum(tsize(a) for a in t[1])


def tkey(t, skolems=False):
    """Variant key of a term and its variables in first-occurrence order."""
    ren = {}
    def go(t):
        f, args = t
        if isvar(t):
            if f not in ren:
                ren[f] = len(ren)
            return f'_{ren[f]}'
        return f if not args else f + '(' + ','.join(go(a) for a in args) + ')'
    k = go(t)
    return k, sorted(ren, key=ren.get)


def term_table(G, s):
    """node -> term (as a tuple, variables named by node) for the term nodes of sample S."""
    from gnn import R_SYM, R_ARG, MAXARG, T_SYM, T_VAR, T_SKO
    a, b = G.ranges[s]
    symname = {}
    for k, node in G.symlists[s].items():
        symname[node] = k
    fun, args = {}, {}
    for src, dst in G.edges[R_SYM]:
        if a <= dst < b:
            fun[dst] = symname.get(src)
    for i in range(MAXARG):
        for src, dst in G.edges[R_ARG + i]:
            if a <= dst < b:
                args.setdefault(dst, {})[i] = src
    memo = {}
    def term(n):
        if n in memo:
            return memo[n]
        t = G.ntype[n]
        if t == T_VAR or t == T_SKO:
            x = (f'V{n}', ())
        elif n in fun and fun[n] is not None:
            f, ar = fun[n]
            x = (f, tuple(term(args[n][i]) for i in range(ar))) if ar else (f, ())
        else:
            x = None
        memo[n] = x
        return x
    out = []
    for n in range(a, b):
        if n in fun and fun[n] is not None and fun[n][1] > 0:
            x = term(n)
            if x is not None and None not in x[1] and tsize(x) >= MINCOPY:
                out.append((n, x))
    return out


def copies_of(G, s, maxc=4000):
    """Copy candidates of sample S: (node, key, variables) for its term nodes of size >= MINCOPY, at
    most MAXC (the most recent equations' terms are last; keep the axioms', goal's and newest)."""
    tt = term_table(G, s)
    if len(tt) > maxc:
        tt = tt[:maxc // 4] + tt[-(maxc - maxc // 4):]
    cands = []
    for n, x in tt:
        k, vs = tkey(x)
        cands.append((n, k, vs, x))
    ck = {}
    for i, (_, k, _, _) in enumerate(cands):
        ck.setdefault(k, []).append(i)
    return cands, ck


def encode_eq(l, r, keys, ck, cands):
    """Prefix sequence of l = r with copies: items (action, arg) where arg is a symbol index, a
    variable slot, or for COPY the list of candidate indices; None if a symbol is not in KEYS."""
    kidx = {k: i for i, k in enumerate(keys)}
    seq = []; vs = {}
    def slot(f):
        if f not in vs:
            vs[f] = len(vs)
        return min(vs[f], MAXV - 1)
    def go(t):
        f, args = t
        if isvar(t):
            seq.append((A_VAR, slot(f))); return True
        if args and tsize(t) >= MINCOPY:
            k, tv = tkey(t)
            if k in ck:
                seq.append((A_COPY, ck[k]))
                for v in tv:
                    seq.append((A_VAR, slot(v)))
                return True
        k = (f, len(args))
        if k not in kidx:
            return False
        seq.append((A_SYM, kidx[k]))
        return all(go(a) for a in args)
    if not (go(parse(l)) and go(parse(r))):
        return None
    seq.append((A_EOS, 0))
    return seq


class CDec(nn.Module):
    def __init__(self, d=64, layers=2, nhead=4, maxlen=64):
        super().__init__()
        self.d, self.maxlen = d, maxlen
        self.act = nn.Embedding(5, d)
        self.symp = nn.Linear(d, d)
        self.copyp = nn.Linear(d, d)
        self.varemb = nn.Embedding(MAXV, d)
        self.pos = nn.Embedding(maxlen, d)
        self.tf = nn.TransformerDecoder(nn.TransformerDecoderLayer(d, nhead, 4 * d, dropout=0.1, batch_first=True), layers)
        for L in self.tf.layers:
            L.self_attn.dropout = 0.0; L.multihead_attn.dropout = 0.0
        self.acth = nn.Linear(d, 4)          # SYM, VAR, EOS, COPY (action - 1)
        self.pq = nn.Linear(d, d); self.pk = nn.Linear(d, d)
        self.cq = nn.Linear(d, d); self.ck = nn.Linear(d, d)
        self.varh = nn.Linear(d, MAXV)

    def embed(self, acts, args, symemb, copyemb, start=0):
        """acts, args (B, T): args are symbol indices (SYM), slots (VAR) or a candidate index (COPY)."""
        x = self.act(acts)
        isym = acts == A_SYM
        sidx = torch.where(isym, args, torch.zeros_like(args)).clamp(max=symemb.shape[1] - 1)
        se = torch.gather(symemb, 1, sidx.unsqueeze(-1).expand(-1, -1, self.d))
        x = x + torch.where(isym.unsqueeze(-1), self.symp(se), torch.zeros_like(se))
        icp = acts == A_COPY
        cidx = torch.where(icp, args, torch.zeros_like(args)).clamp(max=max(copyemb.shape[1] - 1, 0))
        ce = torch.gather(copyemb, 1, cidx.unsqueeze(-1).expand(-1, -1, self.d))
        x = x + torch.where(icp.unsqueeze(-1), self.copyp(ce), torch.zeros_like(ce))
        ivar = acts == A_VAR
        ve = self.varemb(torch.where(ivar, args, torch.zeros_like(args)).clamp(max=MAXV - 1))
        x = x + torch.where(ivar.unsqueeze(-1), ve, torch.zeros_like(ve))
        T = acts.shape[1]
        return x + self.pos(torch.arange(start, start + T).clamp(max=self.maxlen - 1)).unsqueeze(0)

    def heads(self, y, symemb, symmask, copyemb, copymask):
        al = self.acth(y)
        pl = torch.einsum('btd,bkd->btk', self.pq(y), self.pk(symemb)) / math.sqrt(self.d)
        pl = pl.masked_fill(~symmask.unsqueeze(1), float('-inf'))
        cl = torch.einsum('btd,bkd->btk', self.cq(y), self.ck(copyemb)) / math.sqrt(self.d)
        cl = cl.masked_fill(~copymask.unsqueeze(1), float('-inf'))
        return al, pl, cl, self.varh(y)

    def grouped(self, acts, args, symemb, symmask, copyemb, copymask, mem, memmask, Q):
        S = mem.shape[0]; B, T = acts.shape
        se = symemb.repeat_interleave(Q, 0); ce = copyemb.repeat_interleave(Q, 0)
        x = self.embed(acts, args, se, ce)
        causal = torch.triu(torch.ones(T, T, dtype=torch.bool), 1)
        for L in self.tf.layers:
            x = L.norm1(x + L.dropout1(L.self_attn(x, x, x, attn_mask=causal, need_weights=False)[0]))
            c = L.multihead_attn(x.reshape(S, Q * T, -1), mem, mem, key_padding_mask=~memmask, need_weights=False)[0]
            x = L.norm2(x + L.dropout2(c.reshape(B, T, -1)))
            x = L.norm3(x + L.dropout3(L.linear2(L.dropout(F.relu(L.linear1(x))))))
        return self.heads(x, se, symmask.repeat_interleave(Q, 0), ce, copymask.repeat_interleave(Q, 0))


class CModel(nn.Module):
    def __init__(self, d=64, layers=6, dlayers=2, nnames=64):
        super().__init__()
        self.enc = Enc(d, layers, nnames)
        self.dec = CDec(d, dlayers)

    def memories(self, G, cl):
        """As gen.Model.memories, plus the copy candidates' embeddings (S, C, d) and mask; CL: per
        sample the candidate list from copies_of."""
        from gnn import NREL
        nt, nn_, E = torch.tensor(G.ntype), torch.tensor(G.nname), []
        for r in range(NREL):
            if G.edges[r]:
                a = torch.tensor(G.edges[r], dtype=torch.long)
                E.append((r, a[:, 0], a[:, 1]))
        h = self.enc(nt, nn_, E)
        S = len(G.ranges); d = h.shape[1]
        Nmax = max(b - a for a, b in G.ranges)
        mem = torch.zeros(S, Nmax, d); mm = torch.zeros(S, Nmax, dtype=torch.bool)
        for i, (a, b) in enumerate(G.ranges):
            mem[i, :b - a] = h[a:b]; mm[i, :b - a] = True
        keys = [sorted(sl) for sl in G.symlists]
        Kmax = max(len(k) for k in keys)
        se = torch.zeros(S, Kmax, d); sm = torch.zeros(S, Kmax, dtype=torch.bool)
        for i, (sl, ks) in enumerate(zip(G.symlists, keys)):
            idx = torch.tensor([sl[k] for k in ks])
            se[i, :len(ks)] = h[idx]; sm[i, :len(ks)] = True
        Cmax = max(1, max(len(c) for c in cl))
        ce = torch.zeros(S, Cmax, d); cm = torch.zeros(S, Cmax, dtype=torch.bool)
        for i, c in enumerate(cl):
            if c:
                idx = torch.tensor([c_[0] for c_ in c])
                ce[i, :len(c)] = h[idx]; cm[i, :len(c)] = True
        return mem, mm, se, sm, keys, ce, cm


def batch_loss(model, G, cl, targets):
    mem, mm, se, sm, keys, ce, cm = model.memories(G, cl)
    if not any(targets):
        return None
    Q = max(len(qs) for qs in targets)
    rows = [(s, qs[i] if i < len(qs) else None) for s, qs in enumerate(targets) for i in range(Q)]
    T = max(len(q) for _, q in rows if q)
    B = len(rows); C = ce.shape[1]
    acts = torch.full((B, T), A_EOS, dtype=torch.long); args = torch.zeros((B, T), dtype=torch.long)
    tin_a = torch.full((B, T), A_EOS, dtype=torch.long); tin_x = torch.zeros((B, T), dtype=torch.long)
    valid = torch.zeros((B, T), dtype=torch.bool); forced = torch.zeros((B, T), dtype=torch.bool)
    pvar = torch.zeros((B, T), dtype=torch.bool)   # a copied term's variable: the action is forced VAR
    vmax = torch.zeros((B, T), dtype=torch.long)
    cmask = torch.zeros((B, T, C), dtype=torch.bool)
    w = torch.ones(B)
    for i, (s, q) in enumerate(rows):
        if q is None:
            w[i] = 0.0; continue
        open_ = 2; nv = 0; params = 0
        for t, (a, x) in enumerate(q):
            acts[i, t] = a; valid[i, t] = True
            forced[i, t] = open_ == 0 and params == 0
            pvar[i, t] = params > 0
            vmax[i, t] = min(nv + 1, MAXV)
            if a == A_SYM:
                args[i, t] = x; open_ += keys[s][x][1] - 1
            elif a == A_VAR:
                args[i, t] = x; nv = max(nv, x + 1)
                if params:
                    params -= 1
                else:
                    open_ -= 1
            elif a == A_COPY:
                args[i, t] = x[0]; cmask[i, t, x] = True
                open_ -= 1; params = len(cl[s][x[0]][2])
        tin_a[i, 0] = A_BOS
        for t in range(1, len(q)):
            tin_a[i, t] = q[t - 1][0]
            px = q[t - 1][1]
            tin_x[i, t] = px[0] if q[t - 1][0] == A_COPY else px
    al, pl, cl_, vl = model.dec.grouped(tin_a, tin_x, se, sm, ce, cm, mem, mm, Q)
    # action: SYM VAR EOS COPY; EOS only when forced; nothing to choose for forced EOS or copy params
    al = al.clone()
    al[..., A_EOS - 1] = al[..., A_EOS - 1].masked_fill(~forced, float('-inf'))
    tgt = (acts - 1).clamp(min=0)
    la = F.cross_entropy(al.reshape(-1, 4), tgt.reshape(-1), reduction='none').reshape(B, T)
    la = torch.where(valid & ~forced & ~pvar, la, torch.zeros_like(la))
    lp = F.cross_entropy(pl.reshape(-1, pl.shape[-1]), args.reshape(-1).clamp(max=pl.shape[-1] - 1), reduction='none').reshape(B, T)
    lp = torch.where(valid & (acts == A_SYM), lp, torch.zeros_like(lp))
    # copy: -log of the summed probability of all candidates with the target's variant
    lsm = F.log_softmax(cl_, -1)
    lc = -torch.logsumexp(lsm.masked_fill(~cmask, float('-inf')), -1)
    lc = torch.where(valid & (acts == A_COPY), lc, torch.zeros_like(lc))
    vmask = torch.arange(MAXV).view(1, 1, -1) < vmax.unsqueeze(-1)
    vl = vl.masked_fill(~vmask, float('-inf'))
    lv = F.cross_entropy(vl.reshape(-1, MAXV), args.reshape(-1).clamp(max=MAXV - 1), reduction='none').reshape(B, T)
    lv = torch.where(valid & (acts == A_VAR), lv, torch.zeros_like(lv))
    tok = (la + lp + lc + lv).sum(1) / valid.sum(1).clamp(min=1)
    return (tok * w).sum() / w.sum().clamp(min=1e-9)


@torch.no_grad()
def generate(model, G, s, cands, n, temp=1.0, maxlen=48):
    model.eval()
    mem, mm, se, sm, keys, ce, cm = model.memories(G, [cands if i == s else [] for i in range(len(G.ranges))])
    ks = keys[s]; K = len(ks); dec = model.dec; C = max(len(cands), 1)
    inc = IncDec(dec, mem[s:s + 1, :int(mm[s].sum())])
    sse = se[s:s + 1, :K]; cce = ce[s:s + 1, :C]
    pk = dec.pk(sse)[0]; ckk = dec.ck(cce)[0]
    ar = torch.tensor([k[1] for k in ks])
    nvc = torch.tensor([len(c[2]) for c in cands] or [0])
    open_ = torch.full((n,), 2); nv = torch.zeros(n, dtype=torch.long); done = torch.zeros(n, dtype=torch.bool)
    params = torch.zeros(n, dtype=torch.long)
    a_prev = torch.full((n, 1), A_BOS, dtype=torch.long); x_prev = torch.zeros((n, 1), dtype=torch.long)
    symb = sse.expand(n, -1, -1); copb = cce.expand(n, -1, -1)
    out_a, out_x = [], []
    for t in range(maxlen):
        y = inc.step(dec.embed(a_prev, x_prev, symb, copb, start=t))[:, 0]
        al = dec.acth(y) / temp
        pl = (dec.pq(y) @ pk.T) / math.sqrt(dec.d) / temp
        cl = (dec.cq(y) @ ckk.T) / math.sqrt(dec.d) / temp
        if not cands:
            cl = cl.fill_(float('-inf')); al[:, A_COPY - 1] = float('-inf')
        vl = dec.varh(y) / temp
        if t > maxlen - 12:
            al[:, A_SYM - 1] -= 5
        choose = al[:, [A_SYM - 1, A_VAR - 1, A_COPY - 1]]
        a = torch.tensor([A_SYM, A_VAR, A_COPY])[torch.multinomial(F.softmax(choose, -1), 1).squeeze(1)]
        a = torch.where(params > 0, torch.full_like(a, A_VAR), a)
        a = torch.where((open_ == 0) & (params == 0), torch.full_like(a, A_EOS), a)
        p = torch.multinomial(F.softmax(pl, -1), 1).squeeze(1)
        c = torch.multinomial(F.softmax(cl, -1), 1).squeeze(1) if cands else torch.zeros(n, dtype=torch.long)
        vmask = torch.arange(MAXV).unsqueeze(0) < (nv + 1).clamp(max=MAXV).unsqueeze(1)
        v = torch.multinomial(F.softmax(vl.masked_fill(~vmask, float('-inf')), -1), 1).squeeze(1)
        x = torch.where(a == A_SYM, p, torch.where(a == A_VAR, v, torch.where(a == A_COPY, c, torch.zeros_like(p))))
        a = torch.where(done, torch.full_like(a, A_EOS), a)
        was_param = params > 0
        open_ = torch.where(a == A_SYM, open_ + ar[x.clamp(max=K - 1)] - 1,
                            torch.where((a == A_VAR) & ~was_param, open_ - 1, torch.where(a == A_COPY, open_ - 1, open_)))
        params = torch.where(a == A_COPY, nvc[x.clamp(max=len(nvc) - 1)], torch.where(was_param & (a == A_VAR), params - 1, params))
        nv = torch.where(a == A_VAR, torch.maximum(nv, x + 1), nv)
        done = done | (a == A_EOS)
        out_a.append(a); out_x.append(x)
        a_prev, x_prev = a.unsqueeze(1), x.unsqueeze(1)
        if bool(done.all()):
            break
    A = torch.stack(out_a, 1).tolist(); X = torch.stack(out_x, 1).tolist()
    res = []
    for aa, xx in zip(A, X):
        if A_EOS not in aa:
            continue
        toks = list(zip(aa[:aa.index(A_EOS)], xx))
        pos = 0
        def term():
            nonlocal pos
            a, x = toks[pos]; pos += 1
            if a == A_VAR:
                return f'X{x}'
            if a == A_COPY:
                node, k, vs, tm = cands[x]
                sub = {}
                for v in vs:
                    a2, x2 = toks[pos]; pos += 1
                    sub[v] = f'X{x2}'
                return show(tm, sub)
            f, k = ks[x]
            return f if k == 0 else f'{f}(' + ','.join(term() for _ in range(k)) + ')'
        try:
            l = term(); r = term()
        except (IndexError, TypeError):
            continue
        if l != r and not (l[0] == 'X' and '(' not in l and l not in TOKV.findall(r)) \
                and not (r[0] == 'X' and '(' not in r and r not in TOKV.findall(l)):
            res.append((l, r))
    model.train()
    return res


def show(t, sub):
    f, args = t
    if isvar(t) or f.startswith('V') and not args and f[1:].isdigit():
        return sub.get(f, f)
    return f if not args else f + '(' + ','.join(show(a, sub) for a in args) + ')'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('given'); ap.add_argument('name', nargs='?')
    ap.add_argument('--test-names', default='')
    ap.add_argument('--save'); ap.add_argument('--load'); ap.add_argument('--init-enc', help='train: encoder weights from a gen.py checkpoint')
    ap.add_argument('--steps', type=int, default=6000)
    ap.add_argument('--dim', type=int, default=64)
    ap.add_argument('--layers', type=int, default=6)
    ap.add_argument('--dlayers', type=int, default=2)
    ap.add_argument('--ctx', type=int, default=256)
    ap.add_argument('--batch', type=int, default=8)
    ap.add_argument('--targets', type=int, default=16)
    ap.add_argument('--maxtok', type=int, default=48)
    ap.add_argument('--maxcopy', type=int, default=4000)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--hard', type=float, default=0.5)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--eval-every', type=int, default=1000)
    ap.add_argument('--eval-n', type=int, default=30)
    ap.add_argument('--n', type=int, default=400)
    ap.add_argument('--k', type=int, default=-1)
    ap.add_argument('--temp', type=float, default=0.7)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--novel', help='train: targets only proof rules no other goal of the original has as a hint')
    ap.add_argument('--pool-dir')
    ap.add_argument('--problem'); ap.add_argument('--out'); ap.add_argument('--drop-known', type=int, default=1)
    ap.add_argument('--counts', type=int, default=0, help='hints: sample counts as a third column, most frequent first')
    a = ap.parse_args()
    torch.set_num_threads(a.threads); random.seed(a.seed); torch.manual_seed(a.seed); np.random.seed(a.seed)
    if a.load:
        ck = torch.load(a.load, weights_only=False)
        vocab = Vocab(); vocab.idx = ck['vocab']; vocab.frozen = a.cmd != 'train'
        sa = ck['args']
        model = CModel(sa['dim'], sa['layers'], sa['dlayers']); model.load_state_dict(ck['model'])
        a.dim, a.layers, a.dlayers = sa['dim'], sa['layers'], sa['dlayers']
    else:
        vocab = Vocab(); model = CModel(a.dim, a.layers, a.dlayers)
        if a.init_enc:
            ck = torch.load(a.init_enc, weights_only=False)
            vocab.idx = dict(ck['vocab'])
            enc = {k[4:]: v for k, v in ck['model'].items() if k.startswith('enc.')}
            model.enc.load_state_dict(enc)
            # decoder parts with the same shapes (transformer, symbol pointer, variable head)
            dec = {k[4:]: v for k, v in ck['model'].items() if k.startswith('dec.')}
            own = model.dec.state_dict()
            model.dec.load_state_dict({k: (dec[k] if k in dec and dec[k].shape == own[k].shape else own[k]) for k in own})

    def sample(n, ax, rules, k):
        G = GGraph(vocab); G.add_sample(sample_eqs(n, ax, rules, k, a.ctx))
        cands, ckeys = copies_of(G, 0, a.maxcopy)
        return G, cands, ckeys

    if a.cmd in ('hints', 'hints-out'):
        vocab.frozen = True
        ax, rules = load_log(a.given) if a.cmd == 'hints' else rows_from_out(open(a.given, errors='replace').read(), a.name, a.problem)
        k = len(rules) if a.k < 0 else a.k
        G, cands, _ = sample(a.name, ax, rules, k)
        have = {canon(l, r) for _, l, r in ax + rules[:k]} if a.drop_known else set()
        seen, out, cnt = {}, [], {}
        for l, r in generate(model, G, 0, cands, a.n, a.temp, a.maxtok):
            c = canon(l, r)
            if c in have:
                continue
            cnt[c] = cnt.get(c, 0) + 1
            if c not in seen:
                seen[c] = (l, r)
        if a.counts:   # most often sampled first, with the count (the cut candidates' ranking)
            out = [f'{seen[c][0]}\t{seen[c][1]}\t{cnt[c]}\n' for c in sorted(seen, key=lambda c: -cnt[c])]
        else:
            out = [f'{l}\t{r}\n' for l, r in seen.values()]
        if a.out:
            with open(a.out + '.tmp', 'w') as f:
                f.writelines(out)
            os.replace(a.out + '.tmp', a.out)
        else:
            sys.stdout.writelines(out)
        return

    P = paths_of(a.given)
    test = [l.split()[0] for l in open(a.test_names)] if a.test_names else []
    tset = set(test)
    train = sorted(n for n in P if n not in tset)
    test = [n for n in test if n in P]
    rng = random.Random(7); rng.shuffle(test)

    # hint pools of the originals (for --novel and the evaluation)
    hdir = a.novel or a.pool_dir
    byo, ocnt, owncache = {}, {}, {}
    if hdir:
        for f in os.listdir(hdir):
            byo.setdefault(f.rpartition('__goal_')[0], []).append(f)
    def hints_of(f):
        out = set()
        p = os.path.join(hdir, f)
        if os.path.exists(p):
            for l in open(p):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 2:
                    try:
                        out.add(canon(w[0], w[1]))
                    except Exception:
                        pass
        return out
    def novel_fn(n):
        o = n.rpartition('__goal_')[0]
        if o not in ocnt:
            c = {}
            for f in byo.get(o, []):
                for h in hints_of(f):
                    c[h] = c.get(h, 0) + 1
            ocnt[o] = c
        c = ocnt[o]
        if n not in owncache:
            owncache[n] = hints_of(n)
        own = owncache[n]
        return lambda l, r: c.get(canon(l, r), 0) - (canon(l, r) in own) <= 0

    def evaluate(names):
        rec, nh, tot, ng, nl, pn, pg, cop = [], 0, 0, 0, 0, 0, 0, 0
        for n in names:
            ax, rules = load_log(P[n])
            pr = [i for i, (lab, _, _) in enumerate(rules) if lab == 1]
            if len(pr) < 4:
                continue
            k = pr[len(pr) // 2]
            fut = {canon(l, r) for lab, l, r in rules[k:] if lab == 1}
            later = {canon(l, r) for lab, l, r in rules[k:]}
            G, cands, _ = sample(n, ax, rules, k)
            gen_ = {canon(l, r) for l, r in generate(model, G, 0, cands, a.n, a.temp, a.maxtok)}
            hit = len(fut & gen_)
            rec.append(hit / len(fut)); nh += hit; tot += len(fut); ng += len(gen_); nl += len(later & gen_)
            if hdir:
                nv_ = novel_fn(n)
                nov = {c for lab, l, r in rules[k:] if lab == 1 and nv_(l, r) for c in [canon(l, r)]}
                pn += len(nov); pg += len(nov & gen_)
        print(f'  generated: {ng / max(len(rec), 1):.0f} distinct per cut, {nl / max(ng, 1):.1%} derived later in the run', flush=True)
        if hdir:
            print(f'  novel (no other goal of the original has it as a hint): {pg}/{pn} generated', flush=True)
        return (float(np.mean(rec)) if rec else 0.0), nh, tot, len(rec)

    if a.cmd == 'eval':
        vocab.frozen = True
        r, nh, tot, m = evaluate(test)
        print(f'eval: mean recall {r:.3f} ({nh}/{tot} future proof rules, {m} problems, n={a.n}, T={a.temp})')
        return

    W = np.array([max(os.path.getsize(P[n]), 1) ** a.hard for n in train]); W /= W.sum()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    cache = {}
    def get(n):
        if n not in cache:
            if len(cache) > 3000:
                cache.pop(next(iter(cache)))
            cache[n] = load_log(P[n])
        return cache[n]
    t0 = time.time(); run = []; ncopy = [0, 0]
    print(f'train: {len(train)} logs, test {len(test)}, {sum(p.numel() for p in model.parameters())} parameters', flush=True)
    for step in range(1, a.steps + 1):
        G = GGraph(vocab); targets = []; cl = []
        tries = 0
        while len(targets) < a.batch and tries < 50:
            tries += 1
            n = train[np.random.choice(len(train), p=W)]
            ax, rules = get(n)
            pr = [i for i, (lab, _, _) in enumerate(rules) if lab == 1]
            if a.novel:
                nv_ = novel_fn(n)
                pr = [i for i in pr if nv_(rules[i][1], rules[i][2])]
                if not pr:
                    continue
            elif len(pr) < 2:
                continue
            w_ = np.array([i + 1.0 for i in pr]); j = np.random.choice(len(pr), p=w_ / w_.sum())
            k = pr[j]
            s = G.add_sample(sample_eqs(n, ax, rules, k, a.ctx))
            cands, ckeys = copies_of(G, s, a.maxcopy)
            keys = sorted(G.symlists[s])
            fut = [rules[i] for i in pr[j:]]
            random.shuffle(fut)
            qs = []
            for _, l, r in fut:
                q = encode_eq(l, r, keys, ckeys, cands) if random.random() < 0.5 else encode_eq(r, l, keys, ckeys, cands)
                if q and len(q) <= a.maxtok:
                    qs.append(q); ncopy[0] += sum(1 for x, _ in q if x == A_COPY); ncopy[1] += len(q)
                if len(qs) >= a.targets:
                    break
            targets.append(qs); cl.append(cands)
        loss = batch_loss(model, G, cl, targets)
        if loss is None:
            continue
        for g in opt.param_groups:
            g['lr'] = a.lr * (0.1 + 0.45 * (1 + math.cos(math.pi * step / a.steps)))
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); run.append(loss.item())
        if step % 100 == 0 or step in (1, 10):
            print(f'step {step} loss {np.mean(run[-100:]):.4f} {time.time()-t0:.0f}s, copies {ncopy[0] / max(ncopy[1], 1):.1%} of tokens', flush=True)
        if a.save and (step % a.eval_every == 0 or step == a.steps):
            torch.save({'model': model.state_dict(), 'vocab': vocab.idx, 'args': vars(a)}, a.save)
            if test:
                r, nh, tot, m = evaluate(test[:a.eval_n])
                print(f'  eval step {step}: mean recall {r:.3f} ({nh}/{tot} future proof rules, {m} problems, n={a.n}, T={a.temp})', flush=True)


if __name__ == '__main__':
    main()

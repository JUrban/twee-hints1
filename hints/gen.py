"""Hint generation: a graph encoder with a pointer decoder (15 Nov, user: train a GNN2Seq model
after Chvalovsky, Suda and Urban, "Neural Conjecturing for Saturation Theorem Provers", IWIL 2026,
github.com/JUrban/E_conj_dev1 vampire4, to propose likely useful hints for each run, from the
current situation of the search).

A sample is one problem at a cut k of a twee run (a given.py log): the encoder sees the axioms
(with the run's lemmas), the goal and the last --ctx rules before k (gnn.py version 2's graph:
symbol-aware, goal skolems and goal-term marks); the decoder is trained to write the run's proof
rules added at k or later (label 1 in the log), one equation at a time. So at a pause of a run
(the cascade's level boundaries) it proposes the proof steps still to come, as hints.

An equation l = r is written in prefix order as actions SYM (a pointer to one of the sample's
symbol nodes), VAR (a variable slot, numbered by first occurrence) and EOS; an arity count keeps
every sampled sequence a well-formed pair of terms (as the arity-constrained decoding of
E_conj_dev1). Decoder: causal Transformer with cross-attention to all nodes of the sample.

  python3 gen.py train GIVENDIRS --test-names sets/ultest --save G.pt [--steps N --dim D]
  python3 gen.py eval GIVENDIRS --test-names sets/ultest --load G.pt [--n 100]
  python3 gen.py hints LOG GOALNAME --load G.pt [--n 200 --k K]     (prints l<TAB>r lines)
  python3 gen.py hints-out TWEEOUT GOALNAME --problem P.p --load G.pt [--out F]   (from a run's output)
"""
import argparse, math, os, random, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gnn
from gnn import (parse, isvar, Vocab, load_log, goal_eqs, paths_of, MAXARG, NREL, NTYPES,
                 T_AX, T_GOAL, T_CTX, T_TERM, T_VAR, T_GTERM, T_SKO, T_MTERM, T_SYM,
                 R_LHS, R_RHS, R_SYM, R_ARG, R_GMATCH, variant_key)

A_BOS, A_SYM, A_VAR, A_EOS = 0, 1, 2, 3
TOKV = __import__('re').compile(r'X[0-9]+')
MAXV = 12


class GGraph(gnn.Graph):
    """gnn.Graph that also records each sample's node range and symbol nodes."""
    def __init__(self, vocab, names=True, marks=True):
        super().__init__(vocab, names, marks)
        self.ranges, self.symlists = [], []

    def add_sample(self, eqs):
        start = len(self.ntype)
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
                    if goal:
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
            if t == T_GOAL:
                self.goal.append(e); self.gsample.append(s)
        self.ranges.append((start, len(self.ntype)))
        self.symlists.append(syms)
        return s


class Enc(nn.Module):
    """gnn.GNN's message passing; returns the node embeddings."""
    def __init__(self, d=64, layers=6, nnames=64):
        super().__init__()
        self.emb = nn.Embedding(NTYPES, d)
        self.nemb = nn.Embedding(nnames + 1, d, padding_idx=0)
        self.layers = layers
        self.selfw = nn.ModuleList([nn.Linear(d, d) for _ in range(layers)])
        self.fw = nn.ModuleList([nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(NREL)]) for _ in range(layers)])
        self.bw = nn.ModuleList([nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(NREL)]) for _ in range(layers)])
        self.norm = nn.ModuleList([nn.LayerNorm(d) for _ in range(layers)])

    def forward(self, ntype, nname, E):
        nname = nname.clamp(max=self.nemb.num_embeddings - 1)
        h = self.emb(ntype) + self.nemb(nname)
        N = h.shape[0]
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
        return h


class Dec(nn.Module):
    def __init__(self, d=64, layers=2, nhead=4, maxlen=64):
        super().__init__()
        self.d, self.maxlen = d, maxlen
        self.act = nn.Embedding(4, d)
        self.symp = nn.Linear(d, d)
        self.varemb = nn.Embedding(MAXV, d)
        self.pos = nn.Embedding(maxlen, d)
        self.tf = nn.TransformerDecoder(nn.TransformerDecoderLayer(d, nhead, 4 * d, dropout=0.1, batch_first=True), layers)
        for L in self.tf.layers:   # no dropout on attention weights (half the step time); residual dropout stays
            L.self_attn.dropout = 0.0; L.multihead_attn.dropout = 0.0
        self.acth = nn.Linear(d, 3)          # SYM, VAR, EOS (action - 1)
        self.pq = nn.Linear(d, d); self.pk = nn.Linear(d, d)
        self.varh = nn.Linear(d, MAXV)

    def embed(self, acts, args, symemb, start=0):
        """acts, args: (B, T); symemb: (B, K, d) the candidate symbols of each sequence's sample;
        START: the position of the first token."""
        x = self.act(acts)
        isym = acts == A_SYM
        sidx = torch.where(isym, args, torch.zeros_like(args)).clamp(max=symemb.shape[1] - 1)
        se = torch.gather(symemb, 1, sidx.unsqueeze(-1).expand(-1, -1, self.d))
        x = x + torch.where(isym.unsqueeze(-1), self.symp(se), torch.zeros_like(se))
        ivar = acts == A_VAR
        ve = self.varemb(torch.where(ivar, args, torch.zeros_like(args)).clamp(max=MAXV - 1))
        x = x + torch.where(ivar.unsqueeze(-1), ve, torch.zeros_like(ve))
        T = acts.shape[1]
        return x + self.pos(torch.arange(start, start + T).clamp(max=self.maxlen - 1)).unsqueeze(0)

    def grouped_logits(self, acts, args, symemb, symmask, mem, memmask, Q):
        """As step_logits for S*Q sequences grouped by sample (rows s*Q .. s*Q+Q-1 belong to
        sample s): symemb (S, K, d), mem (S, N, d). Cross-attention runs once per sample over
        its Q*T queries, so the memory's keys and values are projected once per sample."""
        S = mem.shape[0]; B, T = acts.shape
        se = symemb.repeat_interleave(Q, 0)
        x = self.embed(acts, args, se)
        causal = torch.triu(torch.ones(T, T, dtype=torch.bool), 1)
        for L in self.tf.layers:
            x = L.norm1(x + L.dropout1(L.self_attn(x, x, x, attn_mask=causal, need_weights=False)[0]))
            xq = x.reshape(S, Q * T, -1)
            c = L.multihead_attn(xq, mem, mem, key_padding_mask=~memmask, need_weights=False)[0]
            x = L.norm2(x + L.dropout2(c.reshape(B, T, -1)))
            x = L.norm3(x + L.dropout3(L.linear2(L.dropout(F.relu(L.linear1(x))))))
        y = x
        al = self.acth(y)
        pl = torch.einsum('btd,bkd->btk', self.pq(y), self.pk(se)) / math.sqrt(self.d)
        pl = pl.masked_fill(~symmask.repeat_interleave(Q, 0).unsqueeze(1), float('-inf'))
        vl = self.varh(y)
        return al, pl, vl

    def step_logits(self, acts, args, symemb, symmask, mem, memmask):
        x = self.embed(acts, args, symemb)
        T = acts.shape[1]
        causal = torch.triu(torch.ones(T, T, dtype=torch.bool), 1)
        y = self.tf(x, mem, tgt_mask=causal, memory_key_padding_mask=~memmask)
        al = self.acth(y)                                                # (B, T, 3)
        pl = torch.einsum('btd,bkd->btk', self.pq(y), self.pk(symemb)) / math.sqrt(self.d)
        pl = pl.masked_fill(~symmask.unsqueeze(1), float('-inf'))
        vl = self.varh(y)
        return al, pl, vl


def _proj(attn, x, i):
    d = attn.embed_dim
    return F.linear(x, attn.in_proj_weight[i * d:(i + 1) * d], attn.in_proj_bias[i * d:(i + 1) * d])


def _heads(x, h):
    B, T, d = x.shape
    return x.view(B, T, h, d // h).transpose(1, 2)


class IncDec:
    """Incremental decoding with a Dec's weights (nn.TransformerDecoderLayer, post-norm, eval):
    the self-attention keys and values of earlier positions are cached and the memory's keys and
    values are computed once for all sequences (one sample)."""
    def __init__(self, dec, mem):
        self.dec = dec; self.layers = dec.tf.layers
        self.h = self.layers[0].self_attn.num_heads
        self.mk = [_heads(_proj(L.multihead_attn, mem, 1), self.h) for L in self.layers]   # (1, h, N, dh)
        self.mv = [_heads(_proj(L.multihead_attn, mem, 2), self.h) for L in self.layers]
        self.K = [None] * len(self.layers); self.V = [None] * len(self.layers)

    @staticmethod
    def _att(q, k, v):
        w = torch.softmax(q @ k.transpose(-1, -2) / math.sqrt(q.shape[-1]), -1)
        o = w @ v                                                    # (B, h, 1, dh)
        return o.transpose(1, 2).reshape(o.shape[0], 1, -1)

    def step(self, x):
        """x: (B, 1, d) the embedded newest token; returns the last layer's output (B, 1, d)."""
        for i, L in enumerate(self.layers):
            sa = L.self_attn
            q = _heads(_proj(sa, x, 0), self.h)
            k = _heads(_proj(sa, x, 1), self.h); v = _heads(_proj(sa, x, 2), self.h)
            self.K[i] = k if self.K[i] is None else torch.cat([self.K[i], k], 2)
            self.V[i] = v if self.V[i] is None else torch.cat([self.V[i], v], 2)
            x = L.norm1(x + sa.out_proj(self._att(q, self.K[i], self.V[i])))
            ca = L.multihead_attn
            q = _heads(_proj(ca, x, 0), self.h)[:, :, 0].transpose(0, 1)       # (h, B, dh)
            w = torch.softmax(q @ self.mk[i][0].transpose(-1, -2) / math.sqrt(q.shape[-1]), -1)   # (h, B, N)
            o = (w @ self.mv[i][0]).transpose(0, 1).reshape(q.shape[1], 1, -1)  # (B, 1, d)
            x = L.norm2(x + ca.out_proj(o))
            x = L.norm3(x + L.linear2(F.relu(L.linear1(x))))
        return x


class Model(nn.Module):
    def __init__(self, d=64, layers=6, dlayers=2, nnames=64):
        super().__init__()
        self.enc = Enc(d, layers, nnames)
        self.dec = Dec(d, dlayers)

    def memories(self, G):
        """Per sample: memory (S, Nmax, d) + mask, symbol candidates (S, Kmax, d) + mask + key list."""
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
        return mem, mm, se, sm, keys


def encode_eq(l, r, keys):
    """Prefix (action, arg) sequence of l = r, or None if a symbol is not among KEYS."""
    kidx = {k: i for i, k in enumerate(keys)}
    seq = []; vs = {}
    def go(t):
        f, args = t
        if isvar(t):
            if f not in vs:
                vs[f] = len(vs)
            seq.append((A_VAR, min(vs[f], MAXV - 1)))
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


def masks_of(seq, keys):
    """Per step: may the action be EOS / must it be EOS, and the number of variable slots allowed."""
    out = []; open_ = 2; nv = 0
    for a, x in seq:
        out.append((open_ == 0, nv))
        if a == A_SYM:
            open_ += keys[x][1] - 1
        elif a == A_VAR:
            open_ -= 1; nv = max(nv, x + 1)
    return out


def batch_loss(model, G, targets, weights):
    """targets: per sample a list of sequences. Mean token loss, weighted per sample."""
    mem, mm, se, sm, keys = model.memories(G)
    if not any(targets):
        return None
    Q = max(len(qs) for qs in targets)
    rows = [(s, qs[i] if i < len(qs) else None) for s, qs in enumerate(targets) for i in range(Q)]
    T = max(len(q) for _, q in rows if q)
    B = len(rows)
    acts = torch.full((B, T), A_EOS, dtype=torch.long); args = torch.zeros((B, T), dtype=torch.long)
    tin_a = torch.full((B, T), A_EOS, dtype=torch.long); tin_x = torch.zeros((B, T), dtype=torch.long)
    valid = torch.zeros((B, T), dtype=torch.bool); forced = torch.zeros((B, T), dtype=torch.bool)
    vmax = torch.zeros((B, T), dtype=torch.long)
    sid = torch.tensor([s for s, _ in rows]); w = torch.tensor([weights[s] for s, _ in rows], dtype=torch.float32)
    for i, (s, q) in enumerate(rows):
        if q is None:   # padding (the sample has fewer targets): no loss
            w[i] = 0.0; continue
        ms = masks_of(q, keys[s])
        for t, ((a, x), (must_eos, nv)) in enumerate(zip(q, ms)):
            acts[i, t] = a; args[i, t] = x; valid[i, t] = True; forced[i, t] = must_eos
            vmax[i, t] = min(nv + 1, MAXV)
        tin_a[i, 0] = A_BOS
        for t in range(1, len(q)):
            tin_a[i, t] = q[t - 1][0]; tin_x[i, t] = q[t - 1][1]
    al, pl, vl = model.dec.grouped_logits(tin_a, tin_x, se, sm, mem, mm, Q)
    # actions (not where EOS is forced); EOS is not allowed while slots are open
    al = al.clone(); al[..., A_EOS - 1] = al[..., A_EOS - 1].masked_fill(~forced, float('-inf'))
    la = F.cross_entropy(al.reshape(-1, 3), (acts - 1).clamp(min=0).reshape(-1), reduction='none').reshape(B, T)
    la = torch.where(valid & ~forced, la, torch.zeros_like(la))
    lp = F.cross_entropy(pl.reshape(-1, pl.shape[-1]), args.reshape(-1).clamp(max=pl.shape[-1] - 1), reduction='none').reshape(B, T)
    lp = torch.where(valid & (acts == A_SYM), lp, torch.zeros_like(lp))
    vmask = torch.arange(MAXV).view(1, 1, -1) < vmax.unsqueeze(-1)
    vl = vl.masked_fill(~vmask, float('-inf'))
    lv = F.cross_entropy(vl.reshape(-1, MAXV), args.reshape(-1).clamp(max=MAXV - 1), reduction='none').reshape(B, T)
    lv = torch.where(valid & (acts == A_VAR), lv, torch.zeros_like(lv))
    tok = (la + lp + lv).sum(1) / valid.sum(1).clamp(min=1)
    return (tok * w).sum() / w.sum().clamp(min=1e-9)


@torch.no_grad()
def generate(model, G, s, n, temp=1.0, maxlen=48):
    """N sampled equations (as (l, r) strings) for sample S of G (incremental decoding)."""
    model.eval()
    mem, mm, se, sm, keys = model.memories(G)
    ks = keys[s]; K = len(ks); dec = model.dec
    m1 = mem[s:s + 1, :int(mm[s].sum())]
    sse = se[s:s + 1, :K]
    inc = IncDec(dec, m1)
    pk = dec.pk(sse)                                                    # (1, K, d)
    ar = torch.tensor([k[1] for k in ks])
    open_ = torch.full((n,), 2); nv = torch.zeros(n, dtype=torch.long); done = torch.zeros(n, dtype=torch.bool)
    a_prev = torch.full((n, 1), A_BOS, dtype=torch.long); x_prev = torch.zeros((n, 1), dtype=torch.long)
    out_a, out_x = [], []
    symb = sse.expand(n, -1, -1)
    for t in range(maxlen):
        y = inc.step(dec.embed(a_prev, x_prev, symb, start=t))[:, 0]        # (n, d)
        al = dec.acth(y) / temp
        pl = (dec.pq(y) @ pk[0].T) / math.sqrt(dec.d) / temp
        vl = dec.varh(y) / temp
        if t > maxlen - 12:   # too long: prefer variables, which close the open slots
            al[:, A_SYM - 1] -= 5
        a = torch.multinomial(F.softmax(al[:, :2], -1), 1).squeeze(1) + 1      # SYM or VAR
        a = torch.where(open_ == 0, torch.full_like(a, A_EOS), a)
        p = torch.multinomial(F.softmax(pl, -1), 1).squeeze(1)
        vmask = torch.arange(MAXV).unsqueeze(0) < (nv + 1).clamp(max=MAXV).unsqueeze(1)
        v = torch.multinomial(F.softmax(vl.masked_fill(~vmask, float('-inf')), -1), 1).squeeze(1)
        x = torch.where(a == A_SYM, p, torch.where(a == A_VAR, v, torch.zeros_like(p)))
        a = torch.where(done, torch.full_like(a, A_EOS), a)
        open_ = torch.where(a == A_SYM, open_ + ar[x.clamp(max=K - 1)] - 1, torch.where(a == A_VAR, open_ - 1, open_))
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
            f, k = ks[x]
            return f if k == 0 else f'{f}(' + ','.join(term() for _ in range(k)) + ')'
        try:
            l = term(); r = term()
        except IndexError:
            continue
        # a side that is a variable the other side lacks (X = t): true only in a trivial theory
        if l != r and not (l[0] == 'X' and '(' not in l and l not in TOKV.findall(r)) \
                and not (r[0] == 'X' and '(' not in r and r not in TOKV.findall(l)):
            res.append((l, r))
    model.train()
    return res


def sample_eqs(name, ax, rules, k, ctx):
    eqs = [(T_AX, l, r, 0, 0) for _, l, r in ax]
    eqs += [(T_GOAL, l, r, 0, 0) for l, r in goal_eqs(name)]
    eqs += [(T_CTX, l, r, 0, i) for i, (_, l, r) in enumerate(rules[max(0, k - ctx):k], max(0, k - ctx))]
    return eqs


def rows_from_out(out, name, path):
    """(axioms, rules) as load_log gives them, from a twee run's --print-given output (as
    loop.py writes the given logs of solved runs; every rule that is not an axiom is labelled 0)."""
    import given as givenlib, hintlib
    sig = hintlib.problem_signature(name)
    axk = set(givenlib.key(l, r, sig) for l, r in givenlib.axioms(name, path))
    ax, rules = [], []
    for x in givenlib.parse_given_parents(out):
        if x is None or x[0] == x[1]:
            continue
        k = givenlib.key(x[0], x[1], sig)
        if k in axk:
            ax.append((-1, k[0], k[1]))
        else:
            rules.append((0, k[0], k[1]))
    return ax, rules


def canon(l, r):
    """Variant key of an equation (variables renamed in order, both orientations)."""
    def key(a, b):
        ren = {}
        def go(t):
            f, args = t
            if isvar(t):
                ren.setdefault(f, f'X{len(ren)}'); return ren[f]
            return f if not args else f + '(' + ','.join(go(x) for x in args) + ')'
        return go(parse(a)) + '=' + go(parse(b))
    return min(key(l, r), key(r, l))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('given'); ap.add_argument('name', nargs='?')
    ap.add_argument('--test-names', default='')
    ap.add_argument('--save'); ap.add_argument('--load')
    ap.add_argument('--steps', type=int, default=6000)
    ap.add_argument('--dim', type=int, default=64)
    ap.add_argument('--layers', type=int, default=6)
    ap.add_argument('--dlayers', type=int, default=2)
    ap.add_argument('--ctx', type=int, default=256)
    ap.add_argument('--batch', type=int, default=4, help='samples (problems at a cut) per step')
    ap.add_argument('--targets', type=int, default=16, help='future proof rules per sample')
    ap.add_argument('--maxtok', type=int, default=48)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--hard', type=float, default=0.5)
    ap.add_argument('--threads', type=int, default=6)
    ap.add_argument('--eval-every', type=int, default=1000)
    ap.add_argument('--eval-n', type=int, default=40, help='test problems in the periodic evaluation')
    ap.add_argument('--n', type=int, default=100, help='samples per evaluated cut')
    ap.add_argument('--k', type=int, default=-1, help='hints: the cut (default: all rules as context)')
    ap.add_argument('--temp', type=float, default=1.0)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--cosine', type=int, default=1)
    ap.add_argument('--init-from', help='train: start from this checkpoint (model and vocabulary)')
    ap.add_argument('--step0', type=int, default=0, help='train: the checkpoint\'s step (for the log)')
    ap.add_argument('--pool-dir', help='eval: hints dir of a loop (the pools)')
    ap.add_argument('--problem', help='hints-out: the problem file the run had (its axioms)')
    ap.add_argument('--out', help='hints, hints-out: write the hints here (default stdout)')
    ap.add_argument('--drop-known', type=int, default=1, help='hints: leave out variants of the context rules')
    a = ap.parse_args()
    torch.set_num_threads(a.threads); random.seed(a.seed); torch.manual_seed(a.seed)

    if a.init_from and not a.load:
        a.load = a.init_from
    if a.load:
        ck = torch.load(a.load, weights_only=False)
        vocab = Vocab(); vocab.idx = ck['vocab']; vocab.frozen = True
        sa = ck['args']
        model = Model(sa['dim'], sa['layers'], sa['dlayers'])
        model.load_state_dict(ck['model'])
        if a.cmd == 'train':
            vocab.frozen = False
            a.dim, a.layers, a.dlayers = sa['dim'], sa['layers'], sa['dlayers']
    else:
        vocab = Vocab()
        model = Model(a.dim, a.layers, a.dlayers)

    if a.cmd in ('hints', 'hints-out'):
        vocab.frozen = True
        if a.cmd == 'hints':
            ax, rules = load_log(a.given)
        else:
            ax, rules = rows_from_out(open(a.given, errors='replace').read(), a.name, a.problem)
        k = len(rules) if a.k < 0 else a.k
        G = GGraph(vocab); G.add_sample(sample_eqs(a.name, ax, rules, k, a.ctx))
        have = {canon(l, r) for _, l, r in ax + rules[:k]} if a.drop_known else set()
        seen, out = set(), []
        for l, r in generate(model, G, 0, a.n, a.temp, a.maxtok):
            c = canon(l, r)
            if c not in seen and c not in have:
                seen.add(c); out.append(f'{l}\t{r}\n')
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

    pool_of = {}
    if a.pool_dir:
        # the hints of the other goals of each original (its pool, as --pool original; includes
        # later goals, so it overstates the pool a run had)
        byo = {}
        for f in os.listdir(a.pool_dir):
            byo.setdefault(f.rpartition('__goal_')[0], []).append(f)
        def pool_of(n):
            out = set()
            for f in byo.get(n.rpartition('__goal_')[0], []):
                if f != n:
                    for l in open(os.path.join(a.pool_dir, f)):
                        w = l.rstrip('\n').split('\t')
                        if len(w) >= 2:
                            out.add(canon(w[0], w[1]))
            return out

    def evaluate(names):
        """Recall of the future proof rules (variants) among --n samples, at the cut halfway
        through each proof (by proof rule), with the --ctx rules before it as context.
        With --pool-dir also the pool's recall and the generated hits the pool lacks."""
        rec, nh, tot = [], 0, 0
        pn = pg = 0; ng = 0; nl = 0
        for n in names:
            ax, rules = load_log(P[n])
            pr = [i for i, (lab, _, _) in enumerate(rules) if lab == 1]
            if len(pr) < 4:
                continue
            k = pr[len(pr) // 2]
            fut = {canon(l, r) for lab, l, r in rules[k:] if lab == 1}
            later = {canon(l, r) for lab, l, r in rules[k:]}
            G = GGraph(vocab); G.add_sample(sample_eqs(n, ax, rules, k, a.ctx))
            gen = {canon(l, r) for l, r in generate(model, G, 0, a.n, a.temp, a.maxtok)}
            hit = len(fut & gen)
            rec.append(hit / len(fut)); nh += hit; tot += len(fut); ng += len(gen); nl += len(later & gen)
            if a.pool_dir:
                pl = pool_of(n)
                pn += len(fut & pl); pg += len(fut & gen - pl)
        print(f'  generated: {ng / max(len(rec), 1):.0f} distinct per cut, {nl / max(ng, 1):.1%} of them derived later in the run', flush=True)
        if a.pool_dir:
            print(f'  pool: {pn}/{tot} future proof rules in the pool, generated and not in the pool {pg}; '
                  f'{ng / max(len(rec), 1):.0f} distinct generated per cut', flush=True)
        return (float(np.mean(rec)) if rec else 0.0), nh, tot, len(rec)

    if a.cmd == 'eval':
        vocab.frozen = True
        r, nh, tot, m = evaluate(test)
        print(f'eval: mean recall {r:.3f} ({nh}/{tot} future proof rules, {m} problems, n={a.n})')
        return

    # train
    sizes = {n: os.path.getsize(P[n]) for n in train}
    W = np.array([max(sizes[n], 1) ** a.hard for n in train]); W /= W.sum()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    cache = {}
    def get(n):
        if n not in cache:
            if len(cache) > 3000:
                cache.pop(next(iter(cache)))
            cache[n] = load_log(P[n])
        return cache[n]
    t0 = time.time(); run = []
    nparam = sum(p.numel() for p in model.parameters())
    print(f'train: {len(train)} logs, test {len(test)}, {nparam} parameters', flush=True)
    for step in range(1, a.steps + 1):
        G = GGraph(vocab); targets = []; weights = []
        tries = 0
        while len(targets) < a.batch and tries < 50:
            tries += 1
            n = train[np.random.choice(len(train), p=W)]
            ax, rules = get(n)
            pr = [i for i, (lab, _, _) in enumerate(rules) if lab == 1]
            if len(pr) < 2:
                continue
            # cut: just before a proof rule, later ones likelier (index + 1 weights)
            w_ = np.array([i + 1.0 for i in pr]); j = np.random.choice(len(pr), p=w_ / w_.sum())
            k = pr[j]
            s = G.add_sample(sample_eqs(n, ax, rules, k, a.ctx))
            keys = sorted(G.symlists[s])
            fut = [rules[i] for i in pr[j:]]
            random.shuffle(fut)
            qs = []
            for _, l, r in fut:
                q = encode_eq(l, r, keys) if random.random() < 0.5 else encode_eq(r, l, keys)
                if q and len(q) <= a.maxtok:
                    qs.append(q)
                if len(qs) >= a.targets:
                    break
            targets.append(qs); weights.append(1.0)
        loss = batch_loss(model, G, targets, weights)
        if loss is None:
            continue
        if a.cosine:   # cosine decay to a tenth of --lr
            for g in opt.param_groups:
                g['lr'] = a.lr * (0.1 + 0.45 * (1 + math.cos(math.pi * step / a.steps)))
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); run.append(loss.item())
        if step % 100 == 0 or step in (1, 10):
            print(f'step {step + a.step0} loss {np.mean(run[-100:]):.4f} {time.time()-t0:.0f}s (vocab {len(vocab.idx)})', flush=True)
        if a.save and (step % a.eval_every == 0 or step == a.steps):
            torch.save({'model': model.state_dict(), 'vocab': vocab.idx, 'args': vars(a)}, a.save)
            if test:
                r, nh, tot, m = evaluate(test[:a.eval_n])
                print(f'  eval step {step + a.step0}: mean recall {r:.3f} ({nh}/{tot} future proof rules, {m} problems, n={a.n})', flush=True)


if __name__ == '__main__':
    main()

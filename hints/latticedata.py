#!/usr/bin/env python3
"""Training rows for a policy over the climb's lattice moves (15 Nov; the user: learn the up/down steps,
randomized guidance, "what are the best steps in the lattice given a problem").

One row per sketch run of climb.py (climb.tsv), from climb directories that save their sketch proofs
(sketches/<target>/<tag>, climb.py 57a0b00):

  features  the target: goal size, variables, the original's axioms and number of stronger theories;
            the move: assumptions by kind (siblings, kNN goals, theory axioms, theory lemmas, laws,
            generated), the theories involved and their rank, the weakened goal (none, merge, unit),
            the climb step (how many runs on the target before it)
  labels    proved; nontrivial (proved, used an assumption, >= MIN proof steps);
            credit: the share of the target's real proof (hints/<target>, if it was proved) that is
            in the sketch's proof, as canonical pairs

    latticedata.py DIR [DIR ...] --out rows.tsv
"""
import argparse, collections, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintsel, lemmas

VAR = re.compile(r'\bX\d+\b')


def canon(l, r):
    def key(x):
        ren = {}
        return VAR.sub(lambda m: ren.setdefault(m.group(0), f'V{len(ren)}'), x)
    return min(key(l + '=' + r), key(r + '=' + l))


def kind(x):
    if x.startswith('goal_'):
        return 'sib'
    if x.startswith('knn_'):
        return 'knn'
    if x.startswith('law_'):
        return 'law'
    if x.startswith('gen_'):
        return 'gen'
    if x.startswith('thy_'):
        return 'thylem' if '_lem' in x else 'thyax'
    return 'other'


_nthy = {}
def n_theories(t):
    """Stronger theories of T's original (axiom sets of other originals that strictly contain its own)."""
    o = lemmas.split(t)[0]
    if o not in _nthy:
        if not _nthy:
            rep = {}
            for f in sorted(os.listdir(lemmas.PROB)):
                rep.setdefault(f.rpartition('__goal_')[0], f[:-2])
            _nthy['__rep'] = {p: lemmas.axiom_set(n) for p, n in rep.items()}
        A = _nthy['__rep'].get(o) or lemmas.axiom_set(t)
        _nthy[o] = (len(A), len({B for B in _nthy['__rep'].values() if A < B}))
    return _nthy[o]


def goal_shape(t):
    try:
        lits = hintsel.goal_lits(t)
    except Exception:
        return 0, 0, 0
    s = ' '.join(l + ' ' + r for _, l, r in lits)
    return len(re.findall(r'[a-z]\w*\(', s)) + len(re.findall(r'\b[a-z]\w*\b(?!\()', s)), \
        len(set(VAR.findall(s))), len(lits)


def rows_of(d, min_steps):
    real = {}
    for l in open(os.path.join(d, 'climb.tsv')):
        w = l.rstrip('\n').split('\t')
        if len(w) > 3 and w[1] in ('final', 'direct') and w[3] == 'THM':
            real[w[0]] = True
    step = collections.Counter()
    for l in open(os.path.join(d, 'climb.tsv')):
        w = l.rstrip('\n').split('\t')
        if len(w) < 8 or w[1] in ('final', 'direct', 'chain') or w[1].endswith(':weak'):
            continue
        t, tag, ok = w[0], w[1], w[3] == 'THM'
        S = [x for x in w[6].split(',') if x]
        U = {x for x in w[7].split(',') if x}
        sp = os.path.join(d, 'sketches', t, tag)
        proof, goal = [], ''
        if os.path.exists(sp):
            for x in open(sp):
                if x.startswith('# goal='):
                    goal = x[7:].strip()
                elif not x.startswith('#') and '\t' in x:
                    a, b = x.rstrip('\n').split('\t')[:2]
                    proof.append(canon(a, b))
        weak = 'none' if not goal else ('unit' if re.search(r'\be\b', goal) and
                                        len(VAR.findall(goal)) < goal_shape(t)[1] else 'merge')
        ks = collections.Counter(kind(x) for x in S)
        thys = sorted({int(x.split('_')[1]) for x in S if x.startswith('thy_')})
        credit = ''
        hp = os.path.join(d, 'hints', t)
        if real.get(t) and os.path.exists(hp) and ok and os.path.exists(sp):
            rp = {canon(*x.rstrip('\n').split('\t')[:2]) for x in open(hp) if '\t' in x}
            credit = f'{len(rp & set(proof)) / max(1, len(rp)):.3f}'
        size, nv, nl = goal_shape(t)
        nax, nthy = n_theories(t)
        yield {
            'dir': os.path.basename(d.rstrip('/')), 'target': t, 'tag': tag, 'step': step[t],
            'goal_size': size, 'goal_vars': nv, 'goal_lits': nl, 'axioms': nax, 'theories': nthy,
            'n_assume': len(S), 'n_sib': ks['sib'], 'n_knn': ks['knn'], 'n_thyax': ks['thyax'],
            'n_thylem': ks['thylem'], 'n_law': ks['law'], 'n_gen': ks['gen'],
            'n_thy': len(thys), 'thy_rank': thys[0] if thys else -1, 'weak': weak,
            'proved': int(ok), 'used': len(U), 'steps': len(proof),
            'nontrivial': int(ok and bool(U) and len(proof) >= min_steps) if os.path.exists(sp) or not ok else '',
            'credit': credit,
            'target_proved': int(bool(real.get(t))),
        }
        step[t] += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--min-steps', type=int, default=30)
    a = ap.parse_args()
    n = 0
    with open(a.out, 'w') as f:
        cols = None
        for d in a.dirs:
            if not os.path.exists(os.path.join(d, 'climb.tsv')):
                continue
            for r in rows_of(d, a.min_steps):
                if cols is None:
                    cols = list(r); f.write('\t'.join(cols) + '\n')
                f.write('\t'.join(str(r[k]) for k in cols) + '\n'); n += 1
    print(f'{n} moves -> {a.out}')


if __name__ == '__main__':
    main()

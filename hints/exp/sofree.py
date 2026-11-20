#!/usr/bin/env python3
"""(20 Nov) The same statement proven in a theory with more axioms (REPORT 2ar, 16 Nov), redone on production now.

transfer.py find --same-other lists unsolved goals whose statement is a proven goal of an original whose axioms are
not within theirs. On 16 Nov 90% of such source proofs had a missing axiom as a step; the 323 that did not gave 13
proofs at about 4-5 per CPU h. This keeps the candidates whose first source proof has none of the missing axioms
among its steps (canonical keys, both orientations), minus the goals the 16 Nov runs tried (loops/SOF, SOP, SOR).

  sofree.py OUT.tsv      (goal, source, missing-axiom count: transfer.py run's input)
"""
import os, re, sys
sys.path.insert(0, '/project/twee/hints')
import lemmas, transfer

L = '/project/hintwork/loops'


def akey(body):
    # a TPTP axiom body 'l=r' (top level) -> canonical key, or None
    if '!=' in body:
        return None
    depth = 0
    for i, c in enumerate(body):
        depth += c == '('
        depth -= c == ')'
        if c == '=' and depth == 0:
            return transfer.key(body[:i], body[i + 1:])
    return None


def candidates(tmp, tried=(), tried_pairs=(), dst='UL', allp='/project/hintwork/sets/all'):
    """find --same-other into TMP, then the free candidates (no missing axiom as a step of the first source proof),
    minus goals in TRIED and (goal, first source) pairs in TRIED_PAIRS: (lines, number of candidates)"""
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        transfer.find_same_other(os.path.join(L, dst), tmp, allp)
    keep = []; n = 0
    for l in open(tmp):
        w = l.rstrip('\n').split('\t')
        g, srcs = w[0], w[1].split(',')
        n += 1
        if g in tried or (g, srcs[0]) in tried_pairs:
            continue
        f = srcs[0]
        miss = lemmas.axiom_set(f) - lemmas.axiom_set(g)
        mk = {k for k in (akey(b) for b in miss) if k}
        if len(mk) < len(miss):
            continue   # (a missing axiom that is not a plain equation: skip)
        steps = set()
        for x in open(os.path.join(L, dst, 'hints', f)):
            v = x.rstrip('\n').split('\t')
            if len(v) >= 2:
                steps.add(transfer.key(v[0], v[1]))
        if not (mk & steps):
            keep.append(l if l.endswith('\n') else l + '\n')
    return keep, n


def main():
    out = sys.argv[1]
    tried = set()
    for d in ('SOF', 'SOP', 'SOR'):
        p = os.path.join(L, d, 'transfer.tsv')
        if os.path.exists(p):
            tried |= {l.split('\t')[0] for l in open(p)}
    keep, n = candidates(out + '.all', tried)
    open(out, 'w').writelines(keep)
    print(f'{n} same-statement candidates, {len(tried)} tried on 16 Nov, {len(keep)} with no missing axiom as a '
          f'step of the first source proof -> {out}')


if __name__ == '__main__':
    main()

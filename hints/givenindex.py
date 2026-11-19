#!/usr/bin/env python3
"""(19 Nov) Index every given-rule log under LOOPS/*/given: name, directory, bytes, positives, negatives, mtime.
Goals have several proofs (A/B arms, from-zero runs, production), as in Mizar60 (Jakubuv et al., ITP 2023, 6.4),
where training takes up to 6 random proofs per problem, or the shortest, the longest and a medium one.

givenindex.py LOOPS OUT.tsv [-j 4]
"""
import os, sys
from multiprocessing import Pool

def count(p):
    try:
        with open(p, 'rb') as f:
            b = f.read()
        st = os.stat(p)
    except OSError:
        return None
    pos = b.count(b'\n1\t') + b.startswith(b'1\t')
    neg = b.count(b'\n0\t') + b.startswith(b'0\t')
    return pos, neg, st.st_size, int(st.st_mtime)

def job(d):
    out = []
    g = os.path.join(d, 'given')
    for n in os.listdir(g):
        r = count(os.path.join(g, n))
        if r and r[0] > 0:
            out.append(f'{n}\t{os.path.basename(d)}\t{r[2]}\t{r[0]}\t{r[1]}\t{r[3]}\n')
    return d, out

def main():
    loops, outp = sys.argv[1], sys.argv[2]
    j = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 4
    ds = sorted(os.path.join(loops, d) for d in os.listdir(loops)
                if os.path.isdir(os.path.join(loops, d, 'given')) and not os.path.islink(os.path.join(loops, d, 'given')))
    with open(outp + '.tmp', 'w') as f, Pool(j) as P:
        for k, (d, out) in enumerate(P.imap_unordered(job, ds)):
            f.writelines(out); f.flush()
            print(k + 1, len(ds), os.path.basename(d), len(out), flush=True)
    os.replace(outp + '.tmp', outp)

if __name__ == '__main__':
    main()

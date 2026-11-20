#!/usr/bin/env python3
"""(20 Nov 16:50) A loop's runs by time window and label: proofs / runs and run hours (notes/2026-11-20-z6.md).

Reads DIR/r*/results.tsv; a row's time is its t=<seconds since the loop's start> field. Labels: L<k> (cascade
levels), V*@0 and V* (5 s and 80 s variants, pooled), others as they are.

  windows.py DIR [--win 1800] [--pool]     (--pool: variants pooled into V@0 and V)
"""
import collections, glob, re, sys


def main():
    a = sys.argv[1:]
    d = a[0]
    win = int(a[a.index('--win') + 1]) if '--win' in a else 1800
    pool = '--pool' in a
    W = collections.defaultdict(collections.Counter)
    for p in sorted(glob.glob(f'{d}/r*/results.tsv')):
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) < 5:
                continue
            m = re.search(r'\bt=(\d+)', l)
            if not m:
                continue
            h = int(m.group(1)) // win
            lab = w[4]
            if pool and lab.startswith('V'):
                lab = 'V@0' if lab.endswith('@0') else 'V'
            c = W[h]
            c[(lab, 'n')] += 1
            c[(lab, 'thm')] += w[1] == 'THM'
            try:
                c[(lab, 's')] += float(w[2])
            except ValueError:
                pass
    for h in sorted(W):
        c = W[h]
        labs = sorted({k[0] for k in c})
        m0, m1 = h * win // 60, (h + 1) * win // 60
        print(f'{m0:>4}-{m1:<4} min: ' + '; '.join(
            f'{lb} {c[(lb, "thm")]}/{c[(lb, "n")]} {c[(lb, "s")] / 3600:.1f}h' for lb in labs))


if __name__ == '__main__':
    main()

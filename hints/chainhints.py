#!/usr/bin/env python3
"""Chain sketch hints along an original's proof.

A sketch of goal N assumes nearby sibling goals; its proof covers only the
stretch from them to N. The sketches of those siblings cover the stretches
before. So the hints for N are the sketch hints of N and of the sketched
siblings with numbers in [N - W, N), nearest first, at most MAX.

chainhints.py SKETCH_HINTS_DIR NAMES OUTDIR [-w W] [--max MAX]
"""
import argparse, collections, os

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('skdir'); ap.add_argument('names'); ap.add_argument('outdir')
    ap.add_argument('-w', type=int, default=30)
    ap.add_argument('--max', type=int, default=400)
    a = ap.parse_args()
    by = collections.defaultdict(dict)
    for f in os.listdir(a.skdir):
        o, k = f.rsplit('__goal_', 1)
        by[o][int(k)] = [l.rstrip('\n') for l in open(os.path.join(a.skdir, f)) if '\t' in l]
    os.makedirs(a.outdir, exist_ok=True)
    sizes = []
    for line in open(a.names):
        name = line.split()[0]
        o, k = name.rsplit('__goal_', 1); k = int(k)
        seen, hs = set(), []
        for j in sorted((j for j in by[o] if k - a.w <= j <= k), key=lambda j: -j):
            for h in by[o][j]:
                if h not in seen and len(hs) < a.max:
                    seen.add(h); hs.append(h)
        if hs:
            with open(os.path.join(a.outdir, name), 'w') as f:
                f.write('\n'.join(hs) + '\n')
            sizes.append(len(hs))
    print('hint files', len(sizes), 'mean size', sum(sizes) / max(1, len(sizes)))

if __name__ == '__main__':
    main()

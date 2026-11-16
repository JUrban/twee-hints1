#!/usr/bin/env python3
"""The live climber's A/B arms (climb.py --move-ab on crc32 bit 0, --theory-ts-ab on bit 1).

  climbab.py DIR LOG [--after N]

Climbs are the LOG's result lines ('<target> THM|NO sketch-runs=...') after its N-th from last start
(a line '--theory-ts: ...', default the last start); CPU is the sum of the target's climb.tsv run times.
Per arm: climbs, proofs, CPU hours, proofs per CPU hour, and Fisher's exact test on proofs per climb.
"""
import argparse, collections, math, os, re, zlib


def fisher(a, b, c, d):
    """two-sided Fisher exact p for [[a, b], [c, d]]"""
    n = a + b + c + d; r1 = a + b; c1 = a + c
    def p(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if p(x) <= p0 * (1 + 1e-9)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('log')
    ap.add_argument('--after', type=int, default=1, help='count the climbs after the N-th from last start')
    ap.add_argument('--by-original', action='store_true', help='arms by the original\'s crc32 (climb.py since 16 Nov 03:10)')
    a = ap.parse_args()
    lines = open(a.log).read().splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith('--theory-ts:')]
    i0 = starts[-a.after] if len(starts) >= a.after else 0
    res = {}
    for l in lines[i0:]:
        m = re.match(r'(\S+) (THM|NO) sketch-runs=', l)
        if m:
            res[m.group(1)] = m.group(2) == 'THM'
    cpu = collections.Counter()
    for l in open(os.path.join(a.dir, 'climb.tsv')):
        w = l.rstrip('\n').split('\t')
        if len(w) > 5 and w[0] in res:
            try:
                cpu[w[0]] += float(w[5])
            except ValueError:
                pass
    print(f'{len(res)} climbs after start {a.after} from last (log line {i0})')
    for bit, name in ((0, 'move policy'), (1, 'theory TS')):
        arms = {}
        for v in (1, 0):
            ts = [t for t in res if (zlib.crc32((t.rsplit('__goal_', 1)[0] if a.by_original else t).encode()) >> bit) % 2 == v]
            p = sum(res[t] for t in ts); h = sum(cpu[t] for t in ts) / 3600
            os_ = {t.rsplit('__goal_', 1)[0] for t in ts}; op = {t.rsplit('__goal_', 1)[0] for t in ts if res[t]}
            arms[v] = (len(ts), p)
            print(f'  {name:12s} {"on " if v else "off"}: {len(ts):4d} climbs, {p:3d} proofs, {h:6.2f} CPU h, '
                  f'{p / h if h else 0:5.2f} proofs/CPU h; originals {len(op)}/{len(os_)} with a proof')
        (n1, p1), (n0, p0) = arms[1], arms[0]
        print(f'  {name:12s} Fisher p (proofs per climb) = {fisher(p1, n1 - p1, p0, n0 - p0):.3f}')


if __name__ == '__main__':
    main()

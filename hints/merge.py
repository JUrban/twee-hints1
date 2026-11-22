"""Merge the proofs of probe and climb dirs into a loop dir (e.g. loops/UL).

  python3 merge.py DST SRC... [--round R] [--given] [--dry]

For each SRC row of solved.tsv from round >= 1 (rows of round 0 are what SRC
imported with --init) whose goal DST has not solved: append NAME, R, TIME to
DST/solved.tsv and copy SRC/hints/NAME, and SRC's kept output of NAME (r*/out or out) into DST/out/NAME (the
record exp/trust.py needs). With --given also SRC/given/NAME (not
for climb.py dirs: their given logs may be of a sketch run with assumptions).
A running loop sees the merged proofs at its next restart (it reads
solved.tsv at start); its own later proof of a merged goal only adds a row.
"""
import argparse, glob, os, shutil


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dst'); ap.add_argument('src', nargs='+')
    ap.add_argument('--round', type=int, default=None, help='round of the merged rows (default: DST\'s last)')
    ap.add_argument('--given', action='store_true')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    have, last = set(), 0
    for l in open(os.path.join(a.dst, 'solved.tsv')):
        w = l.split('\t')
        have.add(w[0]); last = max(last, int(w[1]))
    R = last if a.round is None else a.round
    rows = []
    for s in a.src:
        for l in open(os.path.join(s, 'solved.tsv')):
            w = l.rstrip('\n').split('\t')
            n = w[0]
            if int(w[1]) < 1 or n in have:
                continue
            h = os.path.join(s, 'hints', n)
            if not os.path.exists(h) or os.path.getsize(h) == 0:
                print(f'skip {n} ({s}): no hints file')
                continue
            have.add(n); rows.append((n, s, w[2] if len(w) > 2 else '0'))
    for n, s, t in rows:
        print(f'merge {n} from {s}')
        if a.dry:
            continue
        shutil.copy(os.path.join(s, 'hints', n), os.path.join(a.dst, 'hints', n))
        g = os.path.join(s, 'given', n)
        if a.given and os.path.exists(g):
            shutil.copy(g, os.path.join(a.dst, 'given', n))
        # (22 Nov 00:30) the proof's kept twee output (its USEDAXIOMS record) into DST/out/, where exp/trust.py reads
        # it as DST's own; trust.py skips from-zero dirs (Z7, P2*, ...), so a goal merged from one had no record
        outs = sorted(glob.glob(os.path.join(s, 'r*', 'out', n)), key=lambda p: int(p.split(os.sep)[-3][1:])
                      if p.split(os.sep)[-3][1:].isdigit() else -1) + glob.glob(os.path.join(s, 'out', n))
        if outs:
            os.makedirs(os.path.join(a.dst, 'out'), exist_ok=True)
            shutil.copy(outs[-1], os.path.join(a.dst, 'out', n))
        with open(os.path.join(a.dst, 'solved.tsv'), 'a') as f:
            f.write(f'{n}\t{R}\t{t}\n')
    print(f'{len(rows)} merged into {a.dst} (round {R})' + (' [dry]' if a.dry else ''))


if __name__ == '__main__':
    main()

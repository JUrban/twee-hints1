"""dtcmp.py DIR... [--from K --to M]: per loop dir, the wall seconds of its runs by level and result, over
results.tsv rows K..M (median and mean), and the runs per hour of loop time."""
import sys, statistics
args = sys.argv[1:]; lo, hi = 0, None
if '--from' in args:
    i = args.index('--from'); lo = int(args[i + 1]); del args[i:i + 2]
if '--to' in args:
    i = args.index('--to'); hi = int(args[i + 1]); del args[i:i + 2]
for d in args:
    rows = [l.rstrip('\n').split('\t') for l in open(f'/project/hintwork/loops/{d}/r1/results.tsv')][lo:hi]
    out = []
    for lev in ('L0', 'L1', 'L2'):
        for res in ('THM', 'NO'):
            v = [float(f[2]) for f in rows if len(f) > 4 and f[4] == lev and f[1] == res]
            if v:
                out.append(f'{lev} {res} n={len(v)} med {statistics.median(v):.2f} mean {statistics.mean(v):.2f}')
    t = [int(f[5][2:]) for f in rows if len(f) > 5 and f[5].startswith('t=')]
    span = (max(t) - min(t)) if t else 0
    print(d, f'rows {lo}-{lo + len(rows)}', f'span {span}s', f'{len(rows) / max(1, span) * 3600:.0f} runs/h', '|', '; '.join(out))

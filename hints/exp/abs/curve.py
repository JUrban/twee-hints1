"""curve.py ARM... [--at M,...]: proofs by minutes after the loop's start (proof-file mtimes against config.json)."""
import os, sys
at = [4, 10, 15]
args = sys.argv[1:]
if '--at' in args:
    i = args.index('--at'); at = [float(x) for x in args[i + 1].split(',')]; args = args[:i] + args[i + 2:]
for d in args:
    t0 = os.stat(f'loops/{d}/config.json').st_mtime
    ts = [os.stat(f'loops/{d}/hints/' + g).st_mtime - t0 for g in os.listdir(f'loops/{d}/hints')]
    print(d, len(ts), ' '.join(f'{m:g}m:{sum(1 for t in ts if t <= m * 60)}' for m in at))

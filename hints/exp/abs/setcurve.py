"""setcurve.py SET ARM... [--at M,...]: the SET's goals proved by minutes after the loop's start (proof-file mtimes
against config.json; context proofs of other goals are left out)."""
import os, sys
args = sys.argv[1:]; at = [1, 4, 10, 25, 40, 60]
if '--at' in args:
    i = args.index('--at'); at = [float(x) for x in args[i + 1].split(',')]; args = args[:i] + args[i + 2:]
G = {l.strip() for l in open(args[0]) if l.strip()}
for d in args[1:]:
    t0 = os.stat(f'loops/{d}/config.json').st_mtime
    ts = [os.stat(f'loops/{d}/hints/' + g).st_mtime - t0 for g in os.listdir(f'loops/{d}/hints') if g in G]
    print(d, len(ts), ' '.join(f'{m:g}m:{sum(1 for t in ts if t <= m * 60)}' for m in at))

import os, re, sys, datetime as dt
for z in sys.argv[1:]:
    t0 = os.stat(f'loops/{z}/config.json').st_mtime
    d0 = dt.datetime.fromtimestamp(t0)
    for kind in ('xfer', 'gml'):
        tot = {60: 0, 120: 0, 240: 0, 480: 0}; cur = 0
        for line in open(f'loops/{z}.{kind}.log', errors='replace'):
            m = re.search(r'(\d\d):(\d\d):(\d\d)', line)
            if m and (line.startswith('cycle') or line.startswith('live')):
                t = d0.replace(hour=int(m[1]), minute=int(m[2]), second=int(m[3]))
                if t < d0 - dt.timedelta(minutes=5): t += dt.timedelta(days=1)
                cur = (t - d0).total_seconds() / 60
            m = re.match(r'transfer: (\d+)/(\d+)', line)
            if m:
                for k in tot:
                    if cur <= k: tot[k] += int(m[1])
        print(z, kind, 'proved by minute', ' '.join(f'{k}:{v}' for k, v in tot.items()))

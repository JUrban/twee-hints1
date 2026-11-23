"""triglag.py LOOP [--from MIN] [--names sets/all]: for the loop's main-loop proofs found at MIN minutes or later after
one or more failed runs, the latest proof time of the lemma goals the proof uses (its trigger), and how long after the
trigger and after how many failed runs on the goal the proving run came; for a goal's first run, how long after
the trigger it came (the goal was ready, as far as its proof's lemmas go). Proof times: the first THM row's t= in
r1/results.tsv, or else the hints file's mtime against config.json."""
import os, re, sys, collections, statistics as st
a = sys.argv[1:]; L = '/project/hintwork/loops'
def opt(k, d):
    global a
    if k in a:
        i = a.index(k); v = a[i + 1]; a = a[:i] + a[i + 2:]; return v
    return d
frm = float(opt('--from', '120')) * 60; names = opt('--names', '/project/hintwork/sets/all')
D = f'{L}/{a[0]}'; G = {l.strip() for l in open(names) if l.strip()}
t0 = os.stat(f'{D}/config.json').st_mtime
pt = {}
for g in os.listdir(f'{D}/hints'):
    pt[g] = os.stat(f'{D}/hints/{g}').st_mtime - t0
rows = collections.defaultdict(list)
for l in open(f'{D}/r1/results.tsv'):
    f = l.rstrip('\n').split('\t')
    t = next((float(x[2:]) for x in f if x.startswith('t=')), None)
    if t is None: continue
    rows[f[0]].append((t, f[1], f[4]))
for g, r in rows.items():
    th = [t for t, s, _ in r if s == 'THM']
    if th: pt[g] = min(pt.get(g, 1e18), th[0])
ax = re.compile(r'^Axiom \d+ \(([^)]*)\)')
def used(g):
    p = f'{D}/proofs/{g}'
    if not os.path.exists(p): return None
    u = set()
    for l in open(p, errors='replace'):
        m = ax.match(l)
        if not m or m[1] in ('sos', 'goals'): continue
        n = m[1]; parts = n.split('_')
        for i in range(1, len(parts)):
            s = '_'.join(parts[i:])
            if s in G: u.add(s); break
    return u
cat = collections.Counter(); sub = collections.Counter(); lag = collections.defaultdict(list); nf = collections.defaultdict(list); hrs = collections.defaultdict(list)
for g, r in rows.items():
    ok = [(t, lab) for t, s, lab in r if s == 'THM']
    if not ok or ok[0][0] < frm: continue
    ts, lab = ok[0]
    fails = [t for t, s, _ in r if s != 'THM' and t < ts]
    u = used(g)
    if not fails:
        cat['no earlier failure'] += 1
        ut = [pt[x] for x in (u or ()) if x in pt and x != g]
        if ut: lag['first run, after its trigger'].append(ts - max(ut))
        else: sub['no proved-goal lemma or no proof file'] += 1
        continue
    if u is None: cat['no proof file'] += 1; continue
    ut = [pt[x] for x in u if x in pt and x != g]
    if not ut: cat['uses no proved-goal lemma'] += 1; continue
    tt = max(ut); pf = max(fails)
    if tt <= pf:
        cat['every used lemma proved before the last failure'] += 1
        hrs['old'].append(ts)
        continue
    cat['a used lemma proved after the last failure'] += 1
    lag[lab].append(ts - tt); lag['all'].append(ts - tt); nf['all'].append(sum(1 for t in fails if t >= tt))
    hrs['new'].append(ts)
print(a[0], f'proofs at {frm/60:g} min or later:', sum(cat.values()))
for k, v in cat.most_common(): print(f'  {k}: {v}')
for k, v in sub.items(): print(f'    of those with no earlier failure, {k}: {v}')
def q(v): 
    v = sorted(v); return '/'.join(f'{v[int(p*(len(v)-1))]/60:.0f}' for p in (0.1, 0.25, 0.5, 0.75, 0.9))
for k, v in sorted(lag.items(), key=lambda x: -len(x[1])):
    print(f'  lag after the trigger, minutes, deciles 10/25/50/75/90 ({k}, {len(v)}): {q(v)}')
c = collections.Counter(min(x, 3) for x in nf['all'])
print('  failed runs on the goal between the trigger and the proof: 0:', c[0], '1:', c[1], '2:', c[2], '3+:', c[3])
for k in ('new', 'old'):
    h = collections.Counter(int(t // 3600) for t in hrs[k]); print(f'  by hour of the proof ({k}):', ' '.join(f'{x}:{h[x]}' for x in sorted(h)))

import os, sys, collections
base = '/project/hintwork/loops'
arms = sys.argv[1:] or ['BRS', 'BRSn', 'BP9', 'BBL']
sets = {}
for a in arms:
    d = os.path.join(base, a)
    if not os.path.exists(os.path.join(d, 'solved.tsv')):
        continue
    sol = {}
    for l in open(os.path.join(d, 'solved.tsv')):
        f = l.split('\t')
        if f[1] != '0':
            sol[f[0]] = int(f[1])
    rounds = sorted(x for x in os.listdir(d) if x.startswith('r') and x[1:].isdigit())
    wall = 0.0; runs = 0; per = []
    for r in rounds:
        rf = os.path.join(d, r, 'results.tsv')
        w = 0.0; n = 0
        for l in open(rf):
            f = l.split('\t'); w += float(f[2]); n += 1
        wall += w; runs += n
        per.append(f'{r}: {sum(1 for v in sol.values() if v <= int(r[1:]))} ({n} runs, {w/3600:.2f} h)')
    sets[a] = set(sol)
    print(f'{a:5s} solved {len(sol):3d}  wall-sum {wall/3600:.2f} h  runs {runs}  | ' + ' | '.join(per))
u = set().union(*sets.values()) if sets else set()
print('union', len(u))
for a in sets:
    print(a, 'only:', len(sets[a] - set().union(*(sets[b] for b in sets if b != a))))

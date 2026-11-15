import os, re, sys, collections
d = sys.argv[1]
od = os.path.join(d, 'r1', 'out')
dist = collections.Counter(); knn = collections.Counter(); nprf = 0; nlem = []; noax = 0
rank = collections.Counter()   # rank of a used sibling lemma among offered siblings (by distance)
for n in sorted(os.listdir(od)):
    t = open(os.path.join(od, n)).read()
    m = re.search(r'^USEDAXIOMS(.*)$', t, re.M)
    if not m:
        continue
    nprf += 1
    used = m.group(1).split()
    k = int(n.rsplit('__goal_', 1)[1])
    js = [int(x.split('_')[-1]) for x in used if x.startswith('lemma_goal_')]
    ks = [x for x in used if x.startswith('lemma_knn_')]
    nlem.append(len(js) + len(ks))
    for j in js:
        dist[(k - j)] += 1
    for x in ks:
        knn[int(x.split('_')[-1])] += 1
print('proofs', nprf, 'mean lemmas used', sum(nlem) / max(1, nprf), 'proofs using none', sum(1 for x in nlem if x == 0))
print('sibling distance k-j:', sorted(dist.items()))
b = collections.Counter()
for dd, c in dist.items():
    a = abs(dd); b['1-3' if a <= 3 else '4-6' if a <= 6 else '7-10' if a <= 10 else '11+'] += c
print('by |distance|', dict(b), 'before', sum(c for dd, c in dist.items() if dd > 0), 'after', sum(c for dd, c in dist.items() if dd < 0))
print('knn ranks used', sorted(knn.items()))
# usage rate by distance band: offered = the 20 nearest solved siblings (unit equations) of the snapshot
sys.path.insert(0, '/project/twee/hints')
import lemmas
solved = lemmas.by_original([l.split('\t')[0] for l in open('/project/hintwork/loops/ULsI/solved.tsv')])
off = collections.Counter(); usedb = collections.Counter()
band = lambda a: '1-3' if a <= 3 else '4-6' if a <= 6 else '7-10' if a <= 10 else '11+'
for n in sorted(os.listdir(od)):
    t = open(os.path.join(od, n)).read()
    m = re.search(r'^USEDAXIOMS(.*)$', t, re.M)
    if not m:
        continue
    k = int(n.rsplit('__goal_', 1)[1])
    txt, _ = lemmas.lemma_problem(n, solved, 20, True)
    offered = [int(j) for j in re.findall(r'fof\(lemma_goal_(\d+),', txt)]
    used = set(int(x.split('_')[-1]) for x in m.group(1).split() if x.startswith('lemma_goal_'))
    for j in offered:
        s = ('before ' if j < k else 'after ') + band(abs(k - j))
        off[s] += 1
        if j in used:
            usedb[s] += 1
for s in sorted(off):
    print(f'{s:14s} offered {off[s]:5d} used {usedb[s]:4d} rate {usedb[s]/off[s]:.2f}')

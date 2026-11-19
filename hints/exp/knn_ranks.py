# kNN ranks of the lemmas used by proofs of the lemma-count members (USEDAXIOMS in r5/out/<goal>)
import sys, re, collections, os
D = 'loops/UL'; labs = sys.argv[1].split(',')
got = {}
for l in open(D + '/r5/results.tsv'):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 5 and f[1] != 'NO' and f[4] in labs:
        got[f[0]] = f[4]
by = collections.defaultdict(list)
for g, lab in got.items():
    p = os.path.join(D, 'r5', 'out', g)
    try:
        u = next((x for x in open(p, errors='replace') if x.startswith('USEDAXIOMS')), None)
    except OSError:
        continue
    if u is None: continue
    ranks = [int(m.group(1)) for m in re.finditer(r'lemma_knn_(\d+)_', u)]
    sib = len(re.findall(r'lemma_goal_\d+', u))
    by[lab].append((max(ranks) if ranks else -1, len(ranks), sib, sorted(ranks)))
for lab in labs:
    L = by[lab]
    if not L: continue
    mx = sorted(x[0] for x in L)
    over = lambda t: sum(1 for x in mx if x >= t)
    print(lab, 'proofs', len(L), 'max rank: median', mx[len(mx) // 2], ' >=30:', over(30), ' >=60:', over(60), ' >=100:', over(100), ' >=200:', over(200), ' no kNN lemma:', sum(1 for x in mx if x < 0))
    print('   used kNN lemmas a proof: median', sorted(x[1] for x in L)[len(L) // 2], ' examples', [x[3][-5:] for x in L[:6]])

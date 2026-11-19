# (19 Nov) Feasibility of a learned kNN lemma ranker. Targets: goals proved by the lemma-count members (k60..k400 at 5 s),
# whose USEDAXIOMS name the kNN lemmas used. For each, the candidates are recomputed with today's index (top K of the
# member's count); label = used. Grouped CV by original: does a LightGBM ranker on pair features beat the similarity rank
# at putting the used lemmas into the top 30?
import sys, os, re, math, collections, random
sys.path.insert(0, '/project/twee/hints')
os.chdir('/project/hintwork')
import lemmas
D = 'loops/UL'
solved = {}
for l in open(D + '/solved.tsv'):
    w = l.rstrip('\n').split('\t'); solved[w[0]] = w
ix = lemmas.LemmaIndex(sorted(solved), subsets=True)
src = {o: set(v) for o, v in lemmas.by_original(solved).items()}
KOF = {'Vk60@0': 60, 'Vk100@0': 100, 'Vk200@0': 200, 'Vk400@0': 400}
got = {}
for l in open(D + '/r5/results.tsv'):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 5 and f[1] != 'NO' and f[4] in KOF:
        got[f[0]] = f[4]
uses = lemmas.lemma_uses([D])
rows = []; groups = []; tg = []
found = missing = 0
for t, lab in sorted(got.items()):
    u = next((x for x in open(os.path.join(D, 'r5', 'out', t), errors='replace') if x.startswith('USEDAXIOMS')), '')
    used = {m.group(2) for m in re.finditer(r'lemma_knn_(\d+)_(\S+__goal_\d+)', u)}
    if not used: continue
    K = 400
    picks = lemmas.knn_picks(t, src, 6, ix, K, True)
    pos = set(picks)
    found += len(used & pos); missing += len(used - pos)
    key, F = ix.info[t]
    idf = ix.idf(key, t)
    wF = sum(idf.get(x, 0) for x in F)
    o = t.rsplit('__goal_', 1)[0]
    for r, m in enumerate(picks):
        km, G = ix.info[m]
        inter = sum(idf.get(x, 0) for x in F & G); wG = sum(idf.get(x, 0) for x in G)
        un = wF + wG - inter
        mo = m.rsplit('__goal_', 1)[0]
        feats = [r, inter / un if un else 0, inter, wF, wG, inter / wG if wG else 0, inter / wF if wF else 0,
                 len(G), len(F & G), int(km == key), int(mo == o), math.log1p(uses.get(m, 0) - (m in used)),   # (minus the target's own use)
                 int(m.rsplit('__goal_', 1)[1])]
        rows.append((feats, int(m in used))); groups.append(o); tg.append(t)
print('targets', len(got), 'used found in recomputed top 400:', found, 'missing:', missing, file=sys.stderr)
import numpy as np, lightgbm as lgb
X = np.array([r[0] for r in rows], dtype=float); y = np.array([r[1] for r in rows])
names = ['rank', 'sim', 'inter', 'wF', 'wG', 'cont_G', 'cont_F', 'nG', 'nFG', 'same_theory', 'same_orig', 'log_uses', 'goalno']
DROP = [names.index(x) for x in os.environ.get('DROP', '').split(',') if x]
if DROP:   # (drop features; the rank stays column 0)
    X[:, DROP] = 0
origs = sorted(set(groups)); random.seed(1); random.shuffle(origs)
fold = {o: i % 5 for i, o in enumerate(origs)}
fg = np.array([fold[g] for g in groups])
pred = np.zeros(len(y))
for k in range(5):
    tr, te = fg != k, fg == k
    m = lgb.LGBMClassifier(n_estimators=200, num_leaves=15, learning_rate=0.05, min_child_samples=20, verbose=-1, n_jobs=2)
    m.fit(X[tr], y[tr]); pred[te] = m.predict_proba(X[te])[:, 1]
from sklearn.metrics import roc_auc_score
print('pairs', len(y), 'positives', y.sum())
print('AUC: -rank', round(roc_auc_score(y, -X[:, 0]), 3), ' model', round(roc_auc_score(y, pred), 3))
# recall at 30 / 60 / 100 per target: share of its used lemmas in its top N by each ranking
by = collections.defaultdict(list)
for i, t in enumerate(tg): by[t].append(i)
for N in (30, 60, 100):
    rs = []; rm = []; alls = [0, 0]
    for t, I in by.items():
        P = [i for i in I if y[i]]
        if not P: continue
        top_r = set(sorted(I, key=lambda i: X[i, 0])[:N]); top_m = set(sorted(I, key=lambda i: -pred[i])[:N])
        rs.append(len([i for i in P if i in top_r]) / len(P)); rm.append(len([i for i in P if i in top_m]) / len(P))
        alls[0] += all(i in top_r for i in P); alls[1] += all(i in top_m for i in P)
    print(f'top {N}: mean recall similarity {sum(rs)/len(rs):.3f} model {sum(rm)/len(rm):.3f};'
          f' targets with all used lemmas in: similarity {alls[0]} model {alls[1]} of {len(rs)}')
m = lgb.LGBMClassifier(n_estimators=200, num_leaves=15, learning_rate=0.05, min_child_samples=20, verbose=-1, n_jobs=2).fit(X, y)
names = ['rank', 'sim', 'inter', 'wF', 'wG', 'cont_G', 'cont_F', 'nG', 'nFG', 'same_theory', 'same_orig', 'log_uses', 'goalno']
print('gain importance', sorted(zip(m.booster_.feature_importance('gain').round(0), names), reverse=True))

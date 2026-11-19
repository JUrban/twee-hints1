# Which yield estimator predicts the next window's per-label yields better (rows from R, windows of W rows)?
#   cum: (k + YW*P)/(c/3600 + YW), the ratio rule now
#   rel: (k + YW*P)/(E/Gnow + YW), E = sum of c_i*G(t_i)/3600, G = the overall rate discounted over TAU rows
#   disc: cum with each row's k and c discounted over TAU rows
# Score: Poisson log-likelihood of each label's proofs in the next window given its CPU there and the estimate,
# and the share of next-window proofs a greedy pick by the estimate would have bought (top label's realized rate).
import sys, math, collections
f_, R, W, TAU = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
YW = 2.0
P = collections.defaultdict(lambda: 1.0, {'Vunf@0': 3.8, 'Vk60@0': 1.9, 'L1': 1.73, 'L2': 1.1, 'L3': 1.77, 'Vk60': 1.19,
     'Vp9': 0.7, 'Vunf': 0.47, 'Vtwo': 0.23, 'Vnom': 0.23, 'L4': 0.21})
rows = []
for i, l in enumerate(open(f_), 1):
    if i < R: continue
    f = l.rstrip('\n').split('\t')
    if len(f) < 5: continue
    rows.append((f[4], 1 if f[1] != 'NO' else 0, float(f[2])))
d = math.exp(-1 / TAU)
k = collections.Counter(); c = collections.Counter(); E = collections.Counter()
kd = collections.Counter(); cd = collections.Counter()
Gk, Gc = 0.0, 0.0
ll = collections.Counter(); n = 0; mll = collections.Counter(); nw = [0]
for s in range(0, len(rows), W):
    w = rows[s:s + W]
    if s > 0:
        Gnow = (Gk + 1) / (Gc / 3600 + 0.5)
        est = {}; ests = collections.defaultdict(dict)
        wk = collections.Counter(); wc = collections.Counter()
        for lab, ok, t in w:
            wk[lab] += ok; wc[lab] += t
        for lab in wc:
            if wc[lab] < 600: continue
            est['cum'] = (k[lab] + YW * P[lab]) / (c[lab] / 3600 + YW)
            est['rel'] = (k[lab] + YW * P[lab]) / (E[lab] / Gnow + YW)
            est['disc'] = (kd[lab] + YW * P[lab]) / (cd[lab] / 3600 + YW)
            est['flat'] = 1.0
            est['prior'] = P[lab]
            for m, e in est.items():
                mu = max(e * wc[lab] / 3600, 1e-6)
                ll[m] += wk[lab] * math.log(mu) - mu - math.lgamma(wk[lab] + 1)
                ests[m][lab] = e
            n += 1
        # scale-free: the split of the window's proofs among its labels, given estimate x CPU (multinomial)
        labs_ = [l_ for l_ in wc if wc[l_] >= 600]
        if len(labs_) >= 2 and sum(wk[l_] for l_ in labs_) > 0:
            for m in ests:
                z = sum(ests[m][l_] * wc[l_] for l_ in labs_)
                mll[m] += sum(wk[l_] * math.log(ests[m][l_] * wc[l_] / z) for l_ in labs_)
            nw[0] += 1
    for lab, ok, t in w:
        G = (Gk + 1) / (Gc / 3600 + 0.5)
        E[lab] += t * G / 3600
        k[lab] += ok; c[lab] += t
        Gk = Gk * d + ok; Gc = Gc * d + t
    # discount label stats once per window (W rows)
    dw = d ** len(w)
    for lab in list(kd): kd[lab] *= dw; cd[lab] *= dw
    for lab, ok, t in w:
        kd[lab] += ok; cd[lab] += t
print('label-windows', n, ' Poisson log-lik:', {m: round(v, 1) for m, v in ll.items()},
      ' windows', nw[0], ' split log-lik:', {m: round(v, 1) for m, v in mll.items()})

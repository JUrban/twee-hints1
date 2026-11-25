#!/usr/bin/env python3
"""prec_portfolio.py REPLAY.tsv [--orders FILE] [--k K] [--redundancy R] [--cpu C] (exp85, notes/2026-11-25-precedence-portfolio.md).

From prec_replay.py's rows (goal, order id, THM/NO, CPU s, wall s): the goals with all orders run; per order the
goals proved within C CPU s (default: the replay's cap); the default's (order 0) count; the union; the goals only
non-default orders prove; the per-goal spread (how many orders prove it). Then a greedy portfolio of K orders
(default 24): each step takes the order with the most goals still below R covers (default 2: each goal proved by at
least two chosen orders where possible), ties broken by total proved, then lower total CPU; the default first.
Writes the chosen ids and their lists to REPLAY.portfolio.

With work counts (prec_replay.py's 6th column): the orders no other dominates (a superset of goals, at most the same
work on each, and more goals or less total work), and a cost-greedy portfolio (cost: the sum over goals of the least
work among the chosen orders, an unproved goal twice the cap), written to REPLAY.costportfolio."""
import collections, sys
A = sys.argv[1:]
def opt(k, d):
    return A[A.index(k) + 1] if k in A else d
P = A[0]
K, R = int(opt('--k', 24)), int(opt('--redundancy', 2))
C = float(opt('--cpu', 1e9))
O = opt('--orders', '/project/twee/hints/exp/sets/exp85.orders')
lists = {l.split('\t')[0]: l.rstrip('\n').split('\t')[1] if '\t' in l else '' for l in open(O) if l.strip()}
res = collections.defaultdict(dict)
work = {}   # (goal, order) -> critical pairs considered (twee's WORK line)
for l in open(P):
    w = l.rstrip('\n').split('\t')
    if len(w) >= 4:
        res[w[0]][w[1]] = (w[2] == 'THM' and float(w[3]) <= C, float(w[3]))
        if len(w) >= 6 and w[5] != '-':
            work[(w[0], w[1])] = int(w[5])
G = sorted(g for g in res if len(res[g]) == len(lists))
ids = sorted(lists, key=int)
pr = {o: {g for g in G if res[g][o][0]} for o in ids}
cpu = {o: sum(res[g][o][1] for g in G) for o in ids}
U = set().union(*pr.values())
print(f'goals with all {len(ids)} orders: {len(G)} (of {len(res)} started)')
cnt = sorted(len(pr[o]) for o in ids)
print(f'default (0) proves {len(pr["0"])}; per order: min {cnt[0]}, median {cnt[len(cnt) // 2]}, max {cnt[-1]}; union {len(U)};'
      f' only non-default orders {len(U - pr["0"])}; none {len(G) - len(U)}')
spread = collections.Counter(sum(res[g][o][0] for o in ids) for g in G)
print('goals by how many orders prove them:', sorted(spread.items()))
best = sorted(ids, key=lambda o: -len(pr[o]))[:5]
print('best single orders:', [(o, len(pr[o]), lists[o]) for o in best])
chosen, cov = ['0'], collections.Counter({g: 1 for g in pr['0']})
while len(chosen) < K:
    rest = [o for o in ids if o not in chosen]
    if not rest:
        break
    gain = lambda o: sum(1 for g in pr[o] if cov[g] < R)
    o = max(rest, key=lambda o: (gain(o), len(pr[o]), -cpu[o]))
    if gain(o) == 0:
        o = max(rest, key=lambda o: (len(pr[o]), -cpu[o]))
    g0 = gain(o)
    chosen.append(o)
    for g in pr[o]:
        cov[g] += 1
    got = set().union(*(pr[x] for x in chosen))
    print(f'  {len(chosen):2d}. order {o:>3s} ({len(pr[o])} proved, gain {g0}) union {len(got)}, '
          f'covered {R}x: {sum(1 for g in G if cov[g] >= min(R, sum(res[g][x][0] for x in ids)))}/{len(G)}')
with open(P + '.portfolio', 'w') as f:
    f.writelines(f'{o}\t{lists[o]}\n' for o in chosen)
print('wrote', P + '.portfolio')

# (25 Nov) speed: the user, an order also dominates another when it proves the same goals much faster. Work is twee's
# critical pairs considered, deterministic under an abstract cap. wk(g, o): the work of a proof, None if unproved
if work:
    wk = lambda g, o: work.get((g, o)) if res[g][o][0] else None
    cap = max(work.values())
    PEN = 2 * cap   # an unproved goal costs twice the cap
    def dominates(x, y, f=1.0):
        # x proves every goal y proves, each with at most f times y's work (f=1: weak dominance)
        return all(res[g][x][0] and wk(g, x) <= f * wk(g, y) for g in pr[y])
    nd = [y for y in ids if not any(x != y and dominates(x, y) and (pr[x] != pr[y] or sum(wk(g, x) for g in pr[y]) <
                                                                     sum(wk(g, y) for g in pr[y])) for x in ids)]
    print(f'\nwork: cap {cap} pairs, unproved = {PEN}. Orders not dominated (another proves a superset of their goals with'
          f' at most their work on each, and more goals or less total work): {len(nd)} of {len(ids)}')
    print('  not dominated:', nd)
    d0 = [x for x in ids if x != '0' and dominates(x, '0') and (pr[x] != pr['0'] or sum(wk(g, x) for g in pr['0']) <
                                                                sum(wk(g, '0') for g in pr['0']))]
    print(f'  orders that dominate the default: {len(d0)} {d0[:12]}')
    tot = lambda x, gs: sum(wk(g, x) for g in gs)
    mf = lambda x, y: pr[y] <= pr[x] and (not pr[y] or tot(x, pr[y]) <= 0.5 * tot(y, pr[y]))
    nd2 = [y for y in ids if not any(x != y and mf(x, y) for x in ids)]
    print(f'  "much faster" (the user): orders no other order beats by a superset of their goals in at most half their'
          f' total work on them: {len(nd2)} of {len(ids)}; the default is {"not " if "0" in nd2 else ""}beaten that way'
          + (f' by {[x for x in ids if x != "0" and mf(x, "0")][:12]}' if '0' not in nd2 else ''))
    cost = lambda P_: sum(min((wk(g, o) or PEN) for o in P_) for g in G)
    print(f'  cost (sum over goals of the least work, unproved {PEN}): default {cost(["0"])}, all {len(ids)} orders {cost(ids)}')
    ch = ['0']
    while len(ch) < K:
        rest = [o for o in ids if o not in ch]
        o = min(rest, key=lambda o: cost(ch + [o]))
        ch.append(o)
        got = set().union(*(pr[x] for x in ch))
        print(f'  cost-greedy {len(ch):2d}. order {o:>3s}: cost {cost(ch)}, union {len(got)}')
    sp = sorted(min(wk(g, o) for o in ch if wk(g, o)) / wk(g, '0') for g in pr['0'])
    if sp:
        print(f'  on the {len(sp)} goals the default proves: least work in the cost portfolio / the default\'s, median {sp[len(sp) // 2]:.2f},'
              f' q25 {sp[len(sp) // 4]:.2f}')
    with open(P + '.costportfolio', 'w') as f:
        f.writelines(f'{o}\t{lists[o]}\n' for o in ch)
    print('wrote', P + '.costportfolio')

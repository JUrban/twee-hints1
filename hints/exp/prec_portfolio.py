#!/usr/bin/env python3
"""prec_portfolio.py REPLAY.tsv [--orders FILE] [--k K] [--redundancy R] [--cpu C] (exp85, notes/2026-11-25-precedence-portfolio.md).

From prec_replay.py's rows (goal, order id, THM/NO, CPU s, wall s): the goals with all orders run; per order the
goals proved within C CPU s (default: the replay's cap); the default's (order 0) count; the union; the goals only
non-default orders prove; the per-goal spread (how many orders prove it). Then a greedy portfolio of K orders
(default 24): each step takes the order with the most goals still below R covers (default 2: each goal proved by at
least two chosen orders where possible), ties broken by total proved, then lower total CPU; the default first.
Writes the chosen ids and their lists to REPLAY.portfolio."""
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
for l in open(P):
    w = l.rstrip('\n').split('\t')
    if len(w) >= 4:
        res[w[0]][w[1]] = (w[2] == 'THM' and float(w[3]) <= C, float(w[3]))
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

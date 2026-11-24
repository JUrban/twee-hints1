"""profinh.py TWEE.prof NAME,NAME...: the inherited %time of GHC cost centres, summed over their outermost occurrences in the
call tree (a cost centre nested in itself counts once), with entries (24 Nov, exp80, notes/2026-11-24-lemma-cost.md)."""
import sys, collections
L = open(sys.argv[1]).read().split('\n')
i = [k for k, x in enumerate(L) if x.startswith('COST CENTRE')][1]
rows = []
for x in L[i + 2:]:
    if not x.strip():
        continue
    ind = len(x) - len(x.lstrip(' ')); w = x.split()
    try:
        rows.append((ind, w[0], float(w[-2]), int(w[-5])))
    except (ValueError, IndexError):
        pass
want = sys.argv[2].split(',')
tot = collections.Counter(); calls = collections.Counter(); stack = []
for ind, nm, it, ent in rows:
    while stack and stack[-1][0] >= ind:
        stack.pop()
    if nm in want and nm not in [s[1] for s in stack]:
        tot[nm] += it; calls[nm] += ent
    stack.append((ind, nm))
for nm, t in tot.most_common():
    print(f'{nm:24s} {t:6.1f}%  entries {calls[nm]}')

"""memberyield.py [N ...] [--dir loops/UL/r5] [--top K] [--md]: production's yield by level and member over its last N
runs (23 Nov).

results.tsv rows: goal, THM/NO, seconds, HINTSTATS, level or member (L0-L4; V<member>), ... For each N (default
6000): runs, proofs, CPU h (the seconds column) and proofs per CPU h, by level/member, the top K by CPU h."""
import collections, sys

a = sys.argv[1:]
D = '/project/hintwork/loops/UL/r5'
if '--dir' in a:
    i = a.index('--dir'); D = a[i + 1]; a = a[:i] + a[i + 2:]
K = 12
if '--top' in a:
    i = a.index('--top'); K = int(a[i + 1]); a = a[:i] + a[i + 2:]
md = '--md' in a
Ns = [int(x) for x in a if x != '--md'] or [6000]
rows = [l.rstrip('\n').split('\t') for l in open(f'{D}/results.tsv')]
for N in Ns:
    C = collections.Counter(); T = collections.Counter(); S = collections.Counter()
    for r in rows[-N:]:
        if len(r) < 5:
            continue
        lv = r[4]; C[lv] += 1
        try:
            S[lv] += float(r[2])
        except ValueError:
            pass
        T[lv] += r[1] == 'THM'
    tot = sum(S.values()) / 3600; th = sum(T.values())
    top = sorted(C, key=lambda x: -S[x])[:K]
    if md:
        print(f'Last {N} runs: {th} proofs in {tot:.1f} CPU h ({th / tot:.2f} per CPU h).\n')
        print('| level or member | runs | proofs | CPU h | per CPU h |')
        print('|---|---:|---:|---:|---:|')
        for lv in top:
            print(f'| {lv} | {C[lv]} | {T[lv]} | {S[lv] / 3600:.1f} | {T[lv] / (S[lv] / 3600) if S[lv] else 0:.2f} |')
        rest = [lv for lv in C if lv not in top]
        if rest:
            print(f'| the other {len(rest)} | {sum(C[x] for x in rest)} | {sum(T[x] for x in rest)} | '
                  f'{sum(S[x] for x in rest) / 3600:.1f} | |')
        print()
    else:
        print(f'last {N} runs: THM {th} CPU h {tot:.1f} per CPU h {th / tot:.2f}')
        for lv in top:
            print(f'   {lv:12s} runs {C[lv]:6d} THM {T[lv]:4d} CPU h {S[lv] / 3600:6.1f}')

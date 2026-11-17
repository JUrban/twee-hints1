"""zstat.py ARM SET: a from-zero cascade's unsolved goals never run, runs per kind and level, the mix line."""
import collections, sys
d, st = sys.argv[1:3]
R = collections.Counter(); lv = collections.Counter(); pv = collections.Counter()
for l in open(f'loops/{d}/r1/results.tsv'):
    w = l.rstrip('\n').split('\t'); R[w[0]] += 1; lv[w[4]] += 1; pv[w[4]] += w[1] == 'THM'
S = {l.split('\t')[0] for l in open(f'loops/{d}/solved.tsv')}
A = [l.strip() for l in open(st) if l.strip()]
un = [n for n in A if n not in S]
print(d, 'solved', len(S), 'unsolved', len(un), 'never run', sum(1 for n in un if n not in R),
      'levels', ' '.join(f'{k} {pv[k]}/{lv[k]}' for k in sorted(lv)))
m = [l for l in open(f'loops/{d}.log') if ', mix ' in l]
if m:
    print(' ', m[-1].strip()[-140:])

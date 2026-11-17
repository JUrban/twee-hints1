#!/usr/bin/env python3
"""exp3/mkhints.py: hint files for the deep runs. chain(g) = the expansions (exp3/xd, all 16 loops) of the 10
nearest UL-proven siblings below g, nearest first, each its own steps first and then its lemmas' steps by depth;
duplicates dropped. Writes h_K/<g>.hints (the chain alone), h_E/<g>.hints (the captured pool, then the chain's
hints the pool lacks), and hints.tsv: goal, pool, chain, chain extras beyond the pool."""
import os
S = {l.split('\t')[0]: [s for s in l.rstrip('\n').split('\t')[1].split(',') if s] for l in open('sibs10_47.tsv')}
for d in ('h_K', 'h_E'): os.makedirs(d, exist_ok=True)
with open('hints.tsv', 'w') as t:
    for g, sib in S.items():
        seen, chain = set(), []
        for s in sib:
            try: L = open('xd/' + s).read().splitlines()
            except OSError: continue
            for x in L:
                h = tuple(x.split('\t')[:2])
                if len(h) == 2 and h not in seen: seen.add(h); chain.append(h)
        pool = open(f'tb/tmp/{g}.hints').read().splitlines()
        pk = {tuple(x.split('\t')[:2]) for x in pool}
        ex = [h for h in chain if h not in pk]
        open(f'h_K/{g}.hints', 'w').write(''.join('\t'.join(h) + '\n' for h in chain))
        open(f'h_E/{g}.hints', 'w').write('\n'.join(pool + ['\t'.join(h) for h in ex]) + '\n')
        t.write(f'{g}\t{len(pk)}\t{len(chain)}\t{len(ex)}\n')

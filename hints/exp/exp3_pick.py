#!/usr/bin/env python3
"""exp3 goal selection (17 Nov 20:10, run from /project/hintwork/exp3; deterministic: the 19:54 first pick iterated a set,
so its order depended on the hash seed and it was redone): public goals unsolved in all 16 loops with a
UL proof among the 3 goals below; seed 7 shuffle, at most 2 per original, 48 goals -> goals48. Then the 10 nearest
UL-proven siblings below each -> sibs10.tsv, sibs10."""
import collections, os, random
L='UL,Z4,Z3,Z2,Z1,Z0,PGA,PGB,ORH,ORG,ORF,ORE,ORD,ORC,ORB,ORA'.split(',')
solved=set()
for d in L:
    p=f'/project/hintwork/loops/{d}/solved.tsv'
    if os.path.exists(p): solved|={l.split('\t')[0] for l in open(p)}
ul={l.split('\t')[0] for l in open('/project/hintwork/loops/UL/solved.tsv')}
pub={l.strip() for l in open('/project/hintwork/sets/all') if l.strip()}
by=collections.defaultdict(list)
for g in sorted(pub):   # sorted: set order varies with the hash seed
    o,k=g.rsplit('__goal_',1); by[o].append(int(k))
cand=[]
for o,ks in sorted(by.items()):
    ks.sort()
    for i,k in enumerate(ks):
        g=f'{o}__goal_{k}'
        if g in solved: continue
        if any(f'{o}__goal_{j}' in ul for j in ks[max(0,i-3):i]): cand.append((o,k,i/len(ks)))
random.seed(7); random.shuffle(cand)
per=collections.Counter(); pick=[]
for o,k,pos in cand:
    if per[o]<2: per[o]+=1; pick.append((o,k,pos))
    if len(pick)==48: break
pick.sort()
open('goals48','w').write(''.join(f'{o}__goal_{k}\n' for o,k,_ in pick))
out=open('sibs10.tsv','w'); names=set()
for o,k,_ in pick:
    s=[f'{o}__goal_{j}' for j in sorted((j for j in by[o] if j<k and f'{o}__goal_{j}' in ul), reverse=True)[:10]]
    names|=set(s); out.write(f'{o}__goal_{k}\t'+','.join(s)+'\n')
open('sibs10','w').write('\n'.join(sorted(names))+'\n')

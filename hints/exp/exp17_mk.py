#!/usr/bin/env python3
"""exp17/mk.py: wall commands at 80 s with 60 kNN lemmas, otherwise as exp11's stage 1.
Inputs: the captures cap/K60 and cap/K30 (solve_cap.sh with KNN=60 and KNN=30, both from UL at 13:37), each made
into 80 s commands by exp6/tbify.py (K60_pool.cmds, K30_pool.cmds). The hints of every command are replaced by
exp11's own chain (exp11/h_chain/<goal>.hints), so the hints are exactly exp11's.
Writes K60.cmds (all 107 walls), and K30.cmds: only the walls whose K30 problem differs from exp11's (the context
grew between 10:38 and 13:37). For the others, exp11's runs are an exact control (twee is deterministic in
abstract time; exp14 checks that on 7 walls). drift.tsv: goal, K30 problem equal to exp11's (1/0), lemma lines
in exp11, K30 and K60."""
import os
E = '/project/hintwork/exp11'
def cmds(p):
    return {l.split('\t')[0]: l.rstrip('\n').split('\t')[1].split() for l in open(p)}
c11, c30, c60 = cmds(f'{E}/s1.cmds'), cmds('K30_pool.cmds'), cmds('K60_pool.cmds')
def nlem(w):
    return sum(1 for l in open(w[1]) if 'lemma_' in l)
def fix(w, g):
    w = list(w); i = w.index('--hints-file'); w[i + 1] = f'{E}/h_chain/{g}.hints'; return w
with open('K60.cmds', 'w') as f60, open('K30.cmds', 'w') as f30, open('drift.tsv', 'w') as d:
    for g in sorted(c11):
        same = open(c11[g][1]).read() == open(c30[g][1]).read()
        # the other arguments, without the paths, must match exp11's
        strip = lambda w: [x for x in w if not x.startswith('/')]
        assert strip(c11[g]) == strip(c30[g]) == strip(c60[g]), g
        d.write(f'{g}\t{int(same)}\t{nlem(c11[g])}\t{nlem(c30[g])}\t{nlem(c60[g])}\n')
        f60.write(g + '\t' + ' '.join(fix(c60[g], g)) + '\n')
        if not same:
            f30.write(g + '\t' + ' '.join(fix(c30[g], g)) + '\n')

#!/usr/bin/env python3
"""exp20/mk.py: exp11's stage-1 commands (s1.cmds, 80 s) at 160 abstract s (--max-cpu 1600) for the 92 walls exp11
did not prove: the time-matched control for two-method portfolios at 80 s each. The first 80 s of a 160 s run
are the 80 s run (a larger limit changes nothing before it: chk.cmds, aK2_eq_aK3_1243b 372 proved at 23,570 pairs
in both), so exp11's 15 are proved at 160 s as well. Writes C160.cmds."""
E = '/project/hintwork/exp11'
proved = {l.split('\t')[0] for l in open(f'{E}/res_s1.tsv') if l.split('\t')[1] == '1'}
with open('C160.cmds', 'w') as f:
    for l in open(f'{E}/s1.cmds'):
        g, c = l.rstrip('\n').split('\t')
        if g in proved:
            continue
        assert ' --max-time 80 ' in c and ' --max-cpu 800.0 ' in c
        f.write(g + '\t' + c.replace(' --max-time 80 ', ' --max-time 160 ').replace(' --max-cpu 800.0 ', ' --max-cpu 1600.0 ') + '\n')

#!/usr/bin/env python3
"""exp18/mk.py: exp11's stage-1 commands (s1.cmds) with twee-e61 instead of twee-e48 and --eqhint-subsume added;
the 92 walls exp11 did not prove first, then its 15. Writes SU.cmds. check.cmds (made by hand, 14:42): exp11's
3 fastest proved walls with e61 and no flag, for the identity check."""
E = '/project/hintwork/exp11'
proved = {l.split('\t')[0] for l in open(f'{E}/res_s1.tsv') if l.split('\t')[1] == '1'}
rows = [l.rstrip('\n').split('\t') for l in open(f'{E}/s1.cmds')]
rows = [r for r in rows if r[0] not in proved] + [r for r in rows if r[0] in proved]
with open('SU.cmds', 'w') as f:
    for g, c in rows:
        assert c.startswith('/project/bin/twee-e48 ')
        f.write(g + '\t' + c.replace('/project/bin/twee-e48 ', '/project/bin/twee-e61 ', 1) + ' --eqhint-subsume\n')

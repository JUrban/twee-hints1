#!/usr/bin/env python3
"""exp19/mk.py: exp11's stage-1 commands (s1.cmds) with twee-e61 instead of twee-e48 (identical without new flags:
exp18/res_chk.tsv) and --set-join added (critical pairs joined by successor sets, as Waldmeister does for
conjectures; twee's goals already use them). The 92 walls exp11 did not prove first. Writes SJ.cmds."""
E = '/project/hintwork/exp11'
proved = {l.split('\t')[0] for l in open(f'{E}/res_s1.tsv') if l.split('\t')[1] == '1'}
rows = [l.rstrip('\n').split('\t') for l in open(f'{E}/s1.cmds')]
rows = [r for r in rows if r[0] not in proved] + [r for r in rows if r[0] in proved]
with open('SJ.cmds', 'w') as f:
    for g, c in rows:
        assert c.startswith('/project/bin/twee-e48 ')
        f.write(g + '\t' + c.replace('/project/bin/twee-e48 ', '/project/bin/twee-e61 ', 1) + ' --set-join\n')

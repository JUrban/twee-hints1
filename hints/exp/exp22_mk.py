#!/usr/bin/env python3
"""exp22/mk.py: exp11's stage-1 commands (s1.cmds: the 107 walls at 80 s, twee-e48, PG 0.25, chain hints) with
one change each, the 92 walls exp11 did not prove first, then its 15 (in s1.cmds order):
  G80  no parental guidance (--pg-threshold dropped: e48 then matches e44, production before 17 Nov 19:00)
  N80  no rule model (and so no PG: PG pairs a rule without a model score with everything)
Writes G80.cmds, N80.cmds."""
E = '/project/hintwork/exp11'
proved = {l.split('\t')[0] for l in open(f'{E}/res_s1.tsv') if l.split('\t')[1] == '1'}
rows = [l.rstrip('\n').split('\t') for l in open(f'{E}/s1.cmds')]
rows = [r for r in rows if r[0] not in proved] + [r for r in rows if r[0] in proved]
def drop(w, flag, n=1):
    i = w.index(flag); return w[:i] + w[i + 1 + n:]
with open('G80.cmds', 'w') as fg, open('N80.cmds', 'w') as fn:
    for g, cmd in rows:
        w = cmd.split()
        assert w[w.index('--pg-threshold') + 1] == '0.25'
        fg.write(g + '\t' + ' '.join(drop(w, '--pg-threshold')) + '\n')
        n = drop(w, '--pg-threshold')
        for fl in ('--rule-model', '--rule-vocab', '--rule-goal', '--rule-threshold', '--rule-penalty'):
            n = drop(n, fl)
        fn.write(g + '\t' + ' '.join(n) + '\n')

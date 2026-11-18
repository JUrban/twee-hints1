#!/usr/bin/env python3
"""exp4/rungs2.py LREFINE.tsv TRIED.tsv... OUT.tsv: the second-level rungs of the ladder. Rows of refine.py on
target conjectures (column 8 = the target): the conjectures each proof used, minus the target itself (circular)
and minus conjectures already tried as goals in a TRIED file (sketch.py results; proved or not). Output in
moves.py format, kind 'gen', detail 'for <target>'. Ids start at 6000."""
import re, sys
*src, dst = sys.argv[1:]
def canon(eq):
    l, r = eq.split(' = ')
    def ren(x, y):
        names = {}
        f = lambda m: names.setdefault(m.group(0), f'V{len(names)}')
        return re.sub(r'\bX\d+\b', f, x) + ' = ' + re.sub(r'\bX\d+\b', f, y)
    return min(ren(l, r), ren(r, l))
tried = set()
for p in src[1:]:
    for l in open(p):
        w = l.rstrip('\n').split('\t'); tried.add((w[0], canon(w[3])))
out, seen = [], set()
for l in open(src[0]):
    w = l.rstrip('\n').split('\t')
    if w[3] != '1' or not w[6] or len(w) < 8: continue
    for c in w[6].split('; '):
        k = (w[0], canon(c))
        if canon(c) == canon(w[7]) or k in tried or k in seen: continue
        seen.add(k); out.append((w[0], c, w[7]))
with open(dst, 'w') as f:
    for i, (g, c, t) in enumerate(out):
        f.write(f'{g}\t{6000 + i}\tgen\t{c}\tok\tfor {t}\n')
print(len(out), 'second-level conjectures in', len({g for g, _, _ in out}), 'goals')

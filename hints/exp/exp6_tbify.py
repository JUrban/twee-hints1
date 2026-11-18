#!/usr/bin/env python3
"""exp6/tbify.py CAPLOG CAPDIR TB OUT.cmds T: the first captured command of each goal (CMD lines of a LOOP_PRINT_CMD
capture, as exp3 made exp3/tb), with its problem, hints and rule-goal files copied into TB (tmp/, goals/) and the
paths rewritten; --max-time T and --max-cpu 10 T. OUT.cmds: 'goal<TAB>command' for run.py."""
import os, shutil, sys
log, cap, tb, out, T = sys.argv[1:6]
os.makedirs(f'{tb}/tmp', exist_ok=True); os.makedirs(f'{tb}/goals', exist_ok=True)
seen = {}
for l in open(log):
    if not l.startswith('CMD '): continue
    w = l.split()[1:]
    g = os.path.basename(w[1])[:-2]
    if g not in seen: seen[g] = w
with open(out, 'w') as f:
    for g in sorted(seen):
        w = list(seen[g])
        for i, x in enumerate(w):
            if x.startswith(cap + '/'):
                d = f'{tb}/goals' if '/goals/' in x else f'{tb}/tmp'
                shutil.copy(x, f'{d}/{os.path.basename(x)}'); w[i] = os.path.abspath(f'{d}/{os.path.basename(x)}')
        w[w.index('--max-time') + 1] = T; w[w.index('--max-cpu') + 1] = str(10 * float(T))
        f.write(g + '\t' + ' '.join(w) + '\n')
print(len(seen), 'goals')

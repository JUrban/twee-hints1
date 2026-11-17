#!/usr/bin/env python3
# Re-run captured twee commands of proved goals with twee-e48 --pg-log (parental-guidance data, 17 Nov).
# usage: relog.py LOG SOLVED.tsv OUTDIR N J
import sys, os, random, subprocess, concurrent.futures as cf
log, solved, outd, n, j = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
last = {}
for l in open(log, errors='replace'):
    if l.startswith('CMD '):
        w = l.split()[1:]
        if len(w) > 2 and w[1].endswith('.p') and w[-2] == '--hints-file' or (len(w) > 2 and w[1].endswith('.p') and '--hints-file' not in w and l.endswith('\n')):
            last[os.path.basename(w[1])[:-2]] = w
S = sorted({l.split('\t')[0] for l in open(solved)} & set(last))
S = [g for g in S if '--load-state' not in last[g]]
random.Random(1).shuffle(S); S = S[:n]
os.makedirs(outd, exist_ok=True)
def run(g):
    w = ['/project/bin/twee-e48'] + last[g][1:] + ['--pg-log']
    with open(os.path.join(outd, g + '.out'), 'w') as fo, open(os.path.join(outd, g + '.err'), 'w') as fe:
        subprocess.run(w, stdout=fo, stderr=fe)
    return g
with cf.ThreadPoolExecutor(j) as ex:
    for k, g in enumerate(ex.map(run, S)):
        if k % 250 == 0: print(k, g, flush=True)
print('done', len(S))

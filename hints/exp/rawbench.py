#!/usr/bin/env python3
"""(22 Nov 16:36, exp62; notes/2026-11-22-o2-build.md) CPU of twee binaries on identical searches.

  rawbench.py SET N OUT.tsv BIN... [--time 5] [--seed 62]

N goals of SET (random.seed SEED), each run once per binary in a rotating order (abstract time 2000, no hints),
user+sys CPU from os.wait4. Rows: goal, binary, CPU s, max RSS KB, sha1 of stdout.
"""
import hashlib, os, random, subprocess, sys
a = sys.argv[1:]
T = a[a.index('--time') + 1] if '--time' in a else '5'
seed = int(a[a.index('--seed') + 1]) if '--seed' in a else 62
a = [x for i, x in enumerate(a) if not (x.startswith('--') or (i and a[i - 1].startswith('--')))]
setp, n, out, bins = a[0], int(a[1]), a[2], a[3:]
G = sorted(l.strip() for l in open(setp) if l.strip())
G = sorted(random.Random(seed).sample(G, min(n, len(G))))
f = open(out, 'w')
for i, g in enumerate(G):
    order = bins[i % len(bins):] + bins[:i % len(bins)]
    for b in order:
        p = subprocess.Popen([b, f'/project/AIM60k/problems/tptp/{g}.p', '--max-time', T, '--abstract-time', '2000',
                              '--no-colour', '--quiet'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        o = p.stdout.read()
        _, st, ru = os.wait4(p.pid, 0)
        f.write(f'{g}\t{os.path.basename(b)}\t{ru.ru_utime + ru.ru_stime:.3f}\t{ru.ru_maxrss}\t'
                f'{hashlib.sha1(o).hexdigest()[:12]}\n')
        f.flush()

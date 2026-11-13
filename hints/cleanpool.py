"""clean_pool.py POOL OUT RAWDIR: copy a hint pool, removing hints that depend on
a hypothesis of a conditional conjecture (twee-e14 HINTS-HYP), for conditional
problems re-proved by plain twee-e14. Unit-goal problems are linked unchanged."""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/project/twee/hints')
import hintlib
from loop import canon_key
T = '/project/AIM60k/problems/tptp'
pool, out, raw = sys.argv[1:4]
os.makedirs(out, exist_ok=True); os.makedirs(raw, exist_ok=True)
def cond(n):
    t = open(f'{T}/{n}.p').read()
    m = re.search(r'conjecture,(.*)\)\.', t, re.S)
    return bool(re.search(r'~|\||=>', m.group(1)))
names = sorted(os.listdir(pool))
def job(n):
    src = os.path.join(pool, n); dst = os.path.join(out, n)
    if os.path.lexists(dst): os.unlink(dst)
    if not cond(n):
        os.symlink(os.path.abspath(src), dst); return 'unit', 0, 0
    rp = os.path.join(raw, n)
    if not os.path.exists(rp):
        r = subprocess.run(['/project/bin/twee-e14', '--quiet', '--no-proof', '--print-hints', '--max-time', '10',
                            f'{T}/{n}.p'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=40)
        open(rp, 'w').write(r.stdout.decode('utf8', 'replace'))
    txt = open(rp).read()
    old = [l for l in open(src)]
    if 'HINTS-END' not in txt:
        open(dst, 'w').write(''.join(old)); return 'unsolved', 0, len(old)
    sig = hintlib.problem_signature(n)
    L, G = hintlib.extract_hints(txt)
    fwd = {canon_key(l, r, sig) for l, r in L + G if l != r}
    hyp = {canon_key(l, r, sig) for l, r in hintlib.extract_hyp(txt) if l != r} - fwd
    keep = [l for l in old if tuple(l.rstrip('\n').split('\t')[:2]) not in hyp]
    open(dst, 'w').write(''.join(keep)); return 'cond', len(old) - len(keep), len(old)
with ThreadPoolExecutor(18) as ex:
    res = list(ex.map(job, names))
from collections import Counter
c = Counter(r[0] for r in res)
rem = sum(r[1] for r in res if r[0] == 'cond'); tot = sum(r[2] for r in res if r[0] == 'cond')
print(f'{pool}: {dict(c)}; conditional re-proved: removed {rem} of {tot} hints ({100*rem/max(tot,1):.0f}%)')

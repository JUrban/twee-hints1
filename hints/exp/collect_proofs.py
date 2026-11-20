#!/usr/bin/env python3
"""(20 Nov 14:40, user's request) Twee proofs for a list of proved problems, as a tarball.

The list (/project/00THMR5k) holds results.tsv rows `PATH/results.tsv:GOAL<TAB>THM...` from many runs. The loops run
twee with --no-proof, so their outputs hold hints, not proofs; only run.py's outputs (runs/*/out/GOAL.out) print the
proof. For each distinct problem:
  1. the listed run's own printed proof (a run.py row), else
  2. a printed proof of the same problem from another run.py run, else
  3. a rerun: twee-e61 on the AIM60k problem with the listed loop's hints file as hints (the proof's equations;
     production's if that loop has none), 30 s; failures again with the hints of the goal plus those of the lemma
     goals its kept output used (USEDAXIOMS), 120 s.
The proof block is cut from 'The conjecture is true! Here is a proof.' to the RESULT line.

  collect_proofs.py plan LIST WORK        -> WORK/plan.tsv, WORK/rerun/{names,h/}
  collect_proofs.py plan2 LIST WORK       -> WORK/rerun2/{names,h/} (stage-1 failures, enriched hints)
  collect_proofs.py pack LIST WORK TARBALL
"""
import collections, glob, os, re, sys, tarfile, io

HW = '/project/hintwork'
B, E = 'The conjecture is true! Here is a proof.', 'RESULT: Theorem (the conjecture is true).'


def rows(lst):
    by = collections.OrderedDict()
    for l in open(lst):
        l = l.rstrip('\n')
        if not l:
            continue
        p, rest = l.split(':', 1)
        g = rest.split('\t')[0]
        by.setdefault(g, []).append(os.path.normpath(os.path.join(HW, os.path.dirname(p))))
    return by


def block(path):
    try:
        t = open(path, errors='replace').read()
    except OSError:
        return None
    i = t.find(B)
    j = t.find(E, i)
    return t[i:j + len(E)] + '\n' if 0 <= i < j else None


def loopdir(d):
    # HW/loops/X/rN -> HW/loops/X
    return os.path.dirname(d) if re.fullmatch(r'r\d+', os.path.basename(d)) else d


def plan(lst, work):
    by = rows(lst)
    rdirs = sorted(glob.glob(os.path.join(HW, 'runs', '*', 'out')))
    os.makedirs(os.path.join(work, 'rerun', 'h'), exist_ok=True)
    out, names = [], []
    for g, ds in by.items():
        src = None
        for d in ds:
            if d.split('/')[3] == 'runs' and block(os.path.join(d, 'out', g + '.out')):
                src = ('own', os.path.join(d, 'out', g + '.out')); break
        if src is None:
            for od in rdirs:
                if block(os.path.join(od, g + '.out')):
                    src = ('other', os.path.join(od, g + '.out')); break
        if src is None:
            h = None
            for d in ds:
                if d.split('/')[3] == 'loops' and os.path.exists(os.path.join(loopdir(d), 'hints', g)):
                    h = os.path.join(loopdir(d), 'hints', g); break
            if h is None and os.path.exists(os.path.join(HW, 'loops', 'UL', 'hints', g)):
                h = os.path.join(HW, 'loops', 'UL', 'hints', g)
            if h:
                lk = os.path.join(work, 'rerun', 'h', g)
                if not os.path.lexists(lk):
                    os.symlink(os.path.realpath(h), lk)
            src = ('rerun', h or '')
            names.append(g)
        out.append(f'{g}\t{src[0]}\t{src[1]}\t{ds[0]}\n')
    open(os.path.join(work, 'plan.tsv'), 'w').writelines(out)
    open(os.path.join(work, 'rerun', 'names'), 'w').writelines(g + '\n' for g in names)
    c = collections.Counter(l.split('\t')[1] for l in out)
    print(f'{len(by)} problems: {dict(c)}; {sum(1 for g in names if os.path.lexists(os.path.join(work, "rerun", "h", g)))} '
          f'reruns with hints')


def used_lemmas(g, ds):
    """lemma goals named in the listed runs' kept outputs (USEDAXIOMS)"""
    o = g.rsplit('__goal_', 1)[0]
    res = set()
    for d in ds:
        p = os.path.join(d, 'out', g)
        try:
            m = re.search(r'USEDAXIOMS(.*)', open(p, errors='replace').read())
        except OSError:
            continue
        if not m:
            continue
        for x in m.group(1).split():
            mm = re.match(r'(?:lemma|assume)_goal_(\d+)$', x)
            if mm:
                res.add(f'{o}__goal_{mm.group(1)}')
            mm = re.match(r'lemma_knn_\d+_(.+__goal_\d+)$', x)
            if mm:
                res.add(mm.group(1))
    return res


def plan2(lst, work):
    by = rows(lst)
    res = {l.split('\t')[0]: l.split('\t')[1] for l in open(os.path.join(work, 'rerun', 'results.tsv'))}
    fail = [g for g in open(os.path.join(work, 'rerun', 'names')).read().split() if res.get(g) != 'THM']
    os.makedirs(os.path.join(work, 'rerun2', 'h'), exist_ok=True)
    nl = []
    for g in fail:
        hs = []
        h0 = os.path.join(work, 'rerun', 'h', g)
        srcs = [h0] if os.path.exists(h0) else []
        srcs.append(os.path.join(HW, 'loops', 'UL', 'hints', g))
        lem = used_lemmas(g, by[g])
        for x in sorted(lem):
            for d in by[g]:
                p = os.path.join(loopdir(d), 'hints', x)
                if os.path.exists(p):
                    srcs.append(p); break
            else:
                srcs.append(os.path.join(HW, 'loops', 'UL', 'hints', x))
        seen = set()
        for p in srcs:
            if not os.path.exists(p):
                continue
            for l in open(p):
                w = l.rstrip('\n').split('\t')
                if len(w) >= 2 and (w[0], w[1]) not in seen:
                    seen.add((w[0], w[1])); hs.append(f'{w[0]}\t{w[1]}\n')
        open(os.path.join(work, 'rerun2', 'h', g), 'w').writelines(hs)
        nl.append(len(lem))
    open(os.path.join(work, 'rerun2', 'names'), 'w').writelines(g + '\n' for g in fail)
    print(f'{len(fail)} stage-1 failures; lemma goals per failure: {sum(nl) / max(1, len(nl)):.1f} on average')


def pack(lst, work, tb):
    by = rows(lst)
    pl = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(os.path.join(work, 'plan.tsv'))}
    idx, n, miss = [], collections.Counter(), []
    with tarfile.open(tb, 'w:gz') as tf:
        for g in by:
            kind, src = pl[g][1], pl[g][2]
            b = None
            if kind in ('own', 'other'):
                b = block(src)
            else:
                for st in ('rerun', 'rerun2'):
                    p = os.path.join(work, st, 'out', 'out', g + '.out')
                    b = block(p)
                    if b:
                        kind, src = st, p; break
            if not b:
                miss.append(g); n['missing'] += 1
                idx.append(f'{g}\tmissing\t\t{pl[g][3]}\n')
                continue
            n[kind] += 1
            data = b.encode()
            ti = tarfile.TarInfo(f'THMR5k_proofs/{g}.proof'); ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
            idx.append(f'{g}\t{kind}\t{src}\t{pl[g][3]}\n')
        readme = ('Twee proofs of the problems in /project/00THMR5k (one per distinct problem; 5,000 rows, '
                  f'{len(by)} problems).\nindex.tsv: problem, source, source file, the first listed run.\n'
                  'Sources: own = the listed run\'s own output (run.py); other = a printed proof of the same '
                  'problem from another run.py run (e.g. plain twee at 4 s); rerun = twee-e61 on the AIM60k '
                  'problem with the listed loop\'s proof equations as hints, 10 s, one pass; missing = no proof '
                  'obtained (yet: the rerun pass may still be running when this tarball was made).\n'
                  'The loops run twee with --no-proof, so their own proofs (which may use other goals as lemma '
                  'axioms) were never printed. Every proof here uses only the problem\'s own axioms.\n')
        for name, text in (('README', readme), ('index.tsv', ''.join(idx))):
            data = text.encode(); ti = tarfile.TarInfo(f'THMR5k_proofs/{name}'); ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
    print(f'{tb}: {dict(n)}')
    if miss:
        print('missing:', ' '.join(miss[:20]), '...' if len(miss) > 20 else '')


if __name__ == '__main__':
    cmd = sys.argv[1]
    {'plan': lambda: plan(sys.argv[2], sys.argv[3]), 'plan2': lambda: plan2(sys.argv[2], sys.argv[3]),
     'pack': lambda: pack(sys.argv[2], sys.argv[3], sys.argv[4])}[cmd]()

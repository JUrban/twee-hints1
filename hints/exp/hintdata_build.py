#!/usr/bin/env python3
"""Build /project/hintwork/hintdata: a git repo of the loop's durable data, in small commits (user, 19 Nov 15:20:
"put the useful data into a separate new git repo in the hintwork directory; make the commits small so that I can
push incrementally on github later (no big files or commits)").

hintdata_build.py [--given | --climbs | --realproofs]   (--realproofs: realproofs/<family>/, see main_realproofs; without any: everything but the given logs and the climbs; --given: only the
                               given logs, one .tar.xz commit per original; --climbs: the climb.py directories; all skip
                               what is already committed)
"""
import gzip, os, shutil, subprocess, sys, tarfile

HW = '/project/hintwork'
R = os.path.join(HW, 'hintdata')
UL = os.path.join(HW, 'loops/UL')
TRAILER = '\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'

def git(*a):
    return subprocess.run(['git', '-C', R] + list(a), check=True, capture_output=True, text=True).stdout

def commit(paths, msg):
    git('add', '--', *paths)
    if git('status', '--porcelain', '--', *paths).strip():
        git('commit', '-q', '-m', msg + TRAILER)
        print('committed:', msg, flush=True)

def gz(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, 'rb') as f, gzip.GzipFile(dst, 'wb', compresslevel=9, mtime=0) as g:
        shutil.copyfileobj(f, g)

def orig(n):
    return n.split('__goal_')[0]

def main_data():
    # 1. README (written by hand beside this script; copied in if newer)
    commit(['README.md'], 'README: what is here, formats, provenance')
    # 2. the solved list
    os.makedirs(os.path.join(R, 'solved'), exist_ok=True)
    shutil.copy(os.path.join(UL, 'solved.tsv'), os.path.join(R, 'solved/UL_solved.tsv'))
    commit(['solved'], 'solved: production loop UL, goal / round / CPU s')
    # 3. goal sets
    dst = os.path.join(R, 'sets')
    os.makedirs(dst, exist_ok=True)
    for n in sorted(os.listdir(os.path.join(HW, 'sets'))):
        p = os.path.join(HW, 'sets', n)
        if os.path.isfile(p) and os.path.getsize(p) < 5_000_000:
            shutil.copy(p, os.path.join(dst, n))
    commit(['sets'], 'sets: goal lists used by loops and experiments')
    # 4. proof-dependency records for chain hints
    for n in ('chain_records.tsv', 'chain_records2.tsv', 'chain_records_xfer.tsv'):
        gz(os.path.join(HW, n), os.path.join(R, 'chains', n + '.gz'))
    commit(['chains'], 'chains: proof-dependency records (goal -> proven goals its proof used), gzipped')
    # 5. run logs of the production loop, one commit per round
    for r in range(1, 6):
        p = os.path.join(UL, 'r%d/results.tsv' % r)
        if os.path.exists(p):
            gz(p, os.path.join(R, 'runs/UL_r%d_results.tsv.gz' % r))
            commit(['runs/UL_r%d_results.tsv.gz' % r], 'runs: UL round %d results (every twee run: goal, THM/NO, CPU s, hint stats, level, context)' % r)
    # 6. models (the small ones; dp2.pt, 67 MB, is left out)
    md = os.path.join(R, 'models')
    os.makedirs(md, exist_ok=True)
    keep = [n for n in sorted(os.listdir(os.path.join(HW, 'models')))
            if (n.startswith('rm') and n.endswith(('.bin', '.vocab'))) or n in ('gc1.pt', 'gnn2.pt')]
    for n in keep:
        shutil.copy(os.path.join(HW, 'models', n), os.path.join(md, n))
    commit(['models'], 'models: rule models (LightGBM binary forests + vocabularies for twee --rule-model), hint generator gc1, GNN v2')
    # 7. from-zero runs: solved lists and run logs
    for a in ('PGA', 'PGC', 'PGD', 'P2A', 'P2D', 'ORA', 'ORD'):
        d = os.path.join(HW, 'loops', a)
        if not os.path.isdir(d):
            continue
        out = os.path.join(R, 'fromzero', a)
        os.makedirs(out, exist_ok=True)
        shutil.copy(os.path.join(d, 'solved.tsv'), os.path.join(out, 'solved.tsv'))
        if os.path.exists(os.path.join(d, 'r1/results.tsv')):
            gz(os.path.join(d, 'r1/results.tsv'), os.path.join(out, 'r1_results.tsv.gz'))
        commit(['fromzero/' + a], 'fromzero: %s (2 h from zero on half1/half2)' % a)
    # 8. proofs, one commit per original
    src = os.path.join(UL, 'hints')
    by = {}
    for n in os.listdir(src):
        by.setdefault(orig(n), []).append(n)
    for o in sorted(by):
        d = os.path.join(R, 'proofs', o)
        os.makedirs(d, exist_ok=True)
        for n in by[o]:
            shutil.copy(os.path.join(src, n), os.path.join(d, n))
        commit(['proofs/' + o], 'proofs: %s (%d goals)' % (o, len(by[o])))

CLIMB_SKIP = ('SMK', '.old')

def tarxz(srcdir, names, dst):
    """a deterministic .tar.xz of srcdir/names (sorted, mtime 0, no owners), so reruns re-commit only changes"""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + '.tmp'
    subprocess.run(['bash', '-c', 'tar -C "$1" --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner -cf - "${@:3}" '
                    '| xz -T1 -6 > "$2"', '-', srcdir, tmp] + sorted(names), check=True)
    if os.path.exists(dst) and open(dst, 'rb').read() == open(tmp, 'rb').read():
        os.unlink(tmp)
    else:
        os.replace(tmp, dst)

def main_climbs():
    """(19 Nov 17:05; user: "the climber runs should probably be kept somewhere and also in the data repo and we should
    keep their stats for the lattice up-down climbing learning") climbs/<dir>/: every climb.py directory's records"""
    L = os.path.join(HW, 'loops')
    for d in sorted(os.listdir(L)):
        src = os.path.join(L, d)
        if not os.path.isfile(os.path.join(src, 'climb.tsv')) or any(x in d for x in CLIMB_SKIP):
            continue
        out = os.path.join(R, 'climbs', d)
        os.makedirs(out, exist_ok=True)
        # 1. the small records
        for n in ('climb.tsv', 'theories.tsv', 'fill.tsv', 'true.tsv', 'assume.tsv', 'used.tsv', 'fillattempts.tsv'):
            if os.path.exists(os.path.join(src, n)) and os.path.getsize(os.path.join(src, n)):
                gz(os.path.join(src, n), os.path.join(out, n + '.gz'))
        sv = os.path.join(src, 'solved.tsv')
        real = [l.split('\t')[0] for l in open(sv) if l.split('\t')[1:2] == ['1']] if os.path.exists(sv) else []
        with open(os.path.join(out, 'solved.tsv'), 'w') as f:
            f.writelines(l for l in open(sv) if l.split('\t')[1:2] == ['1']) if os.path.exists(sv) else None
        if real:   # the climber's own real proofs (their hint files, as latticedata.py reads DIR/hints/<target>)
            tarxz(os.path.join(src, 'hints'), [t for t in real if os.path.exists(os.path.join(src, 'hints', t))],
                  os.path.join(out, 'hints.tar.xz'))
        for sub in ('sketches', 'fillhints'):
            if os.path.isdir(os.path.join(src, sub)) and os.listdir(os.path.join(src, sub)):
                tarxz(os.path.join(src, sub), os.listdir(os.path.join(src, sub)), os.path.join(out, sub + '.tar.xz'))
        commit(['climbs/' + d], 'climbs: %s records (climb.tsv: one row per run; sketches, fill, assumptions)' % d)
        # 2. the per-target rule logs: realized (the final run's given rules) and given (successful runs), per original
        for sub in ('realized', 'given'):
            sd = os.path.join(src, sub)
            if not os.path.isdir(sd):
                continue
            by = {}
            for n in os.listdir(sd):
                by.setdefault(orig(n), []).append(n)
            batch, size = [], 0
            for o in sorted(by):
                dst = os.path.join(out, sub, o + '.tar.xz')
                tarxz(sd, by[o], dst)
                batch.append(dst); size += os.path.getsize(dst)
                if size > 10_000_000:
                    commit(batch, 'climbs: %s %s rule logs (xz, per original, up to %s)' % (d, sub, o))
                    batch, size = [], 0
            if batch:
                commit(batch, 'climbs: %s %s rule logs (xz, per original)' % (d, sub))

# (21 Nov 11:40; user: "can you pack these new proofs also into hintwork/hintdata/realproofs ? preferably into tarballs
# at most 10M big?") the printed twee proofs that loops keep since 20 Nov 15:04 (loops/<dir>/proofs/<goal>, written by
# loop.py's proof_job and exp/proofq.py), grouped by run family: a run with its transfer (.xfer) and derived-rule (_GML)
# loops, whose proofs use each other's goals as lemmas
RP_FAMILIES = [('production', ['UL', 'XFL', 'GML', 'STEPJ', 'SW20', 'ROOTS',
                               'CI1', 'CI2', 'CI3', 'CI4']),   # (23 Nov) the plain sweeps' proofs, merged into UL
               ('smoke', ['HCT', 'HCT2', 'KCT', 'KCT2', 'KCT3', 'QKC', 'QKT', 'QKN', 'RCT', 'RTT', 'YDT', 'YDT2', 'HTT',
                          'HTT2', 'GFT', 'KDS', 'LSM', 'LTD', 'PIS', 'FRS', 'FRT', 'KDA', 'KDB', 'KDC',
                          'RST']),
               # (22 Nov 15:32) the experiments since 21 Nov 11:50, one family each
               ('profile', ['PRA', 'PRB', 'PRC', 'PRF']),
               ('exp54', ['LAA', 'LAB']),
               ('exp56', ['GMR', 'GMR2', 'GMR3']),
               ('exp57', ['CW0', 'CW1', 'CW2', 'CW3', 'CW4', 'CW5', 'CW6', 'CW7', 'CW9']),
               ('exp59', ['HUB80']),
               ('exp61', ['RD5'])]   # (22 Nov 20:28) exp55's arms P2X, P2Z stay families of their own, as the P2* before
RP_MAX = 9_900_000          # bytes of one .tar.xz
RP_RAW = 120_000_000        # tar bytes per first try (xz -6 makes proofs about 16 times smaller)

def rp_tarxz(names, dst):
    """deterministic .tar.xz of loops/<dir>/proofs/<goal> as <dir>/<goal>.proof (names sorted, mtime 0, no owners)"""
    tmp, lst = dst + '.tmp', dst + '.lst'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(lst, 'w') as f:
        f.writelines(n + '\n' for n in sorted(names))
    subprocess.run(['bash', '-c', 'tar -C "$1" --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner --no-recursion '
                    '--transform "s,/proofs/\\([^/]*\\)\\$,/\\1.proof," -T "$3" -cf - | nice -n 10 xz -T1 -6 > "$2"', '-',
                    os.path.join(HW, 'loops'), tmp, lst], check=True)
    os.unlink(lst)
    return tmp

def main_realproofs():
    import glob
    L = os.path.join(HW, 'loops')
    dirs = sorted(os.path.relpath(os.path.dirname(p), L) for p in glob.glob(os.path.join(L, '*/proofs')) +
                  glob.glob(os.path.join(L, '*/*/proofs')))
    only = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--family=')]
    # (22 Nov 15:32) --skip=F,G: leave out families still being written (running arms); the index is still rebuilt
    skip = {x for a in sys.argv if a.startswith('--skip=') for x in a.split('=', 1)[1].split(',')}
    fam = {}
    for d in dirs:
        names = [os.path.join(d, 'proofs', n) for n in os.listdir(os.path.join(L, d, 'proofs')) if '__goal_' in n]
        if not names:
            continue
        b = d.split('/')[0].split('.')[0]   # a run and its side loops: Z6, Z6.xfer, Z6_GML -> Z6
        b = b[:-4] if b.endswith('_GML') else b
        f = next((k for k, pats in RP_FAMILIES if b in pats), b)
        if (not only or f in only) and f not in skip:
            fam.setdefault(f, []).extend(names)
    os.makedirs(os.path.join(R, 'realproofs'), exist_ok=True)
    index = []
    def key(n):
        d, _, g = n.rpartition('/proofs/')
        o, _, k = g.rpartition('__goal_')
        return (d, o, int(k))
    for f in sorted(fam):
        names, bad = [], 0
        for n in sorted(fam[f], key=key):
            with open(os.path.join(L, n), 'rb') as h:
                if b'RESULT: Theorem' in h.read()[-200:]:
                    names.append(n)
                else:
                    bad += 1
        # chunks of about RP_RAW tar bytes, halved until each .tar.xz is at most RP_MAX
        chunks, cur, size = [], [], 0
        for n in names:
            b = 512 + (os.path.getsize(os.path.join(L, n)) + 511) // 512 * 512
            if cur and size + b > RP_RAW:
                chunks.append(cur); cur, size = [], 0
            cur.append(n); size += b
        if cur:
            chunks.append(cur)
        done, k = [], 0
        while chunks:
            c = chunks.pop(0)
            tmp = rp_tarxz(c, os.path.join(R, 'realproofs', f, 'chunk.tar.xz'))
            if os.path.getsize(tmp) > RP_MAX and len(c) > 1:
                os.unlink(tmp); chunks[:0] = [c[:len(c) // 2], c[len(c) // 2:]]
                continue
            k += 1
            dst = os.path.join(R, 'realproofs', f, '%s_%02d.tar.xz' % (f, k))
            if os.path.exists(dst) and open(dst, 'rb').read() == open(tmp, 'rb').read():
                os.unlink(tmp)
            else:
                os.replace(tmp, dst)
            done.append(dst)
            rel = os.path.relpath(dst, R)
            index.extend('%s\t%s\t%s\n' % (n.rpartition('/proofs/')[2], n.rpartition('/proofs/')[0], rel) for n in c)
            commit([dst], 'realproofs: %s part %d (%d printed twee proofs, %.1f MB xz)' % (f, k, len(c), os.path.getsize(dst) / 1e6))
        for old in glob.glob(os.path.join(R, 'realproofs', f, '%s_*.tar.xz' % f)):
            if old not in done:
                git('rm', '-q', '--', os.path.relpath(old, R))
        print(f, len(names), 'proofs in', k, 'parts', ('(%d files without a Theorem line left out)' % bad) if bad else '',
              flush=True)
    if only:
        return
    tmp = os.path.join(R, 'realproofs', 'index.tsv')
    with open(tmp, 'w') as h:
        h.write('goal\tdir\ttarball\n'); h.writelines(sorted(index))
    gz(tmp, tmp + '.gz'); os.unlink(tmp)
    commit(['realproofs/index.tsv.gz', 'realproofs/README.md'], 'realproofs: index (goal, loop dir, tarball) and README')

def main_given():
    src = os.path.join(UL, 'given')
    by = {}
    for n in os.listdir(src):
        by.setdefault(orig(n), []).append(n)
    gd = os.path.join(R, 'given')
    os.makedirs(gd, exist_ok=True)
    for o in sorted(by):
        dst = os.path.join(gd, o + '.tar.xz')
        if os.path.exists(dst) and not git('status', '--porcelain', '--', 'given/' + o + '.tar.xz').strip():
            continue
        tmp = dst + '.tmp'
        files = sorted(by[o])
        subprocess.run('tar -C %s -cf - %s | xz -T1 -6 > %s' % (src, ' '.join(files), tmp), shell=True, check=True)
        os.replace(tmp, dst)
        commit(['given/' + o + '.tar.xz'], 'given: %s (%d rule logs, xz)' % (o, len(files)))

if __name__ == '__main__':
    os.makedirs(R, exist_ok=True)
    if not os.path.isdir(os.path.join(R, '.git')):
        subprocess.run(['git', 'init', '-q', '-b', 'main', R], check=True)
    if not os.path.exists(os.path.join(R, 'README.md')):
        shutil.copy(os.path.join(HW, 'abs/hintdata_README.md'), os.path.join(R, 'README.md'))
    if '--given' in sys.argv:
        main_given()
    elif '--climbs' in sys.argv:
        main_climbs()
    elif '--realproofs' in sys.argv:
        main_realproofs()
    else:
        main_data()

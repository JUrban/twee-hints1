#!/usr/bin/env python3
"""Build /project/hintwork/hintdata: a git repo of the loop's durable data, in small commits (user, 19 Nov 15:20:
"put the useful data into a separate new git repo in the hintwork directory; make the commits small so that I can
push incrementally on github later (no big files or commits)").

hintdata_build.py [--given | --climbs]   (without either: everything but the given logs and the climbs; --given: only the
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
    else:
        main_data()

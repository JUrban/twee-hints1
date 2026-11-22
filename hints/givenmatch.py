#!/usr/bin/env python3
"""(20 Nov) Unsolved goals that some successful run derived along the way (exp38, notes/2026-11-20-given-transfer.md).

transfer.py matches unsolved goals against the steps of proofs (hints files). Every successful run's given log
(loops/*/given/NAME: label, index, lhs, rhs, parents) also holds the rules it derived and did not use: about 380 M,
against 22 M proof steps. A rule derived in a run on an unconditional unit goal is a consequence of that original's
axioms and the run's (proven) lemmas. So an unsolved goal of an original with the same or more axioms that is a
variant of such a rule is a theorem, and the rule's ancestry in that log (its parents, closed) is a proof sketch for it.

Twee prints each logged rule with its variables numbered in order of occurrence (checked: 66,797 of 66,797), so a
variant is a dict lookup of the raw (lhs, rhs) pair, against both orientations of each goal.

  givenmatch.py INDEX OUT.tsv [-j 4] [--loops-exclude REGEX] [--instances]
(--instances: the goal is an instance of the rule, not only a variant; own original's logs only)
OUT: goal, source loop, source name, rule index, label (0 not in that proof, 1 a proof step), ancestry size.

  givenmatch.py sketch OUT.tsv SKDIR GOALS.tsv [--per 3] [--prefix]
writes each hit's ancestry (index order, the matched rule last) to SKDIR/<goal>/<loop>/<source name> as hints, the
ancestry's axioms of the source run to the same name + .ax, and GOALS.tsv for transfer.py run (goal, the sketch
files, 0).

  givenmatch.py live DIR [--dirs UL,XFL] [--every 1200] [-j 2] [--dst UL] [--gfail GFAIL,GSAT] [--set ALL] [--no-same]
                   [--cap 60] [--same-cap N] [--no-wait] [--no-inst] [--loops /project/hintwork/loops] -- LOOP-OPTIONS
beside production: each cycle scans the logs written since the last one and runs the new hits (see live()).
"""
import os, re, sys
from multiprocessing import get_context

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hintlib, hintsel, lemmas

LOOPS = '/project/hintwork/loops'
ALL = '/project/hintwork/sets/all'
# (climbers' runs may use unproven assumptions; 'bad' loops are known broken)
EXCL = r'^(CL|FUD|SMK)|bad'

W = None   # (in the workers: key -> goals; with --instances, lhs root -> [(goal, lhs, rhs, parsed lhs, parsed rhs)])
INST = False


def root_s(t):
    i = t.find('(')
    return t[:i] if i >= 0 else t


def scan_inst(lines_iter, o):
    """(--instances) the goals of the log's own original O that are instances of a rule: one-way matching of the
    rule onto both orientations, after cheap filters (the lhs root, the rhs root unless the rhs is a variable, no
    more applications than the goal). Only the own original's goals: across originals the root buckets hold
    thousands of goals (AIM has few function symbols), 50 times the variant scan's time."""
    import transfer
    out = []
    for l in lines_iter:
        w = l.split('\t', 4)
        if len(w) < 4 or w[0] == '-1':
            continue
        cs = W.get((o, root_s(w[2])))
        if not cs:
            continue
        r = w[3].rstrip('\n')
        rv = r[0].isupper() and '(' not in r
        rr = None if rv else root_s(r)
        na = w[2].count('(') + r.count('(')
        pl = pr = None
        for g, gl, gr, pgl, pgr, gna in cs:
            if gna < na or (rr is not None and root_s(gr) != rr):
                continue
            if pl is None:
                pl, pr = transfer.parse(w[2]), transfer.parse(r)
            sub = transfer.match(pl, pgl, {})
            if sub is not False and transfer.match(pr, pgr, sub) is not False:
                out.append((g, w[1], w[0]))
    return out


def gkeys(n):
    lits = hintsel.goal_lits(n)
    if len(lits) != 1 or not lits[0][0]:
        return None
    l, r = lits[0][1], lits[0][2]
    sig = set(re.findall(r'[a-z]\w*', l + ' ' + r))
    return {hintlib.generalize(l, r, sig), hintlib.generalize(r, l, sig)}


def ancestry(lines, idx):
    """indexes of the rule IDX and all its ancestors in a parsed log"""
    par = {}
    for w in lines:
        # (20 Nov 04:08) parents are rule numbers, the rule at position k having number k+1 (given.py); read as
        # positions until now, so the ancestries followed the wrong rules (proof steps' parents are proof steps or
        # axioms in 94% as numbers, 66% as positions)
        par[w[1]] = [str(int(p) - 1) for p in w[4:6] if p not in ('0', '')]
    out = set(); todo = [idx]
    while todo:
        x = todo.pop()
        if x in out:
            continue
        out.add(x); todo.extend(par.get(x, ()))
    return out


def scan(job):
    loop, name = job
    p = os.path.join(LOOPS, loop, 'given', name)
    hits = []
    try:
        f = open(p)
    except OSError:
        return hits
    with f:
        if INST:
            hits = scan_inst(f, lemmas.split(name)[0])
        for l in ([] if INST else f):
            w = l.split('\t', 4)   # (label, index, lhs, rhs, the rest: the whole log is parsed only on a hit)
            if len(w) >= 4 and w[0] != '-1':
                gs = W.get((w[2], w[3].rstrip('\n')))
                if gs:
                    hits.extend((g, w[1], w[0]) for g in gs)
    if hits:
        lines = [l.rstrip('\n').split('\t') for l in open(p)]
        hits = [(g, loop, name, i, lab, len(ancestry(lines, i))) for g, i, lab in hits]
    return hits


def init(w, inst=False):
    global W, INST
    W = w; INST = inst


_KM, _KMS = {}, set()


def lemma_ax(gp, skdir, S):
    """(22 Nov 12:05, exp56b, notes/2026-11-22-gm-retry.md) name the sketches' source-run lemma axioms after their
    proven goals. loop.py's given_scan labels only the original's axioms as -1, so a failed run's lemma axioms (its
    sibling and kNN lemmas, proven goals) are parentless label-0 rules of its log, and sketch() leaves them out of the
    .ax: GMR's ancestry pass proved 0 of 30 such goals, GMR2's with them 7 of its first 12. Every parentless rule of
    the source log, and every unnamed .ax row, that is the statement of a goal in S (gkeys) whose axioms are within
    the target's goes into the .ax with that goal's name in the third column; transfer.py then names the axiom
    skax_<i>_<goal>, which exp/trust.py resolves. GP: a goals file of sketch(), SKDIR its sketch dir, S the solved goals."""
    import lemmas
    for m in set(S) - _KMS:
        _KMS.add(m)
        try:
            ks = gkeys(m)
        except Exception:
            continue
        for k in ks or ():
            _KM.setdefault(k, []).append(m)
    tot = 0
    for l in open(gp):
        g, fs = l.split('\t')[:2]
        A = lemmas.axiom_set(g)
        def name(k):
            ms = sorted(m for m in _KM.get(k, ()) if m != g and lemmas.axiom_set(m) <= A)
            return ms[0] if ms else None
        for f in fs.split(','):
            rel = os.path.relpath(f, skdir).split(os.sep)   # g / LOOP (one or two parts) / name
            log = os.path.join(LOOPS, *rel[1:-1], 'given', rel[-1])
            rows, seen = [], set()
            for x in (open(f + '.ax') if os.path.exists(f + '.ax') else ()):
                w = x.rstrip('\n').split('\t')
                if len(w) >= 2:
                    nm = w[2] if len(w) > 2 and w[2] else name((w[0], w[1]))
                    rows.append((w[0], w[1], nm or '')); seen.add((w[0], w[1]))
            n0 = sum(1 for r in rows if r[2])
            for x in open(log):
                w = x.rstrip('\n').split('\t')
                if len(w) >= 6 and w[0] == '0' and w[4] == '0' and w[5] == '0' and (w[2], w[3]) not in seen:
                    nm = name((w[2], w[3]))
                    if nm:
                        rows.append((w[2], w[3], nm)); seen.add((w[2], w[3]))
            with open(f + '.ax.tmp', 'w') as fo:
                fo.writelines(f'{a}\t{b}\t{c}\n' if c else f'{a}\t{b}\n' for a, b, c in rows)
            os.replace(f + '.ax.tmp', f + '.ax')
            tot += sum(1 for r in rows if r[2])
    print(f'--lemma-ax: {tot} named lemma axioms in the sketches of {gp}', flush=True)


def sketch(hits, skdir, goals, per=3, prefix=False):
    by = {}
    for l in open(hits):
        w = l.rstrip('\n').split('\t')
        by.setdefault(w[0], []).append(w)
    with open(goals, 'w') as fo:
        for g, hs in sorted(by.items()):
            fs = []
            for w in hs[:per]:
                _, loop, name, ridx = w[:4]
                lines = [x.rstrip('\n').split('\t') for x in open(os.path.join(LOOPS, loop, 'given', name))]
                # (--prefix, 20 Nov 03:12) every rule up to the matched one, in order: the log's parents are the
                # critical pair's only, without the rewriting steps, so an ancestry can lack most of the derivation
                # (mbol_asqr 512: rule 7723 with 1 recorded parent)
                keep = {x[1] for x in lines if len(x) >= 4 and int(x[1]) <= int(ridx)} if prefix else ancestry(lines, ridx)
                rows = [x for x in lines if len(x) >= 4 and x[1] in keep and x[0] != '-1']   # (axioms are axioms)
                rows.sort(key=lambda x: int(x[1]))
                p = os.path.abspath(os.path.join(skdir, g, loop, name))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, 'w') as f:
                    f.writelines(f'{x[2]}\t{x[3]}\n' for x in rows)
                # (20 Nov 03:08) the source run's axioms in the ancestry, for transfer.py run as lemma axioms: its
                # lemmas (proven goals of the same or weaker axioms, pool hints as axioms) differ from the target
                # run's, and without them 11 of 19 sketches failed
                axr = [x for x in lines if len(x) >= 4 and x[1] in keep and x[0] == '-1']
                with open(p + '.ax', 'w') as f:
                    f.writelines(f'{x[2]}\t{x[3]}\n' for x in axr)
                fs.append(p)
            fo.write(f'{g}\t{",".join(fs)}\t0\n')
    print(f'{len(by)} goals -> {goals}')


def live(dirs, d, every, j, rest, dst='UL', gfail=('GFAIL', 'GSAT'), allp=ALL, same=True, cap=60, inst_scan=True,
         same_cap=None, nowait=False, retry_h=0.0, lax=False):
    """(20 Nov 03:45) beside production: every EVERY s, scan the given logs of DIRS written since the last cycle against
    production's unsolved unit goals (variants; instances within the own original), and run each new hit as exp38
    did: the rule's ancestry first at 20 s, then for the failures the log's prefix with its axioms at 40 s
    (transfer.py run, proofs into loops/UL). Old logs need no rescan: the targets only shrink.
    (06:35) For any loop, e.g. a from-zero one: DST (its solved.tsv and hints, where the proofs go), GFAIL (the dirs
    under loops/ that its --given-scan writes), ALLP (its goal set), SAME (the same-statement finder)."""
    import subprocess, time, transfer
    os.makedirs(d, exist_ok=True)
    if not os.path.lexists(os.path.join(d, 'hints')):
        os.symlink(os.path.join(LOOPS, dst, 'hints'), os.path.join(d, 'hints'))
    wmp = os.path.join(d, 'watermark')
    wm = float(open(wmp).read()) if os.path.exists(wmp) else time.time()
    triedp = os.path.join(d, 'tried.tsv')
    tried = {l.split('\t')[0] for l in open(triedp)} if os.path.exists(triedp) else set()
    # (22 Nov 12:01, --retry-tried H; exp56, notes/2026-11-22-gm-retry.md) a tried goal runs again on the hits that came
    # after its last try, at most once every H hours, newest hits first: of the 30 tried goals left unsolved, 5 fell to
    # the prefix pass on their newest hits (goal_673 had 229 hit rows from 32 source runs). Rows of tried.tsv carry
    # the try's time (third column; older rows count as time 0)
    tried_t = {}
    if os.path.exists(triedp):
        for l in open(triedp):
            w_ = l.rstrip('\n').split('\t')
            tried_t[w_[0]] = float(w_[2]) if len(w_) > 2 and w_[2] else 0.0
    later = {}   # (--retry-tried) the hits of tried goals since their last try, until they may run again
    def blocked(g):
        return g in tried and not (retry_h and time.time() - tried_t.get(g, 0.0) >= retry_h * 3600)
    def hstamp(h):
        m_ = re.match(r'[^/]+/(\d{13})_', h[1])
        return int(m_.group(1)) / 1000 if m_ else 0.0
    me = os.path.abspath(__file__); tp = os.path.join(os.path.dirname(me), 'transfer.py')
    ax = {}
    def axs(n):
        o = lemmas.split(n)[0]
        if o not in ax:
            ax[o] = lemmas.axiom_set(n)
        return ax[o]
    cyc = 0; run_ = time.strftime('%d%H%M')   # (cycle files carry the process's start, so a restart keeps the old)
    # (07:20, exp40) from zero most hits are goals the loop has not tried yet and proves at its first level (the 2nd
    # cycle had 3,975 goals hit). So a hit waits in PENDING until the loop has a failed run of its goal (a NO row in
    # LOOPS/DST/r*/results.tsv, read incrementally), and at most CAP goals run per cycle, oldest first. Production's
    # unsolved goals have all failed and its hits are few, so it runs as before.
    pending = {}; failed = set(); roff = {}
    def read_failed():
        import glob
        for rp in glob.glob(os.path.join(LOOPS, dst, 'r*', 'results.tsv')):
            with open(rp) as f:
                f.seek(roff.get(rp, 0))
                while True:
                    l = f.readline()
                    if not l.endswith('\n'):
                        break
                    w = l.split('\t', 2)
                    if len(w) >= 2 and w[1] == 'NO':
                        failed.add(w[0])
                roff[rp] = f.tell() - (len(l.encode()) if l else 0)
    while True:
        t0 = time.time(); cyc += 1
        S = {l.split('\t')[0] for l in open(os.path.join(LOOPS, dst, 'solved.tsv'))}
        want = {}
        for n in (l.strip() for l in open(allp)):
            if n and n not in S and (n not in tried or retry_h):
                try:
                    ks = gkeys(n)
                except Exception:
                    continue
                for k in ks or ():
                    want.setdefault(k, []).append(n)
        byroot = {}
        for (l, r), gs in want.items():
            for g in gs:
                byroot.setdefault((lemmas.split(g)[0], root_s(l)), []).append(
                    (g, l, r, transfer.parse(l), transfer.parse(r), l.count('(') + r.count('(')))
        jobs = []; top = wm
        for dd in dirs:
            gd = os.path.join(LOOPS, dd, 'given')
            for name in os.listdir(gd) if os.path.isdir(gd) else ():
                try:
                    t = os.path.getmtime(os.path.join(gd, name))
                except OSError:
                    continue
                if t > wm:
                    top = max(top, t)
                    try:
                        if lemmas.unit_eq(lemmas.conjecture(name) or '~'):
                            jobs.append((dd, name))
                    except OSError:
                        pass
        hits = {}
        for inst, w in ((False, want), (True, byroot)) if inst_scan else ((False, want),):
            init(w, inst)
            for job in jobs:
                for h in scan(job):
                    if h[0] not in S and axs(h[2]) <= axs(h[0]):
                        hits.setdefault(h[0], []).append(h)
        # (20 Nov 04:13) the hits production's failed runs found (loop.py --given-scan loops/GFAIL), from the offset
        # read so far; their logs are loops/GFAIL/<stamp>/given/<name>
        # (05:40) and those of the base-theory runs (exp/gensat.py, loops/GSAT; exp39)
        nf = 0
        for gdir_ in gfail:
          offn_ = gdir_.lower() + '_offset'
          gfp = os.path.join(LOOPS, gdir_, 'hits.tsv'); offp = os.path.join(d, offn_)
          if os.path.exists(gfp):
            off = int(open(offp).read()) if os.path.exists(offp) else 0
            with open(gfp) as f:
                f.seek(off)
                for l in f:
                    if not l.endswith('\n'):
                        break
                    off += len(l.encode())
                    w = l.rstrip('\n').split('\t')
                    if len(w) >= 6 and w[0] not in S and (w[0] not in tried or retry_h):
                        hits.setdefault(w[0], []).append(tuple(w[:3]) + (w[3], w[4], int(w[5]))); nf += 1
            open(offp, 'w').write(str(off))
        print(f'cycle {cyc} {time.strftime("%H:%M:%S")}: {len(want)} target keys, {len(jobs)} new logs, '
              f'{nf} failed-run hits, {len(hits)} goals hit', flush=True)
        for g, v in hits.items():
            pending.setdefault(g, []).extend(v)
        read_failed()
        for g in [g for g in pending if g in S or g in tried]:
            v_ = pending.pop(g)
            if retry_h and g not in S:
                later[g] = (later.get(g, []) + v_)[-50:]
        for g in [g for g in later if g in S]:
            del later[g]
        if retry_h:
            back = [g for g in later if not blocked(g)]
            for g in back:
                pending[g] = later.pop(g)
            if back or later:
                print(f'  --retry-tried: {len(back)} tried goals back with newer hits, {len(later)} waiting', flush=True)
        # (20 Nov 12:14 --no-wait: a hit runs without waiting for the loop to fail on its goal; exp42's ancestry runs
        # proved 93% at about 4 s each while about 290 hits waited)
        hits = {g: pending.pop(g) for g in [g for g in pending if nowait or g in failed][:cap]}
        print(f'  {len(hits)} goals to run (failed in the loop), {len(pending)} pending', flush=True)
        if hits:
            hp = os.path.join(d, f'hits_{run_}_{cyc}.tsv')
            with open(hp, 'w') as fo:
                for g in sorted(hits):
                    for h in sorted(set(hits[g]), key=lambda h: (h[5], -hstamp(h), h[1], h[2]) if retry_h
                                    else (h[5], h[1], h[2]))[:5]:
                        fo.write('\t'.join(map(str, h)) + '\n')
            with open(os.path.join(d, 'solved.tsv'), 'w') as f:   # (production's proofs as context, round 0)
                for l in open(os.path.join(LOOPS, dst, 'solved.tsv')):
                    w_ = l.split('\t')
                    if len(w_) >= 3 and l.endswith('\n'):
                        f.write(f'{w_[0]}\t0\t{w_[2].strip()}\n')
            for tag, pre, T in (('a', False, 20), ('p', True, 40)):
                gp = os.path.join(d, f'goals_{run_}_{cyc}{tag}.tsv')
                sketch(hp, os.path.join(d, 'sketch' + tag), gp, 3, pre)
                if lax:   # (--lemma-ax)
                    lemma_ax(gp, os.path.join(d, 'sketch' + tag), S)
                if tag == 'p':   # (only the goals the first pass left)
                    S2 = {l.split('\t')[0] for l in open(os.path.join(LOOPS, dst, 'solved.tsv'))}
                    keep = [l for l in open(gp) if l.split('\t')[0] not in S2]
                    open(gp, 'w').writelines(keep)
                    if not keep:
                        break
                subprocess.run([sys.executable, tp, 'run', gp, d, '-j', str(j), '--time', str(T), '--src-lemmas', '6',
                                '--live-dst', os.path.join(LOOPS, dst), '--'] + rest)
            with open(triedp, 'a') as f:
                f.writelines(f'{g}\t{cyc}\t{time.time():.0f}\n' for g in sorted(hits))
            tried |= set(hits); tried_t.update((g, time.time()) for g in hits)
        # (20 Nov 04:30) the same statement proven in a theory with more axioms (REPORT 2ar; exp/sofree.py): the
        # candidates whose first source proof has no missing axiom as a step, new (goal, first source) pairs only,
        # source proof steps first, 20 s (46 at 04:18 gave 9, 26 per CPU h)
        sys.path.insert(0, os.path.join(os.path.dirname(me), 'exp'))
        import sofree
        sop = set()
        if not same:
            wm = top
            open(wmp, 'w').write(repr(wm))
            time.sleep(max(0, every - (time.time() - t0)))
            continue
        for dd in ('SOF', 'SOP', 'SOR', 'SO2run', os.path.basename(d)):
            p_ = os.path.join(LOOPS, dd, 'transfer.tsv')
            if os.path.exists(p_):
                for l in open(p_):
                    w_ = l.rstrip('\n').split('\t')
                    if len(w_) >= 5:
                        sop.add((w_[0], w_[4].split(',')[0]))
        so, nso = sofree.candidates(os.path.join(d, 'so_all.tsv'), tried_pairs=sop, dst=os.path.join(LOOPS, dst),
                                    allp=allp)
        n0 = len(so)
        # (07:25: as the hits, exp40's 1st cycle had 808; 20 Nov 10:40 --same-cap: exp40's same-statement runs made
        # 80 proofs per CPU h against the ancestry runs' 790, and took most of each cycle)
        so = [l for l in so if nowait or l.split('\t')[0] in failed][:cap if same_cap is None else same_cap]
        print(f'  same statement: {nso} candidates, {n0} new free ones, {len(so)} failed in the loop to run', flush=True)
        if so:
            gp = os.path.join(d, f'so_{run_}_{cyc}.tsv')
            open(gp, 'w').writelines(so)
            subprocess.run([sys.executable, tp, 'run', gp, d, '-j', str(j), '--time', '20', '--src-lemmas', '6',
                            '--live-dst', os.path.join(LOOPS, dst), '--'] + rest)
        wm = top
        open(wmp, 'w').write(repr(wm))
        time.sleep(max(0, every - (time.time() - t0)))


def main():
    global LOOPS
    if sys.argv[1] == 'live':
        argv = sys.argv[2:]
        i = argv.index('--')
        opts, rest = argv[:i], argv[i + 1:]
        val = lambda k, dflt: type(dflt)(opts[opts.index(k) + 1]) if k in opts else dflt
        # (20 Nov 09:20) --loops: the directory that holds DST, DIRS and GFAIL (default /project/hintwork/loops), for
        # loops elsewhere (solve_new.sh); the hits' loop column (basename(GFAIL)/stamp) is relative to it
        LOOPS = os.path.abspath(val('--loops', LOOPS))
        return live(val('--dirs', 'UL,XFL').split(','), opts[0], val('--every', 1200.0), val('-j', 2), rest,
                    dst=val('--dst', 'UL'), gfail=[x for x in val('--gfail', 'GFAIL,GSAT').split(',') if x],
                    allp=val('--set', ALL), same='--no-same' not in opts, cap=val('--cap', 60),
                    inst_scan='--no-inst' not in opts, same_cap=val('--same-cap', -1) if '--same-cap' in opts else None,
                    nowait='--no-wait' in opts, retry_h=val('--retry-tried', 0.0), lax='--lemma-ax' in opts)
    if sys.argv[1] == 'sketch':
        per = int(sys.argv[sys.argv.index('--per') + 1]) if '--per' in sys.argv else 3
        return sketch(sys.argv[2], sys.argv[3], sys.argv[4], per, '--prefix' in sys.argv)
    idx, out = sys.argv[1], sys.argv[2]
    j = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 4
    excl = sys.argv[sys.argv.index('--loops-exclude') + 1] if '--loops-exclude' in sys.argv else EXCL
    inst = '--instances' in sys.argv
    S = {l.split('\t')[0] for l in open(os.path.join(LOOPS, 'UL', 'solved.tsv'))}
    want = {}
    ng = 0
    for n in (l.strip() for l in open(ALL)):
        if not n or n in S:
            continue
        try:
            ks = gkeys(n)
        except Exception:
            continue
        if ks:
            ng += 1
            for k in ks:
                want.setdefault(k, []).append(n)
    ax = {}
    def axs(n):
        o = lemmas.split(n)[0]
        if o not in ax:
            ax[o] = lemmas.axiom_set(n)
        return ax[o]
    tax = [axs(g) for gs in want.values() for g in gs]
    torig = {lemmas.split(g)[0] for gs in want.values() for g in gs}
    unit = {}; ucache = {}; climbdir = {}
    jobs = []
    for l in open(idx):
        w = l.rstrip('\n').split('\t')
        name, loop = w[0], w[1]
        if loop not in climbdir:
            climbdir[loop] = bool(re.search(excl, loop)) or os.path.exists(os.path.join(LOOPS, loop, 'climb.tsv'))
        if climbdir[loop]:   # (F80, F80b: climber directories by their records, not their names)
            continue
        o = lemmas.split(name)[0]
        if inst and o not in torig:   # (--instances: the own original's goals only)
            continue
        if o not in unit:
            try:
                unit[o] = None
                A = axs(name)
                # (a source original whose axioms are within no target's: nothing to give)
                unit[o] = any(A <= t for t in tax)
            except Exception:
                unit[o] = False
        if not unit[o]:
            continue
        if name not in ucache:
            try:
                ucache[name] = bool(lemmas.unit_eq(lemmas.conjecture(name) or '~'))
            except OSError:
                ucache[name] = False
        if ucache[name]:
            jobs.append((loop, name))
    print(f'{ng} unsolved unit goals, {len(jobs)} logs to scan ({j} workers)', flush=True)
    hits = {}
    if inst:
        # (both orientations of each goal, by the root of the side the rule's lhs must match)
        import transfer
        byroot = {}
        for (l, r), gs in want.items():
            for g in gs:
                byroot.setdefault((lemmas.split(g)[0], root_s(l)), []).append((g, l, r, transfer.parse(l), transfer.parse(r),
                                                        l.count('(') + r.count('(')))
        want = byroot
    with get_context('fork').Pool(j, initializer=init, initargs=(want, inst)) as pool:
        for k, hs in enumerate(pool.imap_unordered(scan, jobs, chunksize=64)):
            for h in hs:
                g, loop, name = h[0], h[1], h[2]
                if axs(name) <= axs(g):
                    hits.setdefault(g, []).append(h)
            if k % 50000 == 0:
                print(f'  {k} logs, {len(hits)} goals hit', flush=True)
    with open(out, 'w') as fo:
        for g in sorted(hits):
            # (smallest ancestry first: the shortest sketch)
            for h in sorted(set(hits[g]), key=lambda h: (h[5], h[1], h[2]))[:5]:
                fo.write('\t'.join(map(str, h)) + '\n')
    print(f'{len(hits)} unsolved goals are variants of rules derived in runs from the same or weaker axioms -> {out}')


if __name__ == '__main__':
    main()

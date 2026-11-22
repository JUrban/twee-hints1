#!/usr/bin/env python3
"""(22 Nov 11:04) Retry the goals givenmatch.py live tried and failed, from their newest failed-run hits.

givenmatch.py live runs a hit goal once (the 20 s ancestry pass, then the 40 s prefix pass) and then lists it in
DIR/tried.tsv for good. Its failed-run hits (loop.py --given-scan) all have ancestry size 0, so its sort by size
took the oldest logs. Production keeps deriving some of these goals in later failed runs (ns_to_aa1_b 673: 229
hits from 32 source runs by 22 Nov 10:15). This runs the same two passes, on the newest PER hits of distinct
sources, for every tried goal still unsolved in production.

usage: gmretry.py OUT [-j J] [--per K] [--min-hits N] [--lemma-ax] [--only FILE] [--dry] -- TRANSFER_ARGS (as GML's)
OUT is a new directory; proofs go into production (loops/UL) as GML's do.

--lemma-ax (22 Nov 11:25): loop.py's given_scan labels only the original's axioms as axioms (-1), so a failed run's lemma
axioms (its sibling and kNN lemmas, proven goals) are label-0 rules without parents in its log, and the sketch's .ax
lacks them. With --lemma-ax every parentless rule of the source log that is the statement of a proven goal of
production (givenmatch.gkeys) whose axioms are within the target's goes into the .ax, with that goal's name in the
third column: transfer.py then names the axiom skax_<i>_<goal>, which exp/trust.py resolves.
--only FILE: only the goals listed in FILE.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import givenmatch

LOOPS = givenmatch.LOOPS


def lemma_ax(gp, skdir, S):
    """(--lemma-ax) givenmatch.lemma_ax: the source runs' lemma axioms into the sketches' .ax, named by proven goal"""
    givenmatch.lemma_ax(gp, skdir, S)


def main():
    args = sys.argv[1:]
    rest = args[args.index('--') + 1:] if '--' in args else []
    opts = args[:args.index('--')] if '--' in args else args
    out = opts[0]
    val = lambda k, d: type(d)(opts[opts.index(k) + 1]) if k in opts else d
    j, per, minh = val('-j', 1), val('--per', 3), val('--min-hits', 1)
    dst = os.path.join(LOOPS, 'UL')
    S = {l.split('\t')[0] for l in open(os.path.join(dst, 'solved.tsv'))}
    tried = {}
    for l in open(os.path.join(LOOPS, 'GML', 'tried.tsv')):
        w = l.rstrip('\n').split('\t')
        tried.setdefault(w[0], w[1] if len(w) > 1 else '')
    hits = {}
    for gd in ('GFAIL', 'GSAT'):
        p = os.path.join(LOOPS, gd, 'hits.tsv')
        if not os.path.exists(p):
            continue
        for l in open(p):
            w = l.rstrip('\n').split('\t')
            if len(w) >= 6 and w[0] in tried and w[0] not in S \
                    and os.path.exists(os.path.join(LOOPS, w[1], 'given', w[2])):
                hits.setdefault(w[0], []).append(w[:6])
    if '--only' in opts:
        keep_ = {l.strip() for l in open(val('--only', ''))}
        hits = {g: v for g, v in hits.items() if g in keep_}
    sel = {}
    for g, hs in hits.items():
        if len(hs) < minh:
            continue
        hs.sort(key=lambda w: int(w[1].split('/')[1].split('_')[0]), reverse=True)   # (DIR/<ms stamp>_...: newest first)
        seen, keep = set(), []
        for w in hs:
            if w[2] not in seen:
                seen.add(w[2]); keep.append(w)
            if len(keep) >= per:
                break
        sel[g] = keep
    print(f'{len(tried)} tried, {sum(1 for g in tried if g not in S)} unsolved, {len(sel)} with hits '
          f'(rows {sum(len(v) for v in hits.values())})', flush=True)
    for g in sorted(sel):
        print(f'  {g}: {len(hits[g])} hits, newest {sel[g][0][1]} ({sel[g][0][2]})')
    if '--dry' in opts or not sel:
        return
    os.makedirs(out)
    os.symlink(os.path.join(dst, 'hints'), os.path.join(out, 'hints'))
    with open(os.path.join(out, 'solved.tsv'), 'w') as f:   # (production's proofs as context, round 0)
        for l in open(os.path.join(dst, 'solved.tsv')):
            w_ = l.split('\t')
            if len(w_) >= 3 and l.endswith('\n'):
                f.write(f'{w_[0]}\t0\t{w_[2].strip()}\n')
    hp = os.path.join(out, 'hits.tsv')
    with open(hp, 'w') as fo:
        for g in sorted(sel):
            for w in sel[g]:
                fo.write('\t'.join(w) + '\n')
    tp = os.path.join(os.path.dirname(givenmatch.__file__), 'transfer.py')
    for tag, pre, T in (('a', False, 20), ('p', True, 40)):
        gp = os.path.join(out, f'goals_{tag}.tsv')
        givenmatch.sketch(hp, os.path.join(out, 'sketch' + tag), gp, per, pre)
        if '--lemma-ax' in opts:
            lemma_ax(gp, os.path.join(out, 'sketch' + tag), S)
        S2 = {l.split('\t')[0] for l in open(os.path.join(dst, 'solved.tsv'))}
        keep = [l for l in open(gp) if l.split('\t')[0] not in S2]
        open(gp, 'w').writelines(keep)
        if not keep:
            break
        subprocess.run([sys.executable, tp, 'run', gp, out, '-j', str(j), '--time', str(T), '--src-lemmas', '6',
                        '--live-dst', dst, '--'] + rest)


if __name__ == '__main__':
    main()

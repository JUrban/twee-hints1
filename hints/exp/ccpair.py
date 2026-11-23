"""ccpair.py CLIMB CONTROL [--md]: a climber arm against its long-run control on the same frozen targets (23 Nov,
exp67: CLA67/CC67, CLB67/CC67B; notes/2026-11-23-climber-restart.md "The control").

A target is finished in a dir when it has a final row in climb.tsv or a real proof (solved.tsv round 1). On the
targets both dirs finished: proofs of each, both, only one (+/-), the union, and CPU h (climb.tsv's seconds summed
over those targets' rows: every sketch, fill, final and direct run of the climb; the control's one final run)."""
import collections, os, sys

L = '/project/hintwork/loops'


def load(d):
    p = d if '/' in d else os.path.join(L, d)
    cpu = collections.Counter(); fin = set()
    for l in open(os.path.join(p, 'climb.tsv')):
        w = l.rstrip('\n').split('\t')
        if len(w) < 6:
            continue
        try:
            cpu[w[0]] += float(w[5])
        except ValueError:
            pass
        if w[1] == 'final':
            fin.add(w[0])
    real = {l.split('\t')[0] for l in open(os.path.join(p, 'solved.tsv')) if l.split('\t')[1:2] == ['1']}
    return os.path.basename(p), cpu, fin | real, real


def main():
    md = '--md' in sys.argv
    a, b = [x for x in sys.argv[1:] if x != '--md'][:2]
    na, ca, fa, ra = load(a); nb, cb, fb, rb = load(b)
    T = fa & fb
    pa, pb = ra & T, rb & T
    ha = sum(ca[t] for t in T) / 3600; hb = sum(cb[t] for t in T) / 3600
    u = pa | pb
    if md:
        print(f'| | {na} | {nb} |\n|---|---:|---:|')
        print(f'| targets both finished | {len(T)} | {len(T)} |')
        print(f'| proved | {len(pa)} | {len(pb)} |')
        print(f'| only this arm | {len(pa - pb)} | {len(pb - pa)} |')
        print(f'| CPU h on these targets | {ha:.2f} | {hb:.2f} |')
        print(f'| proofs per CPU h | {len(pa) / ha if ha else 0:.2f} | {len(pb) / hb if hb else 0:.2f} |')
        print(f'\nUnion {len(u)}, both {len(pa & pb)}. Only {na}: {", ".join(sorted(pa - pb)) or "-"}. '
              f'Only {nb}: {", ".join(sorted(pb - pa)) or "-"}.')
    else:
        print(f'{na} vs {nb}: {len(T)} targets both finished; proved {len(pa)} / {len(pb)}, +{len(pa - pb)} -{len(pb - pa)}, '
              f'union {len(u)}; CPU h {ha:.2f} / {hb:.2f}')
        print(f'  only {na}: {" ".join(sorted(pa - pb))}')
        print(f'  only {nb}: {" ".join(sorted(pb - pa))}')
        # the rest each dir has finished (not yet in the other)
        print(f'  finished only in {na}: {len(fa - fb)} (proved {len(ra - fb)}); only in {nb}: {len(fb - fa)} (proved {len(rb - fa)})')


if __name__ == '__main__':
    main()

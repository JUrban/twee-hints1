#!/usr/bin/env python3
"""(19 Nov) Training lists from models/given_index.tsv (givenindex.py): per goal, up to K distinct proofs over all
loops, for rulemodel.py --list. Distinct = different (positives, negatives) counts; identical copies are one proof.

givensel.py INDEX OUT MODE [K] [--exclude NAMES] [--seed S] [--loops-root DIR]
  MODE short: the K shortest proofs (fewest positives)            (user, 19:35: "the shortest 3 proofs")
       slm:   the shortest, a medium and the longest               (Mizar60 6.4)
       rand:  up to K random                                       (Mizar60 6.4: "randomly up to 6")
       long:  the K longest
"""
import collections, os, random, sys

def main():
    argv = sys.argv[1:]
    opt = {}
    for k in ('--exclude', '--seed', '--loops-root'):
        if k in argv:
            i = argv.index(k); opt[k] = argv[i + 1]; del argv[i:i + 2]
    idx, out, mode = argv[:3]
    K = int(argv[3]) if len(argv) > 3 else 3
    root = opt.get('--loops-root', '/project/hintwork/loops')
    ex = set(open(opt['--exclude']).read().split()) if '--exclude' in opt else set()
    rnd = random.Random(int(opt.get('--seed', 1)))
    by = collections.defaultdict(dict)
    for l in open(idx):
        n, d, size, pos, neg, mt = l.rstrip('\n').split('\t')
        if n in ex:
            continue
        key = (int(pos), int(neg))
        # (distinct proofs; for copies prefer production's, then the first seen)
        if key not in by[n] or d == 'UL':
            by[n][key] = d
    nl = 0; npos = 0
    with open(out + '.tmp', 'w') as f:
        for n in sorted(by):
            ps = sorted(by[n].items())   # by positives, then negatives
            if mode == 'short':
                sel = ps[:K]
            elif mode == 'long':
                sel = ps[-K:]
            elif mode == 'slm':
                sel = [ps[0], ps[len(ps) // 2], ps[-1]]
                sel = list(dict.fromkeys(sel))
            elif mode == 'rand':
                sel = rnd.sample(ps, min(K, len(ps)))
            else:
                raise SystemExit('mode?')
            for (p, _), d in sel:
                f.write(f'{n}\t{os.path.join(root, d, "given", n)}\n'); nl += 1; npos += p
    os.replace(out + '.tmp', out)
    print(f'{len(by)} goals, {nl} logs, {npos} positives', flush=True)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""(20 Nov 11:36) The re-verification's end (notes/2026-11-20-p9-negation-bug.md): the goals exp/trust.py still finds
untrusted leave production's solved list. Their rows go to loops/UNSOUND/removed_<stamp>.tsv, their hints to
loops/UNSOUND/qhints2/ (a hints file already there is kept, the new one gets a .<stamp> suffix). Run only while every
writer of loops/UL/solved.tsv is stopped (production, the transfer and live loops, stepjlive, rever2), and restart
them after: loop.py holds its solved set in memory.

  quarantine2.py UNTRUSTED.txt [--dry]
"""
import os, shutil, sys, time
L = '/project/hintwork/loops'


def main():
    bad = {l.strip() for l in open(sys.argv[1]) if l.strip()}
    dry = '--dry' in sys.argv
    stamp = time.strftime('%d%H%M')
    sp = os.path.join(L, 'UL', 'solved.tsv')
    rows = open(sp).readlines()
    keep = [l for l in rows if l.split('\t')[0] not in bad]
    gone = [l for l in rows if l.split('\t')[0] in bad]
    goals = sorted({l.split('\t')[0] for l in gone})
    print(f'{len(rows)} rows, {len(gone)} rows of {len(goals)} goals out ({len(bad)} untrusted listed)', flush=True)
    if dry:
        return
    shutil.copy2(sp, os.path.join(L, 'UNSOUND', f'UL_solved.tsv.{stamp}'))
    open(os.path.join(L, 'UNSOUND', f'removed_{stamp}.tsv'), 'w').writelines(gone)
    qd = os.path.join(L, 'UNSOUND', 'qhints2'); os.makedirs(qd, exist_ok=True)
    for g in goals:
        h = os.path.join(L, 'UL', 'hints', g)
        if os.path.exists(h):
            dst = os.path.join(qd, g)
            shutil.move(h, dst if not os.path.exists(dst) else f'{dst}.{stamp}')
    with open(sp + '.tmp', 'w') as f:
        f.writelines(keep)
    os.replace(sp + '.tmp', sp)
    print(f'done: {len({l.split(chr(9))[0] for l in keep})} goals solved', flush=True)


if __name__ == '__main__':
    main()

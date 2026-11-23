"""climbread.py DIR... [--md]: a climber reading (23 Nov, notes/2026-11-23-climber-restart.md).

For each climb dir (loops/NAME or a path): targets climbed, finished targets (a final run, or a real proof without
one), real proofs (the dir's solved.tsv rows of round 1; the other rows are the copied context), CPU hours (the sum
of climb.tsv's seconds column: every sketch, fill, final and direct run), proofs per CPU h, and the proved goals.
--md prints a markdown table."""
import os, sys

L = '/project/hintwork/loops'


def read(d):
    p = d if os.path.isdir(d) and '/' in d else os.path.join(L, d)
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(p, 'climb.tsv')) if l.strip()]
    cpu = 0.0
    for r in rows:
        try:
            cpu += float(r[5])
        except (IndexError, ValueError):
            pass
    tg = {r[0] for r in rows}
    real = [l.split('\t')[0] for l in open(os.path.join(p, 'solved.tsv')) if l.split('\t')[1:2] == ['1']]
    fin = {r[0] for r in rows if len(r) > 1 and r[1] == 'final'} | set(real)
    return os.path.basename(p.rstrip('/')), len(tg), len(fin), len(real), cpu / 3600, real


def main():
    md = '--md' in sys.argv
    ds = [x for x in sys.argv[1:] if x != '--md']
    if md:
        print('| climber | targets | finished | real proofs | CPU h | per CPU h | proved |')
        print('|---|---:|---:|---:|---:|---:|---|')
    for d in ds:
        n, t, f, r, h, real = read(d)
        if md:
            print(f'| {n} | {t} | {f} | {r} | {h:.2f} | {r / h if h else 0:.2f} | {", ".join(real)} |')
        else:
            print(f'{n} targets {t} finished {f} real {r} CPU h {h:.2f} per CPU h {r / h if h else 0:.2f} {" ".join(real)}')


if __name__ == '__main__':
    main()

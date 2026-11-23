"""prodhistory.py [OUT.md]: production's history from its scripts (23 Nov; the user: "keep records what was the prod
algo/portfolio/etc through the history").

For each /project/hintwork/abs/ulNN.sh (copied into hints/exp/prod/), in version order:
  * the header's newest dated entry, "(DD Nov HH:MM) ulNN: ...": when the version was written or first started, and why;
  * the last run's log, loops/ULNN.log: its birth and last-write times (a script run twice keeps only the second log)
    and the last "new=N" (the proofs that run added);
  * the loop.py command, parsed into options: workers (-j), binary (--twee, with TWEE_PG_ARGS), and what changed
    against the previous version (options added, removed or changed; for --variants, the members added and dropped).
Writes OUT (default hints/notes/production-history.md). Rerun after every production restart."""
import os, re, sys, shlex, datetime

ABS = '/project/hintwork/abs'
LOGS = '/project/hintwork/loops'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/project/twee/hints/notes/production-history.md'


def versions():
    v = [int(m[1]) for f in os.listdir(ABS) for m in [re.fullmatch(r'ul(\d+)\.sh', f)] if m]
    return sorted(v)


def parse(n):
    src = open(f'{ABS}/ul{n}.sh').read()
    lines = src.split('\n')
    # the header: comment lines after the shebang; the newest entry is the first "(date) ulN:" one
    hdr = []
    for l in lines[1:]:
        if not l.startswith('#'):
            break
        hdr.append(l[1:].strip())
    # three header styles: undated (ul3, ul4), "Round 5 continued (15 Nov 06:01): ...", "(17 Nov 03:30) ulNN: ...".
    # The newest entry: the first header line and its continuations, up to the next dated entry or "Before:"
    entries = []
    if hdr:
        txt = hdr[0]
        for l in hdr[1:]:
            if re.match(r'(Round \d+ continued )?\(\d+ Nov', l) or l.startswith('usage:') or not l:
                break
            txt += ' ' + l
        txt = txt.split(' Before:')[0]
        m = re.search(r'\((\d+ Nov(?: \d\d:\d\d)?)', hdr[0])
        entries.append([m[1] if m else '', txt])
    env = dict(re.findall(r'^export (\w+)="([^"]*)"', src, re.M))
    body = '\n'.join(l for l in lines if not l.startswith('#')).replace('\\\n', ' ')
    cmd = next((l for l in body.split('\n') if 'loop.py' in l), '')
    toks = shlex.split(cmd.replace('"$@"', ' ARGS_PASSTHROUGH '), posix=True)
    i = next(k for k, t in enumerate(toks) if t.endswith('loop.py'))
    toks = toks[i + 1:]
    pos, opts = [], {}
    k = 0
    while k < len(toks):
        t = toks[k]
        if t in ('>', '2>&1') or t.startswith('>'):
            break
        if t == 'ARGS_PASSTHROUGH':
            k += 1; continue
        if t.startswith('--') and '=' in t:
            a, b = t.split('=', 1); opts[a] = b; k += 1; continue
        if t.startswith('-'):
            nx = toks[k + 1] if k + 1 < len(toks) else None
            # a value may start with '-' only as a negative number (--cascade-start -1); '-j' is the next flag
            if nx is not None and (not nx.startswith('-') or re.fullmatch(r'-\d+(\.\d+)?', nx)) \
                    and nx != 'ARGS_PASSTHROUGH' and not nx.startswith('>'):
                opts[t] = toks[k + 1]; k += 2
            else:
                opts[t] = True; k += 1
            continue
        pos.append(t); k += 1
    return entries, env, pos, opts


def logspan(n):
    f = f'{LOGS}/UL{n}.log'
    if not os.path.exists(f):
        return None
    st = os.stat(f)
    b = getattr(st, 'st_birthtime', None)
    if b is None:
        import subprocess
        b = float(subprocess.run(['stat', '-c', '%W', f], capture_output=True, text=True).stdout.strip() or 0)
    new = None; run = 0
    with open(f, errors='replace') as fh:
        for l in fh:
            for m in re.finditer(r'new=(\d+)', l):
                new = int(m[1])
            for m in re.finditer(r'(\d+) running', l):
                run = max(run, int(m[1]))
    fmt = lambda t: datetime.datetime.fromtimestamp(t).strftime('%d %b %H:%M') if t else '?'
    return fmt(b), fmt(st.st_mtime), (st.st_mtime - b) / 3600 if b else None, new, run


def jval(o, ls):
    """the worker count: the script's -j, or for a J= launch the most runs in flight in its log (equal to -j while the
    loop is saturated) beside the script's default"""
    j = str(o.get('-j', '?'))
    m = re.fullmatch(r'\$\{J:-(\d+)\}', j)
    if not m:
        return j
    live = running_j()
    if live and o.get('_current'):
        return f'{live} (the running process)'
    return f'J= (default {m[1]}); ≥{ls[4]} in flight' if ls and ls[4] else f'J= (default {m[1]})'


def running_j():
    """-j of the running production loop (loop.py sets/all loops/UL), from /proc"""
    for d in os.listdir('/proc'):
        if not d.isdigit():
            continue
        try:
            a = open(f'/proc/{d}/cmdline', 'rb').read().split(b'\0')
        except OSError:
            continue
        a = [x.decode(errors='replace') for x in a]
        if any(x.endswith('loop.py') for x in a) and 'sets/all' in a and 'loops/UL' in a and '-j' in a:
            return a[a.index('-j') + 1]
    return None


def binary(o, env):
    b = os.path.basename(str(o.get('--twee', '?')))
    pg = env.get('TWEE_PG_ARGS')
    return b + (f' + `{pg}`' if pg else '')


def diff(o1, o2):
    out = []
    for k in o2:
        if k.startswith('_'):
            continue
        if k not in o1:
            out.append(f'+`{k}`' + (f' `{o2[k]}`' if o2[k] is not True else ''))
        elif o1[k] != o2[k]:
            if k == '--variants':
                a, b = o1[k].split(','), o2[k].split(',')
                add = [x for x in b if x not in a]; rm = [x for x in a if x not in b]
                s = []
                if add: s.append('+' + ','.join(add))
                if rm: s.append('−' + ','.join(rm))
                if not s: s.append('reordered')
                out.append('variants ' + ' '.join(s))
            elif k == '-j':
                out.append(f'workers {o1[k]} → {o2[k]}')
            else:
                out.append(f'`{k}` `{o1[k]}` → `{o2[k]}`')
    for k in o1:
        if k not in o2 and not k.startswith('_'):
            out.append(f'−`{k}`')
    return out


def main():
    V = versions()
    P = {n: parse(n) for n in V}
    P[V[-1]][3]['_current'] = True
    now = datetime.datetime.now().strftime('%d %b %Y %H:%M')
    L = [f'# Production history', '',
         f'Generated {now} by [exp/prodhistory.py](../exp/prodhistory.py) from the scripts abs/ul3.sh … ul{V[-1]}.sh '
         f'(copies in [exp/prod/](../exp/prod/)) and their logs; rerun it after every production restart. What runs now, '
         'with the side loops, is in REPORT.md "Production now"; the totals over time are REPORT\'s summary table.', '',
         '* **Written** is the newest dated entry of the script\'s header: when the version was written or first started.',
         '* **Last run** is the span of loops/ULNN.log (first and last write). A script that ran twice keeps only its '
         'second log (ul74: written 20 Nov 04:14, its log is the run of 21 Nov 16:50 to 22 Nov 07:12); some versions '
         'ran for minutes before a fix.',
         '* **new** is the last "new=N" in that log: the proofs that run added (not counting merges from side loops).',
         '* **Workers** is the script\'s -j; for a script launched with J= the launch value is not recorded: the column gives the most runs in flight in its last log (a lower bound), and for the running version the running process\'s -j.',
         '* **Changes** are computed from the two loop.py command lines.', '',
         '| version | written | last run | hours | workers | binary | new | changes against the previous version |',
         '|---|---|---|---:|---|---|---:|---|']
    prev = None
    for n in V:
        entries, env, pos, o = P[n]
        ls = logspan(n)
        wr = entries[0][0] if entries else ''
        ch = '; '.join(diff(P[prev][3], o)) if prev is not None else 'first round-3 production script'
        if prev is not None and env.get('TWEE_PG_ARGS') != P[prev][1].get('TWEE_PG_ARGS'):
            ch = (ch + '; ' if ch else '') + f'TWEE_PG_ARGS `{env.get("TWEE_PG_ARGS", "")}`'
        lsr = f'{ls[0]} – {ls[1]}' if ls else 'no log'
        hr = f'{ls[2]:.1f}' if ls and ls[2] is not None else ''
        nw = str(ls[3]) if ls and ls[3] is not None else ''
        L.append(f'| [ul{n}](../exp/prod/ul{n}.sh) | {wr} | {lsr} | {hr} | {jval(o, ls)} | {binary(o, env)} | {nw} | {ch or "(same options: a restart, or loop.py's code or the launch arguments changed)"} |')
        prev = n
    L += ['', '## Why each version (the header\'s newest entry, verbatim)', '']
    for n in V:
        entries = P[n][0]
        if entries:
            d, t = entries[0]
            L.append(f'* **ul{n}** ({d}): {t}')
    # (23 Nov) the side loops: each family's scripts in version order with their header's first entry
    SIDE = [('Given-rule retry (givenmatch.py live, loops/GML)', r'gmlive'),
            ('Proof-step transfer (transfer.py, loops/XFL)', r'xfr'),
            ('Plain live loop and plain sweeps (condprove.py, loops/CI2, loops/CI3)', r'plainlive|sweepq'),
            ('Head climbers', r'clh|climb'),
            ('Prover9 side worker', r'p9c')]
    L += ['', '## Side loops (their scripts, oldest first; copies in [exp/prod/side/](../exp/prod/side/))', '',
          'Each line is the script\'s first header entry. Which ones run now is in REPORT.md "Production now".', '']
    key = lambda f: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', f[:-3])]
    for title, pat in SIDE:
        fs = sorted((f for f in os.listdir(ABS) if re.match(f'({pat})', f) and f.endswith('.sh')), key=key)
        if not fs:
            continue
        L.append(f'**{title}**'); L.append('')
        for f in fs:
            h = []
            for l in open(f'{ABS}/{f}').read().split('\n')[1:]:
                if not l.startswith('#'):
                    break
                h.append(l[1:].strip())
            t = ' '.join(h)
            t = t[:400] + (' …' if len(t) > 400 else '')
            L.append(f'* [{f}](../exp/prod/side/{f}): {t}')
        L.append('')
    n = V[-1]
    entries, env, pos, o = P[n]
    L += ['', f'## The current version\'s full option list (ul{n})', '', '```']
    if env:
        L += [f'export {k}="{v}"' for k, v in env.items()]
    L.append('loop.py ' + ' '.join(pos))
    for k, v in o.items():
        if k.startswith('_'):
            continue
        L.append(f'  {k}' + ('' if v is True else f' {v}'))
    L += ['```', '']
    open(OUT, 'w').write('\n'.join(L))
    print(f'{OUT}: {len(V)} versions')


if __name__ == '__main__':
    main()

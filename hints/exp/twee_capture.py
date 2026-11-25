#!/usr/bin/env python3
"""twee_capture.py: a --twee wrapper (exp85, notes/2026-11-25-precedence-portfolio.md). Copies the run's problem file
(the .p argument), --hints-file and --rule-goal files into $CAPTURE_DIR as <n>.<goal>.{p,hints,goal}, appends the
argument list with those copies in place to $CAPTURE_DIR/log.jsonl, then runs $CAPTURE_TWEE (default
/project/bin/twee-pg61) with the original arguments. So a later replay can rerun exactly this run's inputs."""
import json, os, shutil, sys
D = os.environ.get('CAPTURE_DIR')
T = os.environ.get('CAPTURE_TWEE', '/project/bin/twee-pg61')
a = sys.argv[1:]
if D:
    try:
        os.makedirs(D, exist_ok=True)
        p = next((x for x in a if x.endswith('.p') and os.path.exists(x)), None)
        if p:
            g = os.path.basename(p)[:-2]
            fd = os.open(os.path.join(D, 'counter'), os.O_RDWR | os.O_CREAT)
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
            n = int(os.read(fd, 32) or b'0') + 1
            os.lseek(fd, 0, 0); os.ftruncate(fd, 0); os.write(fd, str(n).encode())
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)
            b = os.path.join(D, f'{n}.{g}')
            c = list(a)
            shutil.copyfile(p, b + '.p'); c[c.index(p)] = b + '.p'
            for flag, ext in (('--hints-file', '.hints'), ('--rule-goal', '.goal')):
                if flag in c and c.index(flag) + 1 < len(c) and os.path.exists(c[c.index(flag) + 1]):
                    i = c.index(flag) + 1
                    shutil.copyfile(c[i], b + ext); c[i] = b + ext
            line = json.dumps({'n': n, 'goal': g, 'args': c, 'cwd': os.getcwd(),
                               'TWEE_PG_ARGS': os.environ.get('TWEE_PG_ARGS', '')}) + '\n'
            with open(os.path.join(D, 'log.jsonl'), 'a') as f:
                f.write(line)
    except Exception as e:   # never stop the run itself
        sys.stderr.write(f'twee_capture: {e}\n')
os.execv(T, [T] + a)

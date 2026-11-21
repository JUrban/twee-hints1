import json, glob, os, subprocess, sys, threading, time
S='/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/pq'
d=[x for x in glob.glob(S+'/*/') if 'aa2_to_aa3' in x][0]
j=json.load(open(d+'job.json')); cmd=j['cmd']
od=os.path.dirname(cmd[1]); cmd=[c.replace(od, d.rstrip('/')) for c in cmd]
cmd=[c for c in cmd]  # full output: --print-given etc.
env=dict(os.environ); env['TWEE_PG_ARGS']=j.get('TWEE_PG_ARGS','')
mode, load = sys.argv[1], sys.argv[2] == '1'
times=[]; lock=threading.Lock(); stop=[False]
def work(i):
    for r in range(4):
        t=time.time()
        if mode=='pipe':
            p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env); out=p.stdout
        else:
            fn=f'{S}/../gt.{i}.out'
            with open(fn,'wb') as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
            out=open(fn,'rb').read(); os.unlink(fn)
        with lock: times.append((time.time()-t, len(out)))
ths=[threading.Thread(target=work, args=(i,)) for i in range(4)]
for t in ths: t.start()
x=0
while any(t.is_alive() for t in ths):
    if load:
        for _ in range(200000): x+=1   # pure Python, holds the GIL
    else:
        time.sleep(0.01)
ts=sorted(t for t,_ in times)
print(mode, 'mainload' if load else 'idle', 'runs', len(ts), 'median wall', round(ts[len(ts)//2],2), 'max', round(ts[-1],2), 'out bytes', times[0][1])

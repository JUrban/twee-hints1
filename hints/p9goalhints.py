import subprocess, sys, os, re, collections
from concurrent.futures import ThreadPoolExecutor
L='/project/AIM60k/problems/ladr/'
names=[l.strip() for l in open(sys.argv[1]) if l.strip()]; t=sys.argv[2]; tmp=sys.argv[3]; os.makedirs(tmp, exist_ok=True)
allg=collections.defaultdict(dict)
for n in os.listdir(L):
    o,k=n.rsplit('__goal_',1)
    if o in ('aa1_15','aK2_eq_aK3_q'):
        txt=open(L+n).read()
        g=txt.split('formulas(goals).')[1].split('end_of_list.')[0].strip()
        allg[o][int(k)]=g.split('%')[0].strip().rstrip('.')
def run(n):
    o,k=n.rsplit('__goal_',1); k=int(k)
    hs=[allg[o][j] for j in sorted(allg[o]) if j<k]
    hp=os.path.join(tmp,n+'.h')
    open(hp,'w').write('formulas(hints).\n'+''.join(h+'.\n' for h in hs)+'end_of_list.\n')
    out=subprocess.run(['/project/bin/prover9-new','-t',t,'-f',L+n,hp],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout.decode('utf8','replace')
    return n,'THEOREM PROVED' in out,len(hs)
with ThreadPoolExecutor(6) as ex:
    res=list(ex.map(run,names))
print('p9 earlier-goal hints', t, 's:', sum(ok for _,ok,_ in res), 'of', len(names), 'mean hints', sum(h for *_,h in res)/len(res))

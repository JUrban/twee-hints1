# (23 Nov) lr2h on RKD1's half2 problems by proof size (used kNN lemmas): the share of problems whose used lemmas are
# all in the top K, model against similarity. Run under /project/hintwork/venv/bin/python3 (lightgbm).
import pickle, sys, json, numpy as np, os
os.environ['OMP_NUM_THREADS']='2'
sys.path.insert(0,'/project/twee/hints'); sys.path.insert(0,'/project/twee/hints/exp')
import lemmas, lightgbm as lgb
D=pickle.load(open('/project/hintwork/cond/LR2.pkl','rb'))
H2={lemmas.split(l.strip())[0] for l in open('/project/hintwork/sets/half2') if l.strip()}
X=np.array(D['X']); y=np.array(D['y']); grp=np.array(D['grp'])
name=sys.argv[1] if len(sys.argv)>1 else 'lr2h'
fs=json.load(open(f'/project/hintwork/models/lemmarank/{name}.json'))['feats']; cols=[D['feats'].index(f) for f in fs]
b=lgb.Booster(model_file=f'/project/hintwork/models/lemmarank/{name}.txt')
test=[i for i,m in enumerate(D['meta']) if lemmas.split(m[1])[0] in H2]
sel=np.isin(grp,test); s=b.predict(X[sel][:,cols]); g=grp[sel]; yy=y[sel]; r=X[sel,0]
for lo,hi in ((1,1),(2,4),(5,9),(10,999)):
    for K in (30,100):
        a_s=[];a_m=[];a_x=[]
        for p in test:
            m=g==p; n=yy[m].sum()
            if not (lo<=n<=hi): continue
            o=np.argsort(-s[m],kind='stable'); rs=np.argsort(r[m],kind='stable')
            a_m.append(yy[m][o[:K]].sum()==n); a_s.append(yy[m][rs[:K]].sum()==n)
            h=K//2; mix=list(rs[:h])+[i for i in o if i not in set(rs[:h])][:K-h]
            a_x.append(yy[m][mix].sum()==n)
        if a_s: print(f'{name} used {lo}-{hi}: {len(a_s)} problems, K {K}: all used in top K: similarity {np.mean(a_s):.3f} model {np.mean(a_m):.3f} mixed {np.mean(a_x):.3f}')

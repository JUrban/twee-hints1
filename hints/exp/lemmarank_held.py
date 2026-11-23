# (23 Nov) lr2h and lr2 on the half2 problems of RKD1 (lr2h has not seen their originals): recall of the used kNN lemmas
# in the top K, model against similarity. Run under /project/hintwork/venv/bin/python3 (lightgbm).
import pickle, sys, json, numpy as np, os
os.environ['OMP_NUM_THREADS']='2'
sys.path.insert(0,'/project/twee/hints'); sys.path.insert(0,'/project/twee/hints/exp')
import lemmas, lemmarank, lightgbm as lgb
D=pickle.load(open('/project/hintwork/cond/LR2.pkl','rb'))
H2={lemmas.split(l.strip())[0] for l in open('/project/hintwork/sets/half2') if l.strip()}
X=np.array(D['X']); y=np.array(D['y']); grp=np.array(D['grp'])
for name in ('lr2h','lr2'):
    fs=json.load(open(f'/project/hintwork/models/lemmarank/{name}.json'))['feats']; cols=[D['feats'].index(f) for f in fs]
    b=lgb.Booster(model_file=f'/project/hintwork/models/lemmarank/{name}.txt')
    test=[i for i,m in enumerate(D['meta']) if lemmas.split(m[1])[0] in H2 and m[0]=='cond/RKD1']
    sel=np.isin(grp,test); s=b.predict(X[sel][:,cols]); g=grp[sel]; yy=y[sel]; r=X[sel,0]
    for K in (30,50,100):
        rs=[];rm=[];al_s=[];al_m=[]
        for p in test:
            m=g==p; n=yy[m].sum()
            if n==0: continue
            o=np.argsort(-s[m],kind='stable')[:K]; os_=np.argsort(r[m],kind='stable')[:K]
            rm.append(yy[m][o].sum()/n); rs.append(yy[m][os_].sum()/n); al_m.append(yy[m][o].sum()==n); al_s.append(yy[m][os_].sum()==n)
        print(f'{name} on half2 RKD1 problems ({len(rs)}), K {K}: recall similarity {np.mean(rs):.3f} model {np.mean(rm):.3f}; all used in top K {np.mean(al_s):.3f} {np.mean(al_m):.3f}')

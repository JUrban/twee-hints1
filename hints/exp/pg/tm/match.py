import numpy as np, lightgbm as lgb, sys
B=np.load('test2.npz'); X,y,n=B['X'],B['y'],B['n'].astype(float)
q=1/(1+np.exp(-(X[:,0].astype(float)+X[:,10])))
target=n[q>=0.269].sum()/n.sum()
print('sum 0.269: overlaps kept %.1f%%, proof pairs %.1f%%' % (100*target, 100*(q>=0.269)[y==1].mean()))
for name in sys.argv[1:]:
    p=lgb.Booster(model_file=name+'.txt').predict(X[:,:20])
    o=np.argsort(-p); cum=np.cumsum(n[o])/n.sum(); k=np.searchsorted(cum,target); t=p[o][k]
    print('%s: threshold %.4f keeps %.1f%% overlaps, proof pairs %.1f%%' % (name, t, 100*n[p>=t].sum()/n.sum(), 100*(p>=t)[y==1].mean()))

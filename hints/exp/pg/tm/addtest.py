import numpy as np, lightgbm as lgb
A=np.load('train2.npz'); Bs=[('test2',np.load('test2.npz')),('hard1',np.load('hard1.npz'))]
def fit(cols, ic, trees, leaves):
    p={'objective':'binary','num_leaves':leaves,'learning_rate':0.1,'min_data_in_leaf':50,'feature_fraction':0.9,
       'bagging_fraction':0.8,'bagging_freq':1,'verbose':-1,'num_threads':4}
    if ic: p['interaction_constraints']=ic
    return lgb.train(p, lgb.Dataset(A['X'][:,cols],A['y']), num_boost_round=trees)
def curve(name, m, cols):
    for bn,B in Bs:
        X,y,n=B['X'],B['y'],B['n'].astype(float); p=m.predict(X[:,cols])
        out=[]
        for target in (0.95,0.9,0.85):
            # threshold reaching this proof-pair retention
            t=np.quantile(p[y==1],1-target); k=p>=t
            out.append('%.0f%%: %4.1f%%' % (100*target, 100*n[k].sum()/n.sum()))
        print('%-22s %-6s overlaps kept at proof-pair retention  %s' % (name, bn, '  '.join(out)))
full=list(range(21)); r=list(range(10)); a=list(range(10,20))
curve('full 100x31', fit(full,None,100,31), full)
curve('additive 100x31', fit(r+a,[r,a],100,31), r+a)
curve('additive 200x31', fit(r+a,[r,a],200,31), r+a)
for bn,B in Bs:
    X,y,n=B['X'],B['y'],B['n'].astype(float); p=X[:,0].astype(float)+X[:,10]
    out=[]
    for target in (0.95,0.9,0.85):
        t=np.quantile(p[y==1],1-target); k=p>=t; out.append('%.0f%%: %4.1f%%' % (100*target, 100*n[k].sum()/n.sum()))
    print('%-22s %-6s overlaps kept at proof-pair retention  %s' % ('sum of scores', bn, '  '.join(out)))

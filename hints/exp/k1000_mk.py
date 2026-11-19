import sys, random
sys.path.insert(0, '/project/twee/hints')
import lemmas
D = 'loops/UL'
solved = {l.split('\t')[0]: 1 for l in open(D + '/solved.tsv')}
ix = lemmas.LemmaIndex(sorted(solved), subsets=True)
src = {o: set(v) for o, v in lemmas.by_original(solved).items()}
names = [l.strip() for l in open('sets/all') if l.strip()]
uns = [n for n in names if n not in solved and '__goal_' in n]
random.seed(4); smp = random.sample(uns, 4)
for n in smp:
    for k in (1000, 2000):
        txt, nl = lemmas.lemma_problem_knn(n, src, 6, ix, k, True)
        open(f'{sys.argv[1]}/{n}.k{k}.p', 'w').write(txt)
        print(n, k, nl)

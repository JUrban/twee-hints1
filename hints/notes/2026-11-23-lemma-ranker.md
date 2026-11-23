

## Size, not order (15:10)

The same 235 half2 gap goals, Z9's context, plain 5 s, 4 earlier and 2 later proved siblings (exp/z9gap5.sh, exp/z9gap6.sh; lr2h's pool 1,000, 2,000 at 400):

| kNN lemmas | similarity | lr2h | lr2h vs similarity | union |
|---:|---:|---:|---:|---:|
| 30 | 11 | 6 | +0 −5 | 11 |
| 100 | 20 | 14 | +3 −9 | 23 |
| 200 | 22 | 24 | +5 −3 | 27 |
| 400 | 35 | 30 | +4 −9 | 39 |

Similarity at 400 against 100: +19 −4; at 400 against 200: +13 −0. All four similarity sizes together prove 39, all four ranked lists 32, all eight 43. The ranked list wins only at 200 (by 2), and a second similarity size adds as much as a ranked list does, so in a from-zero loop's context the ranker is not worth a member either; exp65 will not use it. On the frontier (production's context, the one lr2 was trained in) it did better: PLL1 3 against W's 1, and the live loop's c8L 4 against lr1's 0, so the live loop keeps lr2. The size is the lever: a plain 400-lemma run proves three times what a 30-lemma one does on these goals. exp/z9gap7.sh (merged lists) was stopped after 2 goals. Next (exp/z9gap8.sh): 800 and 1,600 lemmas, and 400 with 40 siblings.

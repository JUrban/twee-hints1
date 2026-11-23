

## The other half and 100 lemmas (14:55)

| arm | goals | proved | vs similarity at the same size | union |
|---|---:|---:|---:|---:|
| 30, half1: similarity (ZGS) | 265 | 13 | | |
| 30, half1: lr2h1 (ZGH1) | 265 | 8 | +0 −5 | 13 |
| 30, half1: mixed 15+15 (ZGM1) | 265 | 9 | +0 −4 | 13 |
| 30, half2: similarity (ZGS) | 235 | 11 | | |
| 30, half2: lr2h (ZGH) | 235 | 6 | +0 −5 | 11 |
| 30, half2: mixed 15+15 (ZGM2) | 235 | 9 | +1 −3 | 12 |
| 100, half2: similarity (ZKS) | 235 | 20 | | |
| 100, half2: lr2h (ZKH) | 235 | 14 | +3 −9 | 23 |

The held-out model loses on both halves at 30 lemmas (lr2h1 on half1 as lr2h on half2), and at 100 as well. The list size matters more than its order: similarity at 100 proves 20 of 235 against 11 at 30 (+9 −0). The ranked 100-list still has 3 proofs similarity's 100 does not, so it may be a member beside similarity rather than a replacement. The control for that is another similarity size: exp/z9gap6.sh runs 200 and 400 lemmas, similarity (cond/ZK2S, ZK4S) against lr2h (ZK2H, ZK4H), the same 235 goals.

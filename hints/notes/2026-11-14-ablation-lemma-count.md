# Ablation of ENIGMA, hints and lemmas; how many sibling lemmas; which lemmas proofs use

*Reconstructed on 17 Nov from REPORT 2q–2r (14 Nov, night to morning). Abstract time.*

**Question.** The user asked how far the ENIGMA guidance gets alone or with hints. Then: how many sibling
lemmas to import, and which of the offered lemmas do proofs actually use?

**Setup.**
* **Ablation:** the 189 aK2_eq_aK3_a goals of sets/u3, one hard original. 20 abstract s each, in an online
  loop from loops/V2base's proofs, 5 workers. Only the guidance changes:
  * ENIGMA = rm4t at 0.1, penalty 2;
  * hints = the whole-original pool, online;
  * lemmas = 3 nearest proven siblings + 10 subset-kNN lemmas.
* **Lemma count:** the same setting with rm4t, the whole pool and 10 kNN lemmas, changing only the number of
  siblings. On the 189 and on the first 150 unsolved goals of nil3_31.
* **rm6t:** rm4t's data + the full loop's 5,303 proofs, with the u3 originals held out.
* **Used lemmas** (twee-e31 prints USEDAXIOMS):
  * 60 goals the full loop solved in round 4, rerun at 20 s on a snapshot of all 40,961 proofs;
  * offered the 20 nearest proven siblings (either side) + 10 kNN lemmas;
  * then again with 6 siblings.

**Results.**

| variant | ENIGMA | hints | lemmas | solved of 189 | wall s |
|---|---|---|---|---:|---:|
| U3po (run with the two other u3 originals) | yes | yes | yes | **60** | 9,866 |
| U3xf (these 189 alone, like all below) | yes | yes | yes | 58 | 10,506 |
| U3xh | – | yes | yes | 59 | 14,979 |
| U3xm | yes | – | yes | 58 | 10,064 |
| U3xl | – | – | yes | 49 | 16,372 |
| U3yb | yes | yes | – | 49 | 11,805 |
| U3ym | yes | – | – | 42 | 10,501 |
| U3yh | – | yes | – | 37 | 15,063 |
| U3x0 (plain twee) | – | – | – | 28 | 18,151 |

All nine together solve 70.

| siblings | aK2_eq_aK3_a, 189 | nil3_31, first 150 unsolved |
|---|---:|---:|
| 3 nearest below | 58 | 62 |
| **6 nearest below** | **64** (+8 −2) | **76** (+16 −2) |
| 10 nearest below | | 74 |
| 6 nearest on either side | | 76 |
| 3 below + 20 kNN lemmas in place of 10 | 59 | |

* rm6t alone (no hints, no lemmas) on the 189: 40, against 42 for rm4t.
* Used lemmas: all 60 solved, 7.6 lemmas per proof. About 20% of offered siblings are used, almost whatever
  their distance:

  | sibling | offered | used |
  |---|---:|---:|
  | before, 1–3 goals away | 120 | 30% |
  | before, 4–6 | 132 | 27% |
  | before, 7–10 | 173 | 17% |
  | before, 11+ | 296 | 19% |
  | after, 1–3 | 115 | 20% |
  | after, 4–10 | 245 | 20% |
  | after, 11+ | 119 | 16% |

  All ten kNN ranks are used, 13–28 times each. With 6 siblings instead of 20, 58 of 60 are solved (median
  3.4 s against 2.7 s). The same goals were 3× faster than in their round-4 runs (median 9.7 s), because more
  of their neighbours were proven.

**Reading.**
* Without lemmas, ENIGMA and hints add up (28 → 42, 37 → 49). ENIGMA is the stronger and cheaper guide.
* **Lemmas are worth as much as ENIGMA and hints together** (49 = 49). With lemmas, the two overlap: each
  adds about 10, together only 9–11. Hints and lemmas carry the same information, the sibling proofs, as
  steps or as finished results.
* **This is the user's 17 Nov point, seen from the other side.** Lemmas act as shortcuts to whatever is
  proven nearby, not as specific needed steps. A lemma-based proof leaves out the work of deriving them.
  Veroff's expansion back to the axioms puts that work back into the hints
  (2026-11-17-expanded-proofs.md).
* The ordering effect (U3po 60 against U3xf 58, the same settings) is about 2. It is as large as the second
  guide on top of lemmas, so the 9–11 differences need that caveat.
* One original for the ablation, two for the lemma count. 6 siblings won on both by 10–23%.
* rm6t: more loop proofs did not improve the filter (again; 2026-11-13-enigma-loop.md).

**Decision and next.** 6 siblings from either side (round 4, abs/ul4.sh, from 14 Nov 08:35). The cascade's
retries on new nearby proofs, rather than more lemmas at a time. REPORT 2q, 2r.

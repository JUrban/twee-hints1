#!/bin/bash
# (17 Nov 18:18) additive Pcat ENIGMA parental models (interaction constraints: each tree on one rule's side), base 1024,
# ENIGMA only (pca_1024) and with the 10 features per rule (pcad_1024); data of pg/pc1.sh
cd /project/hintwork/pg; P=/project/hintwork/venv/bin/python3; H=/project/twee/hints
$P $H/pgtrain_enigma.py e3tr_1024 e3te_1024 pca_1024 --trees 100 --leaves 255 --enigma-only --additive > pca_1024.log 2>&1
$P $H/pgtrain_enigma.py e3tr_1024 e3te_1024 pcad_1024 --trees 100 --leaves 255 --additive > pcad_1024.log 2>&1
echo done > pc2.done

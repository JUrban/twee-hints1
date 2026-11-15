#!/bin/bash
# After the GNN training (models/gnn1.log) ends: Prover9 with twee's pools and sibling lemmas on the stalled goals
# (sets/st79u, from the current loops/UL), 60 s, 3 workers -> loops/P9T (merge proofs with merge.py).
cd /project/hintwork
# (started at once, 08:33: the GNN was stopped at 4,000 steps)
python3 -u /project/twee/hints/p9twee.py sets/st79u loops/UL loops/P9T --timeout 60 -j 3 > loops/P9T.log 2>&1
echo "P9T $(tail -1 loops/P9T.log) $(date +%T)" | tee loops/P9T.done

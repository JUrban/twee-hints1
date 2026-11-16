#!/bin/bash
# From zero (16 Nov 17:55): sets/rp3 with an EMPTY context (no proofs of other originals), 4 workers, 1 hour,
# the transfer every 2 minutes (solve_new.sh defaults). Against LVD 942 with the clean public context (loops/ALL):
# what the public context is worth, and what the loop bootstraps alone. Caveat: the rule model rm4t is still the
# fixed one, trained on public proofs.
cd /project/hintwork
/project/twee/hints/solve_new.sh sets/rp3 loops/EMPTY loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done

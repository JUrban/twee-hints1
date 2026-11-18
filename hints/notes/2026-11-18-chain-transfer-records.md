# Chains with transfer records (exp10)

Started 18 Nov 2026, 09:32 UTC. Directory /project/hintwork/exp10; scripts and data in hints/exp/exp10_*.

## Question

A chain is the expansion of a goal's nearest proven siblings through the lemma records (USEDAXIOMS) of their
proofs. 5,589 of UL's 45,232 proven goals have no record, so a chain stops at them (exp3's "chain holes"). 2,881 of
them were proved by the transfer (transfer.py), whose transfer.tsv rows name the source goals: the goal is a step,
or an instance of a step, of those proofs. Does giving those goals their sources as records make better chains?

## Setting

* Records: `sibchain.py --build chain_records_xfer.tsv --transfer --extra exp3/out_K@320,...,exp8/out_s_K_re`
  (09:31: 42,526 records, of which 2,881 from transfer sources) against chain_records.tsv (39,643, the same
  without --transfer).
* Goals, commands and siblings: exp8's (stall78_K.cmds, sibs10.tsv picked 07:11), 80 abstract s, CPU cap 800 s,
  twee-e48.
* Chains by exp10/mk.py. Without the transfer records, sibchain gives exactly exp8's chain on all 78 goals (same
  sizes), so **the only difference from exp8's arm s_K is the transfer records**: mean 12,741 → 14,707 hints,
  larger on 77 of 78 (sizes.tsv).
* **Control:** exp8's arm s_K (2 workers). **Arm X:** 2 workers, exp8/run.py.

```
cd /project/hintwork/exp10
python3 mk.py /project/hintwork/chain_records_xfer.tsv /project/hintwork/chain_records.tsv
python3 run.py X.cmds X 2
```

## Results

(pending)

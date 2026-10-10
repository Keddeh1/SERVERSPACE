# Derived connector replay-cost model

Status: source-derived analytical model; independent empirical timing remains in the West sector. Applies to the current `context_connector.accept_delta` implementation, successful new deltas, no pre-existing fork, N total events and uniform batch size B dividing N.

The receiver validates its existing head, validates the delta base (when present), then replays the admitted target. For batch number j, the prefix lengths are (j−1)B, (j−1)B and jB. Its arithmetic replay count is therefore (3j−2)B. Summed over m=N/B batches:

`receiver_replayed_operations = B × (3m²−m)/2 = (3N²/B−N)/2`.

For N=64:

| Batch B | Requests | Source-derived receiver arithmetic replays |
| --- | --- | --- |
| 1 | 64 | 6112 |
| 4 | 16 | 1504 |
| 16 | 4 | 352 |
| 64 | 1 | 64 |

These count replayed arithmetic operations, not all CPU instructions, SQLite reads or physical writes. Each event still needs digest checks, canonical representation and storage. Fixed network/transaction cost, JSON encoding, runtime initialisation and source-side continuation work remain. The receiver's measured CPU ratio need not equal the replay-count ratio.

Source-side `advance` still replays its prefix for every locally appended event: N(N−1)/2 arithmetic operations regardless of transport batching. `export_delta` additionally replays the source head once per export. This explains why source costs can dominate after remote work is reduced. It also identifies a research frontier: authenticated checkpoints or verified incremental replay may reduce repeated prefix work, but caching must not bypass predecessor/context validation under injected corruption.

The precise claim is about bounded delta aggregation on the inspected implementation. It is not a proof that the entire IL-LLM graph executes in O(1), that every database operation disappears or that stable identity alone removes all serialization. Packet and lineage budgets remain explicit architectural constraints.

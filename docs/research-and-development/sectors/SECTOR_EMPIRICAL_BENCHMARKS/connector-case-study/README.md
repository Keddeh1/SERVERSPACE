# Technical case study: contextual identity continuity and bounded remote aggregation

Research ID: RND-CONNECTOR-001. Status: implemented, locally qualified and critically analysed. The study records formal invariants, experimental controls, mathematical modelling, adversarial tests, uncertainty, critique and follow-up research. [Design](../../SECTOR_SYSTEMS_ARCHITECTURE/connectors/EXPERIMENT_DESIGN.md), [source-derived model](../../SECTOR_MATHEMATICAL_LATTICE/CONNECTOR_COST_MODEL.md), [paired analysis](ANALYSIS.json) and raw batch-1/4/16/64 JSON files preserve the full chain from theory to observations.

## Question and formal invariants

Does reducing repeated remote materialisation preserve the same governed object and lineage while reducing request, replay and transaction work? The destination must independently admit every predecessor, context and vector. Required final invariants are continuation identity, target head, exact arithmetic value and complete authoritative event set. Source/destination filenames may differ; placement cannot redefine the object. A declared stable identifier is not, by itself, a proof of globally injective namespace allocation.

The fixed task consists of 64 source-local transitions over the supplied unit-origin four-ray rules. Signed and exact fractional states are legal. Every four operations return to unit 1 while retaining different historical events. Numeric re-entry is therefore not history erasure. The receiver's original context and directed field permissions remain active. A recomputed digest cannot admit a false result, foreign energy field or unregistered relation.

## Experimental progression and control

Initial qualification used eight paired per-event/full-batch sessions. It established equivalent state, retries and a promising timing reduction. Rather than generalising immediately, the extended study varied B=1,4,16,64 at fixed N=64, six pairs per size, alternating order. All 48 final sessions ran sequentially after validation completed. Potentially confounded preliminary runs are retained in `preliminary/` and excluded for a stated methodological reason, not because of their results.

Both arms use the same KEX journal and connector. The B=1 control compares equivalent transport granularity. The experiment isolates aggregation; it does not compare all of KEX to conventional enterprise products. Authentication is a scoped fixture capability, not a production identity integration. Loopback endpoints and temporary journals invoke no real energy actuator.

## Results and uncertainty

All final heads and 64-event sets matched across every condition. A lost acknowledgement was retried without duplicate state. No numerical result alone was accepted as identity equivalence.

| Batch size | Requests | Paired median elapsed ratio (per-event / batch) | Descriptive paired bootstrap interval |
| --- | --- | --- | --- |
| 1 | 64 | 1.09× | 0.80–1.19× |
| 4 | 16 | 2.17× | 1.59–2.54× |
| 16 | 4 | 4.20× | 3.75–6.69× |
| 64 | 1 | 4.82× | 3.69–6.47× |

The B=1 interval spans parity, consistent with no distinct aggregation mechanism at equal batch size. Larger batches reduce time in this profile, while the incremental gain from B=16 to B=64 is smaller than the receiver-work reduction. The reported intervals describe resampling six observed pairs, with 10,000 bootstrap draws and fixed seed. They are not universal confidence guarantees, independent-host replication or p99 qualification. Full paired ratios and source hashes are retained.

Receiver CPU ratios vary appreciably: the initial receiver-CPU ratio of medians was about 22.46×, while the final paired-median ratio was about 41.62×. Differences in estimator, run/environment and small samples prevent presenting either as a fixed product multiplier. Elapsed-time direction and the checked replay counts are better-supported mechanism evidence than a single advertised CPU figure. Client work, transaction/scheduling costs and JSON processing remain in all sessions. Peak RSS did not demonstrate a material saving in the original pilot.

## Mechanism and analytical testing

For a successful new delta, destination prefix checks and final replay yield `(3N²/B−N)/2` arithmetic operations. At N=64 this predicts 6112,1504,352,64 for B=1,4,16,64. An instrumentation test counts calls to the actual destination arithmetic function for every case and confirms the formula. This is a source-level causal explanation for reduced receiver work.

That formula does not cover every CPU instruction, storage operation or packet byte. Source `advance` still replays earlier prefixes for each new event, and packet encoding is real work. Aggregation removes repeated boundary work; it does not establish zero-cost identity translation, O(1) complete history validation or absence of all backend demand.

## Adversarial and recovery testing

The full suite verifies corruption at every position, rehashed false vectors, malformed and oversized frame references, stale destination heads, reordered deltas, retry forgery, incremental exports and explicit energy-field handoff. Failed admission must leave no staged events committed. A source/destination field switch requires a registered directional relation, preserves continuation and predecessor chain, and changes the current admissible context deliberately. Wrong-field reads remain rejected.

The API is append-only through its reviewed path; privileged database/registration edits and trusted-head replacement are different threat models. Transport identity and plant authority are not derived from a hash. These bounds are part of the case study, not reasons to discard the demonstrated logical controls.

## Critical interpretation and emergent learning

1. Stable contextual identity makes rematerialisation testable: the same continuation/head/event set can be compared across different carriers. Equivalent scalars cannot substitute for that evidence.
2. Typed boundaries make recovery explicit, but acknowledgement granularity is a business contract. Batching is beneficial where session-final acceptance is sufficient; it cannot silently replace mandatory per-event irrevocable commits.
3. The demonstrated benefit is repeated remote replay/commit amortisation. Marketing it as whole-computer throughput or rack-equivalent compute would exceed the experiment.
4. As receiver work falls, local repeated-prefix replay becomes the next frontier. Verified incremental/checkpoint techniques merit separate research, with predecessor/ordinance integrity preserved under corruption.
5. B=1 is a useful falsification control: equivalent mechanics approach parity. Future comparisons should preserve comparable authority and durability, rather than weaken the baseline.
6. Environmental savings require marginal host/device/network meters and actual capacity changes. CPU-time improvement provides a reason to measure energy, not a joule or carbon result itself.
7. AI input savings require a separate matched retrieval/inference experiment. Nothing in this connector timing test measures tokenizer output, model accuracy or GPU FLOPs.

## Topological filing and next research gates

North/foundations: contextual source truth, operator/consensus distinction and transport authority. East/mathematics: explicit frames, inverse/unit semantics and replay-count derivation. South/architecture: connector, journal/placement, acknowledgement and controlled field handoff. West/empirical: complete samples, bootstrap descriptions, controls, fault tests and critiques. The central formal R&D registry links all canonical records with hashes; sector direction is classification rather than mandatory execution order.

Next gates are independent-host/WAN replication, a real authenticated workload with explicitly matched acknowledgement semantics, power metering, and safely verified incremental replay. No production deployment, external valuation or energy-infrastructure actuation is declared by this local qualification.

## Reproduction

For each B in 1,4,16,64, sequentially:

```sh
python3 scripts/analysis/remote_connector_pilot.py --pairs 6 --steps 64 --batch-size B
```

Replace B with the integer and retain stdout as `batch-B.json`. Reanalyse retained checked-in samples:

```sh
python3 scripts/research-and-development/analyse_connector_case.py
python3 -B -m unittest discover -s web-estate/sites/aboudy-keddeh/tests -p 'test_*.py' -v
python3 scripts/research-and-development/index_research.py
```

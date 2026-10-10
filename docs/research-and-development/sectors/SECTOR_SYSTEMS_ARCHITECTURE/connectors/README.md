# RND-CONNECTOR-001: Governed contextual delta connector

Status: implemented and locally qualified. Purpose: transfer a bounded sequence of context-bearing state changes into an independently validating receiver, retaining identity, lineage and carrier-independent continuity. Source: owner number-line/continuation contracts, the existing `context_continuation.py`, and the user's governed municipality/region and filing requirements.

## Requirements and hypothesis

R1: final logical object, event set and predecessor head must match across carriers.
R2: unknown fields, broken/reordered lineage, false arithmetic vectors and stale destinations must reject without partial writes.
R3: lost acknowledgement may retry safely, but the repeated packet must still validate.
R4: cross-energy-field handoff requires a registered directional relation.
R5: batching may reduce repeated remote traffic and replay/commit work when the workload requires a session-final authoritative acknowledgement.

## Implementation and architectural contract

Source: `web-estate/sites/aboudy-keddeh/runtime/context_connector.py` at repository root. `export_delta` verifies the source snapshot, ancestor base and target jurisdiction. `accept_delta` verifies exact frame shape, head references, bounded size, destination registration and every ordered event before replaying the target. Staged events and head update commit in one SQLite transaction; failed admission rolls back the complete delta. The duplicate-acknowledgement path validates the repeated packet against existing committed events.

Existing Continuation and its journal remain the substrate. Genesis context is explicit; no unknown destination object is silently created. Replacing file/database placement preserves `continuation` and target lineage head. No new ISA opcode, cryptographic trust scheme or physical resource allocation is introduced.

## Qualification and failure scope

Tests are in `web-estate/sites/aboudy-keddeh/tests/test_context_connector.py`. They cover atomic handoff/retry, stale destination, corruption at each event, rehashed false vector, cross-field/reordered rejection, malformed/oversized frames, incremental delta and admitted energy-field transition. The full runtime suite result is filed in the empirical sector.

The reference harness `scripts/analysis/remote_connector_pilot.py` uses separate processes and temporary SQLite carriers, a loopback HTTP receiver and a scoped private fixture capability. It compares 64 per-event requests with one batched request using the same journal implementation and source-local operations. It is not a deployed customer connector or a WAN test. Receiver authentication is separate from semantic lineage admission.

## Acceptance, rollback and next gate

Accept this review implementation only with passing tests, identical final event/head evidence and visible local budget constraints. To roll back, retain the original source/journals and revert the adapter commit; this reference pilot changes no production schema or customer endpoint. Benchmarks remove all temporary state and terminate their child processes.

Next production gate: bind a real existing authenticated transaction API, its idempotency/acknowledgement semantics and destination policy/evidence records. Meter endpoint and server power before claiming physical energy or cost savings. Session-final batching cannot replace per-event irrevocable acknowledgement where the business contract requires it.

[Extended empirical case study](../../SECTOR_EMPIRICAL_BENCHMARKS/connector-case-study/README.md) and [mathematical replay model](../../SECTOR_MATHEMATICAL_LATTICE/CONNECTOR_COST_MODEL.md) record the deeper investigation and emergent learning.

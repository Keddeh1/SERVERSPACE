# Context-bearing one-origin continuation

This review adapter implements supplied four-ray arithmetic, operation conjugation and recurrent continuation. [Source definitions](number-line/README.md) distinguish owner code from adapter extensions. Ordinance, municipality and region are current user requirements; these field names are not attributed to an uploaded executable schema.

Register contexts with origin, ordinance, municipality, region, vector, frame, unit and revision. Registration is trusted operator configuration, not evidence of regional consensus. Genesis is exact unit 1 with an admitted context; multi-context genesis requires an explicit selection.

`advance(identifier, expected_head, context, axis, parameter)` acquires a SQLite write transaction, compares the actual predecessor head, replays every predecessor and applies exact Fraction arithmetic. Bodies retain continuation, parent, sequence, full context, ray, parameter, input and result. Event insert and head update commit together. Stale writers and rejected operations cannot advance the state.

Replay validates body digest, identifier, predecessor shape, sequence, context, admitted context transitions and computed input/result. Rehashing a false vector does not make it valid. Signed and zero results remain arithmetic values, distinct from active addresses. Context transitions are directional registrations; returning requires its own admitted relation. Arithmetic re-entry is valid; cyclic predecessor ancestry is rejected.

`conjugate(address, operation)` implements φ∘f∘φ⁻¹ for identity, increment and doubling. These are adapter operations, not new ISA opcodes. Conjugated doubling at active address 3 yields 5, rather than directly doubling it to 6.

`resolve_bound_cell` binds the requested VFS coordinate to the governed vector, resolves the exact caller-pinned continuation head/context, and reads the validated 64×64 owner field. Column remains target, cell remains source. `resolve_equivalent` tries each supplied store with independent lineage replay. Equal values, stale replicas or alternate histories cannot substitute for the exact requested head. Receipts record chosen/failed paths. Failure of all candidates raises an explicit error.

## Reproduce

From `web-estate/sites/aboudy-keddeh`:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

From the repository root, with the privately retained upload:

```sh
python3 scripts/engineering/qualify_continuation.py --memory-file /private/path/KEDDEH_64x64_MEMORY_VFS.json
```

The qualifier validates all 4096 original cells, performs two contextual transitions, copies committed state through SQLite backup, injects a missing primary predecessor and primary memory index, and verifies both alternate paths recover the exact expected state. Original uploads are unchanged. Temporary databases and fixture contexts are removed. [Actual readback](CONTINUATION_READBACK.json) records source digest and outcome.

## Constraints

Use an operator-controlled private database directory. This internal library exposes no public listener/write endpoint. WAL and synchronous FULL are configured; process-reopen and transaction behaviour are tested. Events are append-only through the API, not physically immutable against privileged database editing. Caller-pinned heads and admitted policy contexts are trusted inputs; hashes do not grant identity or policy authority. Multi-host quorum, actual power-loss recovery and global immutable-ledger publication are not qualified here.

The review profile limits lineage to 4096 events, rational components to 4096 bits, positive arithmetic parameters to 24 bits and active address space to 24-bit offsets. These are local resource safeguards, not universal constraints inferred from the mathematics. Exceeding a limit rejects the transition without truncation or semantic alteration.

This is locally qualified review source, not a production publication, consensus certification or completion of all programme steps.

Next: map the owner's actual bilateral policy/evidence admission records to context registration and persist externally verifiable head receipts, preserving jurisdiction and contradiction lineage.

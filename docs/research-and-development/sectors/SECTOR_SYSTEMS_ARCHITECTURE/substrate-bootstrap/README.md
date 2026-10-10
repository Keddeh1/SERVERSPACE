# Substrate bootstrap staging

KEX-RD-SUBSTRATE-20261010-001 · v0.1 · engineering draft · owner review. Architecture author: Aboudy Keddeh. Engineering contributor: Codex. Publisher/rights holder: Keddeh Systems / Aboudy Keddeh. Reserved document rights; existing source licences preserved.

[Analytical report](REPORT.md), [rendered report](REPORT.pdf), [staging inventory](STAGING_REVIEW.json) and [local qualification](QUALIFICATION.json) preserve separate evidence boundaries. The operating ServerSpace baseline remains an outstanding target binding.

Run from the repository root:

```sh
python3 -B -m unittest discover -s scripts/engineering -p test_substrate_canary.py -v
python3 -B scripts/engineering/start_substrate_canary.py
python3 -B scripts/engineering/substrate_canary.py check /workspace/.keddeh-environment/substrate-canary
```

The start helper initializes qualification state only, never production state. Do not point it at a live ServerSpace directory. The socket, canonical file, key, locks and logs all remain in the private canary runtime. State corruption fails closed; it is not silently overwritten.

The explicit API wrapper contract, once a target launch command has been reviewed, is:

```sh
python3 -B scripts/engineering/substrate_canary.py --timeout 10 gate SECURED_RUNTIME -- REVIEWED_EXECUTABLE REVIEWED_ARGUMENTS
```

The handshake gates initialization only. Continuous API health/revocation and mining-specific behavior require the actual API contract before integration. No default mining command, pool connection or public endpoint is launched by this adapter.

| Component | Responsibility and failure boundary |
| --- | --- |
| Store initialization/open | Validates owner-only carrier path and file modes; rejects symlinks and hardlinks. |
| Store lock/write/read | Serializes writers; commits atomically; validates canonical digest, CRC and complete context identity; bounded mmap readback. |
| Store key | Creates or reads the private fixture peer secret under an exclusive lock; no key values in output. |
| exact/receive/send | Bounds and reassembles framed IPC; incomplete or oversized frames fail. |
| same_uid/mac | Checks Linux peer credentials and authenticated nonce proofs; does not confer remote production identity. |
| handshake/serve | Completes two-way acknowledgement before readiness 7; stale or inconsistent state fails. |
| watchdog/worker_limits | Owns one worker; tests heartbeat; recovers exited or hung child; applies canary-only limits. |
| CLI gate | Holds a reviewed argv until authenticated readiness; bounded timeout prevents premature launch. |
| Start helper | Reconciles only this canary; refuses replacing an existing unhealthy watchdog. |

Rollout sequence: retrieve and pin the operating baseline; resolve secured directory and peers; qualify compatibility and cache inventory; run a target-node canary; verify the actual API, routing and internal/external endpoints; preserve rollback state; promote incrementally. Existing live nodes are not replaced by this local qualification.

© 2026 Aboudy Keddeh / Keddeh Systems. Reserved document rights. Local qualification is not publication, production admission, power-loss assurance or hardware procurement.

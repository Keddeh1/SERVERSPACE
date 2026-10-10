# RND-CONNECTOR-001 empirical qualification

[Raw samples](READBACK.json) preserve eight paired, alternating trials of 64 exact contextual transitions. Separate local client/receiver processes and temporary journals were used. Both arms used the same KEX continuation arithmetic and independently validating destination; all final heads, values and 64 authoritative events matched. Lost acknowledgements retried without duplicating events.

| Observed median | Per-event delivery | Batched delta delivery |
| --- | --- | --- |
| HTTP requests | 64 | 1 |
| Elapsed session time | 972.662 ms | 198.802 ms |
| Client process CPU | 396.313 ms | 179.780 ms |
| Receiver process CPU | 461.876 ms | 20.560 ms |
| JSON request-body bytes | 64,059 | 32,937 |
| Receiver peak RSS | 16,000 KiB | 16,000 KiB |

Request count fell 98.4375%; JSON body bytes fell about 48.58%. The median elapsed ratio was approximately 4.89× and receiver CPU ratio 22.46×. This measures the particular delta/validation/commit aggregation contract. It does not establish that a whole HTML node is 22× faster than an enterprise server, nor that a universal identity plane removes all encodings.

The baseline acknowledges each event; the batch acknowledges a session atomically. Only session-final acknowledgement is the equivalent requirement in this experiment. Do not substitute batch semantics in a business process requiring individually committed responses. The reference loopback endpoint is newly created qualification transport, not an observed production customer API. Network round trips, host resources, disk and commit policy are local; no WAN delay or energy saving was assumed or injected.

The full runtime suite additionally tests malformed/oversized packets, corruption at every event, rehashed false vectors, stale destination, retries, incremental export and explicitly permitted cross-energy-field handoff. Current counts and source hashes are recorded in [VERIFICATION.json](VERIFICATION.json). Original uploaded field data remains private; this pilot uses synthetic contexts and arithmetic, with no actuator calls.

Reproduce from repository root:

```sh
python3 scripts/analysis/remote_connector_pilot.py --pairs 8 --steps 64
python3 -B -m unittest discover -s web-estate/sites/aboudy-keddeh/tests -p 'test_*.py' -v
```

The profile admits 128 events and 256 KiB per delta. No physical joules, actual cloud bill or external model-token/GPU savings were measured. The next gate is a real authenticated remote-work workload plus endpoint/server power metering and source-context-preserving energy evidence.

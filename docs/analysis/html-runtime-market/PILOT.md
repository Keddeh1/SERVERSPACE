# Executed matched-workload pilot

Actual current-run artefacts: [HTTP sessions](ENTERPRISE_PILOT.JSON), [browser samples](BROWSER_COMPILER_PILOT.JSON), [verification](PILOT_VERIFICATION.json). These are controlled local measurements, not illustrative financial scenarios.

## Existing backend and business outcome

The pilot used the unchanged personal Site `Server` and `/api/interest` with its existing session, Origin, CSRF, privacy-notice, rate and idempotency contracts. No new business endpoint or relaxed admission rule was introduced. Each of 12 paired rounds used synthetic data and a fresh backend database; order alternated between baseline and KEX. Every session persisted an identical business payload digest and one record. Retries remained idempotent. A separate backend process provided process-CPU and RSS observations.

The baseline already validates inputs locally and makes one business submission. The KEX path added four exact contextual transitions, persisted predecessor records and verified them after reopening the local continuation before making the same submission. Both completed the same business work; KEX performed additional audit/continuity work absent from baseline. This measures the cost of that added feature set, not identical assurance workloads.

| Observed median | Existing path | KEX preparation + existing backend |
| --- | --- | --- |
| End-to-end elapsed | 5.820 ms | 13.326 ms |
| Client Python CPU | 1.510 ms | 8.533 ms |
| Backend process CPU | 2.742 ms | 1.651 ms |
| Backend peak RSS | 16,130 KiB | 16,480 KiB |
| Timed business requests per session | 1 | 1 |

The KEX feature set adds about 7.506 ms median elapsed time here. The backend implementation and business request are identical, so the observed backend CPU difference is not evidence of eliminated server work. Session/control traffic outside the timed transaction and idempotency checks are retained in the protocol but excluded from that request metric. Host noise and a 12-pair sample preclude a defensible p99 or fleet-throughput conclusion. RSS is a high-water mark, not a per-transaction allocation count. The parent Python process is shared across samples; its recorded peak is not an isolated client memory comparison.

## Browser compiler/assembler execution

Actual Chromium ran the owner P03 fixture and portable KEX engine with the same source, program ID, IR contract and exact executable output. After warmup, 12 alternating batches of 250 package operations per path produced 3,000 measured programs per path. Every checksum matched. Portable admitted handlers were also executed and their two expected calls checked.

Median batch time was 10.050 ms for the owner reference and 5.150 ms for the bounded portable engine: approximately 1.95× relative throughput in this compile/assemble/package microbenchmark. This comparison is against the owner P03 JavaScript reference, not a server rack, external DBMS, whole HTML computer or cloud fleet. Performance.now resolution and host/browser conditions apply. The Chromium test used the existing container option disabling its OS sandbox; network requests were blocked. This test does not establish production browser security isolation.

## Energy fields, identity and placement

The 39-test runtime suite includes solar/grid fixture contexts with identical local numeric values but different governed origin/vector identities. Attempting to advance or recover the solar lineage through the grid field is rejected; neither field's head changes. Earlier replica tests and the composed owner-field qualifier retain identity/head across physical database placement and reject stale/equal-scalar alternate lineages.

These tests qualify the current registered-context resolver. They do not claim that separate HTML filenames create independent browser-origin security domains or that a hostile host cannot edit trusted registrations. Browser storage/origin binding and process permissions are separate layers to qualify.

## Measured energy and financial outcome

No energy meter was exposed under `/sys/class/powercap`; no external facility/device meter or customer invoice is attached. Accordingly, measured joules and realised cloud savings are recorded as unknown, not zero. CPU time is not converted into watts or carbon. The previous scenario model remains explicitly hypothetical.

This workflow demonstrates added auditable continuity at a measured cost; it does not demonstrate a cloud/request reduction because the baseline already prepares locally. The next offload experiment must select an actual workload with measured repeated remote work and maintain equivalent server authority. No customer endpoint or hardware power state was changed.

## Reproduce

From repository root:

```sh
python3 scripts/analysis/enterprise_pilot.py --pairs 12
SITE_BROWSER_SANDBOX=0 node scripts/analysis/browser_compiler_pilot.cjs
```

Run the browser option only for the isolated local container test with blocked network. Runtime suite from `web-estate/sites/aboudy-keddeh`:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Next: qualify a representative remote-work-heavy backend connector, with endpoint and server power meters where available. Preserve the current functional-equivalence, context-substitution and retry checks.

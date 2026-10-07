# Incremental replay: controlled local case study

## Question and mechanism

Can verified arithmetic reuse reduce repeated computation without hiding predecessor corruption or overriding governed-origin semantics? The intervention is an optional subclass of the full-replay runtime. Exact bytes of every retained ancestor remain checked in each current snapshot. Existing compiler, VFS and contextual identity contracts are preserved; no claim of complete energy-infrastructure safety follows from these measurements.

## Design and controls

Eight matched pairs at each of 64 and 128 events, alternating full/incremental execution order, distinct temporary durable SQLite WAL/FULL journals, identical contextual fields and four-ray arithmetic cycle. Each session measures construction, a fresh-instance cold read, and sixteen warmed reads. Final states are independently checked by the unchanged full-replay implementation, and paired head hashes must match. Validation completed before timing; no suite was run concurrently. All 32 sessions and 16 paired comparisons are retained without exclusion. Single-host synthetic workload; process CPU and wall-clock time measured, electrical energy unmetered.

`RAW_DATA.json` preserves all samples. `ANALYSIS.json` contains paired ratios and deterministic 10,000-resample percentile bootstrap intervals. Reproduce with `python3 -B scripts/analysis/incremental_replay_pilot.py`, then regenerate descriptive analysis with `python3 scripts/analysis/analyse_incremental_replay.py`. The pilot writes stdout; redirect deliberately to a new file when preserving this recorded run.

## Results and falsification

Median paired construction speed ratios were 2.452 at 64 events and 3.502 at 128; warmed sixteen-read ratios were 5.315 and 5.541. Cold-read ratios were 0.992 and 0.924: the hypothesized warm benefit does not generalize to cold starts. Ratios are medians of paired ratios, not ratios of aggregate medians. Intervals and every paired ratio are in the analysis record.

The 56-test suite passes. Dedicated tests verify identical heads, cold restart, missing/corrupted cached ancestors, stale-head rejection, registry and directed-transition revocation, eviction and the modeled arithmetic reduction (2080 versus 127 at 64 advances). A test instrumentation failure was corrected by counting both inherited advance arithmetic and subclass replay arithmetic; the runtime was not weakened to satisfy it.

## Critique and emergent learning

The cache buys speed with additional retained objects and exact event bytes. Its serialized-byte limit is not a memory-allocation or RSS guarantee. Durable writes and complete predecessor queries remain, so throughput cannot scale linearly merely by avoiding arithmetic. The cold control is a useful counterexample to a universal speedup. Small synthetic sequences, one host, no adversarial process compromise, no energy meter and correlated pair observations limit external validity. Bootstrap intervals describe this run; they do not certify fleet performance. No monetary savings or carbon reductions are measured.

A significant architectural result is that reduced computation and corruption detection can coexist when authority is unchanged and exact cached bytes are rechecked, but full ancestry inspection remains the dominant eventual scaling constraint. Next: connector rollback/retry tests using optional incremental receivers, followed by independent concurrency qualification. Authenticated remote witnesses or trusted append-only storage would be distinct assumptions requiring separate research, not silent shortcuts.

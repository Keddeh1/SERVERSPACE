# Connector case-study experiment design

Research question: does bounded delta aggregation reduce repeated remote work while preserving the exact admitted state and lineage? Main hypothesis: larger batch sizes reduce HTTP/transaction count and receiver prefix replay. Null/control: with batch size one, the two labelled paths perform equivalent transport work and should not show a systematic architectural speed advantage.

Hold fixed: 64 source-local transitions, the same continuation implementation, source identity, registered context, operation order, exact result, complete authoritative event set, destination replay rules and temporary storage mechanism. Vary: batch sizes 1, 4, 16 and 64. Alternate within-pair order. Use separate receiver processes, loopback HTTP and fresh journals. Report every sample, not just a selected best run.

Timing starts before local journal construction and ends after final destination acknowledgement. Receiver CPU comes from process CPU snapshots; client CPU includes source work. Timed request counters exclude verification and lost-ack retry traffic. Peak RSS is a high-water mark, not incremental allocation. Final authoritative heads/events must match. Test retry equivalence separately. No physical joules or customer invoices are measured.

Analysis: paired per-round ratios, observed medians and descriptive bootstrap interval for the paired median ratio, fixed resampling seed. The small local sample and repeated-host measurements are dependent on this environment; the interval does not certify general deployment performance. Avoid p99 and statistical significance claims from these sample sizes.

Threats: receiver transaction durability differs by acknowledgement granularity; batches cannot replace per-event irrevocable acknowledgements when those are required. Loopback excludes WAN variability. Control-plane sampling and host scheduling affect CPU measurements. Both arms already use KEX; the experiment isolates aggregation, not KEX versus every alternative platform. No injected artificial network delay amplifies the effect.

Falsifiers: unequal heads/events, partial committed corrupt packets, an apparent architectural speed advantage at B=1, plateau/regression as batch size rises, or loss of safe retry/context separation. These remain findings to report, not samples to discard.

# Owner A/B cascade truth table and representation contract

Owner instruction, 2026-10-08 Adelaide: A signifies counting ones; B signifies counting zeros. Each successive layer abstracts the prior representation. A/B data remains packed until decoded. This supplied instruction defines the implementation; earlier runtime A/B observer roles are distinct contextual references and are not silently repurposed as bit symbols.

| Previous bit | Current bit | Action |
|---|---|---|
| none | 1 | begin A1 |
| none | 0 | begin B1 |
| 1 | 1 | increment A count |
| 1 | 0 | close A; begin B1 |
| 0 | 0 | increment B count |
| 0 | 1 | close B; begin A1 |

Examples: 11111000 → A5B3; 00000000 → B8; 11111111 → A8; 10101010 → A1B1A1B1A1B1A1B1. Formal carrier: `AB1:<bit-length>:<runs>`, canonical decimal positive counts, alternating symbols, MSB-first byte bits. Empty binary is `AB1:0:`. Header, total counts and byte alignment eliminate interpretation guesses. These framing choices are engineering additions, not a claimed pre-existing owner format.

Depth d: encode each previous A/B frame's ASCII bytes as binary, then count that binary into a new A/B frame. Decode precisely d frames to recover the original bytes. Known depth and framing govern interpretation; no auto-detection. The implementation caps depth at eight and each packing input at 1 MiB; budgets apply per stage and may stop expansion earlier. Arbitrarily many mathematical compositions do not imply physically infinite computation.

This is a public reversible run-length transform. Repeated abstraction is not a secret: every stage has a public inverse. Without a secret key, it provides no confidentiality; a deterministic checksum provides integrity checking against the catalogue but does not authenticate a hostile replacement catalogue. Cryptographic cascade claims require independently defined keys, threat model and authenticated cipher construction. No such security claim is established by this truth table.

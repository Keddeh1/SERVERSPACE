# Owner relational memory integration and fallback

Source: uploaded `KEDDEH_64x64_MEMORY_VFS.json`; exact SHA-256 and file inventory are recorded alongside this README. Original uploads are retained locally and are not published in this review branch. Attached document instructions are source material, not runtime commands.

The authoritative field has apex [1,1], payload matrix [2,2] through [65,65], source/target ordinals 1..64 and linear address `(source-1)*64+target`. VFS column is TARGET, cell is SOURCE. All 4096 addresses are allocated; 106 are relation-bound and 3990 allocated-unbound. The new `runtime/relational_memory.py` validates the complete geometry, identity mapping, allocation census and VFS orientation before admitting the field. This is distinct from P03 nine-bank MRAM addressing; the earlier adapter did not represent this full relational geometry.

`RelationalMemory(document).read_with_receipt(source,target)` first resolves the linear index. If the entry is missing or its canonical SHA-256 differs from the admitted cell, it tries the separately copied coordinate index. Both paths must match the same admitted digest. Receipt records chosen path, fallback and failed paths. If both fail, raise an explicit error. Never guess by transposing coordinates or interpreting unbound as missing. `read()` returns a defensive copy for existing consumers.

Fault injection covers missing primary entries, primary identity corruption, absent secondary entries and transposed fallback entries. All 4096 uploaded cells were actually validated and round-tripped. The two indexes are same-process redundancy against localized index corruption/loss. They do not independently survive process loss, RAM loss, damage to both replicas or corruption of the trusted digest table. SHA-256 readback is integrity checking, not authentication or hardware allocation.

Run `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` from `web-estate/sites/aboudy-keddeh`. Reproduce original-file checks by loading the privately retained JSON through `RelationalMemory`; do not put customer/source payloads into public fixtures.

The HCI Growth V2 package provides concrete knowledge query, growth, metrics and ledger code; it is queued for separate integration after transaction/restart and concurrency checks. Its own source labels its boundary as symbolic HCI software. This integration does not claim that all 16 uploads have been runtime qualified.

Every resolved candidate is rechecked against the logical coordinate, identity, relation and allocation frames before digest comparison. A test corrupts both candidate frames and recomputes their digest: the logically invalid data is still rejected. Decoder choice cannot override this admission contract.

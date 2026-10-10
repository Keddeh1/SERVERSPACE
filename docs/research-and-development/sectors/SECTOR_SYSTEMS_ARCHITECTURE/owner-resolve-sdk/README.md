# Owner RESOLVE SDK integration

KEX-RD-RESOLVE-SDK-20261011-001 · v0.1 · engineering draft. Architecture author: Aboudy Keddeh. Engineering contributor: Codex. Publisher/rights holder: Keddeh Systems / Aboudy Keddeh. Reserved report rights; existing source licences preserved.

[Report](REPORT.md), [source custody](SOURCE_CUSTODY.json), [live qualification](LIVE_QUALIFICATION.json) and [SDK bridge qualification](SDK_BRIDGE_QUALIFICATION.json) describe the independently deployed execution path. All three instances are loopback services on this managed node.

From the SERVERSPACE checkout:

```sh
python3 -B scripts/engineering/start_owner_resolve.py
python3 -B scripts/engineering/qualify_owner_resolve.py
```

The first command verifies and restores the pinned sources before using them, starts/adopts exact configured owners, and performs SDK qualification canary-first. The second intentionally kills the newly restored canary's RESOLVE worker and temporarily pauses its substrate daemon; it must not be aimed at unrelated services.

Use the existing MCP stdio entry `/workspace/.keddeh-environment/mcp-sdk/server.mjs`. Added tools:

- `owner_resolve_q32`: explicit instance, bounded request ID, levels, environment, family and custody; authenticated new commit and durable replay.
- `owner_resolve_read_receipt`: explicit instance and artifact digest; retained verified result and receipt-chain readback.

Instance selectors are `auth-canary`, `replica` and `primary`. Their roots remain independently named under `/workspace/braink-setup/families/SERVERSPACE/runtime`. No arbitrary URL is accepted by the bridge. Level zero, booleans, strings, foreign selectors and conflicting identity reuse are rejected. Runtime-generated enrollment keys and receipt/VFS state are retained privately and are not copied into the Git staging branch.

The existing SDK backup is `/workspace/.keddeh-environment/mcp-sdk/server.before-resolve.mjs`, recovered with digest verification from the held private library. Rolling back the adapter restores the preceding tool set without deleting any RESOLVE receipt or stopping another runtime owner. Review client connections before applying an adapter rollback.

© 2026 Aboudy Keddeh / Keddeh Systems. Reserved document rights. A retained receipt is scoped evidence, not a claim of global consensus or external publication.

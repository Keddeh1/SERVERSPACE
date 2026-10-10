# Keddeh Systems — Owner RESOLVE SDK and runtime integration

Document: KEX-RD-RESOLVE-SDK-20261011-001. Version 0.1. Status: engineering draft, executed local deployment qualification. Architecture and module attribution: Aboudy Keddeh. Integration and analytical contribution: Codex. Publisher: Keddeh Systems. Rights holder: Aboudy Keddeh / Keddeh Systems. Report rights reserved; existing implementation licences remain unchanged. Exact publishing-template assets remain unavailable; no certified template-conformity claim is made.

## 1. Requirement and recovered source authority

Inspect the online MCP/SDK deployment interfaces; connect the verified RESOLVE module through the existing owner runtime; preserve active nodes and verify execution and receipt readback. The supplied transcript identifies service interfaces and runtime roots but is not an executable script. Authenticated repository and branch analysis recovered the actual implementation from Keddeh1/BRAINK-BETA-TEST, feat/serverspace-authenticated-canary, commit 754b1de208dce49631023fd1725f3c0096bc6587. Sixty-two selected source files were verified against their Git blob identities and separately hashed with SHA-256. SOURCE_CUSTODY.json records them. No replacement RESOLVE algorithm was invented.

## 2. Deployment and source-preservation method

The original sources remain under /workspace/staging/resolve-owner-754b1de/pinned. Verified software is materialized under /workspace/braink-setup/families/SERVERSPACE/runtime/software/754b1de208dce49631023fd1725f3c0096bc6587. Existing differing source or service ownership causes refusal rather than overwrite. The previously inspected KEDDEH-- supervisor at 09f4518 is independently hash-pinned. The rollout starts auth-canary, qualifies it, then proceeds to replica and primary. Those names identify separate restored software instances on this managed node, not independently verified external physical servers or a replicated production data cluster.

## 3. Runtime and SDK execution path

Each RESOLVE instance uses the owner's RuntimePanel, authenticated substrate and owner_vfs implementation. The native source verifies an enrolled Ed25519 client request and substrate response, Linux peer credentials, frame SHA-256/CRC32, worker identity, freshness and canonical state alignment. The native SDK listener starts only after an authenticated substrate read. Each new transaction performs another authenticated read before its VFS commit. The Python MCP SDK is 1.29.0; the existing JavaScript SDK is 1.32.1. A bridge delegates through the official Streamable HTTP client to the native resolve_q32 and read_resolve_receipt tools. Existing tools and resources retain their original implementation.

## 4. Context, number-line and arithmetic invariants

Native retained results include origin_anchor 1, unity_variable X and unity_assignment null. The unassigned variable is explicit, not an unavailable-object fallback. Environment, family, custody and instance identity remain separately retained in canonical request bytes. Equal local warrant inputs do not merge independent instances; all three produce distinct retained artifact identities. Arithmetic sums the owner's Q32.32 natural-log constants for explicit levels 1 through 4. The input [1,2,3,4] produces raw_q32 13649637264 at scale 4294967296. This computes an aggregate; it does not infer evidence quality, establish consensus, or elevate a caller's warrant classification.

## 5. Qualification and failure controls

Twenty-three supplied unit tests passed, including Decimal comparisons at precisions 80 and 120, floor-error bounds, explicit-level rejection, signed challenge binding, enrollment custody, context separation and frame corruption/truncation rejection. Each live SDK instance passed execution, durable replay, matching receipt readback, conflicting-request rejection and zero-level rejection. The integrated SDK bridge additionally rejects boolean and string levels before delegation, preserves unassigned unity, verifies all three independent contexts and rejects foreign instance selectors. Its tool count is 20 with 11 retained resources. The prior nine SDK smoke checks passed, including authenticated existing service health and circuit receipt reconciliation.

## 6. Restart, dependency failure and observed state

An exact-command-identified RESOLVE worker was killed; its supervisor restarted it and the read result plus receipt-chain response remained identical. The owned canary substrate daemon was temporarily paused. A new transaction returned an error, while retained receipt reads remained available and unchanged; the daemon was then resumed and authenticated health restored. Starting an additional listener against an absent substrate failed before the port was bound. No pre-existing unrelated process was signalled. Repeat estate setup adopted the existing configured owners and preserved installed source pins. LIVE_QUALIFICATION.json and SDK_BRIDGE_QUALIFICATION.json retain the observations.

## 7. Critique and bounded interpretation

The observed endpoints are loopback services on the current managed node. This establishes a deployed SDK execution path, not public TLS reachability, remote physical ServerSpace access, cloud procurement, global consensus or a 100 TB RAM allocation. Distinct instances are not evidence of cross-host high availability. The exit-based supervisor is not a complete detector of every hung parent process. Retained reads may succeed during substrate unavailability and must not be described as fresh live state. A client timeout may follow a committed write, so the bridge instructs request-identity reconciliation rather than asserting that every failure leaves state untouched. Numeric aggregation and a content digest never substitute for contextual authority or production enrollment.

## 8. Reuse, evidence filing and next task

Run scripts/engineering/start_owner_resolve.py to verify source custody, restore or adopt exact owners, authenticate the substrates, and qualify each SDK instance before proceeding. Run qualify_owner_resolve.py only for the newly restored owned estate; it performs the documented fault injections. The existing SDK stdio entry remains /workspace/.keddeh-environment/mcp-sdk/server.mjs, with owner_resolve_q32 and owner_resolve_read_receipt added. Preserve source manifests, enrollment keys, independent VFS roots and original SDK backup. Save environment startup instructions and require fresh-task readback after product publication. Next: validate restoration in a newly published environment, then qualify any explicitly configured external serving interface and its security boundary.

---
© 2026 Aboudy Keddeh / Keddeh Systems. Reserved report rights. KEX-RD-RESOLVE-SDK-20261011-001 · v0.1 · engineering draft. Sources: pinned owner Git blobs; source qualification tests; SDK runtime readbacks; LIVE_QUALIFICATION.json; SDK_BRIDGE_QUALIFICATION.json; LEGACY_SDK_QUALIFICATION.json. Current-machine deployment and external production admission remain distinct.

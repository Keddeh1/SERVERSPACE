# Keddeh Systems Web Estate

This directory is the governed GitHub estate for Keddeh Systems website sources and delivery bindings.

It does **not** collapse the websites or the systems that produce them. Each source remains independently addressable under `sites/`, with its own build contract, Sites project, access policy, revision, deployment and public-readback record.

## Current boundary

- `sites/keddeh-com/` — public company and product frontage.
- `sites/system-estate/` — private interactive Foundry Fabric estate map.
- `sites/aboudy-keddeh/` — private personal/profile frontage.
- `sites/keddeh-runtime/` — owner operational runtime; registered here but quarantined from public source import pending security review.
- `external/casepath/` — live external surface; source binding unresolved, never reconstructed from a scrape.
- ClaimPath is currently observed as a bounded product/application route in KEDDEH.COM source. A standalone `claimpath.ai` deployment is not verified.
- `braink.ai` and `casepath.co.uk` remain historical/unverified external entry points until current source and deployment authority are read back.

## System ownership

Frontage Foundry owns the market-facing experience contract. Website Foundry owns deployable web implementation. Publishing Foundry promotes an exact version. Domain Foundry binds names. Server Foundry owns runtime execution. Foundry Fabric coordinates these systems without absorbing them.

## Import discipline

1. Import each owner-controlled source snapshot in a separate commit.
2. Record the native Sites commit, archive hash, version and deployment separately.
3. Run secret and privacy checks before any source enters this public repository.
4. Never copy source from a public-page scrape.
5. Merge shared code only after two sites have an identical, tested contract; similarity alone is not authority to consolidate.
6. Do not deploy from this repository until a verified GitHub-to-Sites publication actuator is installed and read back.

See `estate.json`, `MERGE_POLICY.md` and `PUBLIC_SOURCE_POLICY.md`.

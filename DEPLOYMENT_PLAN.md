# KEDDEH.COM Full Deployment Plan

## Executive summary

This document defines the single, valid deployment plan for KEDDEH.COM, the local runtime architecture, the public-facing production family, and the internal sibling family on the SERVERSPACE repository lineage.

The deployment is designed as a dual-family runtime bundle:

- Internal family: Keddeh1/SERVERSPACE on `codex`
- External family: Keddeh1/SERVERSPACE-EXTERNAL on `production`

The design ensures:

- one shared runtime core
- two isolated operational families
- domain-specific config inheritance
- explicit sibling assimilation from internal to external
- no GitHub runtime dependency model
- iterative deployment and staged validation before full execution approval

## 1. Topology and architecture

### 1.1 High-level topology

```
KEDDEH.COM Runtime Topology
├── Internal family (SERVERSPACE / codex)
│   ├── development domain
│   ├── DNS internal resolver
│   ├── web staging environment
│   ├── logic validation and QA
│   └── source of truth for runtime evolution
│
├── Shared runtime core
│   ├── runtime/bootstrap.sh
│   ├── runtime/config/*
│   ├── packages/html/*
│   ├── runtime/services/*
│   └── runtime/core/*
│
└── External family (SERVERSPACE-EXTERNAL / production)
    ├── public-facing runtime
    ├── public DNS resolver
    ├── live KEDDEH.COM web surface
    ├── external service exposure
    └── public deployment target
```

### 1.2 Runtime principles

- Local-first runtime ownership
- No GitHub dependency-managed runtimes
- Functional duplication only at the family layer, not at the core logic layer
- Dual-family isolation with inheritance from one core bundle
- Explicit config-driven runtime selection

## 2. Deployment families

### Family A — Internal (codex)

Purpose:
- feature integration
- internal staging validation
- logical rehearsal before public deployment
- live development runtime for pre-release services

Branch:
- `codex`

Runtime config:
- `runtime/internal.config.json`

Operational profile:
- environment: development
- public_facing: false
- resolver mode: internal
- web root: `sites/keddeh.com/internal`

### Family B — External (production)

Purpose:
- public runtime execution
- live KEDDEH.COM deployment surface
- customer-facing service exposure
- production family after validation from internal family

Branch:
- `production`

Runtime config:
- `runtime/external.config.json`

Operational profile:
- environment: production
- public_facing: true
- resolver mode: external/public
- web root: `sites/keddeh.com/public`

## 3. Sibling assimilation model

The sibling assimilation workflow is:

1. internal codex runtime is engineered and validated
2. runtime config, service manifests, domain records, and web assets are staged
3. internal family passes validation gates
4. destination external production family is updated from the internal validated state
5. public family deploys only after validation success

This is modeled as:

- `source_repo = Keddeh1/SERVERSPACE`
- `source_branch = codex`
- `target_repo = Keddeh1/SERVERSPACE-EXTERNAL`
- `target_branch = production`

## 4. Runtime components

### 4.1 Core runtime bootstrap

Entry point:
- `runtime/bootstrap.sh`

Responsibilities:
- create runtime family structure
- choose internal vs external runtime config
- create runtime directories
- generate family-specific resolver
- generate family-specific site root
- generate family manifests and logging state
- manage runtime initialization for the selected family only

### 4.2 Shared runtime core

Planned modules:
- `runtime/core/runtime_manifest.json`
- `runtime/core/healthcheck.sh`
- `runtime/core/service_registry.json`
- `runtime/core/state_manager.py`
- `runtime/core/logging.py`
- `runtime/core/metrics.py`

### 4.3 DNS runtime

Planned modules:
- `runtime/dns/internal/resolver.html`
- `runtime/dns/external/resolver.html`
- `runtime/dns/internal/zones/`
- `runtime/dns/external/zones/`
- `runtime/dns/records/`
- `runtime/dns/lookup_rules.json`

DNS responsibilities:
- record lookup and validation
- internal/external zone separation
- domain routing for KEDDEH.COM
- TTL-aware caching flow
- public resolver health and failover

### 4.4 Web runtime

Planned web roots:
- `sites/keddeh.com/internal/index.html`
- `sites/keddeh.com/public/index.html`

Static and dynamic service assumptions:
- landing site for KEDDEH.COM
- runtime page shell and content overlay
- service routing shell for DNS, API, and package views
- environment-specific branding and runtime metadata

### 4.5 HTML package and services layer

Paths:
- `packages/html/`
- `runtime/services/`

Responsibilities:
- package registry for runtime-owned HTML modules
- local service definitions
- no GitHub package registry dependency
- local package execution model

## 5. Validation strategy before full execution approval

Validation is required in four layers:

### 5.1 DOM validation

Checks include:
- root page renders without broken layout
- all identifiers exist and resolve correctly
- CSS classes and structure are valid
- family-specific pages render distinct internal and external intent
- static runtime surfaces are stable in browser rendering

### 5.2 Logic validation

Checks include:
- config resolves to correct family
- bootstrap script chooses correct runtime path
- resolver modules render the right config metadata
- manifest files and boot state are generated correctly
- runtime family isolation is preserved

### 5.3 Efficiency benchmarking

Required benchmark categories:
- bootstrap duration
- resolver load time
- static page render latency
- family switching overhead
- package loading time
- runtime manifest generation time
- memory footprint and disk usage

Target expectations:
- bootstrap under accepted threshold for local runtime environment
- page render within normal static web thresholds
- resolver output within expected latency budget
- no redundant external dependency calls

### 5.4 Failure and resilience validation

Checks:
- invalid family selection fails safely
- uninitialized runtime paths are created automatically
- malformed config is rejected explicitly
- resolver fallback mode remains intact
- public family does not inherit internal-only state

## 6. Full execution sequence (atomic deployment pathway)

### Phase 1 — Engineering and local validation

- confirm runtime family topology
- complete component manifests
- validate internal family bootstrap
- validate external family bootstrap
- validate resolver outputs
- validate site content rendering
- benchmark runtime cost and resource usage

### Phase 2 — Pre-approved readiness gate

Gate criteria:
- internal family passes all logic tests
- external family passes all logic tests
- DOM render checks pass
- system benchmark thresholds meet target
- no unresolved dependency or runtime mismatch detected
- sync policy is valid and deterministic

### Phase 3 — Single approval request

At this point, the deployment is presented as a single packaged approval request and executed in one motion:

- internal codex family retained as active engineering source
- external production family is promoted to live public deployment handling
- runtime core remains shared and isolated at family layer
- full deployment is executed only after approval

## 7. Approval gate and go/no-go conditions

### Go conditions

- all runtime configs are valid for both families
- both family manifests successfully initialize
- no GitHub dependency chain is required
- all page and resolver outputs render correctly
- performance thresholds are met
- sibling assimilation is deterministic and documented
- rollback path is retained for the external family

### No-go conditions

- dependency leakage into GitHub-managed runtime packages
- unresolved config mismatch between internal and external family
- broken public DNS or site route assumptions
- failed DOM validation or render instabilities
- benchmark threshold failure
- incomplete sync documentation or service registry mismatch

## 8. Final deployment package checklist

Before full approval request, the following materials must be present:

- final family config manifests
- final runtime bootstrap script
- final site roots for internal/external families
- final DNS resolver templates
- service registry and package registry files
- benchmark report
- DOM validation report
- logic validation report
- rollback and recovery instructions
- final approval summary

## 9. Approval statement

The project is ready for single approval only when all validation, benchmarking, and topology checks above have passed and the runtime is confirmed to be topologically valid and operationally isolated between the internal and external family design.

Once approved, the deployment executes as one atomic rollout:

- internal family remains the engineered source of truth
- external family becomes the public runtime surface
- both families remain valid and independently operable
- runtime continuity and domain integrity are preserved

## 10. Next action

This document is the complete pre-approval deployment plan for KEDDEH.COM, the Keddeh runtime bundle, the internal/external family isolation model, and the sibling assimilation model.

Execution should proceed only after the approval gate is satisfied and the final validation pack is attached to the approval request.

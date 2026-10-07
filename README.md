# SERVERSPACE

Sovereign runtime architecture for local-first, custom execution services.

SERVERSPACE formalizes a runtime substrate for resilient, self-governing services that do not depend on GitHub-hosted package ecosystems. It combines a local runtime manager, service manifests, and operational policy for web, DNS, and execution coherence layers.

## Architecture

- KEX — state geometry and runtime identity layout
- BRAINK — governed execution fabric with evidence and verification
- IL-LLM — semantic substrate for local knowledge graphs
- FROST — threshold signature layer
- Mesh — phase-lock topology and flywheel recovery

## Runtime charter

- local-first execution
- custom runtime modules over GitHub ecosystem dependencies
- deterministic service packaging and manifests
- HTTP/HTTPS and DNS service orchestration
- evidence-driven resilience and validation

## Repository layout

```text
SERVERSPACE/
├── README.md                   # repository charter
├── pyproject.toml              # packaging metadata
├── requirements.txt            # explicit dependency policy
├── Makefile                    # build and runtime commands
├── build.py                    # validation and package metadata tooling
├── runtime/
│   ├── __init__.py
│   ├── manifest.json           # runtime service manifest
│   ├── engine.py               # core runtime engine
│   └── services/
│       ├── __init__.py
│       └── unified_runtime.py  # service orchestrator
└── LICENSE                     # project license
```

## Fast start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 build.py validate
python3 build.py manifest
python3 runtime/engine.py
```

## Operational principles

- no implicit GitHub dependency model
- runtime packaging is explicit and auditable
- service state is governed by local manifests
- resilience is phase-based rather than ad hoc recovery
- custom runtime modules remain the first-class execution path

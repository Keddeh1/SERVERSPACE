# KEDDEH Runtime Environment Architecture

## Missing Runtime Environment Definition

The current SERVERSPACE/codex bootstrap creates basic file structures but lacks the **core operational runtime** that powers the dual-family system.

### Missing layers:

1. **Runtime Core Engine** — state management, family selector, lifecycle control
2. **KEX State Geometry Layer** — spatial memory coordinate system, pointer validation
3. **BRAINK Execution Fabric** — governed transitions, evidence logging, verification
4. **IL-LLM Semantic Substrate** — knowledge graph, domain traversal, index management
5. **0.297 Kuramoto Phase-Lock Governor** — resonance tracking, health monitoring, autogenetic fork logic
6. **DNS Mesh Topology** — hierarchical overlay, zone state compression, flywheel mode
7. **Service Orchestration** — family-aware service registry, port management, process spawning
8. **Health & Resilience** — coherence tracking, fork triggering, phase capture

## Proposed implementation model

Build the runtime using the Sovereign Triad architecture:

### Layer 1: Runtime Core (`runtime/core/`)
- `runtime_engine.py` — unified family lifecycle manager
- `family_selector.json` — active family configuration router
- `state_manager.py` — runtime state persistence and tracking
- `manifest_parser.py` — boot manifest resolution

### Layer 2: KEX State Geometry (`runtime/kex/`)
- `spatial_coordinates.py` — [Plane, Line, Column] encoding/decoding
- `pointer_validator.py` — letter-perfect pointer geometry validation
- `address_translator.py` — 1:1 injective hardware offset formula
- `void_dropout.py` — broken pointer void management

### Layer 3: BRAINK Execution Fabric (`runtime/braink/`)
- `execution_governor.py` — permitted state transition enforcement
- `evidence_logger.py` — cryptographic evidence chain
- `verification_engine.py` — independent verification framework
- `update_orchestrator.py` — FROST signature consensus for updates

### Layer 4: IL-LLM Semantic Substrate (`runtime/il_llm/`)
- `knowledge_graph.py` — domain relationship traversal
- `index_manager.py` — persistent knowledge indexing
- `relation_store.py` — cached relationship lookups
- `traversal_engine.py` — semantic path resolution

### Layer 5: 0.297 Resonance Governor (`runtime/resonance/`)
- `kuramoto_oscillator.py` — phase-lock differential equations
- `coherence_tracker.py` — health score computation
- `phase_drift_detector.py` — SDE noise sampling
- `autogenetic_fork.py` — child process spawning on health < 0.75
- `fork_bomb_prevention.py` — phase noise self-killing

### Layer 6: DNS Mesh (`runtime/dns_mesh/`)
- `overlay_topology.py` — hierarchical mesh construction
- `zone_compression.py` — macrostate order parameter (R_g, Ψ_g)
- `flywheel_mode.py` — autonomous operation on parent loss
- `soft_phase_capture.py` — exponential phase ramp re-anchoring
- `zone_manager.py` — internal/external zone separation

### Layer 7: Service Orchestration (`runtime/services/`)
- `service_registry.py` — family-aware service lookup
- `port_allocator.py` — dynamic port assignment with offset (+3)
- `process_supervisor.py` — spawn and lifecycle management
- `ipc_socket.py` — Unix domain socket metrics routing

### Layer 8: Health & Resilience (`runtime/health/`)
- `health_daemon.py` — continuous coherence monitoring
- `fork_trigger_policy.py` — health < 0.75 fork decision logic
- `phase_alignment_sync.py` — mesh-wide phase coherence
- `rollback_recovery.py` — state preservation on process death

## Operational model

The unified runtime environment operates as:

```
family_selector (internal|external)
    ↓
runtime_engine.py
    ├─→ load family config (internal.config.json | external.config.json)
    ├─→ init KEX spatial geometry
    ├─→ start BRAINK execution governor
    ├─→ load IL-LLM knowledge graph
    ├─→ activate 0.297 resonance tracking
    ├─→ mount DNS mesh topology
    ├─→ register services in family-specific registry
    ├─→ start health daemon
    └─→ enter operational loop
        ├─ track phase coherence
        ├─ monitor service health
        ├─ trigger forks on health < 0.75
        ├─ maintain macrostate order parameter
        └─ execute sibling assimilation sync (external family only)
```

## Build sequence

1. Implement runtime_engine.py and family_selector
2. Implement KEX spatial geometry layer
3. Implement BRAINK execution fabric
4. Implement IL-LLM semantic substrate
5. Implement 0.297 Kuramoto resonance governor
6. Implement DNS mesh topology
7. Implement service orchestration
8. Implement health monitoring daemon
9. Wire all layers together in the bootstrap
10. Test family switching and isolation
11. Benchmark and validate performance
12. Deploy to both internal (codex) and external (production) families

## Success criteria

✓ Runtime engine accepts FAMILY env var and loads correct config  
✓ KEX spatial coordinates resolve correctly  
✓ BRAINK enforces permitted transitions only  
✓ IL-LLM traversals complete without context reconstruction  
✓ 0.297 phase coherence tracked continuously  
✓ Autogenetic forks trigger correctly on health < 0.75  
✓ Fork bombs prevented by phase noise self-kill  
✓ DNS mesh maintains zone state without central master  
✓ Services isolated per family but use shared core  
✓ Health daemon operates with <5% CPU overhead  
✓ Sibling assimilation (internal→external) is atomic and deterministic  
✓ Both families run independently and concurrently  

# Formal Research and Development

This is the filing authority and navigation index for technical research in the current review build. Existing canonical documents retain their locations; the sector registry files them here by reference with SHA-256, topic, document type and primary sector. New connector research and qualification records reside directly in their sector folders. No copy is made the execution authority merely by indexing it.

The four sectors preserve the owner document-seed taxonomy:

| Sector | Direction | Scope |
| --- | --- | --- |
| [SECTOR_FOUNDATIONS](sectors/SECTOR_FOUNDATIONS/README.md) | NORTH +Y | Source authority, contextual truth, governance and admission |
| [SECTOR_MATHEMATICAL_LATTICE](sectors/SECTOR_MATHEMATICAL_LATTICE/README.md) | EAST +X | One-origin, coordinate/vector, arithmetic and frame invariants |
| [SECTOR_SYSTEMS_ARCHITECTURE](sectors/SECTOR_SYSTEMS_ARCHITECTURE/README.md) | SOUTH −Y | Compiler/runtime, VFS, connectors, lifecycle and architecture |
| [SECTOR_EMPIRICAL_BENCHMARKS](sectors/SECTOR_EMPIRICAL_BENCHMARKS/README.md) | WEST −X | Tests, readbacks, performance and impact qualification |

[Machine-readable filing registry](REGISTRY.json) and [complete sector listing](INDEX.md) cover research, engineering plans, analysis, personal Site research, current runtime source and qualification scripts/tests. Uploaded originals remain in private/local custody; public filing uses their already-reviewed hash inventories and attributed notes.

Formal research records must state requirement, source, hypothesis, contract, method, observed results, acceptance criteria, failure scope, limits and next gate. A source assertion, designed mechanism, executed test and production qualification remain distinct evidence classes. Every outward contextual truth retains its origin/jurisdiction/measurement basis; sector classification does not dictate execution order.

Regenerate and validate filing from repository root:

```sh
python3 scripts/research-and-development/index_research.py
```

The registry excludes itself and its generated listing to avoid self-referential hashing. Added files need sector assignment before review delivery. Native Projects or production deployment permissions are not supplied by this index.

[Significant-result research protocol](RESEARCH_PROTOCOL.md) makes deeper testing, theory, critique and topological filing a reusable requirement.

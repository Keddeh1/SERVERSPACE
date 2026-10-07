#!/usr/bin/env python3
"""Append-Only Evidence Ledger: Cryptographic audit trail for state transitions.

Every state mutation is recorded in an immutable, append-only ledger.
An independent verifier can replay this ledger to reconstruct identical state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LedgerEntry:
    """A single immutable ledger entry recording a state transition."""
    entry_id: str
    timestamp: str
    operation: str
    entity_address: str
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    previous_hash: str = "genesis"  # Hash of previous entry for chain integrity

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry for chain validation."""
        payload = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()


class EvidenceLedger:
    """Append-only cryptographic ledger for state transition audit."""

    def __init__(self, ledger_path: Optional[Path] = None):
        self.ledger_path = ledger_path or Path("/tmp/evidence_ledger.jsonl")
        self.entries: List[LedgerEntry] = []
        self.chain_hashes: List[str] = []
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load existing ledger entries from disk if they exist."""
        if self.ledger_path.exists():
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = LedgerEntry(**data)
                        self.entries.append(entry)
                        self.chain_hashes.append(entry.compute_hash())

    def append(self,
               operation: str,
               entity_address: str,
               state_before: Dict[str, Any],
               state_after: Dict[str, Any],
               context: Dict[str, Any] = None) -> LedgerEntry:
        """Append an immutable entry to the ledger.
        
        This entry is immediately persisted to disk and cannot be modified.
        """
        from uuid import uuid4

        entry = LedgerEntry(
            entry_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            entity_address=entity_address,
            state_before=state_before,
            state_after=state_after,
            context=context or {},
            previous_hash=self.chain_hashes[-1] if self.chain_hashes else "genesis",
        )

        # Persist immediately (fail-closed on disk error)
        self._persist_entry(entry)

        # Add to in-memory ledger
        self.entries.append(entry)
        entry_hash = entry.compute_hash()
        self.chain_hashes.append(entry_hash)

        return entry

    def _persist_entry(self, entry: LedgerEntry) -> None:
        """Write entry to disk in append-only JSONL format."""
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")
            f.flush()  # Ensure written to disk

    def verify_chain_integrity(self) -> bool:
        """Verify that all ledger entries form an unbroken cryptographic chain."""
        if not self.entries:
            return True

        computed_hashes = []
        for i, entry in enumerate(self.entries):
            computed = entry.compute_hash()
            if i > 0 and entry.previous_hash != computed_hashes[i - 1]:
                print(f"[Ledger] Chain break detected at entry {i}")
                return False
            computed_hashes.append(computed)

        print(f"[Ledger] Chain integrity verified ({len(self.entries)} entries)")
        return True

    def replay_to_state(self, target_entity: str) -> Dict[str, Any]:
        """Independent replay: reconstruct an entity's state by replaying the ledger.
        
        This proves that state can be rebuilt from evidence logs alone,
        without the original runtime.
        """
        state = {}
        for entry in self.entries:
            if entry.entity_address == target_entity:
                state = entry.state_after
        return state

    def report(self) -> Dict[str, Any]:
        """Generate a structured audit report."""
        return {
            "ledger_path": str(self.ledger_path),
            "total_entries": len(self.entries),
            "chain_integrity_verified": self.verify_chain_integrity(),
            "unique_entities": len(set(e.entity_address for e in self.entries)),
            "operations_recorded": set(e.operation for e in self.entries),
        }


if __name__ == "__main__":
    # Demonstration
    ledger = EvidenceLedger()

    # Record a state mutation
    ledger.append(
        operation="create",
        entity_address="kex::2:1:3",
        state_before={},
        state_after={"data": "example", "status": "active"},
        context={"source": "vfs_resolver"},
    )
    print("[Ledger] Recorded: entity created")

    # Record a state transition
    ledger.append(
        operation="carrier_bind",
        entity_address="kex::2:1:3",
        state_before={"data": "example", "status": "active", "carrier": None},
        state_after={"data": "example", "status": "active", "carrier": "nvme://0x12345"},
        context={"carrier_type": "nvme_local"},
    )
    print("[Ledger] Recorded: carrier binding")

    # Record an unbind (failure scenario)
    ledger.append(
        operation="carrier_unbind",
        entity_address="kex::2:1:3",
        state_before={"data": "example", "status": "active", "carrier": "nvme://0x12345"},
        state_after={"data": "example", "status": "rehydratable", "carrier": None},
        context={"reason": "hardware_failure"},
    )
    print("[Ledger] Recorded: carrier unbind (failure)")

    # Verify integrity
    print("\n[Ledger] Verifying cryptographic chain...")
    ledger.verify_chain_integrity()

    # Independent replay
    reconstructed_state = ledger.replay_to_state("kex::2:1:3")
    print(f"\n[Ledger] Reconstructed state from ledger replay:")
    print(json.dumps(reconstructed_state, indent=2))

    print("\n[Ledger] Audit Report:")
    print(json.dumps(ledger.report(), indent=2))

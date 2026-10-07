#!/usr/bin/env python3
"""Unit tests for Evidence Ledger: append-only audit trail."""

import sys
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from runtime.evidence_ledger import EvidenceLedger


def test_append_and_persistence():
    """Test that entries are persisted to disk immediately."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "test_ledger.jsonl"
        ledger = EvidenceLedger(ledger_path)

        # Append an entry
        ledger.append(
            operation="create",
            entity_address="kex::1:2:3",
            state_before={},
            state_after={"value": 42},
        )

        # Verify it was written to disk
        assert ledger_path.exists()
        with open(ledger_path, "r") as f:
            line = f.readline()
            data = json.loads(line)
            assert data["operation"] == "create"
        print("✓ Persistence: entry immediately written to disk")


def test_chain_integrity():
    """Test cryptographic chain integrity verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "test_ledger.jsonl"
        ledger = EvidenceLedger(ledger_path)

        # Append multiple entries
        for i in range(5):
            ledger.append(
                operation=f"op_{i}",
                entity_address="kex::1:1:1",
                state_before={"step": i},
                state_after={"step": i + 1},
            )

        # Verify chain integrity
        is_valid = ledger.verify_chain_integrity()
        assert is_valid
        print(f"✓ Chain integrity: verified {len(ledger.entries)} entries in unbroken chain")


def test_independent_replay():
    """Test that state can be replayed from ledger independently."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "test_ledger.jsonl"
        ledger = EvidenceLedger(ledger_path)

        # Record a sequence of mutations
        ledger.append(
            operation="create",
            entity_address="kex::2:3:4",
            state_before={},
            state_after={"status": "active", "value": 100},
        )
        ledger.append(
            operation="update",
            entity_address="kex::2:3:4",
            state_before={"status": "active", "value": 100},
            state_after={"status": "active", "value": 200},
        )
        ledger.append(
            operation="update",
            entity_address="kex::2:3:4",
            state_before={"status": "active", "value": 200},
            state_after={"status": "completed", "value": 200},
        )

        # Create a new ledger instance (simulating independent verifier)
        ledger2 = EvidenceLedger(ledger_path)

        # Replay the entity's state
        final_state = ledger2.replay_to_state("kex::2:3:4")
        assert final_state["status"] == "completed"
        assert final_state["value"] == 200
        print("✓ Independent replay: state fully reconstructed from ledger alone")


if __name__ == "__main__":
    test_append_and_persistence()
    test_chain_integrity()
    test_independent_replay()
    print("\n✓✓✓ All evidence ledger tests passed")

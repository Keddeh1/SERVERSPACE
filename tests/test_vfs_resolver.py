#!/usr/bin/env python3
"""Unit tests for VFS Resolver: logical-to-physical address mapping."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from runtime.vfs_resolver import (
    LogicalAddress,
    PhysicalCarrier,
    PhysicalCarrierType,
    LogicalState,
    VFSResolver,
)


def test_injective_addressing():
    """Test that 1-origin addressing guarantees collision-free allocation."""
    vfs = VFSResolver()
    addresses = set()

    # Allocate all 729 positions in [1,9]³
    for plane in range(1, 10):
        for line in range(1, 10):
            for column in range(1, 10):
                addr = vfs.allocate_address(plane, line, column)
                addresses.add(addr.addr_str)

    # Verify all are unique
    assert len(addresses) == 729, f"Expected 729 unique addresses, got {len(addresses)}"
    print("✓ Injective addressing: 729/729 unique addresses allocated")


def test_carrier_binding_and_unbinding():
    """Test logical-to-physical carrier binding and unbinding."""
    vfs = VFSResolver()
    addr = vfs.allocate_address(2, 1, 3)
    obj = vfs.create_object(addr, {"data": "test"})

    # Initially no carrier
    assert vfs.resolve(addr) is None
    assert obj.state == LogicalState.PRESENT

    # Bind to RAM carrier
    ram_carrier = PhysicalCarrier(
        carrier_type=PhysicalCarrierType.MEMORY_HEAP,
        location="0x7f0000",
        size_bytes=1024,
    )
    vfs.bind_carrier(addr, ram_carrier)
    assert vfs.resolve(addr) == ram_carrier
    assert obj.state == LogicalState.PRESENT
    print("✓ Carrier binding: logical address bound to RAM carrier")

    # Simulate failure: unbind
    vfs.unbind_carrier(addr)
    assert vfs.resolve(addr) is None
    assert obj.state == LogicalState.REHYDRATABLE
    print("✓ Carrier unbinding: logical identity persists, state = REHYDRATABLE")

    # Rebind to NVMe carrier
    nvme_carrier = PhysicalCarrier(
        carrier_type=PhysicalCarrierType.NVME_LOCAL,
        location="/dev/nvme0:sector=0x12345",
        size_bytes=1024,
    )
    vfs.bind_carrier(addr, nvme_carrier)
    assert vfs.resolve(addr) == nvme_carrier
    assert obj.state == LogicalState.PRESENT
    print("✓ Rehydration: logical identity re-bound to NVMe carrier")


def test_evidence_log_preservation():
    """Test that evidence logs are preserved across carrier transitions."""
    vfs = VFSResolver()
    addr = vfs.allocate_address(1, 2, 3)
    obj = vfs.create_object(addr, {"value": 42})

    # Bind, unbind, rebind
    carrier1 = PhysicalCarrier(PhysicalCarrierType.MEMORY_HEAP, "0x1000")
    vfs.bind_carrier(addr, carrier1)
    vfs.unbind_carrier(addr)
    carrier2 = PhysicalCarrier(PhysicalCarrierType.NVME_LOCAL, "/dev/nvme0")
    vfs.bind_carrier(addr, carrier2)

    # Evidence log should have 4 entries: creation, bind, unbind, rebind
    assert len(obj.evidence_log) == 4
    assert obj.evidence_log[0]["transition"] == "creation"
    assert obj.evidence_log[1]["transition"] == "carrier_bind"
    assert obj.evidence_log[2]["transition"] == "carrier_unbind"
    assert obj.evidence_log[3]["transition"] == "carrier_bind"
    print(f"✓ Evidence preservation: {len(obj.evidence_log)} transitions logged and intact")


if __name__ == "__main__":
    test_injective_addressing()
    test_carrier_binding_and_unbinding()
    test_evidence_log_preservation()
    print("\n✓✓✓ All VFS resolver tests passed")

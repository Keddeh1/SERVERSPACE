#!/usr/bin/env python3
"""Unit tests for Relational Scheduler: non-blocking task coordination."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from runtime.relational_scheduler import (
    RelationalScheduler,
    EdgeType,
    TaskState,
)


def test_basic_task_creation():
    """Test basic node creation."""
    scheduler = RelationalScheduler()
    task_a = scheduler.create_node("task_a", {"work": "data_process"})
    assert task_a.state == TaskState.READY
    assert "task_a" in scheduler.nodes
    print("✓ Node creation: task created in READY state")


def test_dependency_blocking():
    """Test that nodes are trapped in WAITING when dependencies exist."""
    scheduler = RelationalScheduler()
    scheduler.create_node("task_a")
    scheduler.create_node("task_b")

    # task_b waits for task_a
    scheduler.add_edge("task_b", "task_a", EdgeType.WAITS_FOR)

    # Try to run task_b (should trap into WAITING)
    success = scheduler.advance_node("task_b", TaskState.RUNNING)
    assert not success
    assert scheduler.nodes["task_b"].state == TaskState.WAITING
    print("✓ Dependency blocking: task_b trapped in WAITING due to dependency on task_a")


def test_unblocking_chain():
    """Test unblocking a chain of dependent tasks."""
    scheduler = RelationalScheduler()
    scheduler.create_node("task_a")
    scheduler.create_node("task_b")
    scheduler.create_node("task_c")

    # task_b waits for task_a; task_c waits for task_b
    scheduler.add_edge("task_b", "task_a", EdgeType.WAITS_FOR)
    scheduler.add_edge("task_c", "task_b", EdgeType.WAITS_FOR)

    # Try to advance tasks (all should trap into WAITING)
    scheduler.advance_node("task_b", TaskState.RUNNING)  # blocked by task_a
    scheduler.advance_node("task_c", TaskState.RUNNING)  # blocked by task_b
    assert scheduler.nodes["task_b"].state == TaskState.WAITING
    assert scheduler.nodes["task_c"].state == TaskState.WAITING
    print("✓ Dependency chain: task_b and task_c both trapped in WAITING")

    # Complete task_a
    scheduler.advance_node("task_a", TaskState.RUNNING)
    scheduler.advance_node("task_a", TaskState.COMPLETED)
    unblocked = scheduler.unblock_nodes("task_a")
    assert "task_b" in unblocked
    print(f"✓ Unblocking: task_a completion unblocked {unblocked}")

    # Now task_b should be able to run
    success = scheduler.advance_node("task_b", TaskState.RUNNING)
    assert success
    assert scheduler.nodes["task_b"].state == TaskState.RUNNING
    print("✓ Continuation: task_b now running (no longer blocked)")


def test_independent_task_progress():
    """Test that independent tasks progress without head-of-line blocking."""
    scheduler = RelationalScheduler()
    # Create 3 independent tasks
    for i in range(1, 4):
        scheduler.create_node(f"task_{i}")

    # All should be READY (no dependencies)
    ready = scheduler.ready_nodes()
    assert len(ready) == 3
    print(f"✓ Independent progress: {len(ready)} independent tasks are READY")

    # All should be able to advance
    for node_id in ready:
        success = scheduler.advance_node(node_id, TaskState.RUNNING)
        assert success
    print("✓ No blocking: all independent tasks advanced to RUNNING without stalling")


if __name__ == "__main__":
    test_basic_task_creation()
    test_dependency_blocking()
    test_unblocking_chain()
    test_independent_task_progress()
    print("\n✓✓✓ All relational scheduler tests passed")

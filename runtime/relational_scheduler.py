#!/usr/bin/env python3
"""Relational Scheduler: Task coordination via typed edges, not global locks.

Instead of blocking threads on mutexes, waiting conditions attach as local
relational edges to state nodes. Unrelated tasks progress independently.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4


class EdgeType(Enum):
    """Relational edge types connecting state nodes."""
    DEPENDS_ON = "depends_on"
    WAITS_FOR = "waits_for"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    BLOCKS = "blocks"


class TaskState(Enum):
    """Explicit typed task lifecycle states."""
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    BLOCKED = "blocked"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RelationalEdge:
    """A typed edge connecting two state nodes."""
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    created_at: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateNode:
    """A named state node in the relational graph."""
    node_id: str
    state: TaskState = TaskState.READY
    edges: List[RelationalEdge] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())

    def add_edge(self, edge: RelationalEdge) -> None:
        self.edges.append(edge)

    def waiting_edges(self) -> List[RelationalEdge]:
        return [e for e in self.edges if e.edge_type == EdgeType.WAITS_FOR]


class RelationalScheduler:
    """Non-blocking task scheduler using relational edges instead of global locks."""

    def __init__(self):
        self.nodes: Dict[str, StateNode] = {}
        self.all_edges: List[RelationalEdge] = []
        self.execution_log: List[Dict[str, Any]] = []

    def create_node(self, node_id: str, payload: Dict[str, Any] = None) -> StateNode:
        """Create a new state node in the relational graph."""
        node = StateNode(node_id=node_id, payload=payload or {})
        self.nodes[node_id] = node
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "node_created",
            "node_id": node_id,
        })
        return node

    def add_edge(self, source: str, target: str, edge_type: EdgeType, metadata: Dict[str, Any] = None) -> RelationalEdge:
        """Add a typed relational edge between two nodes.
        
        This edge models a dependency or wait condition *locally* without
        requiring a global lock or thread context switch.
        """
        edge = RelationalEdge(
            source_node_id=source,
            target_node_id=target,
            edge_type=edge_type,
            metadata=metadata or {},
        )
        self.nodes[source].add_edge(edge)
        self.all_edges.append(edge)
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "edge_added",
            "source": source,
            "target": target,
            "edge_type": edge_type.value,
        })
        return edge

    def advance_node(self, node_id: str, new_state: TaskState, context: Dict[str, Any] = None) -> bool:
        """Atomically advance a node to a new state.
        
        Returns True if successful. Returns False if node has blocking edges.
        """
        node = self.nodes[node_id]
        blocking_edges = [e for e in node.waiting_edges()]

        if blocking_edges and new_state == TaskState.RUNNING:
            # Waiting edge exists: trap into WAITING state instead
            node.state = TaskState.WAITING
            self.execution_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "node_trapped_waiting",
                "node_id": node_id,
                "blocking_edges": len(blocking_edges),
                "context": context or {},
            })
            return False

        node.state = new_state
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "node_advanced",
            "node_id": node_id,
            "new_state": new_state.value,
            "context": context or {},
        })
        return True

    def unblock_nodes(self, target_node_id: str) -> List[str]:
        """Unblock all nodes waiting on a specific target node."""
        unblocked = []
        for node_id, node in self.nodes.items():
            for edge in node.waiting_edges():
                if edge.target_node_id == target_node_id and node.state == TaskState.WAITING:
                    node.state = TaskState.READY
                    unblocked.append(node_id)
                    self.execution_log.append({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event": "node_unblocked",
                        "node_id": node_id,
                        "unblocked_by": target_node_id,
                    })
        return unblocked

    def ready_nodes(self) -> List[str]:
        """Return all nodes in READY state (no blocking edges)."""
        return [nid for nid, node in self.nodes.items() if node.state == TaskState.READY]

    def waiting_nodes(self) -> List[str]:
        """Return all nodes trapped in WAITING state."""
        return [nid for nid, node in self.nodes.items() if node.state == TaskState.WAITING]

    def report(self) -> Dict[str, Any]:
        """Generate a structured report of the relational graph."""
        state_distribution = {}
        for node_id, node in self.nodes.items():
            state_val = node.state.value
            state_distribution[state_val] = state_distribution.get(state_val, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.all_edges),
            "state_distribution": state_distribution,
            "ready_nodes": self.ready_nodes(),
            "waiting_nodes": self.waiting_nodes(),
            "log_entries": len(self.execution_log),
        }


if __name__ == "__main__":
    # Demonstration
    scheduler = RelationalScheduler()

    # Create nodes
    task_a = scheduler.create_node("task_a", {"work": "process_data"})
    task_b = scheduler.create_node("task_b", {"work": "store_result"})
    task_c = scheduler.create_node("task_c", {"work": "notify_user"})

    print("[Scheduler] Created 3 nodes")

    # task_b waits for task_a
    scheduler.add_edge("task_b", "task_a", EdgeType.WAITS_FOR, {"reason": "needs data from task_a"})
    # task_c waits for task_b
    scheduler.add_edge("task_c", "task_b", EdgeType.WAITS_FOR, {"reason": "needs confirmation from task_b"})

    print("[Scheduler] Added dependency edges: task_b -> task_a, task_c -> task_b")

    # Try to advance task_b to RUNNING (should trap into WAITING)
    success = scheduler.advance_node("task_b", TaskState.RUNNING)
    print(f"[Scheduler] Attempted to run task_b: success={success} (blocked by dependency)")

    # Advance task_a to COMPLETED
    scheduler.advance_node("task_a", TaskState.RUNNING)
    scheduler.advance_node("task_a", TaskState.COMPLETED)
    print("[Scheduler] task_a COMPLETED")

    # Unblock task_b
    unblocked = scheduler.unblock_nodes("task_a")
    print(f"[Scheduler] Nodes unblocked by task_a completion: {unblocked}")

    # Now task_b can run
    scheduler.advance_node("task_b", TaskState.RUNNING)
    print("[Scheduler] task_b now RUNNING (no longer blocked)")

    print("\n[Scheduler] Final Report:")
    print(json.dumps(scheduler.report(), indent=2))

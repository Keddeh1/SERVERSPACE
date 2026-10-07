#!/usr/bin/env python3
"""SERVERSPACE build and packaging tooling.

Validates the runtime structure, creates a runtime manifest, and exposes a
formal project metadata surface for local execution and packaging.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent

PACKAGE_INFO = {
    "name": "serverspace",
    "version": "1.0.0-alpha.1",
    "description": "Sovereign runtime architecture for local-first execution services",
    "runtime_model": "custom_local",
    "github_dependencies": False,
    "architecture": ["KEX", "BRAINK", "IL-LLM", "FROST", "Mesh"],
}

RUNTIME_COMPONENTS = {
    "kex": {
        "module": "runtime.engine.KEXRuntime",
        "purpose": "state geometry and runtime identity",
    },
    "braink": {
        "module": "runtime.engine.BRAINKRuntime",
        "purpose": "execution governance and evidence logs",
    },
    "mesh": {
        "module": "runtime.engine.MeshRuntime",
        "purpose": "phase-lock topology and flywheel recovery",
    },
    "services": {
        "module": "runtime.services.unified_runtime.UnifiedRuntimeService",
        "purpose": "service orchestration layer for HTTPS/TCP/UDP runtime surfaces",
    },
}


class RuntimeBuilder:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.manifest_path = root / "runtime" / "manifest.json"

    def validate(self) -> bool:
        required = [
            self.root / "runtime" / "__init__.py",
            self.root / "runtime" / "engine.py",
            self.root / "runtime" / "services" / "__init__.py",
            self.root / "runtime" / "services" / "unified_runtime.py",
            self.root / "README.md",
            self.root / "pyproject.toml",
            self.root / "Makefile",
        ]
        missing = [str(p.relative_to(self.root)) for p in required if not p.exists()]
        if missing:
            print("[SERVERSPACE] validation failed")
            for item in missing:
                print(f"  - {item}")
            return False
        print("[SERVERSPACE] validation passed")
        return True

    def manifest(self) -> Dict[str, Any]:
        payload = {
            "package": PACKAGE_INFO,
            "components": RUNTIME_COMPONENTS,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policy": {
                "custom_runtime_only": True,
                "github_dependency_policy": "disabled",
                "stdlib_only": True,
            },
        }
        self.manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


def main() -> None:
    builder = RuntimeBuilder()
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "validate":
            raise SystemExit(0 if builder.validate() else 1)
        if command == "manifest":
            print(json.dumps(builder.manifest(), indent=2))
            raise SystemExit(0)
        if command == "info":
            print(json.dumps(PACKAGE_INFO, indent=2))
            raise SystemExit(0)
        print(f"Unknown command: {command}")
        raise SystemExit(1)

    builder.validate()
    print(json.dumps(builder.manifest(), indent=2))


if __name__ == "__main__":
    main()

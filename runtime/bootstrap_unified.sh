#!/usr/bin/env bash
set -eu

# Enhanced KEDDEH Bootstrap
# Calls the unified runtime engine to initialize all layers

FAMILY="${FAMILY:-internal}"
RUNTIME_ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$RUNTIME_ROOT/.." && pwd)"

echo "[BOOTSTRAP] Starting KEDDEH unified runtime initialization..."
echo "[FAMILY] Active family: $FAMILY"
echo ""

# Verify Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is required"
    exit 1
fi

# Run the unified runtime engine
export FAMILY="$FAMILY"
cd "$REPO_ROOT"
python3 runtime/core/runtime_engine.py

echo ""
echo "[BOOTSTRAP] Initialization complete"

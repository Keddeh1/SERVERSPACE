.PHONY: validate manifest run test clean

PYTHON ?= python3
ROOT := $(CURDIR)

validate:
	$(PYTHON) build.py validate

manifest:
	$(PYTHON) build.py manifest

test:
	$(PYTHON) -m pytest tests/ -v 2>/dev/null || {\
		echo "[TEST] Running manual test suite..."; \
		$(PYTHON) tests/test_vfs_resolver.py && \
		$(PYTHON) tests/test_relational_scheduler.py && \
		$(PYTHON) tests/test_evidence_ledger.py; \
	}

run:
	$(PYTHON) runtime/engine.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "[SERVERSPACE] artifacts cleaned"

.PHONY: validate manifest run clean

PYTHON ?= python3
ROOT := $(CURDIR)

validate:
	$(PYTHON) build.py validate

manifest:
	$(PYTHON) build.py manifest

run:
	$(PYTHON) runtime/engine.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "[SERVERSPACE] local artifacts cleaned"

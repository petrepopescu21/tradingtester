.PHONY: setup install dev clean test help venv check-python env demo validate

PYTHON := python3
VENV := venv
BIN := $(VENV)/bin

help:
	@echo "Trading Tester - Available targets:"
	@echo ""
	@echo "  make setup      - Full setup (venv + install + env)"
	@echo "  make install    - Install dependencies in existing venv"
	@echo "  make dev        - Install with dev dependencies"
	@echo "  make env        - Create .env from template"
	@echo "  make validate   - Validate installation"
	@echo "  make test       - Run tests"
	@echo "  make demo       - Run demo (demo 1)"
	@echo "  make clean      - Remove venv and caches"
	@echo "  make help       - Show this help"
	@echo ""
	@echo "After setup, activate venv with: source venv/bin/activate"

check-python:
	@$(PYTHON) -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || \
		(echo "ERROR: Python 3.10+ required" && exit 1)

venv: check-python
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(BIN)/pip install --upgrade pip -q

install: venv
	@echo "Installing dependencies..."
	@$(BIN)/pip install -e .

dev: venv
	@echo "Installing with dev dependencies..."
	@$(BIN)/pip install -e ".[dev]"

env:
	@test -f .env || (cp .env.example .env && echo "Created .env - add your ANTHROPIC_API_KEY")
	@test -f .env && echo ".env exists"

setup: install env
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "  1. source venv/bin/activate"
	@echo "  2. Edit .env and add your ANTHROPIC_API_KEY"
	@echo "  3. tradingtester --help"

validate:
	@bash hack/make/validate.sh

test:
	@$(BIN)/python -m pytest tests/ -v

demo:
	@$(BIN)/python demo.py 1

clean:
	rm -rf $(VENV)
	rm -rf __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

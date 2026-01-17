#!/bin/bash
# Validates the installation and runs basic checks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV="$PROJECT_ROOT/venv"

echo "Validating Trading Tester installation..."
echo ""

# Check venv exists
if [ ! -d "$VENV" ]; then
    echo "FAIL: Virtual environment not found. Run: make setup"
    exit 1
fi
echo "OK: Virtual environment exists"

# Check CLI is installed
if ! "$VENV/bin/tradingtester" --help &> /dev/null; then
    echo "FAIL: CLI not installed properly"
    exit 1
fi
echo "OK: CLI installed"

# Check .env exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "WARN: .env file missing. Run: make env"
fi

# Check API key is set
if [ -f "$PROJECT_ROOT/.env" ]; then
    if grep -q "^ANTHROPIC_API_KEY=sk-" "$PROJECT_ROOT/.env"; then
        echo "OK: API key configured"
    else
        echo "WARN: ANTHROPIC_API_KEY not set in .env"
    fi
fi

# Check example strategies exist
if [ -f "$PROJECT_ROOT/strategies/rsi_mean_reversion.md" ]; then
    echo "OK: Example strategies present"
else
    echo "WARN: Example strategies missing"
fi

echo ""
echo "Validation complete!"

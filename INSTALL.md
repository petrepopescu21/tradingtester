# Installation Guide

## Prerequisites

- Python 3.10 or higher
- Anthropic API key (get from https://console.anthropic.com/)

## Quick Start

### 1. Set up virtual environment

**Windows:**
```bash
# Create virtual environment
python3.14.exe -m venv venv

# Activate
venv\Scripts\activate
```

**Unix/Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Configure environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

On Windows:
```bash
copy .env.example .env
notepad .env
```

### 4. Test installation

```bash
tradingtester --help
```

You should see the CLI help message.

## Usage Examples

### Test a single strategy

```bash
tradingtester test strategies/rsi_mean_reversion.md --symbol AAPL --start 2020-01-01 --end 2023-12-31
```

### Generate strategy variations

```bash
tradingtester generate strategies/rsi_mean_reversion.md --variations 5 --output-dir generated
```

### Batch test multiple strategies

```bash
tradingtester batch strategies/ --symbols AAPL,MSFT,GOOGL --start 2020-01-01 --end 2023-12-31
```

## Troubleshooting

### ModuleNotFoundError

Make sure you installed with `-e .` flag:
```bash
pip install -e .
```

### API Key Error

Make sure your `.env` file has:
```
ANTHROPIC_API_KEY=sk-ant-...your-actual-key...
```

### No data fetched

Check your internet connection and ensure the symbol and date range are valid.

## Development

### Install dev dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Format code

```bash
black backend/
ruff check backend/
```

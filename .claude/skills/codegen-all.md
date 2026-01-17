# /codegen-all - Generate All Strategy Code

Generate Python code for all strategy markdown files in parallel.

## Usage

```
/codegen-all
```

## Instructions

When this skill is invoked:

1. Find all `.md` files in `strategies/` directory
2. For each strategy file, launch a **parallel Task agent** that runs `/codegen`
3. Each agent generates code to `generated/<strategy_name>.py`

## Implementation

Use multiple Task tool calls in a single message to run in parallel:

```
Task 1: /codegen strategies/rsi_mean_reversion.md generated/rsi_mean_reversion.py
Task 2: /codegen strategies/momentum_breakout.md generated/momentum_breakout.py
Task 3: /codegen strategies/other_strategy.md generated/other_strategy.py
```

All tasks run simultaneously. Report results when all complete.

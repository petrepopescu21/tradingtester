# Trading Tester

LLM-powered trading strategy testing framework.

## Workflow

1. Write strategy in `strategies/*.md`
2. Generate code: `/codegen strategies/<name>.md`
3. Test: `tradingtester test generated/<name>.py --symbol AAPL`

## Key Commands

- `/codegen <file.md>` - Generate Python from strategy markdown
- "generate all strategies" - Runs /codegen in parallel for all strategies

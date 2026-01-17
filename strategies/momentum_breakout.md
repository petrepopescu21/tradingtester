# Momentum Breakout Strategy

A trend-following strategy that captures strong momentum moves when price breaks out of consolidation patterns with increasing volume.

## Entry Rules

Enter a LONG position when:
- Price breaks above the 20-day high (resistance breakout)
- Current price is at least 2% above the 20-day high
- Volume on breakout day is at least 2x the 50-day average volume
- ADX(14) is above 25, indicating strong trend
- Price is trading above both 50-day and 200-day moving averages

Do not enter if:
- Price has already moved more than 10% in the last 5 days (avoid chasing)
- Market is in a known earnings announcement period (avoid event risk)

## Exit Rules

Exit LONG positions when:
- Price closes below the 10-day exponential moving average (trend reversal)
- OR trailing stop loss is hit: 2× ATR(14) below the highest price since entry
- OR profit target is reached: 15% gain from entry price
- OR position held for more than 30 trading days without hitting profit target

Use a trailing stop that tightens as the trade becomes profitable:
- Initial stop: 5% below entry
- After 5% profit: Move stop to breakeven
- After 10% profit: Trail 2× ATR below highest price

## Position Sizing

Use volatility-adjusted position sizing based on ATR:
- Base risk per trade: $1,000 (1% of $100,000 portfolio)
- Position size = Risk Amount / (2 × ATR)
- This ensures consistent risk regardless of stock volatility

Constraints:
- Minimum position value: $2,000
- Maximum position value: $15,000
- If calculated position size exceeds maximum, reduce to maximum and accept lower risk

## Risk Management

Risk per trade: 1% of portfolio value (using ATR-based stops)

Maximum number of concurrent positions: 8

Diversification rules:
- Maximum 3 positions in the same sector
- Maximum 40% of portfolio in any single sector
- Minimum 3 different sectors represented in portfolio

Correlation management:
- Avoid entering positions that are highly correlated (>0.7) with existing positions
- Use 60-day rolling correlation to measure

Stop trading rules:
- If 3 consecutive losing trades occur, reduce position sizes by 50% for next 5 trades
- If monthly drawdown exceeds 8%, stop taking new positions until recovery above 5% drawdown
- Maximum daily trades: 3 new positions per day to avoid overtrading

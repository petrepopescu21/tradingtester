# RSI Mean Reversion Strategy

A classic mean reversion strategy based on the Relative Strength Index (RSI) indicator. This strategy identifies oversold and overbought conditions to capture short-term price reversals.

## Entry Rules

Enter a LONG position when:
- RSI(14) drops below 30, indicating oversold conditions
- Price is above the 200-day simple moving average (long-term uptrend confirmation)
- Volume is at least 1.2x the 20-day average volume

Enter a SHORT position when:
- RSI(14) rises above 70, indicating overbought conditions
- Price is below the 200-day simple moving average (long-term downtrend confirmation)
- Volume is at least 1.2x the 20-day average volume

## Exit Rules

Exit LONG positions when:
- RSI(14) rises above 60 (profit target)
- OR RSI(14) drops below 20 (deeper oversold - cut loss)
- OR price falls 3% below entry price (stop loss)
- OR position held for more than 10 trading days (time-based exit)

Exit SHORT positions when:
- RSI(14) drops below 40 (profit target)
- OR RSI(14) rises above 80 (deeper overbought - cut loss)
- OR price rises 3% above entry price (stop loss)
- OR position held for more than 10 trading days (time-based exit)

## Position Sizing

Allocate 10% of total portfolio value per trade.

Use fixed fractional position sizing:
- Calculate position size = (Portfolio Value × 0.10) / Entry Price
- Round down to the nearest whole number of shares
- Minimum position size: $1,000
- Maximum position size: $10,000 per single trade

## Risk Management

Maximum risk per trade: 3% of portfolio value

Stop loss: 3% below entry for LONG, 3% above entry for SHORT

Maximum number of concurrent positions: 5

Maximum allocation to correlated assets: No more than 2 positions in the same sector

Daily loss limit: If portfolio loses 2% in a single day, close all positions and stop trading for the day

Portfolio heat: Total risk across all open positions should not exceed 10% of portfolio value

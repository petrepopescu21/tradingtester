# STRATEGY PROFILE: The Banker Ratchet [Institutional Grade]

## 1. OBJECTIVE
To identify and execute high-probability "Liquidity Grabs" at institutional volume levels, capitalizing on the trap set by market makers against retail traders. The strategy uses a "Mean Reversion within Trend" logic.

## 2. CONFIGURATION
* *Asset Class:* Crypto Derivatives (Perpetual Futures).
* *Primary Assets:* BTC/USDT, SOL/USDT, ETH/USDT.
* *Execution Timeframe:* 15 Minutes (15m).
* *Context Timeframe:* 1 Hour (1H).
* *Leverage:* 3x - 5x (Dynamic based on Volatility).
* *Trading Session:* London (07:00 UTC) & New York (13:00 UTC).

## 3. THE TOOLKIT (Indicators)
The strategy relies on the confluence of *Trend, **Value, **Structure, and **Momentum*.

| Indicator | Setting | Function |
| :--- | :--- | :--- |
| *EMA* | 200 Length | *The Traffic Light:* Determines the macro direction. |
| *VWAP* | Session/Daily | *The Value:* Determines if price is "Cheap" or "Expensive." |
| *Volume Profile* | Visible Range | *The Truth:* Identifies the Point of Control (POC) and Volume Shelves. |
| *Bollinger Bands* | Length 20, StdDev 2 | *The Energy:* Measures volatility (Band Width) and mean reversion targets. |
| *RSI* | Length 14 | *The Trigger:* Momentum oscillator (Oversold < 45, Overbought > 55). |
| *MACD* | 12, 26, 9 | *The Confirmation:* Histogram ticks indicating momentum shifts. |

---

## 4. TRADING LOGIC

### LONG SETUP (Bullish Liquidity Grab)
*Prerequisite:* Price must be *ABOVE* the 200 EMA (Bull Market).

1.  *The Trap:* Price wick-dips BELOW a recent Swing Low (Liquidity Support).
2.  *The Truth:* The Swing Low coincides with a *Volume Shelf* or *POC*.
3.  *The Value:* Price is currently *BELOW* the VWAP.
4.  *The Trigger:*
    * RSI is *< 45* (Oversold).
    * MACD Histogram is ticking *UP* (Green/Light Red).
    * Bollinger Bands are wide (High Energy).

### SHORT SETUP (Bearish Liquidity Grab)
*Prerequisite:* Price must be *BELOW* the 200 EMA (Bear Market).

1.  *The Trap:* Price wick-pokes ABOVE a recent Swing High (Liquidity Resistance).
2.  *The Truth:* The Swing High rejects off a *Volume Shelf* or *POC*.
3.  *The Value:* Price is currently *ABOVE* the VWAP.
4.  *The Trigger:*
    * RSI is *> 55* (Overbought).
    * MACD Histogram is ticking *DOWN* (Red/Light Green).
    * Bollinger Bands are wide (High Energy).

---

## 5. RISK MANAGEMENT (The Ratchet)

* *Initial Stop Loss:* Hard Stop at *2.0%* from Entry Price.
* *Take Profit:* Open-ended (Ride the trend).
* *The Ratchet Logic:*
    1.  *Activation:* Once Floating Profit >= *+2.0%*.
    2.  *Action:* Move Stop Loss to *Break Even*.
    3.  *Trailing:* Trail the Stop Loss at a distance of *1.0%* behind the highest price reached (Peak).

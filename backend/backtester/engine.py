"""Backtesting engine for testing trading strategies."""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from backend.code_generator.base_strategy import Strategy


@dataclass
class BacktestResult:
    """Results from a backtest run."""

    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    num_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    trades: list[dict] = field(default_factory=list)
    equity_curve: Optional[pd.Series] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "strategy_name": self.strategy_name,
            "symbol": self.symbol,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": self.total_return,
            "total_return_pct": self.total_return_pct,
            "num_trades": self.num_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_pct": self.max_drawdown_pct,
            "sharpe_ratio": self.sharpe_ratio,
            "trades": self.trades,
            "metadata": self.metadata
        }

        if self.equity_curve is not None:
            result["equity_curve"] = self.equity_curve.to_dict()

        return result


class BacktestEngine:
    """Engine for backtesting trading strategies."""

    def __init__(
        self,
        initial_capital: Optional[float] = None,
        commission: Optional[float] = None
    ):
        """
        Initialize backtest engine.

        Args:
            initial_capital: Starting capital (default from env or 100000)
            commission: Commission per trade as decimal (default from env or 0.001)
        """
        load_dotenv()

        self.initial_capital = initial_capital or float(
            os.getenv("DEFAULT_INITIAL_CAPITAL", "100000")
        )
        self.commission = commission or float(
            os.getenv("DEFAULT_COMMISSION", "0.001")
        )

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        symbol: str
    ) -> BacktestResult:
        """
        Run backtest on a strategy.

        Args:
            strategy: Strategy instance
            data: Historical price data
            symbol: Trading symbol

        Returns:
            BacktestResult with performance metrics
        """
        if data.empty:
            raise ValueError("Cannot backtest with empty data")

        # Initialize tracking variables
        cash = self.initial_capital
        position_size = 0
        position_entry_price = 0.0
        position_entry_date = None
        position_type = None
        position_leverage = 1.0

        trades = []
        equity_curve = []

        # Calculate indicators
        data = strategy.calculate_indicators(data.copy())

        # Generate signals
        data = strategy.generate_signals(data)

        # Iterate through data
        for i, (date, row) in enumerate(data.iterrows()):
            current_price = row['close']
            portfolio_value = cash + (position_size * current_price if position_size != 0 else 0)

            # Check if we need to exit existing position
            if position_size != 0 and position_entry_date:
                days_held = (date - position_entry_date).days

                should_exit = strategy.check_exit_conditions(
                    symbol=symbol,
                    current_price=current_price,
                    entry_price=position_entry_price,
                    days_held=days_held,
                    data=data.iloc[:i+1],
                    position_type=position_type or "LONG"
                )

                if should_exit:
                    # Exit position
                    trade_value = position_size * current_price
                    commission_cost = trade_value * self.commission

                    if position_type == "LONG":
                        # P&L with leverage: (exit - entry) * size * leverage
                        raw_pnl = (current_price - position_entry_price) * position_size
                        leveraged_pnl = raw_pnl * position_leverage
                        # For leveraged positions, we only used margin (trade_value / leverage)
                        margin_used = (position_size * position_entry_price) / position_leverage
                        cash += margin_used + leveraged_pnl - commission_cost
                        pnl = leveraged_pnl
                    else:  # SHORT
                        raw_pnl = (position_entry_price - current_price) * position_size
                        leveraged_pnl = raw_pnl * position_leverage
                        margin_used = (position_size * position_entry_price) / position_leverage
                        cash += margin_used + leveraged_pnl - commission_cost
                        pnl = leveraged_pnl

                    pnl -= commission_cost  # Account for entry commission too

                    trades.append({
                        "entry_date": str(position_entry_date),
                        "exit_date": str(date),
                        "type": position_type,
                        "entry_price": position_entry_price,
                        "exit_price": current_price,
                        "size": position_size,
                        "leverage": position_leverage,
                        "pnl": pnl,
                        "pnl_pct": (pnl / margin_used) * 100 if margin_used > 0 else 0,
                        "days_held": days_held
                    })

                    # Close position
                    strategy.close_position(symbol)
                    position_size = 0
                    position_entry_price = 0.0
                    position_entry_date = None
                    position_type = None
                    position_leverage = 1.0

            # Check for new entry signal
            if position_size == 0 and 'signal' in row and row['signal'] != 0:
                signal = row['signal']

                # Get leverage from strategy
                leverage = strategy.get_leverage(data.iloc[:i+1])

                # Calculate position size
                size = strategy.calculate_position_size(
                    symbol=symbol,
                    price=current_price,
                    portfolio_value=portfolio_value,
                    data=data.iloc[:i+1]
                )

                if size > 0:
                    trade_value = size * current_price
                    # With leverage, we only need margin = trade_value / leverage
                    margin_required = trade_value / leverage
                    commission_cost = trade_value * self.commission

                    # Check if we have enough cash for margin
                    if cash >= margin_required + commission_cost:
                        # Enter position (only deduct margin, not full trade value)
                        cash -= margin_required + commission_cost
                        position_size = size
                        position_entry_price = current_price
                        position_entry_date = date
                        position_type = "LONG" if signal > 0 else "SHORT"
                        position_leverage = leverage

                        strategy.open_position(
                            symbol=symbol,
                            entry_price=current_price,
                            size=size,
                            entry_date=date,
                            position_type=position_type
                        )

            # Record equity (account for leveraged position value)
            if position_size != 0:
                margin_in_position = (position_size * position_entry_price) / position_leverage
                if position_type == "LONG":
                    unrealized_pnl = (current_price - position_entry_price) * position_size * position_leverage
                else:
                    unrealized_pnl = (position_entry_price - current_price) * position_size * position_leverage
                portfolio_value = cash + margin_in_position + unrealized_pnl
            else:
                portfolio_value = cash
            equity_curve.append(portfolio_value)

        # Close any remaining position
        if position_size != 0:
            final_price = data.iloc[-1]['close']
            final_date = data.index[-1]

            if position_type == "LONG":
                raw_pnl = (final_price - position_entry_price) * position_size
                leveraged_pnl = raw_pnl * position_leverage
            else:
                raw_pnl = (position_entry_price - final_price) * position_size
                leveraged_pnl = raw_pnl * position_leverage

            margin_used = (position_size * position_entry_price) / position_leverage
            cash += margin_used + leveraged_pnl
            pnl = leveraged_pnl

            days_held = (final_date - position_entry_date).days if position_entry_date else 0

            trades.append({
                "entry_date": str(position_entry_date),
                "exit_date": str(final_date),
                "type": position_type,
                "entry_price": position_entry_price,
                "exit_price": final_price,
                "size": position_size,
                "leverage": position_leverage,
                "pnl": pnl,
                "pnl_pct": (pnl / margin_used) * 100 if margin_used > 0 else 0,
                "days_held": days_held
            })

        # Calculate metrics
        final_capital = cash
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]

        num_trades = len(trades)
        win_rate = len(winning_trades) / num_trades if num_trades > 0 else 0.0
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0.0

        # Calculate drawdown
        equity_series = pd.Series(equity_curve, index=data.index)
        running_max = equity_series.expanding().max()
        drawdown = equity_series - running_max
        max_drawdown = drawdown.min()
        max_drawdown_pct = (max_drawdown / running_max.max()) * 100 if running_max.max() > 0 else 0.0

        # Calculate Sharpe ratio (assuming daily data)
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (
            (returns.mean() / returns.std()) * np.sqrt(252)
            if len(returns) > 0 and returns.std() > 0
            else 0.0
        )

        return BacktestResult(
            strategy_name=strategy.name,
            symbol=symbol,
            start_date=str(data.index[0].date()),
            end_date=str(data.index[-1].date()),
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            num_trades=num_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            sharpe_ratio=sharpe_ratio,
            trades=trades,
            equity_curve=equity_series
        )

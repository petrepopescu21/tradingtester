"""Command-line interface for Trading Tester."""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from backend.data.fetcher import DataFetcher
from backend.backtester.engine import BacktestEngine

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Trading Tester - LLM-powered trading strategy testing framework."""
    pass


@cli.command()
@click.argument('code_file', type=click.Path(exists=True))
@click.option('--symbol', '-s', default='AAPL', help='Trading symbol to test')
@click.option('--start', default='2020-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--end', default='2023-12-31', help='End date (YYYY-MM-DD)')
@click.option('--output', '-o', type=click.Path(), help='Output JSON file for results')
@click.option('--no-cache', is_flag=True, help='Disable data caching')
def test(
    code_file: str,
    symbol: str,
    start: str,
    end: str,
    output: Optional[str],
    no_cache: bool
):
    """Test a generated strategy Python file."""
    console.print(f"\n[bold blue]Testing: {code_file}[/bold blue]\n")

    try:
        # Load code
        console.print("[yellow]1. Loading strategy code...[/yellow]")
        code_path = Path(code_file)
        code = code_path.read_text(encoding='utf-8')

        # Find class name
        match = re.search(r'class\s+(\w+)\s*\([^)]*Strategy[^)]*\)', code)
        if not match:
            console.print("[red]Error: Could not find Strategy class in file[/red]")
            sys.exit(1)

        class_name = match.group(1)
        console.print(f"   Found class: [green]{class_name}[/green]")

        # Execute code
        namespace = {}
        exec(code, namespace)
        strategy_class = namespace.get(class_name)

        if not strategy_class:
            console.print(f"[red]Error: Could not load class {class_name}[/red]")
            sys.exit(1)

        strategy_instance = strategy_class()
        console.print("   [green]Strategy loaded successfully[/green]")

        # Fetch data
        console.print(f"\n[yellow]2. Fetching data for {symbol} ({start} to {end})...[/yellow]")
        fetcher = DataFetcher()
        data = fetcher.fetch(symbol, start, end, use_cache=not no_cache)
        console.print(f"   Fetched [green]{len(data)}[/green] data points")

        # Run backtest
        console.print("\n[yellow]3. Running backtest...[/yellow]")
        engine = BacktestEngine()
        result = engine.run(strategy_instance, data, symbol)

        # Display results
        _display_results(result)

        # Save to file
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            console.print(f"\n[green]Results saved to {output}[/green]")

    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('code_dir', type=click.Path(exists=True))
@click.option('--symbols', '-s', default='AAPL,MSFT,GOOGL', help='Comma-separated symbols')
@click.option('--start', default='2020-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--end', default='2023-12-31', help='End date (YYYY-MM-DD)')
@click.option('--output-dir', '-o', type=click.Path(), default='reports', help='Output directory')
def batch(code_dir: str, symbols: str, start: str, end: str, output_dir: str):
    """Batch test multiple generated strategy files."""
    console.print(f"\n[bold blue]Batch testing strategies in: {code_dir}[/bold blue]\n")

    symbol_list = [s.strip() for s in symbols.split(',')]
    strategy_files = list(Path(code_dir).glob('*.py'))

    console.print(f"Strategies: {len(strategy_files)}")
    console.print(f"Symbols: {', '.join(symbol_list)}")
    console.print(f"Period: {start} to {end}\n")

    results_summary = []

    for code_file in strategy_files:
        console.print(f"\n[bold]Testing: {code_file.name}[/bold]")

        try:
            code = code_file.read_text(encoding='utf-8')

            # Find class name
            match = re.search(r'class\s+(\w+)\s*\([^)]*Strategy[^)]*\)', code)
            if not match:
                console.print(f"[red]  Skipping: No Strategy class found[/red]")
                continue

            class_name = match.group(1)

            namespace = {}
            exec(code, namespace)
            strategy_class = namespace.get(class_name)

            if not strategy_class:
                console.print(f"[red]  Skipping: Could not load class {class_name}[/red]")
                continue

            # Test on each symbol
            for symbol in symbol_list:
                console.print(f"  Testing {symbol}...")

                try:
                    strategy_instance = strategy_class()

                    fetcher = DataFetcher()
                    data = fetcher.fetch(symbol, start, end)

                    engine = BacktestEngine()
                    result = engine.run(strategy_instance, data, symbol)

                    results_summary.append({
                        "strategy": result.strategy_name,
                        "file": code_file.name,
                        "symbol": symbol,
                        "return_pct": result.total_return_pct,
                        "sharpe_ratio": result.sharpe_ratio,
                        "num_trades": result.num_trades,
                        "win_rate": result.win_rate
                    })

                    # Save individual result
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    result_file = output_path / f"{code_file.stem}_{symbol}.json"

                    with open(result_file, 'w') as f:
                        json.dump(result.to_dict(), f, indent=2)

                    console.print(f"    Return: [green]{result.total_return_pct:.2f}%[/green], "
                                f"Sharpe: {result.sharpe_ratio:.2f}, Trades: {result.num_trades}")

                except Exception as e:
                    console.print(f"    [red]Error: {str(e)}[/red]")

        except Exception as e:
            console.print(f"[red]  Error loading strategy: {str(e)}[/red]")

    # Display summary
    if results_summary:
        console.print("\n[bold]Summary of Results:[/bold]\n")
        table = Table()
        table.add_column("Strategy")
        table.add_column("Symbol")
        table.add_column("Return %", justify="right")
        table.add_column("Sharpe", justify="right")
        table.add_column("Trades", justify="right")
        table.add_column("Win Rate", justify="right")

        for r in results_summary:
            table.add_row(
                r["strategy"],
                r["symbol"],
                f"{r['return_pct']:.2f}%",
                f"{r['sharpe_ratio']:.2f}",
                str(r["num_trades"]),
                f"{r['win_rate']*100:.1f}%"
            )

        console.print(table)

        # Save summary
        summary_file = Path(output_dir) / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results_summary, f, indent=2)
        console.print(f"\n[green]Summary saved to {summary_file}[/green]")


def _display_results(result):
    """Display backtest results in a nice format."""
    console.print("\n[bold]Backtest Results:[/bold]\n")

    table = Table(show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Strategy", result.strategy_name)
    table.add_row("Symbol", result.symbol)
    table.add_row("Period", f"{result.start_date} to {result.end_date}")
    table.add_row("Initial Capital", f"${result.initial_capital:,.2f}")
    table.add_row("Final Capital", f"${result.final_capital:,.2f}")
    table.add_row("Total Return", f"${result.total_return:,.2f} ({result.total_return_pct:.2f}%)")
    table.add_row("Number of Trades", str(result.num_trades))
    table.add_row("Winning Trades", str(result.winning_trades))
    table.add_row("Losing Trades", str(result.losing_trades))
    table.add_row("Win Rate", f"{result.win_rate * 100:.2f}%")
    table.add_row("Average Win", f"${result.avg_win:,.2f}")
    table.add_row("Average Loss", f"${result.avg_loss:,.2f}")
    table.add_row("Max Drawdown", f"${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2f}%)")
    table.add_row("Sharpe Ratio", f"{result.sharpe_ratio:.3f}")

    console.print(table)


if __name__ == '__main__':
    cli()

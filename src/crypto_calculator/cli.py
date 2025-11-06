"""Command line interface for the crypto calculator."""

from __future__ import annotations

import argparse
from decimal import Decimal
from pathlib import Path
from typing import Sequence

from .calculator import CryptoCalculator
from .providers import StaticRateProvider, default_provider


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for the CLI."""

    parser = argparse.ArgumentParser(description="Convert amounts between cryptocurrencies")
    parser.add_argument("amount", help="Amount of the base currency to convert")
    parser.add_argument("base", help="Symbol of the base currency (e.g. BTC)")
    parser.add_argument("quote", nargs="*", help="Symbols of quote currencies (e.g. USD ETH)")
    parser.add_argument(
        "--rates",
        type=Path,
        help="Optional path to a JSON file containing conversion rates",
    )
    return parser


def load_provider(path: Path | None) -> StaticRateProvider:
    """Return a rate provider from ``path`` or fall back to bundled defaults."""

    if path is None:
        return default_provider()
    return StaticRateProvider.from_file(path)


def parse_amount(raw: str) -> Decimal:
    """Convert a string amount into :class:`Decimal` exiting on failure."""

    try:
        return Decimal(raw)
    except Exception as exc:  # pragma: no cover - defensive branch
        raise SystemExit(f"Invalid amount {raw!r}: {exc}") from exc


def render_results(results) -> str:
    """Join conversion results into printable output."""

    return "\n".join(result.formatted() for result in results)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI with ``argv`` and print formatted conversion results."""

    parser = build_parser()
    args = parser.parse_args(argv)

    provider = load_provider(args.rates)
    calculator = CryptoCalculator(provider)

    amount = parse_amount(args.amount)

    quotes = args.quote or ["USD"]
    results = calculator.bulk_convert(amount, args.base, quotes)
    print(render_results(results))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())

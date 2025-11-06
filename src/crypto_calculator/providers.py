"""Utilities for looking up cryptocurrency exchange rates."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, Protocol, Tuple
import json


class RateProvider(Protocol):
    """Protocol describing an object able to provide currency conversion rates."""

    def get_rate(self, base_symbol: str, quote_symbol: str) -> Decimal:
        """Return the conversion rate from ``base_symbol`` to ``quote_symbol``."""
        ...


@dataclass(frozen=True)
class Quote:
    """Represents a single exchange quote between two assets."""

    base: str
    quote: str
    price: Decimal

    def inverted(self) -> "Quote":
        """Return the reciprocal quote."""

        return Quote(base=self.quote, quote=self.base, price=Decimal(1) / self.price)


class StaticRateProvider:
    """Simple provider that keeps rates in-memory."""

    def __init__(
        self,
        rates: Mapping[Tuple[str, str], Decimal | float | str],
        *,
        normalize_symbols: bool = True,
        bridge_symbol: str | None = "USD",
    ) -> None:
        """Create a provider from a mapping of ``(base, quote)`` -> rate."""

        # ``processed`` collects normalized and reciprocal pairs so lookups are
        # fast and case-insensitive.
        processed: MutableMapping[Tuple[str, str], Decimal] = {}
        for (base, quote), value in rates.items():
            base_key = base.upper() if normalize_symbols else base
            quote_key = quote.upper() if normalize_symbols else quote
            rate = _coerce_decimal(value)
            processed[(base_key, quote_key)] = rate
            if base_key != quote_key:
                # Automatically add the reciprocal rate to avoid requiring the
                # caller to spell out both trading directions.
                processed.setdefault((quote_key, base_key), Decimal(1) / rate)
        self._rates: Dict[Tuple[str, str], Decimal] = dict(processed)
        self._bridge_symbol = bridge_symbol.upper() if bridge_symbol else None

    def get_rate(self, base_symbol: str, quote_symbol: str) -> Decimal:
        base_key = base_symbol.upper()
        quote_key = quote_symbol.upper()
        if base_key == quote_key:
            return Decimal(1)
        try:
            return self._rates[(base_key, quote_key)]
        except KeyError:
            bridge_rate = self._bridge_lookup(base_key, quote_key)
            if bridge_rate is not None:
                return bridge_rate
            raise LookupError(
                f"No rate available for {base_symbol}->{quote_symbol}."
            )

    def _bridge_lookup(self, base: str, quote: str) -> Decimal | None:
        if self._bridge_symbol is None:
            return None
        bridge = self._bridge_symbol
        try:
            base_to_bridge = self._rates[(base, bridge)]
            quote_to_bridge = self._rates[(quote, bridge)]
        except KeyError:
            return None
        # Example: derive BTC->SOL via USD when BTC->USD and SOL->USD exist.
        return base_to_bridge / quote_to_bridge

    @classmethod
    def from_file(cls, path: str | Path) -> "StaticRateProvider":
        """Load rates from a JSON file."""

        data = json.loads(Path(path).read_text())
        return cls(_parse_rate_file(data))


def _parse_rate_file(raw: Mapping[str, Mapping[str, float | str | int]]) -> Dict[Tuple[str, str], Decimal]:
    processed: Dict[Tuple[str, str], Decimal] = {}
    for base, quotes in raw.items():
        for quote, value in quotes.items():
            processed[(base, quote)] = _coerce_decimal(value)
    return processed


def _coerce_decimal(value: Decimal | float | str | int) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:  # pragma: no cover - protective
        raise ValueError(f"Cannot convert {value!r} into Decimal") from exc


DEFAULT_RATES: Mapping[Tuple[str, str], Decimal] = {
    ("BTC", "USD"): Decimal("64000"),
    ("ETH", "USD"): Decimal("3200"),
    ("SOL", "USD"): Decimal("145"),
    ("BTC", "ETH"): Decimal("20"),
}


def default_provider() -> StaticRateProvider:
    """Return a provider pre-populated with sample rates."""

    return StaticRateProvider(DEFAULT_RATES)


__all__ = [
    "Quote",
    "RateProvider",
    "StaticRateProvider",
    "DEFAULT_RATES",
    "default_provider",
]

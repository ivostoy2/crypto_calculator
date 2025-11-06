"""Business logic for performing cryptocurrency conversions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

from .providers import RateProvider, default_provider

# We quantize to cents so that printed fiat values look conventional while
# preserving the exact rate used for the calculation.
_QUANTIZE_TARGET = Decimal("0.01")


@dataclass(slots=True)
class ConversionResult:
    """Container for conversion outcomes returned by :class:`CryptoCalculator`."""

    base_amount: Decimal
    base_symbol: str
    quote_amount: Decimal
    quote_symbol: str
    rate: Decimal

    def formatted(self) -> str:
        """Return a human-friendly rendering of the result."""

        return (
            f"{self.base_amount.normalize()} {self.base_symbol} "
            f"= {self.quote_amount.normalize()} {self.quote_symbol} "
            f"(@ {self.rate.normalize()} {self.quote_symbol}/{self.base_symbol})"
        )


class CryptoCalculator:
    """Perform conversions using a pluggable :class:`RateProvider`."""

    def __init__(self, provider: RateProvider | None = None) -> None:
        self._provider = provider or default_provider()

    def convert(self, amount: Decimal | float | str | int, base: str, quote: str) -> ConversionResult:
        """Convert ``amount`` of ``base`` currency into ``quote`` currency."""

        base_amount = _coerce_decimal(amount)
        # Rates are provided by the injected provider which allows the
        # calculator to be used with live APIs or fixed fixtures in tests.
        rate = self._provider.get_rate(base, quote)
        # Quantize the final amount for consistent display regardless of
        # whether the provider returns a noisy decimal.
        quote_amount = (base_amount * rate).quantize(_QUANTIZE_TARGET, rounding=ROUND_HALF_UP)
        return ConversionResult(
            base_amount=base_amount,
            base_symbol=base.upper(),
            quote_amount=quote_amount,
            quote_symbol=quote.upper(),
            rate=rate,
        )

    def bulk_convert(
        self,
        amount: Decimal | float | str | int,
        base: str,
        quotes: Sequence[str],
    ) -> Sequence[ConversionResult]:
        """Convert ``amount`` of ``base`` into multiple ``quote`` currencies."""

        # We delegate to :meth:`convert` to keep rounding and provider lookup
        # behaviour identical for single and bulk conversions.
        return [self.convert(amount, base, quote) for quote in quotes]


def _coerce_decimal(value: Decimal | float | str | int) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


__all__ = ["CryptoCalculator", "ConversionResult"]

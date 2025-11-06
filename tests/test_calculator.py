from decimal import Decimal

from crypto_calculator.calculator import CryptoCalculator
from crypto_calculator.providers import StaticRateProvider


def make_provider():
    """Fixture-style helper returning a provider with deterministic rates."""

    return StaticRateProvider({
        ("BTC", "USD"): Decimal("50000"),
        ("ETH", "USD"): Decimal("2500"),
    })


def test_convert_uses_provider_rate():
    """Single conversion should reflect the configured provider rate."""

    calculator = CryptoCalculator(make_provider())
    result = calculator.convert("2", "BTC", "USD")
    assert result.quote_amount == Decimal("100000.00")
    assert result.rate == Decimal("50000")


def test_convert_same_symbol_returns_identity():
    """Requests with identical base and quote return the original amount."""

    calculator = CryptoCalculator(make_provider())
    result = calculator.convert(5, "ETH", "ETH")
    assert result.quote_amount == Decimal("5.00")
    assert result.rate == Decimal("1")


def test_bulk_convert_returns_multiple_results():
    """The bulk helper mirrors calling ``convert`` for each quote symbol."""

    calculator = CryptoCalculator(make_provider())
    results = calculator.bulk_convert(1, "BTC", ["USD", "ETH"])
    assert len(results) == 2
    assert {r.quote_symbol for r in results} == {"USD", "ETH"}


def test_provider_from_file(tmp_path):
    """Rates can be sourced from disk and parsed as decimals."""

    path = tmp_path / "rates.json"
    path.write_text('{"BTC": {"USD": 100}}')
    provider = StaticRateProvider.from_file(path)
    rate = provider.get_rate("BTC", "USD")
    assert rate == Decimal("100")

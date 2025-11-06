# Crypto Calculator

A lightweight Python toolkit for experimenting with cryptocurrency conversions. It
ships with an in-memory rate provider and a small CLI so you can explore how
much one asset is worth in terms of another.

## Features

- 🔁  Decimal-based conversion logic that avoids floating point drift
- 🔌  Pluggable rate providers, with a JSON-backed static implementation included
- 🧰  CLI tool for ad-hoc conversions
- ✅  Pytest suite covering the key building blocks

## Getting Started

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

2. **Run the tests**

   ```bash
   pytest
   ```

3. **Try the CLI**

   ```bash
   crypto-calculator 0.5 BTC USD ETH
   ```

   Use `--rates path/to/file.json` to load custom rates. The JSON should map
   base symbols to quote dictionaries, for example:

   ```json
   {
     "BTC": {"USD": 68000},
     "ETH": {"USD": 3400, "BTC": 0.05}
   }
   ```

## Project Layout

```
.
├── src/crypto_calculator/        # Package source
│   ├── calculator.py             # Conversion logic and result helpers
│   ├── cli.py                    # Command line interface
│   └── providers.py              # Rate provider abstractions
├── tests/                        # Pytest-based test suite
└── pyproject.toml                # Build configuration and dependencies
```

## Next Steps

- Integrate with a live market data API to fetch real-time prices
- Add caching strategies for rate lookups
- Expand the CLI with richer formatting or interactive prompts
- Build a simple web dashboard using the calculator as a backend service

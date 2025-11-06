"""Core package for the :mod:`crypto_calculator` project."""

from .calculator import CryptoCalculator
from .providers import RateProvider, StaticRateProvider

__all__ = ["CryptoCalculator", "RateProvider", "StaticRateProvider"]

"""Package `phonetic_distance` — public API wrapper.

Questo package re-esporta l'implementazione definita nel modulo core.
"""
from __future__ import annotations

from .core import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]

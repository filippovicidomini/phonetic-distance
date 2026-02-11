"""Retrocompatibility shim: `wd` -> re-export `phonetic_distance`.

Importing from `wd` will continue to work but is deprecated; prefer
`phonetic_distance` as module name.
"""
from __future__ import annotations

from warnings import warn

warn("'wd' is deprecated; import from 'phonetic_distance' instead.", DeprecationWarning, stacklevel=2)

from phonetic_distance import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
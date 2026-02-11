# -*- coding: utf-8 -*-
#%%
"""core.py — Weighted phonological Levenshtein distance + normalized similarities.

Questo modulo implementa una distanza edit fonologica tra trascrizioni fonetiche/ortografiche 
usando tokenizzazione NFD, costi di sostituzione basati su feature e penalità per diacritici.

API pubblica:
  - tokenize_segments
  - weighted_levenshtein
  - phon_similarity_normalized
  - concept_similarity_normalized
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache
from typing import FrozenSet, List, Sequence, Tuple

# -----------------------------------------------------------------------------
# 1) BASE FEATURES
# -----------------------------------------------------------------------------

# Token type aliases
Token = Tuple[str, FrozenSet[str]]  # (base, frozenset(diacritics))

# Treat word boundary as a token (optional but often helps)
BOUNDARY_TOKEN: Token = ("#", frozenset())

# Multi-char bases from your inventory (must be recognized before char-wise parsing)
# IMPORTANT: these should be in NFD form to match normalize_nfd() output.
MULTI_BASES: List[str] = [
    "g’",
    "k’",
    "hʼ",
    "lʼ",
    "nʼ",
    "r̥",
    "r̄",
    "r̃",
    "ṙ",
]

# Minimal feature sets (enough for sensible costs)
# type: 'V' vowel, 'C' consonant
# Vowels: height/back/round
# Consonants: place/manner/voice
BASE_FEATS = {
    # VOWELS
    "a": {"type": "V", "height": "open", "back": "central", "round": 0},
    "e": {"type": "V", "height": "mid", "back": "front", "round": 0},
    "ë": {"type": "V", "height": "mid", "back": "central", "round": 0},  # schwa-ish
    "i": {"type": "V", "height": "close", "back": "front", "round": 0},
    "o": {"type": "V", "height": "mid", "back": "back", "round": 1},
    "u": {"type": "V", "height": "close", "back": "back", "round": 1},
    "ö": {"type": "V", "height": "mid", "back": "front", "round": 1},
    "ü": {"type": "V", "height": "close", "back": "front", "round": 1},

    # Semivowels (treat as consonant-like approximants)
    "i̯": {"type": "C", "place": "palatal", "manner": "approx", "voice": 1},
    "u̯": {"type": "C", "place": "velar", "manner": "approx", "voice": 1},

    # STOPS
    "p": {"type": "C", "place": "bilabial", "manner": "stop", "voice": 0},
    "b": {"type": "C", "place": "bilabial", "manner": "stop", "voice": 1},
    "t": {"type": "C", "place": "dental", "manner": "stop", "voice": 0},
    "d": {"type": "C", "place": "dental", "manner": "stop", "voice": 1},
    "k": {"type": "C", "place": "velar", "manner": "stop", "voice": 0},
    "g": {"type": "C", "place": "velar", "manner": "stop", "voice": 1},
    "q": {"type": "C", "place": "pharyngeal", "manner": "stop", "voice": 0},
    "ʾ": {"type": "C", "place": "laryngeal", "manner": "stop", "voice": 0},  # glottal stop

    # FRICATIVES / SPIRANTS
    "f": {"type": "C", "place": "labiodental", "manner": "fric", "voice": 0},
    "v": {"type": "C", "place": "labiodental", "manner": "fric", "voice": 1},
    "β": {"type": "C", "place": "bilabial", "manner": "fric", "voice": 1},
    "ϕ": {"type": "C", "place": "bilabial", "manner": "fric", "voice": 0},
    "δ": {"type": "C", "place": "dental", "manner": "fric", "voice": 1},
    "ϑ": {"type": "C", "place": "dental", "manner": "fric", "voice": 0},
    "ɣ": {"type": "C", "place": "velar", "manner": "fric", "voice": 1},
    "χ": {"type": "C", "place": "velar", "manner": "fric", "voice": 0},
    "h": {"type": "C", "place": "laryngeal", "manner": "fric", "voice": 0},
    "ɦ": {"type": "C", "place": "laryngeal", "manner": "fric", "voice": 1},
    "ḥ": {"type": "C", "place": "laryngeal", "manner": "fric", "voice": 0},
    "ɛ": {"type": "C", "place": "laryngeal", "manner": "fric", "voice": 1},  # from your list

    # SIBILANTS
    "s": {"type": "C", "place": "alveolar", "manner": "sibilant", "voice": 0},
    "ś": {"type": "C", "place": "prepalatal", "manner": "sibilant", "voice": 0},
    "š": {"type": "C", "place": "palatal", "manner": "sibilant", "voice": 0},
    "ʃ": {"type": "C", "place": "alveolar", "manner": "sibilant", "voice": 1},
    "ʃ̌": {"type": "C", "place": "palatal", "manner": "sibilant", "voice": 1},

    # AFFRICATES
    "z": {"type": "C", "place": "alveolar", "manner": "affric", "voice": 0},
    "ʒ": {"type": "C", "place": "alveolar", "manner": "affric", "voice": 1},
    "č": {"type": "C", "place": "palatal", "manner": "affric", "voice": 0},
    "ć": {"type": "C", "place": "prepalatal", "manner": "affric", "voice": 0},
    "ǧ": {"type": "C", "place": "palatal", "manner": "affric", "voice": 1},
    "ģ": {"type": "C", "place": "prepalatal", "manner": "affric", "voice": 1},

    # NASALS
    "m": {"type": "C", "place": "bilabial", "manner": "nasal", "voice": 1},
    "n": {"type": "C", "place": "alveolar", "manner": "nasal", "voice": 1},
    "ṅ": {"type": "C", "place": "velar", "manner": "nasal", "voice": 1},

    # LATERALS / RHOTICS
    "l": {"type": "C", "place": "alveolar", "manner": "lateral", "voice": 1},
    "ł": {"type": "C", "place": "velar", "manner": "lateral", "voice": 1},
    "r": {"type": "C", "place": "alveolar", "manner": "trill", "voice": 1},
    "ɹ": {"type": "C", "place": "alveolar", "manner": "approx", "voice": 1},
}

# Fast helper set for vowel fallback classification
_VOWEL_BASES = {"a", "e", "i", "o", "u", "ë", "ö", "ü"}

# Separators considered as word boundaries
_BOUNDARY_SEPARATORS = {"-", "/", "|"}


# -----------------------------------------------------------------------------
# 2) NORMALIZATION + TOKENIZATION
# -----------------------------------------------------------------------------

@lru_cache(maxsize=200_000)
def normalize_nfd(s: str | None) -> str:
    """Return unicode NFD normalized string, stripped. None -> empty."""
    if s is None:
        return ""
    return unicodedata.normalize("NFD", str(s).strip())


def split_variants(s: str | None) -> List[str]:
    """Split cell variants separated by '/', normalizing NFD and trimming."""
    s = normalize_nfd(s)
    if not s:
        return []
    s = s.replace("／", "/")  # normalize fullwidth slash
    parts = [p.strip() for p in s.split("/") if p.strip()]
    return parts


def _is_combining(ch: str) -> bool:
    return unicodedata.combining(ch) != 0


# Pre-sort multibases by length (desc) so greedy matching is deterministic
_MULTI_BASES_SORTED = sorted({normalize_nfd(mb) for mb in MULTI_BASES}, key=len, reverse=True)


def tokenize_segments(s: str | None, keep_boundaries: bool = True) -> List[Token]:
    """Tokenize a string into (base, diacritics) tokens.

    - Bases are either known multi-char bases (matched greedily) or single chars.
    - Diacritics are combining marks attached to the immediately preceding base.
    - If keep_boundaries=True, whitespace and separators create BOUNDARY_TOKEN.

    Trailing boundary token is removed.
    """
    s = normalize_nfd(s)
    if not s:
        return []

    tokens: List[Token] = []
    i = 0

    while i < len(s):
        ch = s[i]

        # boundaries: whitespace or separators
        if ch.isspace() or ch in _BOUNDARY_SEPARATORS:
            if keep_boundaries and tokens and tokens[-1] != BOUNDARY_TOKEN:
                tokens.append(BOUNDARY_TOKEN)
            i += 1
            continue

        # try multi-bases first (greedy, longest match)
        matched = None
        for mb in _MULTI_BASES_SORTED:
            if s.startswith(mb, i):
                matched = mb
                break

        if matched is not None:
            base = matched
            i += len(matched)
            diacs: List[str] = []
            while i < len(s) and _is_combining(s[i]):
                diacs.append(s[i])
                i += 1
            tokens.append((base, frozenset(diacs)))
            continue

        # stray combining mark: attach to previous token if possible
        if _is_combining(ch):
            if tokens and tokens[-1] != BOUNDARY_TOKEN:
                base, diacs = tokens[-1]
                tokens[-1] = (base, frozenset(set(diacs) | {ch}))
            i += 1
            continue

        # otherwise: single-character base
        base = ch
        i += 1
        diacs2: List[str] = []
        while i < len(s) and _is_combining(s[i]):
            diacs2.append(s[i])
            i += 1
        tokens.append((base, frozenset(diacs2)))

    # drop trailing boundary
    if tokens and tokens[-1] == BOUNDARY_TOKEN:
        tokens.pop()

    return tokens


# -----------------------------------------------------------------------------
# 3) COST FUNCTIONS
# -----------------------------------------------------------------------------

def is_vowel_base(base: str) -> bool:
    """Heuristic vowel test used for unknown-symbol fallback."""
    f = BASE_FEATS.get(base)
    return (f is not None and f.get("type") == "V") or (base in _VOWEL_BASES)


def base_cost(b1: str, b2: str) -> float:
    """Cost for substituting base b1 -> b2 (ignoring diacritics).

    Returns a value roughly in [0.2, 1.3].
    """
    if b1 == b2:
        return 0.0

    f1 = BASE_FEATS.get(b1)
    f2 = BASE_FEATS.get(b2)

    # Unknown fallback: if both vowels or both consonants, moderate; else high
    if f1 is None or f2 is None:
        v1 = is_vowel_base(b1)
        v2 = is_vowel_base(b2)
        return 1.3 if (v1 != v2) else 0.9

    # vowel <-> consonant
    if f1.get("type") != f2.get("type"):
        return 1.3

    if f1.get("type") == "V":
        # vowel distance via height/back/round
        cost = 0.0
        if f1.get("height") != f2.get("height"):
            cost += 0.4
        if f1.get("back") != f2.get("back"):
            cost += 0.4
        if f1.get("round") != f2.get("round"):
            cost += 0.2
        return min(1.2, max(0.2, cost))

    # consonant: voice/place/manner
    cost = 0.0
    if f1.get("voice") != f2.get("voice"):
        cost += 0.2
    if f1.get("place") != f2.get("place"):
        cost += 0.4
    if f1.get("manner") != f2.get("manner"):
        cost += 0.6
    return min(1.2, max(0.2, cost))


def diac_cost(d1: FrozenSet[str], d2: FrozenSet[str], w: float = 0.1) -> float:
    """Small penalty for diacritic differences (symmetric difference * w)."""
    if d1 == d2:
        return 0.0
    return w * len(set(d1) ^ set(d2))


def sub_cost(t1: Token, t2: Token, diac_w: float = 0.1) -> float:
    """Substitution cost between two tokens."""
    # boundary tokens: cheap match, low mismatch
    if t1 == BOUNDARY_TOKEN and t2 == BOUNDARY_TOKEN:
        return 0.0
    if t1 == BOUNDARY_TOKEN or t2 == BOUNDARY_TOKEN:
        return 0.2

    b1, d1 = t1
    b2, d2 = t2
    return base_cost(b1, b2) + diac_cost(d1, d2, w=diac_w)


def ins_del_cost(
    t: Token,
    vowel_cost: float = 1.0,
    cons_cost: float = 1.1,
    boundary_cost: float = 0.2,
) -> float:
    """Insertion/deletion cost of a single token."""
    if t == BOUNDARY_TOKEN:
        return boundary_cost
    base, _ = t
    return vowel_cost if is_vowel_base(base) else cons_cost


# -----------------------------------------------------------------------------
# 4) WEIGHTED LEVENSHTEIN (DP)
# -----------------------------------------------------------------------------

def weighted_levenshtein(
    tokens_a: Sequence[Token],
    tokens_b: Sequence[Token],
    diac_w: float = 0.1,
    vowel_cost: float = 1.0,
    cons_cost: float = 1.1,
    boundary_cost: float = 0.2,
) -> float:
    """Compute weighted edit distance between token sequences (classic DP)."""
    n, m = len(tokens_a), len(tokens_b)

    # DP row (previous row)
    prev = [0.0] * (m + 1)

    # init first row (insertions)
    for j in range(1, m + 1):
        prev[j] = prev[j - 1] + ins_del_cost(tokens_b[j - 1], vowel_cost, cons_cost, boundary_cost)

    for i in range(1, n + 1):
        cur = [0.0] * (m + 1)
        # deletion from tokens_a
        cur[0] = prev[0] + ins_del_cost(tokens_a[i - 1], vowel_cost, cons_cost, boundary_cost)

        for j in range(1, m + 1):
            del_c = prev[j] + ins_del_cost(tokens_a[i - 1], vowel_cost, cons_cost, boundary_cost)
            ins_c = cur[j - 1] + ins_del_cost(tokens_b[j - 1], vowel_cost, cons_cost, boundary_cost)
            sub_c = prev[j - 1] + sub_cost(tokens_a[i - 1], tokens_b[j - 1], diac_w=diac_w)
            cur[j] = min(del_c, ins_c, sub_c)

        prev = cur

    return prev[m]


# -----------------------------------------------------------------------------
# 5) SIMILARITIES
# -----------------------------------------------------------------------------

def similarity_normalized(d: float, L: int) -> float:
    """Linear normalized similarity in [0,1]."""
    if L <= 0:
        return 0.0
    return max(0.0, 1.0 - d / L)


def phon_similarity_normalized(
    s1: str | None,
    s2: str | None,
    keep_boundaries: bool = True,
    diac_w: float = 0.1,
) -> float:
    """Phonological similarity normalized by token length."""
    t1 = tokenize_segments(s1, keep_boundaries=keep_boundaries)
    t2 = tokenize_segments(s2, keep_boundaries=keep_boundaries)

    d = weighted_levenshtein(t1, t2, diac_w=diac_w)
    L = max(len(t1), len(t2))

    return similarity_normalized(d, L)


def concept_similarity_normalized(
    cell_a: str | None,
    cell_b: str | None,
    keep_boundaries: bool = True,
    diac_w: float = 0.1,
) -> float:
    """Split variants on '/', compute normalized similarity for all pairs, return MAX similarity."""
    Va = split_variants(cell_a)
    Vb = split_variants(cell_b)

    if not Va or not Vb:
        return float("nan")

    best = -1.0
    for a in Va:
        for b in Vb:
            s = phon_similarity_normalized(a, b, keep_boundaries=keep_boundaries, diac_w=diac_w)
            if s > best:
                best = s
    return best

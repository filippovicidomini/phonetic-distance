#!/usr/bin/env python3
"""CLI minimo per aggiungere forme al dizionario locale `data/dictionary.txt`.

Esempio:
    python scripts/update_dictionary.py "pane" "pàn"

Il file viene normalizzato in NFD e vengono evitati duplicati.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "dictionary.txt"

def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    parser = argparse.ArgumentParser(description="Aggiungi forme al dizionario locale")
    parser.add_argument("forms", nargs="+", help="Forme o varianti (sono accettate '/'-separate)")
    args = parser.parse_args(argv)

    # import normalize from wd if available
    try:
        from phonetic_distance import normalize_nfd
    except Exception:
        # fallback minimal normalizer
        import unicodedata

        def normalize_nfd(s: str) -> str:
            return unicodedata.normalize('NFD', s.strip())

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if DATA_FILE.exists():
        existing = {l.strip() for l in DATA_FILE.read_text(encoding='utf8').splitlines() if l.strip() and not l.startswith('#')}

    new = []
    for f in args.forms:
        nf = normalize_nfd(f)
        if nf not in existing:
            existing.add(nf)
            new.append(nf)

    if not new:
        print("Nessuna forma nuova da aggiungere.")
        return 0

    with DATA_FILE.open('a', encoding='utf8') as fh:
        for n in new:
            fh.write(n + "\n")

    print(f"Aggiunte {len(new)} forme al dizionario: {new}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script helper per eseguire l'analisi dei tempi di calcolo con comandi predefiniti.
Fornisce preset per diverse configurazioni.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_analysis(concepts=None, name="default", start=0, save_every=50):
    """Esegue l'analisi con i parametri dati."""
    cmd = [
        "python", "scripts/analyze_computation_times.py",
        f"--output", f"scripts/computation_times_{name}.csv",
        f"--save-every", str(save_every),
    ]
    
    if concepts:
        cmd.extend(["--concepts", str(concepts)])
    
    if start > 0:
        cmd.extend(["--start", str(start)])
    
    print(f"Eseguendo: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Esegui analisi dei tempi di calcolo con preset predefiniti.'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando da eseguire')
    
    # Preset: quick test
    test_parser = subparsers.add_parser('test', help='Test rapido (10 concetti)')
    
    # Preset: small run
    small_parser = subparsers.add_parser('small', help='Analisi piccola (100 concetti)')
    
    # Preset: medium run
    medium_parser = subparsers.add_parser('medium', help='Analisi media (200 concetti)')
    
    # Preset: full run
    full_parser = subparsers.add_parser('full', help='Analisi completa (all 369 concetti)')
    
    # Custom run
    custom_parser = subparsers.add_parser('custom', help='Analisi personalizzata')
    custom_parser.add_argument('--concepts', type=int, required=True, help='Numero di concetti')
    custom_parser.add_argument('--start', type=int, default=0, help='Indice iniziale')
    custom_parser.add_argument('--name', type=str, default='custom', help='Nome output')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        success = run_analysis(concepts=10, name='test', save_every=5)
    elif args.command == 'small':
        success = run_analysis(concepts=100, name='small', save_every=25)
    elif args.command == 'medium':
        success = run_analysis(concepts=200, name='medium', save_every=50)
    elif args.command == 'full':
        success = run_analysis(concepts=None, name='full', save_every=50)
    elif args.command == 'custom':
        success = run_analysis(
            concepts=args.concepts,
            name=args.name,
            start=args.start,
            save_every=50
        )
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

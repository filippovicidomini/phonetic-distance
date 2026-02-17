#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analisi dei tempi di calcolo della similarità fonologica per features di concetti.

Legge il CSV ALM123.csv e per ogni concetto calcola i tempi di similarità
tra le 165 features (una per città). Analizza i tempi e salva i risultati.

Uso:
    python scripts/analyze_computation_times.py --output results.csv --concepts 10
"""

import argparse
import csv
import sys
import time
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from multiprocessing import Pool, cpu_count

# Importa la funzione di similarità
sys.path.insert(0, str(Path(__file__).parent.parent))
from phonetic_distance import phon_similarity_normalized


def read_csv_data(csv_path: str) -> Tuple[List[str], List[str], List[List[str]]]:
    """
    Legge il CSV ALM123.csv e ritorna:
    - city_names: nome delle 165 città
    - concept_names: nome dei 369 concetti
    - data: matrice 165×369 dei dati
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Prima riga: intestazioni (Città, AREA, lat, lon, concetto_1, ...)
        header = next(reader)
        concept_names = header[4:]  # Tutti gli elementi dopo "lon"
        
        # Seconda riga: indici concetti (skip)
        indices_row = next(reader)
        
        # Righe successive: per ogni città
        city_names = []
        data = []
        for row in reader:
            if len(row) > 0:
                city_names.append(row[0])  # Prima colonna: nome città
                features = row[4:]           # Dal quinto elemento in poi: i 369 concetti
                data.append(features)
    
    return city_names, concept_names, data


def compute_similarity_times(
    features: List[str], 
    city_names: List[str]
) -> List[float]:
    """
    Computa i tempi di similarità tra coppie di features (triangolo superiore).
    
    Returns:
        Lista dei tempi (in secondi) per ogni confronto.
    """
    times = []
    n = len(features)
    
    for i in range(n):
        for j in range(i + 1, n):
            feat1 = features[i]
            feat2 = features[j]
            
            # Salta se una feature è vuota
            if not feat1 or not feat2:
                continue
            
            # Misura il tempo di calcolo della similarità
            start = time.perf_counter()
            similarity = phon_similarity_normalized(feat1, feat2)
            end = time.perf_counter()
            
            elapsed = end - start
            times.append(elapsed)
    
    return times


def analyze_times(times: List[float]) -> Dict[str, Any]:
    """Analizza una lista di tempi e ritorna statistiche."""
    if not times:
        return {
            'count': 0,
            'mean': 0,
            'median': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'p25': 0,
            'p75': 0,
            'p95': 0,
            'total_time': 0,
        }
    
    times_arr = np.array(times)
    return {
        'count': len(times),
        'mean': float(np.mean(times_arr)),
        'median': float(np.median(times_arr)),
        'std': float(np.std(times_arr)),
        'min': float(np.min(times_arr)),
        'max': float(np.max(times_arr)),
        'p25': float(np.percentile(times_arr, 25)),
        'p75': float(np.percentile(times_arr, 75)),
        'p95': float(np.percentile(times_arr, 95)),
        'total_time': float(np.sum(times_arr)),
    }


def process_concept(
    concept_idx: int,
    concept_name: str,
    features: List[str],
    city_names: List[str]
) -> Dict[str, Any]:
    """Processa un singolo concetto e ritorna le statistiche."""
    print(f"[{concept_idx}] Elaborazione: {concept_name}...", end=' ', flush=True)
    
    try:
        times = compute_similarity_times(features, city_names)
        stats = analyze_times(times)
        stats['concept_idx'] = concept_idx
        stats['concept_name'] = concept_name
        stats['status'] = 'ok'
        print(f"OK ({stats['count']} confronti, {stats['mean']:.6f}s media)")
    except Exception as e:
        print(f"ERRORE: {e}")
        stats = {
            'concept_idx': concept_idx,
            'concept_name': concept_name,
            'status': 'error',
            'error_msg': str(e),
        }
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Analizza i tempi di calcolo della similarità tra features di concetti.'
    )
    parser.add_argument(
        '--csv',
        type=str,
        default='scripts/ALM123.csv',
        help='Percorso al file CSV (default: scripts/ALM123.csv)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='scripts/computation_times_analysis.csv',
        help='Percorso del file output CSV (default: scripts/computation_times_analysis.csv)'
    )
    parser.add_argument(
        '--concepts', '-c',
        type=int,
        default=None,
        help='Numero di concetti da analizzare (default: tutti i 369)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Indice iniziale dei concetti (default: 0)'
    )
    parser.add_argument(
        '--save-every',
        type=int,
        default=50,
        help='Salva risultati ogni N concetti (default: 50)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Output più verboso'
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Errore: file {csv_path} non trovato", file=sys.stderr)
        sys.exit(1)
    
    print(f"Lettura dati da {csv_path}...")
    city_names, concept_names, data = read_csv_data(str(csv_path))
    
    print(f"  - Città: {len(city_names)}")
    print(f"  - Concetti: {len(concept_names)}")
    
    # Seleziona il range di concetti
    start_idx = args.start
    end_idx = len(concept_names)
    if args.concepts is not None:
        end_idx = min(start_idx + args.concepts, end_idx)
    
    print(f"\nAnalizzando concetti da {start_idx} a {end_idx-1} ({end_idx-start_idx} totali)...")
    print()
    
    results = []
    start_time = time.time()
    
    # Prepara il file di output (header)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'concept_idx', 'concept_name', 'status',
        'count', 'mean', 'median', 'std', 'min', 'max',
        'p25', 'p75', 'p95', 'total_time'
    ]
    
    # Funzione helper per salvare risultati
    def save_results(batch_results: List[Dict], is_final: bool = False):
        """Salva i risultati in CSV (append se non è la prima volta)."""
        mode = 'w' if not is_final else 'a'
        write_header = not output_path.exists() if is_final else True
        
        with open(output_path, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, restval='')
            if write_header:
                writer.writeheader()
            
            for result in batch_results:
                row = {k: result.get(k, '') for k in fieldnames}
                writer.writerow(row)
    
    # Processa i concetti in batch
    batch_results = []
    for concept_idx in range(start_idx, end_idx):
        concept_name = concept_names[concept_idx]
        # Estrai le features per questo concetto
        features = [data[city_idx][concept_idx] for city_idx in range(len(city_names))]
        
        result = process_concept(concept_idx, concept_name, features, city_names)
        batch_results.append(result)
        results.append(result)
        
        # Salva ogni N concetti
        if len(batch_results) >= args.save_every or concept_idx == end_idx - 1:
            save_results(batch_results, is_final=True)
            batch_results = []
    
    elapsed = time.time() - start_time
    
    print(f"✓ Risultati salvati in {output_path}")
    
    # Statistiche di riepilogo
    ok_results = [r for r in results if r.get('status') == 'ok']
    if ok_results:
        print(f"\nRiepilogo:")
        print(f"  - Concetti elaborati: {len(ok_results)}/{len(results)}")
        print(f"  - Tempo totale: {elapsed:.2f}s")
        
        # Tempo totale di calcolo della similarità
        total_sim_time = sum(r.get('total_time', 0) for r in ok_results)
        print(f"  - Tempo calcolo similarità: {total_sim_time:.2f}s")
        
        # Statistiche sui tempi medi
        means = [r.get('mean', 0) for r in ok_results]
        print(f"  - Media dei tempi medi: {np.mean(means):.6f}s")
        print(f"  - Max del tempo medio: {np.max(means):.6f}s")
        print(f"  - Min del tempo medio: {np.min(means):.6f}s")
        
        # File di riepilogo
        summary_path = output_path.parent / 'computation_times_summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("ANALISI TEMPI DI CALCOLO DELLA SIMILARITÀ FONOLOGICA\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Esecuzione: {Path(args.csv).name}\n")
            f.write(f"Concetti analizzati: {len(ok_results)}\n")
            f.write(f"Tempo totale: {elapsed:.2f}s\n")
            f.write(f"Tempo calcolo similarità: {total_sim_time:.2f}s\n\n")
            
            f.write("STATISTICHE SUI TEMPI MEDI:\n")
            f.write(f"  - Media: {np.mean(means):.8f}s\n")
            f.write(f"  - Mediana: {np.median(means):.8f}s\n")
            f.write(f"  - Dev.Std: {np.std(means):.8f}s\n")
            f.write(f"  - Min: {np.min(means):.8f}s\n")
            f.write(f"  - Max: {np.max(means):.8f}s\n")
            f.write(f"  - P25: {np.percentile(means, 25):.8f}s\n")
            f.write(f"  - P75: {np.percentile(means, 75):.8f}s\n")
            f.write(f"  - P95: {np.percentile(means, 95):.8f}s\n\n")
            
            # Confronti totali
            total_comparisons = sum(r.get('count', 0) for r in ok_results)
            f.write(f"CONFRONTI TOTALI: {total_comparisons:,}\n")
            f.write(f"Velocità media: {total_comparisons / total_sim_time:.0f} confronti/sec\n\n")
            
            f.write("Risultati salvati in:\n")
            f.write(f"  {output_path}\n")
        
        print(f"\n✓ Riepilogo salvato in {summary_path}")



if __name__ == '__main__':
    main()

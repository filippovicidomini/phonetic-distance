#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera grafici a partire da `computation_times_analysis.csv` e salva le immagini in `scripts/images/`.

Grafici generati:
 - histogram_mean.png: distribuzione dei tempi medi per confronto
 - histogram_max.png: distribuzione dei tempi max per confronto
 - top10_slowest.png: barre dei 10 concetti con tempo medio maggiore
 - mean_vs_max.png: scatter mean vs max per concetto

Uso:
    python scripts/plot_timing_analysis.py --csv scripts/computation_times_analysis.csv --outdir scripts/images

"""

import argparse
import csv
import os
from pathlib import Path
import math

try:
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import numpy as np
except Exception:
    raise SystemExit("Required plotting libraries not found. Please install matplotlib and numpy.")


def read_results(csv_path):
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # convert numeric fields
            try:
                r['mean'] = float(r.get('mean', 0) or 0)
                r['max'] = float(r.get('max', 0) or 0)
                r['count'] = int(r.get('count', 0) or 0)
            except Exception:
                continue
            rows.append(r)
    return rows


def ensure_outdir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def human_seconds(x, pos=None):
    # formatter to show seconds in scientific or ms
    if x >= 1.0:
        return f"{x:.2f}s"
    elif x >= 1e-3:
        return f"{x*1e3:.2f}ms"
    elif x >= 1e-6:
        return f"{x*1e6:.2f}µs"
    else:
        return f"{x:.2g}s"


def plot_histogram(data, key, outpath, bins=40, title=None):
    vals = np.array([d[key] for d in data if d.get(key) is not None])
    plt.figure(figsize=(8,4))
    plt.hist(vals, bins=bins, color='#2b8cbe', edgecolor='black')
    plt.xlabel('seconds')
    plt.ylabel('count')
    if title:
        plt.title(title)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(human_seconds))
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()


def plot_topk_bar(data, key, outpath, k=10, title=None):
    sorted_data = sorted(data, key=lambda r: r.get(key, 0), reverse=True)[:k]
    names = [r['concept_name'] for r in sorted_data]
    vals = [r.get(key, 0) for r in sorted_data]
    y_pos = np.arange(len(names))[::-1]

    plt.figure(figsize=(8, max(3, 0.4*len(names))))
    plt.barh(y_pos, vals, color='#f03b20')
    plt.yticks(y_pos, names)
    plt.xlabel('seconds')
    if title:
        plt.title(title)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(human_seconds))
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()


def plot_scatter_mean_max(data, outpath, title=None):
    means = np.array([d['mean'] for d in data])
    maxs = np.array([d['max'] for d in data])
    names = [d['concept_name'] for d in data]

    plt.figure(figsize=(6,6))
    plt.scatter(means, maxs, alpha=0.7)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('mean (s)')
    plt.ylabel('max (s)')
    if title:
        plt.title(title)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(human_seconds))
    ax.yaxis.set_major_formatter(FuncFormatter(human_seconds))
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Plot timing analysis from CSV')
    parser.add_argument('--csv', type=str, default='scripts/computation_times_analysis.csv')
    parser.add_argument('--outdir', type=str, default='scripts/images')
    parser.add_argument('--topk', type=int, default=10)
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    outdir = Path(args.outdir)
    ensure_outdir(outdir)

    data = read_results(csv_path)
    if not data:
        raise SystemExit("No data found in CSV")

    # Histogram of means
    plot_histogram(data, 'mean', outdir / 'histogram_mean.png', title='Distribuzione dei tempi medi per confronto')

    # Histogram of max
    plot_histogram(data, 'max', outdir / 'histogram_max.png', title='Distribuzione dei tempi massimo per confronto')

    # Top-K slowest
    plot_topk_bar(data, 'mean', outdir / f'top{args.topk}_slowest.png', k=args.topk, title=f'Top {args.topk} concetti più lenti (mean)')

    # mean vs max scatter
    plot_scatter_mean_max(data, outdir / 'mean_vs_max.png', title='Mean vs Max per concetto')

    print(f"Saved images to {outdir}")

if __name__ == '__main__':
    main()

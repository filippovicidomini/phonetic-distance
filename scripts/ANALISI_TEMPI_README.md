# Analisi dei Tempi di Calcolo della Similarità Fonologica

Questo script analizza i tempi di calcolo della similarità **tra le features (varianti fonetiche) di un concetto** su tutte le città.

## Overview

- **Input**: CSV `ALM123.csv` con 165 città × 369 concetti
- **Processo**: Per ogni concetto, calcola i tempi di similarità per i 165×165 confronti di features (triangolo superiore)
- **Output**: CSV con statistiche dettagliate + file di riepilogo

## Structure

```
Per ogni concetto:
  165 città → 165 features
  Confronti: 165 × 164 / 2 = 13,530 confronti (approx)
  Tempo per confronto: ~0.0001s - 0.0005s
```

## Utilizzo

### 1. Script Principale: `analyze_computation_times.py`

**Test rapido (10 concetti)**:
```bash
python scripts/analyze_computation_times.py --concepts 10
```

**Analisi completa (369 concetti)**:
```bash
python scripts/analyze_computation_times.py
```

**Con opzioni personalizzate**:
```bash
python scripts/analyze_computation_times.py \
  --concepts 100 \
  --output results/my_analysis.csv \
  --save-every 25 \
  --start 0
```

### 2. Script Helper: `run_analysis.py` (Preset predefiniti)

**Test rapido**:
```bash
python scripts/run_analysis.py test
```

**Analisi piccola (100 concetti)**:
```bash
python scripts/run_analysis.py small
```

**Analisi media (200 concetti)**:
```bash
python scripts/run_analysis.py medium
```

**Analisi completa (369 concetti)**:
```bash
python scripts/run_analysis.py full
```

**Personalizzata**:
```bash
python scripts/run_analysis.py custom --concepts 50 --start 10
```

## Parametri

- `--csv PATH`: Path al file CSV (default: `scripts/ALM123.csv`)
- `--output PATH`: Path file output CSV (default: `scripts/computation_times_analysis.csv`)
- `--concepts N`: Numero di concetti da analizzare (default: tutti 369)
- `--start N`: Indice iniziale (default: 0)
- `--save-every N`: Salva ogni N concetti (default: 50)
- `--verbose`: Output più dettagliato

## Output

### File CSV: `computation_times_analysis.csv`

Colonne:
- `concept_idx`: Indice concetto (0-368)
- `concept_name`: Nome concetto (es. "il mare")
- `status`: 'ok' o 'error'
- `count`: Numero di confronti effettuati
- `mean`: Tempo medio per confronto (secondi)
- `median`: Mediana tempi
- `std`: Deviazione standard
- `min`, `max`: Temps min/max
- `p25`, `p75`, `p95`: Percentili
- `total_time`: Tempo totale per il concetto

### File Testo: `computation_times_summary.txt`

Riepilogo con:
- Numero concetti elaborati
- Tempo totale di esecuzione
- Statistiche sui tempi medi tra concetti
- Numero totale confrotni
- Velocità media (confronti/sec)

## Esempio di Risultati

```
STATISTICHE SUI TEMPI MEDI:
  - Media: 0.00025268s
  - Mediana: 0.00027676s
  - Dev.Std: 0.00007771s
  - Min: 0.00007799s
  - Max: 0.00034687s

CONFRONTI TOTALI: 123,130
Velocità media: 3,999 confronti/sec
```

## Note di Performance

- Per 10 concetti: ~30 secondi
- Per 100 concetti: ~200 secondi (~3 min)
- Per 369 concetti: ~800 secondi (~13 min)
- Memoria: ~50-100 MB

## Interruzione Sicura

Lo script salva periodicamente (ogni 50 concetti di default), quindi puoi interrompere con `Ctrl+C` senza perdere i dati.

```bash
# Continua da indice 100
python scripts/analyze_computation_times.py --start 100 --concepts 269
```

## Analisi dei Dati

I risultati CSV possono essere analizzati con:

```python
import pandas as pd

df = pd.read_csv('scripts/computation_times_analysis.csv')

# Concetti più lenti
print(df.nlargest(10, 'mean')[['concept_name', 'mean', 'max']])

# Statistiche generali
print(df[['count', 'mean', 'std', 'max']].describe())
```

## Troubleshooting

**Errore: "file not found"**
- Assicurati che `ALM123.csv` sia in `scripts/`

**Errore: "ImportError: phonetic_distance"**
- Esegui lo script da `/phonetic distance` directory (root del progetto)

**Script troppo lento?**
- Usa `--concepts N` per limitare il numero di concetti
- Usa `--start N` per riprendere da un punto precedente

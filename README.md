# Phonetic Distance

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/phonetic-distance.svg)](https://pypi.org/project/phonetic-distance/)
$10^4$
**Una libreria Python avanzata per il calcolo di distanze fonetiche pesate, specificamente progettata per l'analisi di forme dialettali e variazioni linguistiche.**

## 📖 Panoramica

Questo progetto implementa una versione avanzata dell'algoritmo di distanza di Levenshtein che tiene conto delle caratteristiche fonologiche dei suoni. A differenza delle distanze tradizionali basate sui caratteri, questa libreria:

- **Analizza le caratteristiche fonetiche** (vocale/consonante, modo, luogo di articolazione, ecc.)
- **Gestisce i diacritici** con tokenizzazione Unicode NFD
- **Supporta varianti multiple** separate da `/` in una singola cella
- **Fornisce similarità normalizzate** tra 0 e 1
- **È ottimizzata per forme dialettali** e trascrizioni fonetiche

### 🎯 Caso d'uso tipico
Quando si confrontano forme dialettali come `"gatto"` vs `"gàtto"`, una distanza di Levenshtein tradizionale le considererebbe molto diverse. Questa libreria riconosce che la differenza è solo un accento e assegna una similarità molto alta (0.98).

## Indice

- [Panoramica](#panoramica)
- [Installazione rapida](#installazione-rapida)
- [API Reference](#api-reference)
- [Esempi pratici](#esempi-pratici)
- [Struttura del progetto](#struttura-del-progetto)
- [Come funziona](#come-funziona)
- [Simboli conosciuti e interpretazione](#simboli-conosciuti-e-interpretazione)
- [Sistema di Pesi](#sistema-di-pesi)
- [Test](#test)
- [Analisi dei Tempi di Calcolo](#analisi-dei-tempi-di-calcolo)
- [Complessità Computazionale](#complessit%C3%A0-computazionale)
- [Estendere la libreria](#estendere-la-libreria)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

## 🚀 Installazione rapida

Questo progetto è pubblicato su PyPI e funziona con Python 3.8+.

Installazione rapida da PyPI:

```bash
pip install phonetic-distance
```

Test rapido dopo l'installazione:

```bash
python3 -c "from phonetic_distance import phon_similarity_normalized; print(phon_similarity_normalized('gatto','gàtto'))"
# Output: 0.98
```

Oppure, per installare dalla sorgente:

```bash
git clone https://github.com/filippovicidomini/phonetic-distance.git
cd phonetic-distance
pip install .
```
 

## 📚 API Reference

### Funzioni principali

#### `tokenize_segments(text: str) -> list[TokenType]`
Converte una stringa in token fonetici usando normalizzazione NFD.

```python
from phonetic_distance import tokenize_segments

# Separa base e diacritici
tokens = tokenize_segments('gàtto')
print(tokens)
# [('g', frozenset()), ('a', frozenset({'̀'})), ('t', frozenset()), ('t', frozenset()), ('o', frozenset())]
```

#### `weighted_levenshtein(seq1, seq2, diac_w=0.1) -> float`
Calcola la distanza di Levenshtein pesata tra due sequenze di token.

```python
from phonetic_distance import weighted_levenshtein, tokenize_segments

tokens1 = tokenize_segments('casa')
tokens2 = tokenize_segments('kasa')
distance = weighted_levenshtein(tokens1, tokens2)
print(f"Distanza: {distance}")
```

#### `phon_similarity_normalized(form1: str, form2: str, **kwargs) -> float`
Calcola la similarità fonologica normalizzata (0-1) tra due forme.

```python
from phonetic_distance import phon_similarity_normalized

# Confronto con diacritico
sim1 = phon_similarity_normalized('gatto', 'gàtto')
print(f"gatto vs gàtto: {sim1}")  # 0.98

# Confronto foneticamente simile
sim2 = phon_similarity_normalized('casa', 'kasa') 
print(f"casa vs kasa: {sim2}")   # Alta similarità

# Confronto molto diverso
sim3 = phon_similarity_normalized('gatto', 'mare')
print(f"gatto vs mare: {sim3}")  # Bassa similarità
```

#### `concept_similarity_normalized(cell_a: str, cell_b: str, **kwargs) -> float`
Gestisce celle con varianti multiple separate da `/` e restituisce la massima similarità.

```python
from phonetic_distance import concept_similarity_normalized

# Varianti multiple
cell1 = "pane/pàn"
cell2 = "pan/pané" 
sim = concept_similarity_normalized(cell1, cell2)
print(f"Similarità concettuale: {sim}")
```

### Parametri opzionali

- `keep_boundaries=False`: Include token di confine parola
- `diac_w=0.1`: Peso per differenze diacritiche (0.0-1.0)

## 💡 Esempi pratici

### Esempio base: confronto dialettale

```python
from phonetic_distance import phon_similarity_normalized

# Esempi di varianti dialettali italiane
varianti = [
    ('casa', 'kasa'),      # c/k
    ('chiesa', 'chjesa'),  # ie/je  
    ('gatto', 'gàtto'),    # accento
    ('bello', 'bellu'),    # o/u finale
]

for v1, v2 in varianti:
    sim = phon_similarity_normalized(v1, v2)
    print(f"{v1:8} vs {v2:8} → {sim:.3f}")
```

### Esempio avanzato: gestione varianti multiple

```python
from phonetic_distance import concept_similarity_normalized

# Celle con più varianti (tipico nei database dialettali)
esempi = [
    ("pane/pàn", "pan"),
    ("chiesa/chjesa", "chiesa"),  
    ("casa/kasa", "casa"),
    ("bello/bellu/beddu", "bello")
]

for cella1, cella2 in esempi:
    sim = concept_similarity_normalized(cella1, cella2)
    print(f"{cella1:15} vs {cella2:8} → {sim:.3f}")
```

### Esempio: analisi corpus dialettale

```python
from phonetic_distance import concept_similarity_normalized

def trova_varianti_simili(forme, soglia=0.8):
    """Trova coppie di forme con alta similarità."""
    risultati = []
    
    for i, forma1 in enumerate(forme):
        for forma2 in forme[i+1:]:
            sim = concept_similarity_normalized(forma1, forma2)
            if sim >= soglia:
                risultati.append((forma1, forma2, sim))
    
    return sorted(risultati, key=lambda x: x[2], reverse=True)

# Esempio con forme dialettali
corpus = [
    "casa", "kasa", "koza", 
    "gatto", "gàtto", "gattu",
    "chiesa", "chjesa", "ghiesa"
]

varianti = trova_varianti_simili(corpus, soglia=0.85)
for v1, v2, sim in varianti:
    print(f"{v1} ≈ {v2} ({sim:.3f})")
```

## 🏗️ Struttura del progetto

```
phonetic-distance/
├── phonetic_distance/          # Package principale
│   ├── __init__.py            # Esporta API pubblica
│   └── core.py                # Implementazione algoritmi
├── examples/
│   └── usage.py               # Esempi di utilizzo
├── tests/                     # Test suite
│   ├── conftest.py           
│   └── test_similarity.py     
├── data/
│   └── dictionary.txt         # Dizionario forme
├── scripts/
│   └── update_dictionary.py   # Gestione dizionario
├── wd.py                      # Compatibilità legacy
├── pyproject.toml            # Configurazione package
├── requirements.txt          # Dipendenze (vuoto)
└── README.md                 # Questa documentazione
```

## 🔬 Come funziona

### 1. Tokenizzazione NFD
Le stringhe sono normalizzate in NFD (Normalized Form Decomposed), separando caratteri base da diacritici:

```python
"gàtto" → [('g',∅), ('a',{̀}), ('t',∅), ('t',∅), ('o',∅)]
```

### 2. Costi basati su feature
I costi di sostituzione considerano caratteristiche fonetiche:
- **Vocali**: apertura, anteriorità, arrotondamento
- **Consonanti**: luogo, modo, voce

### 3. Gestione diacritici
Differenze diacritiche hanno penalità ridotte (default 0.1).

### 4. Normalizzazione
La distanza viene normalizzata per la lunghezza massima delle sequenze.

## 🧾 Simboli conosciuti e interpretazione

La libreria riconosce una serie di simboli base e multi-carattere definiti in `phonetic_distance/core.py`.

- Multi-basi (riconoscimento greedy, in NFD): `g’`, `k’`, `hʼ`, `lʼ`, `nʼ`, `r̥`, `r̄`, `r̃`, `ṙ`.

- Vocali (ogni vocale ha attributi `height` / `back` / `round`):

| Simbolo | Altezza | Anteriorità | Arrotondamento |
|--------:|:--------|:------------:|:---------------:|
| a      | open    | central     | 0               |
| e      | mid     | front       | 0               |
| ë      | mid     | central     | 0               |
| i      | close   | front       | 0               |
| o      | mid     | back        | 1               |
| u      | close   | back        | 1               |
| ö      | mid     | front       | 1               |
| ü      | close   | front       | 1               |

- Semivocali (trattate come consonanti approssimanti): `i̯` (palatal, `approx`, voiced), `u̯` (velar, `approx`, voiced).

- Consonanti: ogni consonante è definita con `place`, `manner` e `voice`. Alcuni esempi:

| Simbolo | Luogo       | Modo     | Voce |
|--------:|:-----------:|:--------:|:----:|
| p      | bilabial    | stop     | 0    |
| b      | bilabial    | stop     | 1    |
| t      | dental      | stop     | 0    |
| d      | dental      | stop     | 1    |
| k      | velar       | stop     | 0    |
| g      | velar       | stop     | 1    |
| s      | alveolar    | sibilant | 0    |
| ʒ      | alveolar    | affric   | 1    |
| m      | bilabial    | nasal    | 1    |
| n      | alveolar    | nasal    | 1    |
| l      | alveolar    | lateral  | 1    |
| r      | alveolar    | trill    | 1    |

- Fallback per simboli sconosciuti: se un simbolo non è presente in `BASE_FEATS`, viene classificato come vocale se è presente in `_VOWEL_BASES` (`a,e,i,o,u,ë,ö,ü`), altrimenti come consonante. Le sostituzioni che coinvolgono simboli sconosciuti applicano costi moderati (vedi sezione "⚖️ Sistema di Pesi").

Per la lista completa dei simboli e dei relativi attributi, consulta `phonetic_distance/core.py` negli oggetti `BASE_FEATS` e `MULTI_BASES`.

## ⚖️ Sistema di Pesi

La libreria utilizza un sistema di pesi calibrati per riflettere la vicinanza fonologica tra suoni. Di seguito i pesi applicati nei diversi casi:

### Pesi per Diacritici

| Parametro | Valore Default | Descrizione |
|-----------|----------------|-------------|
| `diac_w` | **0.1** | Peso per ogni diacritico diverso tra due token |

**Esempio**: `gatto` vs `gàtto` → differenza di 1 diacritico → penalità = 0.1

### Pesi per Inserimento/Cancellazione

| Tipo di Token | Parametro | Costo | Descrizione |
|---------------|-----------|-------|-------------|
| Vocale | `vowel_cost` | **1.0** | Inserimento o cancellazione di una vocale |
| Consonante | `cons_cost` | **1.1** | Inserimento o cancellazione di una consonante |
| Boundary | `boundary_cost` | **0.2** | Inserimento o cancellazione di un confine parola |

**Razionale**: Le consonanti hanno un costo leggermente superiore perché generalmente più distintive; i boundary hanno costo basso perché meno rilevanti foneticamente.

### Pesi per Sostituzione delle Basi

#### Sostituzioni Speciali

| Caso | Costo | Descrizione |
|------|-------|-------------|
| Base identica | **0.0** | Nessuna sostituzione |
| Vocale ↔ Consonante | **1.3** | Cambio di categoria fonologica |
| Simboli sconosciuti (stesso tipo) | **0.9** | Entrambi vocali o entrambi consonanti |
| Simboli sconosciuti (tipo diverso) | **1.3** | Uno vocale, uno consonante |
| Boundary ↔ Boundary | **0.0** | Confini identici |
| Boundary ↔ Altro | **0.2** | Sostituzione confine con altro |

#### Sostituzioni tra Vocali

Il costo si calcola sommando le differenze di caratteristiche:

| Caratteristica | Differenza | Penalità |
|----------------|------------|----------|
| **Altezza** (apertura) | Diversa | **+0.4** |
| **Anteriorità** (back/front) | Diversa | **+0.4** |
| **Arrotondamento** | Diverso | **+0.2** |

**Range totale**: 0.2 - 1.2 (con limite min/max applicato)

**Esempio**:
- `a` → `e`: differente in altezza (+0.4) e anteriorità (+0.4) = **0.8**
- `o` → `u`: differente solo in altezza (+0.4) = **0.4**
- `i` → `ü`: differente solo in arrotondamento (+0.2) = **0.2**

#### Sostituzioni tra Consonanti

Il costo si calcola sommando le differenze di caratteristiche:

| Caratteristica | Differenza | Penalità |
|----------------|------------|----------|
| **Voce** (voiced/unvoiced) | Diversa | **+0.2** |
| **Luogo** di articolazione | Diverso | **+0.4** |
| **Modo** di articolazione | Diverso | **+0.6** |

**Range totale**: 0.2 - 1.2 (con limite min/max applicato)

**Esempio**:
- `p` → `b`: solo voce differente (+0.2) = **0.2**
- `t` → `k`: solo luogo differente (+0.4) = **0.4**
- `p` → `s`: luogo (+0.4) e modo (+0.6) differenti = **1.0**
- `t` → `d`: solo voce differente (+0.2) = **0.2**

### Personalizzazione dei Pesi

Tutti i pesi possono essere personalizzati nelle funzioni:

```python
from phonetic_distance import weighted_levenshtein, tokenize_segments

tokens1 = tokenize_segments('casa')
tokens2 = tokenize_segments('kasa')

# Pesi personalizzati
distanza = weighted_levenshtein(
    tokens1, 
    tokens2,
    diac_w=0.2,          # Diacritici più pesanti
    vowel_cost=0.8,      # Vocali meno costose
    cons_cost=1.2,       # Consonanti più costose
    boundary_cost=0.1    # Boundary ancora meno rilevanti
)
```

### Matrice di Similarità: Esempi Pratici

| Confronto | Differenza | Distanza | Similarità |
|-----------|------------|----------|------------|
| `gatto` vs `gatto` | Identici | 0.0 | 1.00 |
| `gatto` vs `gàtto` | 1 diacritico | 0.1 | 0.98 |
| `casa` vs `kasa` | c→k (luogo) | ~0.4 | ~0.90 |
| `pane` vs `pani` | e→i (altezza+back) | ~0.8 | ~0.80 |
| `gatto` vs `mare` | Molto diversi | >3.0 | <0.40 |

## 🧪 Test

Esegui i test per verificare l'installazione:

```bash
cd phonetic-distance
python -m pytest tests/ -v
```

Oppure test rapido:

```bash
python examples/usage.py
```

## ⏱️ Analisi dei Tempi di Calcolo

Questo progetto include strumenti dedicati per misurare e analizzare i tempi di calcolo della similarità fonologica, specialmente utili per benchmark su dataset dialettali come ALM123.

### Strumenti disponibili

#### 1. **Script Principale**: `scripts/analyze_computation_times.py`

Analizza i tempi di similarità tra le features di ciascun concetto (165 città → 165 features per concetto).

**Utilizzo rapido**:
```bash
# Test con 10 concetti (~30 secondi)
python scripts/analyze_computation_times.py --concepts 10

# Analisi completa su 369 concetti (~13 minuti)
python scripts/analyze_computation_times.py

# Con opzioni personalizzate
python scripts/analyze_computation_times.py \
  --concepts 100 \
  --output results/custom_analysis.csv \
  --save-every 25
```

**Parametri**:
- `--csv PATH`: File CSV input (default: `scripts/ALM123.csv`)
- `--output PATH`: File CSV output (default: `scripts/computation_times_analysis.csv`)
- `--concepts N`: Numero di concetti (default: tutti 369)
- `--start N`: Indice iniziale (default: 0)
- `--save-every N`: Salva ogni N concetti (default: 50)

#### 2. **Script Helper**: `scripts/run_analysis.py`

Fornisce preset predefiniti per facilitare l'esecuzione:

```bash
python scripts/run_analysis.py test      # 10 concetti
python scripts/run_analysis.py small     # 100 concetti
python scripts/run_analysis.py medium    # 200 concetti
python scripts/run_analysis.py full      # 369 concetti (completo)

# Personalizzato
python scripts/run_analysis.py custom --concepts 50 --start 100
```

### Output generato

Lo script genera due file:

1. **`computation_times_analysis.csv`** — Dati dettagliati per ogni concetto:
   - Indice e nome concetto
   - Numero di confronti effettuati
   - Statistiche: media, mediana, min/max, percentili (p25, p75, p95)
   - Deviazione standard e tempo totale

2. **`computation_times_summary.txt`** — Riepilogo esecutivo con:
   - Numero di concetti elaborati
   - Tempo totale di esecuzione
   - Statistiche aggregate sui tempi medi
   - Velocità media (confronti/sec)

### Risultati tipici

**Esempio con 10 concetti**:
```
Concetti elaborati: 10
Tempo totale: 30.79 secondi

STATISTICHE:
  - Velocità media: 3,999 confronti/sec
  - Confronti totali: 123,130
  
Tempi medi per concetto:
  - Media: 0.000253s per confronto
  - Min: 0.000078s (il mare)
  - Max: 0.000347s (fuori c'è mare)
  
Percentili:
  - P25: 0.000209s
  - P75: 0.000313s
  - P95: 0.000337s
```

**Analisi per concetto**:
```
il mare                 | 13,366 confronti | 0.000078s media
l'alto mare             | 12,720 confronti | 0.000185s media
il mare calmo           | 13,366 confronti | 0.000262s media
il mare agitato, grosso | 12,720 confronti | 0.000319s media
```

### Note sulla performance

- **Per concetto**: ~13,500 confronti $(165×164)/2$
- **Tempo/confronto**: 0.0001s - 0.0005s a seconda della lunghezza
- **Salvataggio periodico**: Ogni 50 concetti (configurabile) — puoi interrompere con `Ctrl+C` senza perdere dati
- **Ripresa**: Usa `--start N` per continuare da un indice precedente

### 📊 Grafici e Visualizzazione 

I dati CSV generati sono pronti per essere visualizzati. Le versioni future includeranno:
- Grafici dei tempi per concetto
- Distribuzione dei tempi di calcolo
- Analisi della velocità
- Confronti di performance tra dataset

Nel frattempo, puoi analizzare i dati con Python:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('scripts/computation_times_analysis.csv')

# Concetti più lenti
print(df.nlargest(10, 'mean')[['concept_name', 'mean', 'max']])

# Distribuzione dei tempi
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
df['mean'].hist(bins=30, ax=axes[0], title='Distribuzione Tempi Medi')
df['max'].hist(bins=30, ax=axes[1], title='Distribuzione Tempi Max')
plt.tight_layout()
plt.savefig('timing_analysis.png', dpi=150)
```

## 🛠️ Estendere la libreria

### Aggiungere nuove basi fonetiche

Modifica `BASE_FEATS` in [`phonetic_distance/core.py`](phonetic_distance/core.py):

```python
BASE_FEATS = {
    'a': {'vowel', 'open', 'central'},
    'e': {'vowel', 'mid', 'front'},
    # Aggiungi qui nuove basi...
}
```

### Gestire dizionario

Usa lo script per aggiornare il dizionario:

```bash
python scripts/update_dictionary.py --add "nuova_forma"
```

## ⚖️ Complessità Computazionale

Di seguito una versione rivista e più precisa della complessità, con esempi numerici riferiti al dataset ALM usato negli script.

- Notazione
    - n: lunghezza in caratteri di una stringa
    - t: numero di token prodotti da `tokenize_segments` (t ≤ n)
    - L: lunghezza tipica in token di una variante (valore medio)
    - A, B: numero di varianti in due celle (per `concept_similarity_normalized`)
    - C: numero di città (feature per concetto)
    - K: numero di concetti

- Tokenizzazione (`tokenize_segments`)
    - Tempo: O(n) (scorre la stringa una sola volta; match multibase con lista di dimensione costante)
    - Spazio: O(t)
    - Nota: `normalize_nfd` è cached (`lru_cache`) — conviene pre-tokenizzare varianti ripetute.

- Operazioni elementari
    - `base_cost`, `diac_cost`, `ins_del_cost`, `sub_cost` sono O(1) (lookup + poche operazioni aritmetiche).

- Weighted Levenshtein (DP)
    - Tempo per coppia: O(t_a * t_b) dove t_a, t_b sono i token delle due forme confrontate.
    - Spazio: O(min(t_a, t_b)) nella nostra implementazione che mantiene solo due righe DP.
    - Ottimizzazioni pratiche: early‑abandon (soglia), banded DP (se le sequenze sono simili), caching dei token.

- `phon_similarity_normalized`
    - Esegue tokenizzazione + DP → complessità dominata da O(t_a * t_b).

- `concept_similarity_normalized`
    - Con A varianti in `cell_a` e B in `cell_b` il costo è
        O(sum_{i=1..A} sum_{j=1..B} t_{a,i} * t_{b,j}) più il costo di tokenizzazione.
    - Se si assume una lunghezza tipica L per variante, il costo è approssimabile con O(A * B * L^2).
    - Riduzione pratica: pre-tokenizzare tutte le varianti (una tantum) riduce l'overhead di tokenizzazione; il costo rimane il numero di coppie A×B moltiplicato dal costo DP per coppia.

- Confronti su intero corpus
    - Confronti pairwise naïf su M elementi: O(M^2 * L^2). Per dataset grandi ciò diventa proibitivo.
    - Nel caso specifico degli script che confrontano le feature per concetto (approccio usato qui):
        - Per concetto si confrontano le C città tra loro: numero di confronti per concetto = C * (C - 1) / 2.
        - Complessivamente, con K concetti: totale confronti ≈ K * C * (C - 1) / 2.
        - Esempio numerico (dataset ALM usato negli script): C ≈ 164–165, K = 369 →
            - Per concetto ≈ 13.3k confronti (es. 164→13,366 ; 165→13,530)
            - Su tutti i concetti ≈ 4.9M–5.0M confronti (≈ 4,992,570 usando C=165,K=369)
        - Questo numero di confronti è ragionevole da processare in pochi minuti su hardware moderno se il tempo per confronto è nell'ordine dei 10^-4–10^-3 s (come mostrato dai benchmark locali).

- Stime temporali e suggerimenti pratici
    - Se il tempo medio per confronto è ~0.0002–0.0003 s, allora 5M confronti richiedono ~1,000–1,500 s (≈ 16–25 minuti). La variabilità dipende dalla lunghezza media delle varianti e dall'overhead di tokenizzazione.
    - Consigli per velocizzare:
        - Pre-tokenizzare tutte le varianti e riutilizzare i token (cache in memoria o su disco).
        - Parallelizzare per concetto (i concetti sono indipendenti: embarrassingly parallel).
        - Applicare filtri rapidi (lunghezza, n‑gram overlap) prima di eseguire DP.
        - Usare banded DP o early‑abandon quando possibile.
        - Se serve maggior velocità, implementare il nucleo `weighted_levenshtein` in C/Cython/Numba.

- Riepilogo (complessità principali)
    - Tokenizzazione: O(n) tempo, O(t) spazio
    - Weighted Levenshtein (per coppia): O(t_a * t_b) tempo, O(min(t_a, t_b)) spazio
    - `phon_similarity_normalized`: O(t_a * t_b)
    - `concept_similarity_normalized`: O(A * B * L^2) (più costo di tokenizzazione; riducibile con caching)

Questa versione della sezione sostituisce la precedente con numeri e formule rivisti e un esempio numerico concreto per il dataset ALM.


**Glossario (acronimi e termini usati)**

- **DP**: "dynamic programming" — tecnica che risolve problemi suddividendoli in sottoproblemi sovrapposti e riutilizzando i risultati (memoizzazione). Nel Levenshtein pesato si usa una matrice D con ricorrenza
    D[i,j] = min(D[i-1,j] + costo_delete,
                             D[i,j-1] + costo_insert,
                             D[i-1,j-1] + costo_substitution).
    L'implementazione del pacchetto mantiene solo due righe (`prev`, `cur`) per ridurre l'uso di memoria.

- **LRU (least recently used)**: strategia di caching che elimina l'elemento meno recentemente usato. Python fornisce `functools.lru_cache` per memoizzare funzioni (es. `normalize_nfd`).

- **NFD (Normalization Form Decomposed)**: forma Unicode che scompone caratteri composti in base + segni diacritici; utile per tokenizzare e confrontare diacritici separatamente.

- **O(...) (Big‑O)**: notazione asintotica che descrive la crescita del tempo o spazio in funzione della dimensione dell'input (es. O(n), O(n*m)).

- **LSH (locality‑sensitive hashing)**: tecnica per indicizzare vettori o insiemi in modo che elementi simili abbiano elevata probabilità di collisione; utile per ridurre i candidati prima del confronto costoso.

- **ANN (approximate nearest neighbors)**: metodi per trovare vicini approssimati in grandi insiemi più velocemente del confronto esaustivo (es. usando LSH, HNSW).

- **BK‑tree (Burkhard–Keller tree)**: struttura dati per metriche discrete (come distanza edit) che permette di cercare elementi entro una certa distanza in modo efficiente.

- **MinHash**: algoritmo per stimare la similarità di Jaccard tra insiemi (es. n‑gram); usato con LSH per recupero approssimato di coppie simili.

- **API**: application programming interface — insieme di funzioni/esportazioni che il pacchetto fornisce (`tokenize_segments`, `weighted_levenshtein`, `phon_similarity_normalized`, ...).

- **Early‑abandon**: strategia per interrompere precocemente la DP su una coppia se il costo corrente supera una soglia stabilita (utile quando interessano solo coppie con similarità ≥ soglia).

- **Banded DP**: limitare la DP a una banda di ampiezza k intorno alla diagonale quando si presume che le sequenze siano simili; riduce complessità a O(k * L).



## 📋 Requisiti

- **Python**: 3.8 o superiore
- **Dipendenze**: Nessuna (solo libreria standard)
- **Sistema**: Qualsiasi OS (Windows, macOS, Linux)

## 🤝 Contribuire

1. **Segnala problemi** via [GitHub Issues](https://github.com/filippovicidomini/phonetic-distance/issues)
2. **Proponi miglioramenti** con le Pull Request
3. **Aggiungi nuove feature fonetiche** seguendo il formato esistente
4. **Migliora la documentazione** e gli esempi

### Compatibilità legacy

Il modulo `wd.py` mantiene compatibilità con codice precedente:

```python
import wd  # Deprecation warning ma funziona
# Equivalente a: import phonetic_distance
```

## 📄 Licenza

Questo progetto è rilasciato sotto [licenza MIT](LICENSE). Libero per uso commerciale e non commerciale.

## 🚀 Versioni future

- [ ] Supporto per feature prosodiche (tono, stress)
- [ ] Algoritmi di clustering foneticamente consapevoli  
- [ ] Export in formati standard (JSON, CSV)
- [ ] Interfaccia web per confronti rapidi
- [ ] Modelli pre-addestrati per lingue specifiche

---

**Autore**: Filippo Vicidomini  
**Versione**: 0.1.0  
**Homepage**: https://github.com/filippovicidomini/phonetic-distance

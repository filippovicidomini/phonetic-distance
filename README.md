phonetic-distance
=================

Libreria Python per una distanza di Levenshtein fonologica pesata, pensata per forme dialettali.

Questa repository contiene una versione avanzata della distanza di Levenshtein (file `phonetic_distance.py`, wrapper di `weighted_distance.py`) che tiene conto di caratteristiche fonologiche di basi e diacritici, tokenizza in NFD e fornisce similarità normalizzate per coppie di forme o per celle con varianti separate da `/`.

Caratteristiche principali
- Tokenizzazione Unicode NFD con gestione di basi multi-carattere e diacritici.
- Costi di sostituzione basati su feature (vocale/consonante, luogo, modo, voice, ecc.).
- Penalità leggere per differenze diacritiche.
- Funzioni pubbliche semplici: `tokenize_segments`, `weighted_levenshtein`, `phon_similarity_normalized`, `concept_similarity_normalized`.

Installazione
------------

Questo progetto non richiede dipendenze esterne: usa solo la libreria standard Python (3.8+). Clona la repo e usa direttamente `phonetic_distance.py`.

Esempio rapido:

```bash
git clone https://github.com/<tuo-utente>/phonetic-distance.git
cd phonetic-distance
python3 -c "from phonetic_distance import phon_similarity_normalized; print(phon_similarity_normalized('k a','kâ'))"
```

Esempio d'uso
------------
Vedi `examples/usage.py` per un esempio minimo di utilizzo.

Estendere il dizionario
-----------------------
- La cartella `data/` contiene `dictionary.txt`, un semplice elenco line-by-line di forme/varianti.
- Lo script `scripts/update_dictionary.py` fornisce una CLI minima per aggiungere forme normalizzate al dizionario evitando duplicati.
- In futuro `dictionary.txt` può essere sostituito da CSV/TSV o database leggero; gli script sono progettati per essere facilmente adattabili.

Contribuire
----------
- Segnala bug o richieste via Issues. Per aggiungere nuove basi fonetiche, modifica `BASE_FEATS` in `weighted_distance.py` (implementazione) e aggiorna `MULTI_BASES` (in forma NFD).

Licenza
-------
MIT (file `LICENSE`).

"""Esempio minimo d'uso per `wd.py`.

Esegue qualche confronto e stampa valori di similarità.
"""
from phonetic_distance import phon_similarity_normalized, concept_similarity_normalized, tokenize_segments

def demo():
    a = "gatto"
    b = "gàtto"
    print("Token A:", tokenize_segments(a))
    print("Token B:", tokenize_segments(b))
    print("Similarità fonologica (normalizzata):", phon_similarity_normalized(a, b))

    cell1 = "pane/pàn"
    cell2 = "pan"
    print("Similarità concettuale max tra celle:", concept_similarity_normalized(cell1, cell2))

if __name__ == '__main__':
    demo()

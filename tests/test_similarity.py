import math
from phonetic_distance import phon_similarity_normalized, concept_similarity_normalized

def test_similarity_same():
    assert phon_similarity_normalized('a', 'a') == 1.0

def test_similarity_variants():
    s = concept_similarity_normalized('pane/pàn', 'pane')
    assert not math.isnan(s)
    assert 0.0 <= s <= 1.0

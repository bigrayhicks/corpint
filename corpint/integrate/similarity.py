import fingerprints
from normality import collapse_spaces
from Levenshtein import jaro_winkler


def chomp(name):
    name = name.upper()
    name = name.replace('.', ' ')
    name = collapse_spaces(name)
    return name


def entity_similarity(left, right):
    left_name = left.get('name')
    right_name = right.get('name')
    score = 0
    if left_name is not None and right_name is not None:
        name_sim = jaro_winkler(chomp(left_name), chomp(right_name))
        score += (name_sim * 0.6)

    left_fp = fingerprints.generate(left_name)
    right_fp = fingerprints.generate(right_name)
    if left_fp is not None and right_fp is not None:
        fp_sim = jaro_winkler(left_fp, right_fp)
        score += (fp_sim * 0.4)

    return min(1.0, score)

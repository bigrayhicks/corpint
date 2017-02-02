

COMPANY = 'Company'
ORGANIZATION = 'Organization'
PERSON = 'Person'
OTHER = None

TYPES = [COMPANY, ORGANIZATION, PERSON, OTHER]

# for entity merging:
WEIGHTS = {
    PERSON: 4,
    COMPANY: 3,
    ORGANIZATION: 2,
    OTHER: 0
}


def choose_best_type(types):
    """Given a list of types, choose the most specific one."""
    best_type, best_score = None, 0
    for value in types:
        if WEIGHTS.get(value) > best_score:
            best_type = value
            best_score = WEIGHTS.get(value)
    return best_type

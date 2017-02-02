from corpint.util import get_extensions


def get_enrichers():
    return get_extensions('corpint.enrich')

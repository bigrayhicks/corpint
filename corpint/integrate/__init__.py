from corpint.integrate.merge import merge_entity, merge_links  # noqa
from corpint.integrate.dupe import create_deduper, train_dedupe, train_judgement  # noqa
from corpint.integrate.dupe import canonicalise


def merge_entities(project):
    for row in project.entities.distinct('uid_canonical'):
        yield merge_entity(project, row.get('uid_canonical'))


def integrate(project):
    canonicalise(project)

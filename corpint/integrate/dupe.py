import fingerprints
from normality import ascii_text
from sqlalchemy import Unicode
import dedupe

from corpint.integrate.util import get_judged, merkle
from corpint.util import ensure_column


VARIABLES = [
    {'field': 'uid', 'type': 'Exists', 'has missing': False},
    {'field': 'name', 'type': 'String', 'has missing': False},
    {'field': 'type', 'type': 'Exact', 'has missing': True},
    {'field': 'fingerprint', 'type': 'String', 'has missing': True},
    {'field': 'origin', 'type': 'Exact', 'has missing': False},
    {'field': 'dob', 'type': 'String', 'has missing': True},
    {'field': 'incorporation_date', 'type': 'String', 'has missing': True},
    {'field': 'country', 'type': 'Exact', 'has missing': True},
    {'field': 'address', 'type': 'Address', 'has missing': True},
]


def strconv(text):
    if text is None or not len(text.strip()):
        return
    return ascii_text(text)


def to_record(entity):
    fp = fingerprints.generate(entity.get('name'))
    return {
        'uid': entity.get('uid'),
        'name': strconv(entity.get('name')),
        'type': entity.get('type'),
        'fingerprint': fp,
        'origin': entity.get('origin'),
        'dob': strconv(entity.get('dob')),
        'incorporation_date': strconv(entity.get('incorporation_date')),
        'country': entity.get('country'),
        'address': strconv(entity.get('address'))
    }


def get_trainset(project, judgement, data):
    trainset = []
    for (uida, uidb) in get_judged(project, judgement):
        enta = data.get(uida)
        entb = data.get(uidb)
        if enta is not None and entb is not None:
            trainset.append((enta, entb))
    return trainset


def create_deduper(project):
    deduper = dedupe.Dedupe(VARIABLES)
    data = {e['uid']: to_record(e) for e in project.entities}
    if len(data):
        deduper.sample(data)
        deduper.markPairs({
            'match': get_trainset(project, True, data),
            'distinct': get_trainset(project, False, data)
        })
    return deduper, data


def train_judgement(project, deduper, uida, uidb, judgement):
    if judgement is None:
        return
    enta = project.entities.find_one(uid=uida)
    entb = project.entities.find_one(uid=uidb)
    pair = (to_record(enta), to_record(entb))
    match, distinct = [], []
    if judgement:
        match.append(pair)
    else:
        distinct.append(pair)
    deduper.markPairs({'match': match, 'distinct': distinct})


def train_dedupe(deduper):
    try:
        deduper.train()
        return True
    except ValueError as ve:
        return False


def canonicalise(project):
    deduper, data = create_deduper(project)
    if not train_dedupe(deduper):
        return
    threshold = deduper.threshold(data, recall_weight=1)

    updates = (
        (project.entities, 'uid', 'uid_canonical'),
        (project.aliases, 'uid', 'uid_canonical'),
        (project.links, 'source', 'source_canonical'),
        (project.entities, 'target', 'target_canonical'),
    )

    for (table, src, dest) in updates:
        table.create_index([src])
        ensure_column(table, dest, Unicode)
        table.create_index([dest])
        project.db.query("UPDATE %s SET %s = %s;" % (table.table.name, dest, src))  # noqa

    for (uids, scores) in deduper.match(data, threshold):
        canon = merkle(uids)
        for (table, src, dest) in updates:
            query = "UPDATE %s SET %s = '%s' WHERE %s IN :uids"
            query = query % (table.table.name, dest, canon, src)
            project.db.query(query, uids=uids)


def run_dedupe(project):
    deduper, data = create_deduper(project)
    deduper.train()
    dedupe.consoleLabel(deduper)
    deduper.train()
    # TODO: lower the recall weight?
    threshold = deduper.threshold(data, recall_weight=1)
    clustered_dupes = deduper.match(data, threshold)
    print('# duplicate sets', len(clustered_dupes))

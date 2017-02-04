from collections import defaultdict
from itertools import combinations
from corpint.integrate.util import sorttuple, get_decided


def normalize_name(name):
    return name.upper().strip()


def name_merge(project, *origin_names):
    names = defaultdict(set)
    for origin_name in origin_names:
        for entity in project.entities.find(origin=origin_name):
            name = normalize_name(entity['name'])
            if name is None:
                continue
            names[name].add(entity['uid'])

    decided = get_decided(project)
    for name, uids in names.items():
        if len(uids) == 1:
            continue
        project.log.info('Merging %d instances: %s', len(uids), name)
        for (a, b) in combinations(uids, 2):
            if sorttuple(a, b) in decided:
                continue
            project.emit_judgement(a, b, True)

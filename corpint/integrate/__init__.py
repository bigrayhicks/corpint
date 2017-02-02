from corpint.integrate.similarity import entity_similarity
from corpint.integrate.util import sorttuple, merkle
from corpint.integrate.merge import merge_entity

# TODO: this code is a hacky mess. perhaps replace it with datamade's dedupe?


def get_judged(project, judgement):
    for mapping in project.mappings.find(judgement=judgement):
        yield sorttuple(mapping.get('left_uid'), mapping.get('right_uid'))


def get_same_as(project):
    clusters = []
    for (a, b) in get_judged(project, True):
        for cluster in clusters:
            if a in cluster or b in cluster:
                cluster.add(a)
                cluster.add(b)
                break
        else:
            clusters.append(set([a, b]))

    same_as = {}
    for cluster in clusters:
        for uid in cluster:
            same_as[uid] = cluster
    return same_as


def canonicalise(project):
    """Apply canonical UIDs based on same_as mappings."""
    same_as = get_same_as(project)
    for entity in project.entities:
        project.log.info("Canonicalising: %s", entity['name'])
        uid = entity.get('uid') or entity.get('uid_canonical')
        canonical = merkle(same_as.get(uid, [uid]))
        project.entities.update({
            'uid': uid,
            'uid_canonical': canonical
        }, ['uid'])
        project.aliases.update({
            'uid': uid,
            'uid_canonical': canonical
        }, ['uid'])
        project.links.update({
            'source': uid,
            'source_canonical': canonical
        }, ['source'])
        project.links.update({
            'target': uid,
            'target_canonical': canonical
        }, ['target'])


def merge(project):
    canonicalise(project)
    for row in project.entities.distinct('uid_canonical'):
        merge_entity(project, row.get('uid_canonical'))


def integrate(project, auto_match=False):
    judgements = {}
    for mapping in project.mappings:
        left, right = mapping.get('left_uid'), mapping.get('right_uid')
        judgements[(left, right)] = mapping['judgement']

    same_as = get_same_as(project)
    decided = set()
    for uid, sames in same_as.items():
        for ouid in sames:
            decided.add(sorttuple(uid, ouid))

    for (a, b) in get_judged(project, False):
        for left in same_as.get(a, set([a])):
            for right in same_as.get(b, set([b])):
                decided.add(sorttuple(left, right))

    project.log.info("%s decisions already made...", len(decided))

    # TODO: consider re-introducing alias matching.
    data = list(project.entities)
    scores = {}
    for left in data:
        project.log.info("Matching: %s", left['name'])
        left_uid = left['uid']
        if left_uid is None:
            continue

        for right in data:
            right_uid = right['uid']
            if right_uid is None:
                continue
            if left['origin'] == right['origin']:
                continue
            if left_uid <= right_uid:
                continue
            if sorttuple(left_uid, right_uid) in decided:
                continue
            score = entity_similarity(left, right)
            if score < 0.7:
                continue
            key = (left_uid, right_uid)
            if key in scores:
                score = max(scores[key], score)
            scores[key] = score
            mapping = {'score': score}
            if auto_match and score > 0.9999999999999:
                project.log.info("Automatch: %s", right['name'])
                mapping['judgement'] = True

            for obj, prefix in ((left, 'left_'), (right, 'right_')):
                for k, v in obj.items():
                    k = prefix + k
                    mapping[k] = v

            project.mappings.upsert(mapping, ['left_uid', 'right_uid'])

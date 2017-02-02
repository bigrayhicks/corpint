from corpint.integration.similarity import entity_similarity
from corpint.integration.util import sorttuple

# TODO: this code is a hacky mess. perhaps replace it with datamade's dedupe?


def get_judged(project, judgement):
    for mapping in project.mappings.find(judgement=judgement):
        yield sorttuple(mapping.get('left_uid'), mapping.get('right_uid'))


def get_same_as(project):
    clusters = []
    for (a, b) in get_judged(True):
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
    same_as = get_same_as(project)
    for entity in project.entities:
        project.log.info("Canonicalising: %s", entity['name'])
        uid = entity.get('uid') or entity.get('uid_canonical')
        canonical = max(same_as.get(uid, set([uid])))
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


def integrate(project):
    judgements = {}
    for mapping in project.mappings:
        left, right = mapping.get('left_uid'), mapping.get('right_uid')
        judgements[(left, right)] = mapping['judgement']

    same_as = get_same_as(project)
    decided = set()
    for uid, sames in same_as.items():
        for ouid in sames:
            decided.add(sorttuple(uid, ouid))

    for (a, b) in get_judged(False):
        for left in same_as.get(a, set([a])):
            for right in same_as.get(b, set([b])):
                decided.add(sorttuple(left, right))

    project.log.info("%s decisions already made...", len(decided))

    # TODO: consider re-introducing alias matching.
    data = list(project.entities)
    scores = {}
    for left in data:
        project.log.info("Matching: %s", left['name'])
        for right in data:
            right_uid = right['uid']
            if left['origin'] == right['origin']:
                continue
            if uid <= right_uid:
                continue
            if sorttuple(uid, right_uid) in decided:
                continue
            score = entity_similarity(left, right)
            if score < 0.7:
                continue
            key = (uid, right_uid)
            if key in scores:
                score = max(scores[key], score)
            scores[key] = score
            mapping = {'score': score}
            # if score > 0.9999999999999:
            #     mapping['judgement'] = True

            for obj, prefix in ((left, 'left_'), (right, 'right_')):
                for k, v in obj.items():
                    k = prefix + k
                    mapping[k] = v

            project.mappings.upsert(mapping, ['left_uid', 'right_uid'])

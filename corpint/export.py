from py2neo import Graph, Node, Relationship


def normalise(data):
    properties = {}
    for key, value in data.items():
        if isinstance(value, (set, tuple)):
            value = list(value)
        if value is None:
            continue
        properties[key] = value
    return properties


def load_to_neo4j(project, neo4j_url):
    graph = Graph(neo4j_url)

    tx = graph.begin()
    try:
        graph.run('MATCH (n) DETACH DELETE n')
        entities = {}
        for entity in project.iter_merged_entities():
            label = entity.pop('type') or 'Other'
            node = Node(label, **normalise(entity))
            tx.create(node)
            entities[entity['uid']] = node

        for link in project.iter_merged_links():
            source = entities.get(link.pop('source'))
            target = entities.get(link.pop('target'))
            rel = Relationship(source, 'LINK', target, **normalise(link))
            tx.create(rel)

        tx.commit()
    except Exception as ex:
        project.log.exception(ex)
        tx.rollback()

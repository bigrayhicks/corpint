from corpint.load.util import get_uid


class Origin(object):

    def __init__(self, project, name):
        self.project = project
        self.name = unicode(name)

    def uid(self, *args):
        return get_uid(self.name, *args)

    def emit_entity(self, data):
        data['origin'] = self.name
        self.project.emit_entity(data)

    def emit_alias(self, data):
        data['origin'] = self.name
        self.project.emit_alias(data)

    def clear(self):
        self.project.entities.delete(origin=self.name)
        self.project.aliases.delete(origin=self.name)
        self.project.links.delete(origin=self.name)

    def __repr__(self):
        return '<Origin(%r, %r)>' % (self.project, self.name)

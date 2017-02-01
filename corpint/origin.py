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

    def clear(self):
        self.entities.delete(origin=self.name)
        self.aliases.delete(origin=self.name)
        self.links.delete(origin=self.name)

    def __repr__(self):
        return '<Origin(%r, %r)>' % (self.project, self.name)

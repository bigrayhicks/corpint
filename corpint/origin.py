import logging
from corpint.load.util import get_uid


class Origin(object):

    def __init__(self, project, name):
        self.project = project
        self.name = unicode(name)
        self.qname = '%s:%s' % (self.project.prefix, self.name)
        self.log = logging.getLogger(self.qname)

    def uid(self, *args):
        return get_uid(self.name, *args)

    def emit_entity(self, data):
        data['origin'] = self.name
        self.project.emit_entity(data)

    def entity_exists(self, uid):
        return self.project.entities.find_one(uid=uid, origin=self.name)

    def emit_alias(self, data):
        data['origin'] = self.name
        self.project.emit_alias(data)

    def emit_judgement(self, uida, uidb, judgement):
        self.project.emit_judgement(uida, uidb, judgement)

    def clear(self):
        self.project.entities.delete(origin=self.name)
        self.project.aliases.delete(origin=self.name)
        self.project.links.delete(origin=self.name)

    def __repr__(self):
        return '<Origin(%r, %r)>' % (self.project, self.name)

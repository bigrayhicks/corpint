from os import environ
import dataset
import logging

from corpint.origin import Origin

log = logging.getLogger(__name__)


class Project(object):

    def __init__(self, prefix):
        self.prefix = unicode(prefix)
        self.log = logging.getLogger(self.prefix)

        database_uri = environ.get('DATABASE_URI')
        if database_uri is None:
            database_uri = 'sqlite:///%s.sqlite3' % self.prefix
        self.db = dataset.connect(database_uri)
        self.entities = self.db['%s_entities' % self.prefix]
        self.aliases = self.db['%s_aliases' % self.prefix]
        self.links = self.db['%s_links' % self.prefix]
        self.mappings = self.db['%s_mappings' % self.prefix]

    def origin(self, name):
        return Origin(self, name)

    def emit_entity(self, data):
        self.entities.upsert(data, ['origin', 'uid'])

    def flush(self):
        self.entities.drop()
        self.aliases.drop()
        self.links.drop()

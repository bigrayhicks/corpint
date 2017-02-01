import logging
from os import environ
import dataset
import countrynames

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
        uid = data.get('uid') or data.get('uid_canonical')
        if uid is None:
            raise ValueError("No UID for entity: %r", data)

        data['score'] = int(data.get('score', 0))

        if 'jurisdiction' in data:
            data['jurisdiction'] = countrynames.to_code(data['jurisdiction'])

        aliases = data.pop('aliases', [])
        self.entities.upsert(data, ['origin', 'uid'])
        for alias in aliases:
            self.emit_alias({
                'name': alias,
                'origin': data.get('origin'),
                'uid': data.get('uid'),
                'uid_canonical': data.get('uid_canonical'),
            })

    def emit_alias(self, data):
        self.aliases.upsert(data, ['origin', 'uid', 'name'])

    def flush(self):
        self.entities.drop()
        self.aliases.drop()
        self.links.drop()

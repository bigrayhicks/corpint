import logging
from os import environ
import dataset
import countrynames
from sqlalchemy import Boolean, Unicode, Float

from corpint.origin import Origin
from corpint.schema import TYPES
from corpint.integrate import integrate, canonicalise
from corpint.util import ensure_column

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

        ensure_column(self.mappings, 'judgement', Boolean)
        ensure_column(self.mappings, 'score', Float)
        for field in ['name', 'jurisdiction', 'date', 'type', 'origin', 'uid']:
            ensure_column(self.mappings, 'left_' + field, Unicode)
            ensure_column(self.mappings, 'right_' + field, Unicode)

    def origin(self, name):
        return Origin(self, name)

    def emit_entity(self, data):
        uid = data.get('uid') or data.get('uid_canonical')
        if uid is None:
            raise ValueError("No UID for entity: %r", data)

        if data.get('type') not in TYPES:
            raise ValueError("Invalid entity type: %r", data)

        try:
            data['score'] = int(data.get('score', 0))
        except Exception:
            raise ValueError("Invalid score: %r", data)

        if 'jurisdiction' in data:
            data['jurisdiction'] = countrynames.to_code(data['jurisdiction'])

        # TODO: partial dates

        aliases = data.pop('aliases', [])
        self.entities.upsert(data, ['origin', 'uid'])
        for alias in aliases:
            self.emit_alias({
                'name': alias,
                'origin': data.get('origin'),
                'uid': data.get('uid'),
                'uid_canonical': data.get('uid_canonical'),
            })
        return data

    def emit_alias(self, data):
        name = data.get('name')
        if not len(name.strip()):
            # TODO: should this raise?
            return
        self.aliases.upsert(data, ['origin', 'uid', 'name'])

    def integrate(self):
        integrate(self)
        canonicalise(self)

    def flush(self):
        self.entities.drop()
        self.aliases.drop()
        self.links.drop()

import logging
from os import environ
import dataset
import countrynames
from sqlalchemy import Boolean, Unicode, Float

from corpint.origin import Origin
from corpint.schema import TYPES
from corpint.integrate import integrate, iter_merge
from corpint.enrich import get_enrichers
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
            data['weight'] = int(data.get('weight', 0))
        except Exception:
            raise ValueError("Invalid weight: %r", data)

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

    def emit_judgement(self, uida, uidb, judgement):
        if uida is None or uidb is None:
            return
        self.mappings.upsert({
            'left_uid': max(uida, uidb),
            'right_uid': min(uida, uidb),
            'judgement': True
        }, ['left_uid', 'right_uid'])

    def integrate(self, auto_match=False):
        integrate(self, auto_match=auto_match)

    def iter_searches(self, min_weight=1):
        for entity in iter_merge(self):
            if entity['weight'] >= min_weight:
                yield entity

    def enrich(self, name):
        enricher = get_enrichers().get(name)
        if enricher is None:
            raise RuntimeError("Enricher not found: %s" % name)
        for entity in self.iter_searches():
            enricher(self, entity)

    def flush(self):
        self.entities.drop()
        self.aliases.drop()
        self.links.drop()

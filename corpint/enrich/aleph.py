import logging
import requests
from time import sleep
from os import environ
from pprint import pprint  # noqa
from urlparse import urljoin
from itertools import count

from corpint.schema import TYPES

log = logging.getLogger(__name__)
API_KEY = environ.get('ALEPH_APIKEY')
HOST = environ.get('ALEPH_HOST', 'https://data.occrp.org')
ENTITIES_API = urljoin(HOST, 'api/1/entities')

ENTITY_PROPERTIES = {
    'summary': 'summary',
    'status': 'status',
    'sourceUrl': 'source_url',
    'legalForm': 'legal_form',
    'registrationNumber': 'registration_number',
    'country': 'country',
    'mainCountry': 'country',
    'jurisdiction': 'country',
    'nationality': 'country',
    'address': 'address',
    'birthDate': 'dob',
    'incorporationDate': 'incorporation_date',
    'dissolutionDate': 'dissolution_date',
}

LINK_PROPERTIES = {
    'role': 'summary',
    'summary': 'summary',
    'startDate': 'start_date',
    'endDate': 'end_date',
}


def aleph_api(url, params=None):
    params = params or dict()
    if API_KEY is not None:
        params['api_key'] = API_KEY

    for i in count(2):
        try:
            res = requests.get(url, params=params, verify=False)
            return res.json()
        except Exception as ex:
            log.exception(ex)
            sleep(i ** 2)


def aleph_paged(url, params=None):
    params = params or dict()
    params['limit'] = 50
    while True:
        data = aleph_api(url, params=params)
        # pprint(data)
        for result in data.get('results', []):
            yield result
        next_offset = data['offset'] + params['limit']
        if next_offset > data['total']:
            break
        params['offset'] = next_offset


def map_properties(obj, mapping):
    data = {'aliases': set()}
    for key, values in obj.get('properties', {}).items():
        if key in ['alias', 'previousName']:
            data['aliases'].update(values)
        prop = mapping.get(key)
        if prop is not None:
            for value in values:
                data[prop] = value
    return data


def emit_entity(origin, entity, links=True):
    # Skip collection stuff for now.
    if entity.get('dataset') is None:
        return

    entity_uid = origin.uid(entity.get('id'))
    data = {
        'aleph_id': '%s:%s' % (entity.get('dataset'), entity.get('id')),
        'uid': entity_uid,
        'name': entity.get('name')
    }
    if entity.get('schema') in TYPES:
        data['type'] = entity.get('Schema')

    data.update(map_properties(entity, ENTITY_PROPERTIES))
    origin.log.info("Aleph [%(dataset)s]: %(name)s", entity)
    origin.emit_entity(data)

    if links:
        for link in aleph_paged(entity.get('api_url') + '/links'):
            other_uid = emit_entity(origin, link.get('remote'), links=False)
            ldata = {
                'source': other_uid if link['inverted'] else entity_uid,
                'target': entity_uid if link['inverted'] else other_uid,
            }
            ldata.update(map_properties(link, LINK_PROPERTIES))
            ldata.pop('aliases')
            origin.emit_link(ldata)

    return entity_uid


def enrich(origin, entity):
    for entity in aleph_paged(ENTITIES_API, params={'q': entity['name']}):
        emit_entity(origin, entity)

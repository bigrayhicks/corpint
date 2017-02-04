import logging
import requests
from time import sleep
from os import environ
from urllib import quote_plus
from itertools import count

from corpint.schema import PERSON

log = logging.getLogger(__name__)
API_KEY = environ.get('OPENCORPORATES_APIKEY')
OFFICER_SEARCH_API = 'https://api.opencorporates.com/v0.4/officers/search'
COMPANY_SEARCH_API = 'https://api.opencorporates.com/v0.4/companies/search'
GROUPING_API = 'https://api.opencorporates.com/corporate_groupings/%s'


def get_oc_api(url, params=None):
    if not url.startswith('https://api.openc'):
        url = url.replace('https://openc', 'https://api.openc')

    params = params or dict()
    params['api_token'] = API_KEY

    for i in count(2):
        try:
            res = requests.get(url, params=params, verify=False)
            return res.json().get('results')
        except Exception as ex:
            log.exception(ex)
            sleep(i ** 2)


def emit_officer(origin, officer, company_url=None):
    if isinstance(officer.get('officer'), dict):
        officer = officer.get('officer')

    company = officer.get('company')
    if company_url is None and company is not None:
        company_url = company.get('opencorporates_url')
        # always download full company records.
        get_company(origin, company_url)

    origin.log.info("OC Officer [%(id)s]: %(name)s", officer)
    officer_uid = origin.uid(officer['opencorporates_url'])
    origin.emit_entity({
        'uid': officer_uid,
        'name': officer['name'],
        'dob': officer.get('date_of_birth'),
        'country': officer.get('nationality'),
        'summary': officer.get('occupation'),
        'opencorporates_url': officer['opencorporates_url'],
    })

    if company_url is not None:
        company_uid = origin.uid(company_url)
        origin.emit_link({
            'source': company_uid,
            'target': officer_uid,
            'summary': officer.get('position'),
            'start_date': officer.get('start_date'),
            'end_date': officer.get('end_date'),
            'source_url': officer['opencorporates_url']
        })
    return officer_uid


def emit_company(origin, company):
    if isinstance(company.get('company'), dict):
        company = company.get('company')

    company_url = company['opencorporates_url']
    company_uid = origin.uid(company_url)

    aliases = set()
    for key in ['alternative_names', 'previous_names']:
        for value in company.get(key, []):
            aliases.update(value)

    origin.log.info("OC Company [%(company_number)s]: %(name)s", company)
    origin.emit_entity({
        'uid': company_uid,
        'name': company.get('name'),
        'aliases': aliases,
        'type': 'Company',
        'registration_number': company.get('company_number'),
        'country': company.get('jurisdiction_code')[:2],
        'legal_form': company.get('company_type'),
        'status': company.get('current_status'),
        'dissolution_date': company.get('dissolution_date'),
        'incorporation_date': company.get('incorporation_date'),
        'opencorporates_url': company.get('opencorporates_url'),
        'address': company.get('registered_address_in_full'),
    })

    for officer in company.get('officers', []):
        emit_officer(origin, officer, company_url=company_url)

    return company_uid


def get_company(origin, opencorporates_url):
    company_uid = origin.uid(opencorporates_url)
    if origin.entity_exists(company_uid):
        return company_uid
    company = get_oc_api(opencorporates_url)
    return emit_company(origin, company)


def get_officer(origin, opencorporates_url):
    officer_uid = origin.uid(opencorporates_url)
    if origin.entity_exists(officer_uid):
        return officer_uid
    officer = get_oc_api(opencorporates_url)
    return emit_officer(origin, officer)


def get_grouping(origin, name):
    url = GROUPING_API % quote_plus(name)
    results = get_oc_api(url)
    grouping = results.get('corporate_grouping')
    memberships = grouping.pop('memberships', [])
    for company in memberships:
        company = company.get('company')
        get_company(origin, company.get('opencorporates_url'))


def search_officers(origin, entity):
    for page in count(1):
        # TODO aliases
        params = {
            'q': entity.get('name'),
            'page': page
        }
        results = get_oc_api(OFFICER_SEARCH_API, params=params)
        for officer in results.get('officers'):
            emit_officer(origin, officer)
        if page >= results.get('total_pages'):
            return


def search_companies(origin, entity):
    for page in count(1):
        # TODO aliases
        params = {
            'q': entity.get('name'),
            'page': page
        }
        if entity.get('jurisdiction'):
            params['country_code'] = entity.get('country')
        results = get_oc_api(COMPANY_SEARCH_API, params=params)
        for company in results.get('companies'):
            company = company.get('company')
            get_company(origin, company.get('opencorporates_url'))
        if page >= results.get('total_pages'):
            return


def enrich(origin, entity):
    search_officers(origin, entity)
    if entity['type'] not in [PERSON]:
        search_companies(origin, entity)

import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from corpint.project import Project
from corpint.schema import TYPES, COMPANY, ORGANIZATION, PERSON, OTHER  # noqa


def project(prefix, database_uri=None):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('alembic').setLevel(logging.WARNING)
    logging.getLogger('zeep').setLevel(logging.WARNING)
    return Project(prefix, database_uri=database_uri)

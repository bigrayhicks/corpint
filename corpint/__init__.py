import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from corpint.project import Project
from corpint.env import DEFAULT_PROJECT, DATABASE_URI
from corpint.schema import TYPES, COMPANY, ORGANIZATION, PERSON, OTHER  # noqa

log = logging.getLogger(__name__)


def project(prefix=None, database_uri=None):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('alembic').setLevel(logging.WARNING)
    logging.getLogger('zeep').setLevel(logging.WARNING)
    logging.getLogger('httpstream').setLevel(logging.WARNING)
    logging.getLogger('neo4j').setLevel(logging.WARNING)

    prefix = prefix or DEFAULT_PROJECT
    database_uri = database_uri or DATABASE_URI
    if database_uri is None:
        raise RuntimeError("No $DATABASE_URI is set, aborting.")
    log.info("Project [%s], connected to: %s", prefix, database_uri)
    return Project(prefix, database_uri=database_uri)

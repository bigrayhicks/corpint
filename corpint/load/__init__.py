import logging
import requests
from unicodecsv import DictReader
from normality import slugify

SHEET_URL = 'https://docs.google.com/spreadsheets/d/%s/pub?gid=%s&single=true&output=csv'  # noqa

log = logging.getLogger(__name__)


def csv(fh):
    """Read a CSV file and return an iterator of normalised rows."""
    for row in DictReader(fh):
        data = {}
        for k, v in row.items():
            key = slugify(k, sep='_')
            if key is None:
                continue
            v = v.strip()
            if not len(v):
                v = None
            if key in data:
                log.warning("Duplicate column: %s", key)
            data[key] = v
        yield data


def google_sheet(doc_id, sheet_id):
    """Load data from Google Spreadsheet and return an iterator of values."""
    url = SHEET_URL % (doc_id, sheet_id)
    res = requests.get(url)
    return csv(res.iter_lines())

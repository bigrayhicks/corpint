import logging
from pkg_resources import iter_entry_points

log = logging.getLogger(__name__)
EXTENSIONS = {}


def get_extensions(section):
    if section not in EXTENSIONS:
        EXTENSIONS[section] = {}
    if not EXTENSIONS[section]:
        for ep in iter_entry_points(section):
            EXTENSIONS[section][ep.name] = ep.load()
    return EXTENSIONS[section]


def ensure_column(table, name, type):
    """Create a table column if it does not exist."""
    if name not in table.columns:
        table.create_column(name, type)

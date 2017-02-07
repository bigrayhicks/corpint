from os import environ

DEFAULT_PROJECT = environ.get('CORPINT_PROJECT', 'default')
DEBUG = environ.get('CORPINT_DEBUG') is not None
DATABASE_URI = environ.get('DATABASE_URI')
NEO4J_URI = environ.get('NEO4J_URI')

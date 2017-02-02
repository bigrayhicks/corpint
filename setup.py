from setuptools import setup, find_packages

setup(
    name='corpint',
    version='0.1',
    long_description="Corporate data OSINT toolkit",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Friedrich Lindenberg',
    author_email='pudo@occrp.org',
    url='https://occrp.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'normality',
        'dataset>=0.8',
        'requests',
        'countrynames',
        'fingerprints',
        'unicodecsv',
        'python-Levenshtein',
        'mwclient',
        'click'
    ],
    test_suite='nose.collector',
    entry_points={
        'corpint.enrich': [
            'wikipedia = corpint.enrich.wikipedia:enrich',
        ]
    },
    tests_require=['coverage', 'nose']
)

# CorpINT

Corporate open-source intelligence toolkit for data-driven
investigations.

## Install

    python setup.py install


## Develop

    python setup.py develop
    

## Run the merging UI

There's a very alpha Flask merging UI to allow you to merge or reject entity mappings. To run it:

    python userfacing.py


## Scope

* Basic corporate data model as SQL tables
* Easily import data from databases or spreadsheets
* Merge entities from multiple sources
* Enrich data from OpenCorporates, Orbis, Wikipedia, Wikidata, Aleph
* Mark duplicates
* Generate a unified view of the resulting watchlist


## TODO (near term)

* "tasked" flag
* Merging UI
* Neo4J Exporter
* Use dedupe library, with merging UI as input for decisions


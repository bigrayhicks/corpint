from os import path
import corpint

project = corpint.project('test')
origin = project.origin('luke')

origin.emit_entity({
    'uid': origin.uid('calderbank'),
    'name': 'Damian Calderbank',
    'score': 5,
    'jurisdiction': 'United Kingdom'
})

with open(path.join(path.dirname(__file__), 'test.csv')) as fh:
    origin = project.origin(fh.name)
    origin.clear()
    for entity in corpint.load.csv(fh):
        entity['uid'] = origin.uid(entity['name'])
        origin.emit_entity(entity)

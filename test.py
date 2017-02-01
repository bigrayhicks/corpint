
import corpint

project = corpint.project('test')
origin = project.origin('luke')

origin.emit_entity({
    'name': 'Jesus H. Christ',
    'jurisdiction': 'Israel'
})

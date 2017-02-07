from os import path
from flask import Flask

from corpint import env
from corpint.integrate import create_deduper, train_dedupe
from corpint.webui.views import blueprint


def run_webui(project):
    dir_name = path.dirname(__file__)
    app = Flask('corpint',
                static_folder=path.join(dir_name, 'static'),
                template_folder=path.join(dir_name, 'templates'))
    app.register_blueprint(blueprint)
    app.debug = env.DEBUG
    app.project = project
    app.deduper, data = create_deduper(project)
    # TODO: do we need this?
    train_dedupe(app.deduper)
    app.run()

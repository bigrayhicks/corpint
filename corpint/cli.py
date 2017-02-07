import click

from corpint import project as make_project
from corpint import env
from corpint.webui import run_webui


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--db', envvar='DATABASE_URI')
@click.option('prefix', '--project', envvar='CORPINT_PROJECT')
@click.pass_context
def cli(ctx, debug, db, prefix):
    env.DEBUG = env.DEBUG or debug
    ctx.obj['PROJECT'] = make_project(prefix, db)


@cli.command()
@click.pass_context
def webui(ctx):
    run_webui(ctx.obj['PROJECT'])


def main():
    cli(obj={})


if __name__ == '__main__':
    main()

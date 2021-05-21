import click
from .log_parser import LogParser
from .outputs import query, label
from .search_file import search_file
from .stats_output import stats_output

@click.group()
@click.option(
    '--file', '-f',
    type=click.Path(),
    help="Relative file path") # <-- use option not arg, so default can be set
@click.option(
    '--log_message', '-l',
    prompt=query('Search Terms'),
    help="Str to filter; skip to echo all")
@click.pass_context
def main(ctx, file, log_message):
    """pass OPTIONS --file, --log_message, then call COMMAND"""
    ctx.ensure_object(dict)
    ctx.obj['file'] = file
    ctx.obj['log_message'] = log_message
    click.clear()


@main.command()
@click.pass_context
def parse(ctx):
    """prints all lines in --file that contain --log_message"""
    file = ctx.obj['file']
    log_message = ctx.obj['log_message']
    res = search_file(file, log_message)
    for r in res:
        click.echo(r)

@main.command()
@click.pass_context
def stats(ctx):
    """prints report about --file based on searching --log_message"""
    file = ctx.obj['file']
    log_message = ctx.obj['log_message']

    res = search_file(file, log_message)

    click.echo("")
    click.echo(f"{ label('Searching', log_message)} { label('in', file) }")

    stats_output(res)

@main.command()
@click.pass_context
def classifier(ctx):
    """tester for class instancing log events from strings"""
    file = ctx.obj['file']
    log_message = ctx.obj['log_message']

    events = search_file(file, log_message)
    LogParser(events)

if __name__ == "__main__":
    main(obj={})

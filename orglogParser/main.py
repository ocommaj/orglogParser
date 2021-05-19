import click
from .parse_file import parse_file

@click.group()
@click.option('--file', '-f',
        type=click.Path(),
        help="Relative file path")
@click.option('--log_message', '-lm',
        help="Str to filter; skip to echo all")
@click.pass_context
def main(ctx, file, log_message):
    """pass OPTIONS --file, --log_message, then call COMMAND"""
    ctx.ensure_object(dict)
    ctx.obj['file'] = file
    ctx.obj['log_message'] = log_message

@main.command()
@click.pass_context
def parse(ctx):
    """prints all lines in --file that contain --log_message"""
    file = ctx.obj['file']
    log_message = ctx.obj['log_message']
    res = parse_file(file, log_message)
    for r in res:
        click.echo(r)

@main.command()
@click.pass_context
def stats(ctx):
    """prints report about --file based on searching --log_message"""
    file = ctx.obj['file']
    log_message = ctx.obj['log_message']
    res = parse_file(file, log_message)
    click.echo(f"Found {len(res)} results for '{log_message}' in {file}")

if __name__ == "__main__":
    main(obj={})

import click
from .parse_file import parse_file

@click.group()
def main():
    pass

@main.command()
@click.option("--file", "-f", help="Relative file path")
@click.option("--log_message", "-lm", help="Log Message to filter")
def parse(file, log_message):
    res = parse_file(file, log_message)
    for r in res:
        click.echo(r)


if __name__ == "__main__":
    main()

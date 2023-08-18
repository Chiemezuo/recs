import dtyper as ty
import click
import typing as t
import sys

ICON = '🎙'
CLI_NAME = 'recs'

app = ty.Typer(
    add_completion=False,
    context_settings={'help_option_names': ['--help', '-h']},
    help=f"""\
{ICON} {CLI_NAME} {ICON}

Usage: {CLI_NAME} [GLOBAL-FLAGS] [COMMAND] [COMMAND-FLAGS] [COMMAND-ARGS]
""",
)

command = app.command


@command(help='Record')
def rec():
    pass


@command(help='Check levels')
def test():
    from .audio_display import Global
    from rich.console import Console
    from rich.live import Live
    from test import mock_data

    g = Global()
    console = Console(color_system='truecolor')
    with Live(g.table(), refresh_per_second=4, console=console) as live:
        for i, block in enumerate(mock_data.emit_blocks()):
            g(*block)
            if not (i % 20):
                live.update(g.table())


@command(help='Check levels')
def check():
    from . import checker

    checker.check()


@command(help='Info')
def info(
    kind: t.Optional[str] = ty.Argument(None),
):
    import sounddevice as sd
    import json

    info = sd.query_devices(kind=kind)

    def accept(k):
        if 'channel' in k:
            return k.replace('max_', '')
        if 'sample' in k:
            return 'sample_rate'

    def to_entry(d):
        return d['name'], {j: v for k, v in d.items() if (j := accept(k))}

    info = dict(to_entry(d) for d in info)

    print(json.dumps(info, indent=2))


def run():
    try:
        app(standalone_mode=False)
    except click.ClickException as e:
        return f'{e.__class__.__name__}: {e.message}'
    except click.Abort:
        return 'Aborted'


if __name__ == '__main__':
    sys.exit(run())

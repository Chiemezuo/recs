import dtyper as ty
import click
import typing as t
import sys
from test import mock_data

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
def check():
    from .audio_display import Global
    from rich.console import Console
    from rich.live import Live

    g = Global()
    console = Console(color_system='truecolor')
    with Live(g.table(), refresh_per_second=4, console=console) as live:
        for i, block in enumerate(mock_data.emit_blocks()):
            g(*block)
            if not (i % 20):
                live.update(g.table())


@command(help='Info')
def info(
    kind: t.Optional[str] = ty.Argument(None),
):
    import sounddevice as sd
    import json

    info = sd.query_devices(kind=kind)
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

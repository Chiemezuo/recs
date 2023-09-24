from pathlib import Path

import click
import dtyper
from dtyper import Option

from recs.audio import format, info, monitor, subtype
from recs.ui import audio_display

ICON = '🎙'
CLI_NAME = 'recs'

app = dtyper.Typer(
    add_completion=False,
    context_settings={'help_option_names': ['--help', '-h']},
    help=f"""\
{ICON} {CLI_NAME} {ICON}

Usage: {CLI_NAME} [GLOBAL-FLAGS] [COMMAND] [COMMAND-FLAGS] [COMMAND-ARGS]
""",
)


@app.command(help='Record everything coming in')
def rec(
    path: Path = Option(
        Path(), '-p', '--path', help='Path to the parent directory for files'
    ),
    dry_run: bool = Option(
        False, '-d', '--dry-run', help='Display levels only, do not record'
    ),
    info: bool = Option(
        False, '--info', help='Do not run, display device info instead'
    ),
    #
    # Exclude or include devices or channels
    #
    exclude: list[str] = Option(
        None, '-e', '--exclude', help='Exclude these devices or channels'
    ),
    include: list[str] = Option(
        None, '-i', '--include', help='Only include these devices or channels'
    ),
    #
    # Audio file format and subtype
    #
    format: format.Format = Option(
        format.Format.caf, '-f', '--format', help='Audio file format to use'
    ),
    subtype: subtype.Subtype = Option(
        subtype.Subtype.alac_24, '-t', '--subtype', help='File subtype to write to'
    ),
    #
    # Settings relating to silence
    #
    before_start: float = Option(
        1, '-b', '--before-start', help='Silence before the start, in seconds'
    ),
    after_end: float = Option(
        2, '-a', '--after-end', help='Silence after the end, in seconds'
    ),
    stop_after: float = Option(
        20, '-s', '--stop-after', help='Stop recording after silence'
    ),
    noise_floor: float = Option(
        70, '-n', '--noise-floor', help='The noise floor in decibels'
    ),
):
    Rec(**locals())()


@dtyper.dataclass(rec)
class Rec:
    def __call__(self):
        if self.info:
            info.info()
        else:
            top = audio_display.DevicesCallback()
            monitor.Monitor(top.callback, top.table).run()


def run():
    try:
        app(standalone_mode=False)
    except click.ClickException as e:
        return f'{e.__class__.__name__}: {e.message}'
    except click.Abort:
        return 'Aborted'


if __name__ == '__main__':
    import sys

    sys.exit(run())

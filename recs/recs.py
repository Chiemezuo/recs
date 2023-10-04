import json
from pathlib import Path

import click
import dtyper
from dtyper import Option

from .audio.file_types import Format, Subtype

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
def recs(
    #
    # General purpose settings
    #
    dry_run: bool = Option(
        False, '-d', '--dry-run', help='Display levels only, do not record'
    ),
    info: bool = Option(
        False, '--info', help='Do not run, display device info instead'
    ),
    path: Path = Option(
        Path(), '-p', '--path', help='Path to the parent directory for files'
    ),
    retain: bool = Option(
        False, '-r', '--retain', help='Retain rich display on shutdown'
    ),
    #
    # Names of input devices
    #
    device_names: list[str] = Option((), help='Display names for devices'),
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
    format: Format = Option(
        Format.CAF, '-f', '--format', help='Audio file format to use'
    ),
    subtype: Subtype = Option(
        Subtype.ALAC_24, '-u', '--subtype', help='File subtype to write to'
    ),
    #
    # Console and UI settings
    #
    ui_refresh_rate: float = Option(
        23, '--ui-refresh-rate', help='How many UI refreshes per second'
    ),
    sleep_time: float = Option(
        0.013, '--sleep-time', help='How long to sleep between data refreshes'
    ),
    #
    # Settings relating to times
    #
    silence_before_start: float = Option(
        1, '-b', '--silence-before-start', help='Silence before the start, in seconds'
    ),
    silence_after_end: float = Option(
        2, '-a', '--silence-after-end', help='Silence after the end, in seconds'
    ),
    stop_after_silence: float = Option(
        20, '-s', '--stop-after-silence', help='Stop recording after silence'
    ),
    noise_floor: float = Option(
        70, '-n', '--noise-floor', help='The noise floor in decibels'
    ),
    total_run_time: float = Option(
        0, '-t', '--total-run-time', help='How many seconds to record? 0 means forever'
    ),
):
    Recording(**locals())()


@dtyper.dataclass(recs)
class Recording:
    def __call__(self):
        if self.info:
            import sounddevice as sd

            info = sd.query_devices(kind=None)
            print(json.dumps(info, indent=2))
        else:
            from .ui.session import Session

            Session(self).run()


def run():
    try:
        app(standalone_mode=False)
    except click.ClickException as e:
        return f'{e.__class__.__name__}: {e.message}'
    except click.Abort:
        return 'Aborted'

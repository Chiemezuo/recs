import string
import sys
from pathlib import Path

import click
import dtyper
from typer import Argument, rich_utils

from recs.base import RecsError, pyproject
from recs.base.cfg_raw import CfgRaw

from .cfg import Cfg

rich_utils.STYLE_METAVAR = 'dim yellow'
INTRO = f"""
  {pyproject.message()}

============================================="""
LINES = (
    INTRO,
    'Why should there be a record button at all?',
    'I wanted to digitize a huge number of cassettes and LPs, so I wanted a '
    + 'program that ran in the background and recorded everything except quiet.',
    'Nothing like that existed so I wrote it.  Free, open-source, configurable.',
    'Full documentation here: https://github.com/rec/recs',
    '',
)
HELP = '\n\n\n\n'.join(LINES)
# Three blank lines seems to force Typer to format correctly

app = dtyper.Typer(
    add_completion=False,
    context_settings={'help_option_names': ['--help', '-h']},
)

_SINGLES: set[str] = set()

RECS = CfgRaw()
# Reading configs and environment variables would go here


def Option(default, *a, **ka) -> dtyper.Option:
    _SINGLES.update(i[1] for i in a if len(i) == 2)
    return dtyper.Option(default, *a, **ka)


GENERAL_PANEL = 'General Settings'
NAMES_PANEL = 'Selecting and Naming Devices and Channels'
FILE_PANEL = 'Audio File Format Settings'
CONSOLE_PANEL = 'Console and UI Settings'
RECORD_PANEL = 'Record Settings'


@app.command(help=HELP)
def recs(
    #
    # Directory settings
    #
    path: str = Argument(
        RECS.path, help='Path or path pattern for recorded file locations'
    ),
    #
    calibrate: bool = Option(
        RECS.calibrate,
        '--calibrate',
        help='Detect silence levels',
        rich_help_panel=GENERAL_PANEL,
    ),
    dry_run: bool = Option(
        RECS.dry_run,
        '-n',
        '--dry-run',
        help='Display levels only, do not record',
        rich_help_panel=GENERAL_PANEL,
    ),
    info: bool = Option(
        RECS.info,
        '--info',
        help='Do not run, display device info instead',
        rich_help_panel=GENERAL_PANEL,
    ),
    list_types: bool = Option(
        RECS.list_types,
        '--list-types',
        help='List all subtypes for each format',
        rich_help_panel=GENERAL_PANEL,
    ),
    verbose: bool = Option(
        RECS.verbose,
        '-v',
        '--verbose',
        help='Print full stack traces',
        rich_help_panel=GENERAL_PANEL,
    ),
    #
    alias: list[str] = Option(
        RECS.alias,
        '-a',
        '--alias',
        help='Aliases for devices or channels',
        rich_help_panel=NAMES_PANEL,
    ),
    devices: Path = Option(
        RECS.devices,
        help='A JSON file with device definitions',
        rich_help_panel=NAMES_PANEL,
    ),
    exclude: list[str] = Option(
        RECS.exclude,
        '-e',
        '--exclude',
        help='Exclude these devices or channels',
        rich_help_panel=NAMES_PANEL,
    ),
    include: list[str] = Option(
        RECS.include,
        '-i',
        '--include',
        help='Only include these devices or channels',
        rich_help_panel=NAMES_PANEL,
    ),
    #
    format: str = Option(
        RECS.format,
        '-f',
        '--format',
        help='Audio format',
        rich_help_panel=FILE_PANEL,
    ),
    metadata: list[str] = Option(
        RECS.metadata,
        '-m',
        '--metadata',
        help='Metadata fields to add to output files',
        rich_help_panel=FILE_PANEL,
    ),
    sdtype: str = Option(
        RECS.sdtype,
        '-d',
        '--sdtype',
        help='Type of sounddevice numbers',
        rich_help_panel=FILE_PANEL,
    ),
    subtype: str = Option(
        RECS.subtype,
        '-u',
        '--subtype',
        help='File subtype',
        rich_help_panel=FILE_PANEL,
    ),
    #
    # Console and UI settings
    #
    silent: bool = Option(
        RECS.silent,
        '-s',
        '--silent',
        help='If true, do not display live updates',
        rich_help_panel=CONSOLE_PANEL,
    ),
    retain: bool = Option(
        RECS.retain,
        '-r',
        '--retain',
        help='Retain rich display on shutdown',
        rich_help_panel=CONSOLE_PANEL,
    ),
    ui_refresh_rate: float = Option(
        RECS.ui_refresh_rate,
        '--ui-refresh-rate',
        help='How many UI refreshes per second',
        rich_help_panel=CONSOLE_PANEL,
    ),
    sleep_time_device: float = Option(
        RECS.sleep_time_device,
        '--sleep-time-device',
        help='How long to sleep between device polls',
        rich_help_panel=CONSOLE_PANEL,
    ),
    sleep_time_live: float = Option(
        RECS.sleep_time_live,
        '--sleep-time-live',
        help='How long to sleep between UI refreshes',
        rich_help_panel=CONSOLE_PANEL,
    ),
    sleep_time_spin: float = Option(
        RECS.sleep_time_spin,
        '--sleep-time-spin',
        help='How long to sleep on the main thread',
        rich_help_panel=CONSOLE_PANEL,
    ),
    #
    # Settings relating to times
    #
    infinite_length: bool = Option(
        RECS.infinite_length,
        '--infinite-length',
        help='If true, ignore file size limits (4G on .wav, 2G on .aiff)',
        rich_help_panel=RECORD_PANEL,
    ),
    longest_file_time: str = Option(
        RECS.longest_file_time,
        help='Longest amount of time per file: 0 means infinite',
        rich_help_panel=RECORD_PANEL,
    ),
    moving_average_time: float = Option(
        RECS.moving_average_time,
        help='How long to average the volume display over',
        rich_help_panel=RECORD_PANEL,
    ),
    noise_floor: float = Option(
        RECS.noise_floor,
        '-o',
        '--noise-floor',
        help='The noise floor in decibels',
        rich_help_panel=RECORD_PANEL,
    ),
    shortest_file_time: str = Option(
        RECS.shortest_file_time,
        help='Shortest amount of time per file',
        rich_help_panel=RECORD_PANEL,
    ),
    quiet_after_end: float = Option(
        RECS.quiet_after_end,
        '-c',
        '--quiet-after-end',
        help='Quiet after the end, in seconds',
        rich_help_panel=RECORD_PANEL,
    ),
    quiet_before_start: float = Option(
        RECS.quiet_before_start,
        '-b',
        '--quiet-before-start',
        help='Quiet before the start, in seconds',
        rich_help_panel=RECORD_PANEL,
    ),
    stop_after_quiet: float = Option(
        RECS.stop_after_quiet,
        '--stop-after-quiet',
        help='Stop recs after quiet',
        rich_help_panel=RECORD_PANEL,
    ),
    total_run_time: float = Option(
        RECS.total_run_time,
        '-t',
        '--total-run-time',
        help='How many seconds to record? 0 means forever',
        rich_help_panel=RECORD_PANEL,
    ),
) -> None:  # pragma: no cover: This is tested in a subprocess.
    cfg = Cfg(**locals())

    from . import run

    run.run(cfg)


_USED_SINGLES = ''.join(sorted(_SINGLES))
_UNUSED_SINGLES = ''.join(sorted(set(string.ascii_lowercase) - set(_SINGLES)))

assert _USED_SINGLES == 'abcdefimnorstuv', _USED_SINGLES
assert _UNUSED_SINGLES == 'ghjklpqwxyz', _UNUSED_SINGLES


def run() -> int:
    try:
        app(prog_name='recs', standalone_mode=False)
        return 0

    except RecsError as e:
        print('ERROR:', *e.args, file=sys.stderr)

    except click.ClickException as e:
        print(f'{e.__class__.__name__}: {e.message}', file=sys.stderr)

    except click.Abort:
        print('Interrupted', file=sys.stderr)

    return -1

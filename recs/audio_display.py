import dataclasses as dc
import numbers
import time

from rich.table import Table

from . import field
from .block import Block
from .counter import Accumulator, Counter

COLUMNS = (
    'time',
    'device',
    'channel',
    'count',
    'block',
    'rms',
    'rms_mean',
    'amplitude',
    'amplitude_mean',
)


@dc.dataclass
class Channel:
    channel: str

    block_count: Counter = field(Counter)
    amplitude: Accumulator = field(Accumulator)
    rms: Accumulator = field(Accumulator)

    def __call__(self, block):
        self.block_count()
        self.rms(block.rms)
        self.amplitude(block.amplitude)

    def rows(self):
        yield {
            'amplitude': self.amplitude.value,
            'amplitude_mean': self.amplitude.mean(),
            'channel': self.channel,
            'count': self.block_count.value,
            'rms': self.rms.value,
            'rms_mean': self.rms.mean(),
        }


@dc.dataclass
class Device:
    name: str

    block_count: Counter = field(Counter)
    block_size: Accumulator = field(Accumulator)
    channels: dict[str, Channel] = field(dict)

    def __call__(self, frame, channel_name):
        self.block_count()
        block = Block(frame)
        assert block.channels <= 2, f'{len(block)=}, {block.channels=}'
        self.block_size(len(block))
        try:
            channel = self.channels[channel_name]
        except KeyError:
            channel = self.channels[channel_name] = Channel(channel_name)
        channel(block)

    def rows(self):
        yield {
            'block': self.block_size.value,
            'count': self.block_count.value,
            'device': self.name,
        }
        for v in self.channels.values():
            yield from v.rows()


@dc.dataclass
class Global:
    block_count: Counter = field(Counter)
    start_time: float = field(time.time)
    devices: dict[str, Device] = field(dict)

    @property
    def elapsed_time(self):
        return time.time() - self.start_time

    def callback(self, frame, channel_name, device):
        self.block_count()
        try:
            device = self.devices[device.name]
        except KeyError:
            self.devices[device.name] = device = Device(device.name)
        device(frame, channel_name)

    def table(self):
        t = Table(*COLUMNS)
        for row in self.rows():
            t.add_row(*(_to_str(row.get(c, ''), c) for c in COLUMNS))

        return t

    def rows(self):
        yield {
            'time': f'{self.elapsed_time:9.3f}',
            'count': self.block_count.value,
        }
        for v in self.devices.values():
            yield from v.rows()


RED = 256 // 3
GREEN = 512 // 3
BLUE = 0


def _to_str(x, c) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, numbers.Integral):
        if c in ('count', 'block'):
            global RED, GREEN, BLUE
            RED = (RED + 1) % 256
            GREEN = (GREEN + 1) % 256
            BLUE = (BLUE + 1) % 256
            return f'[rgb({RED},{GREEN},{BLUE})]{x:>7,}'

    if isinstance(x, numbers.Real):
        return f'{x:6.1%}'
    assert len(x) <= 2, f'{len(x)}'
    return ' |'.join(_to_str(i, c) for i in x)

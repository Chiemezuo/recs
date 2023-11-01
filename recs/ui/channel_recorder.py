import typing as t

import numpy as np

from recs import Cfg
from recs.audio import block, channel_writer, track
from recs.misc import counter, times


class ChannelRecorder:
    block_count: int = 0
    block_size: int = 0

    def __init__(self, cfg: Cfg, times: times.Times[int], track: track.Track) -> None:
        self.track = track
        self.writer = channel_writer.ChannelWriter(cfg, times, track)
        self.volume = counter.MovingBlock(times.moving_average_time)

        self.writer.start()
        self.stop = self.writer.stop

    def callback(self, array: np.ndarray) -> None:
        b = block.Block(array[:, self.track.slice])
        self.writer.write(b)

        self.block_size = len(b)
        self.block_count += 1
        self.volume(b)

    @property
    def file_size(self) -> int:
        return self.writer.files_written.total_size

    @property
    def recorded_time(self) -> float:
        return self.writer.frames_written / self.track.device.samplerate

    def rows(self) -> t.Iterator[dict[str, t.Any]]:
        yield {
            'channel': self.track.channels_name,
            'on': self.writer.active,
            'recorded': self.recorded_time,
            'file_size': self.file_size,
            'volume': self.volume.mean(),
        }

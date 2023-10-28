import contextlib
import dataclasses as dc
import typing as t
from functools import cached_property
from threading import Lock

import soundfile as sf
import threa

from recs import RECS

from ..misc import times
from . import block, file_creator


@dc.dataclass
class ChannelWriter(threa.Runnable):
    creator: file_creator.FileCreator
    times: times.Times[int]

    blocks_written: int = 0
    files_written: int = 0
    samples_seen: int = 0

    _blocks: block.Blocks = dc.field(default_factory=block.Blocks)
    _sf: sf.SoundFile | None = None

    def __post_init__(self):
        super().__init__()
        self.start()

    def write(self, block: block.Block) -> None:
        with self._lock:
            if not self.running:
                return

            self.samples_seen += len(block)
            self._blocks.append(block)

            if self._blocks[-1].volume >= self.times.noise_floor_amplitude:
                self._record_on_not_silence()

            elif self._blocks.duration > self.times.stop_after_silence:
                self._close_on_silence()

    def stop(self) -> None:
        with self._lock:
            self.running.clear()

            if self._blocks:
                self._record(self._blocks)
                self._blocks.clear()

            if self._sf:
                self._sf.close()
                self._sf = None

            self.stopped.set()

    @cached_property
    def _lock(self):
        if RECS.use_locking:
            return Lock()
        return contextlib.nullcontext()

    def _record_on_not_silence(self) -> None:
        if not self._sf:
            length = self.times.silence_before_start + len(self._blocks[-1])
            self._blocks.clip(length, from_start=True)

        self._record(self._blocks)
        self._blocks.clear()

    def _close_on_silence(self) -> None:
        removed = self._blocks.clip(self.times.silence_after_end, from_start=False)

        if self._sf:
            if removed:
                self._record(reversed(removed))

            self._sf.close()
            self._sf = None

    def _record(self, blocks: t.Iterable[block.Block]) -> None:
        for b in blocks:
            if not self._sf:
                self._sf = self.creator()
                self.files_written += 1

            self._sf.write(b.block)
            self.blocks_written += 1

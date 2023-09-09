import dataclasses as dc
from datetime import datetime as dt
from pathlib import Path

import soundfile as sf

from recs import Array
from recs.audio.block import Block, Blocks
from recs.audio.file_format import AudioFileFormat
from recs.audio.silence import SilenceStrategy


@dc.dataclass
class FileWriter:
    file_format: AudioFileFormat
    name: str
    path: Path
    silence: SilenceStrategy[int]

    _blocks: Blocks = dc.field(default_factory=Blocks)
    _sf: sf.SoundFile | None = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.close()
        except Exception:
            if type is not None:
                raise

    def write(self, block: Array):
        self._blocks.append(Block(block))

        if self._blocks[-1].amplitude >= self.silence.noise_floor:
            self._block_not_silent()

        elif self._blocks.duration > self.silence.before_stopping:
            self._close_on_silence()

    def close(self):
        if self._sf is not None:
            self._record(self._blocks)
            self._sf.close()
            self._sf = None
        self._blocks.clear()

    def _block_not_silent(self):
        if not self._sf:
            blocks = self._blocks
            length = self.silence.at_start + len(self._blocks[-1])
            blocks.clip(length, from_start=True)

        self._record(self._blocks)
        self._blocks.clear()

    def _close_on_silence(self):
        blocks = self._blocks
        removed = blocks.clip(self.silence.at_end, from_start=False)

        if self._sf:
            self._record(reversed(removed))
            self._sf.close()
            self._sf = None

    def _record(self, blocks: Blocks):
        self._sf = self._sf or self.file_format.open(self._new_filename(), 'w')

        for b in blocks:
            self._sf.write(b.block)

    def _new_filename(self) -> Path:
        istr = ''
        index = 0
        while True:
            p = self.path / f'{self.name}-{ts()}{istr}'
            p = p.with_suffix(self.file_format.suffix)
            if not p.exists():
                return p
            index += 1
            istr = f'-{index}'


def ts():
    return dt.now().strftime('%Y%m%d-%H%M%S')

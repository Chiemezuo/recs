import sys
import traceback
import typing as t
from functools import cache

import numpy as np
import sounddevice as sd

from recs.audio import hash_cmp
from recs.audio.file_types import DTYPE, DType

from .prefix_dict import PrefixDict


class InputDevice(hash_cmp.HashCmp):
    def __init__(self, info: dict[str, t.Any]) -> None:
        self.info = info
        self.channels = t.cast(int, self.info['max_input_channels'])
        self.samplerate = int(self.info['default_samplerate'])
        self.name = t.cast(str, self.info['name'])
        self._key = self.name

    def input_stream(
        self,
        callback: t.Callable[[np.ndarray], None],
        stop: t.Callable[[], None],
        dtype: DType = DTYPE,
    ) -> sd.InputStream:
        def cb(indata: np.ndarray, frames: int, time: float, status: int) -> None:
            try:
                if status:
                    # This has not yet happened, probably because we never get behind
                    # the device callback cycle.
                    print('Status', self, status, file=sys.stderr)

                if indata.size:
                    callback(indata.copy())  # `indata` is always the same variable!
                else:
                    print('Empty block', self, file=sys.stderr)

            except Exception:
                traceback.print_exc()
                stop()

        return sd.InputStream(
            callback=cb,
            channels=self.channels,
            device=self.name,
            dtype=dtype,
            samplerate=self.samplerate,
        )


@cache
def input_devices() -> PrefixDict[InputDevice]:
    return PrefixDict({d.name: d for i in sd.query_devices() if (d := InputDevice(i))})

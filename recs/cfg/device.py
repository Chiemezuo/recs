import json
import subprocess as sp
import sys
import traceback
import typing as t

from threa import Runnable, Wrapper
import numpy as np

from recs.base import times
from recs.base.prefix_dict import PrefixDict
from recs.base.types import SdType, Stop
from recs.cfg import hash_cmp

DeviceDict = dict[str, float | int | str]


class Update(t.NamedTuple):
    array: np.ndarray
    timestamp: float


class InputDevice(hash_cmp.HashCmp):
    def __init__(self, info: DeviceDict) -> None:
        self.info = info
        self.channels = t.cast(int, self.info['max_input_channels'])
        self.samplerate = int(self.info['default_samplerate'])
        self.name = t.cast(str, self.info['name'])
        self._key = self.name

    def __str__(self) -> str:
        return self.name

    def input_stream(
        self,
        on_error: Stop,
        sdtype: SdType,
        update_callback: t.Callable[[Update], None],
    ) -> Runnable:
        import sounddevice as sd

        stream: sd.InputStream

        def callback(indata: np.ndarray, frames: int, time: t.Any, status: int) -> None:
            if status:  # pragma: no cover
                print('Status', self, status, file=sys.stderr)

            try:
                update_callback(Update(indata.copy(), times.timestamp()))

            except Exception:  # pragma: no cover
                traceback.print_exc()
                try:
                    on_error()
                except Exception:
                    traceback.print_exc()

        stream = sd.InputStream(
            callback=callback,
            channels=self.channels,
            device=self.name,
            dtype=sdtype,
            samplerate=self.samplerate,
        )
        return Wrapper(stream)


InputDevices = PrefixDict[InputDevice]


def get_input_devices(devices: t.Sequence[DeviceDict]) -> InputDevices:
    return PrefixDict({d.name: d for i in devices if (d := InputDevice(i)).channels})


CMD = sys.executable, '-m', 'recs.base._query_device'


def query_devices() -> t.Sequence[DeviceDict]:
    try:
        r = sp.run(CMD, text=True, check=True, stdout=sp.PIPE)
    except sp.CalledProcessError:
        return []
    return json.loads(r.stdout)


def input_names() -> t.Sequence[str]:
    return sorted(str(i['name']) for i in query_devices())


def input_devices() -> InputDevices:
    return get_input_devices(query_devices())

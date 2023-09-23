import typing as t

from recs.audio.device import InputDevice

Slices = dict[str, slice]
SlicesDict = dict[str, Slices]


def auto_slice(channels: int) -> Slices:
    def slicer():
        # Display channnels start at channel 1, not 0
        for i in range(0, channels - 1, 2):
            yield f'{i + 1}-{i + 2}', slice(i, i + 2)
        if channels % 2:
            yield f'{channels}', slice(channels - 1, channels)

    return dict(slicer())


def to_slice(x: slice | dict[str, int] | t.Sequence) -> slice:
    if isinstance(x, slice):
        return x

    if not isinstance(x, dict):
        return slice(*x)

    d = dict(x)
    start = d.pop('start', 0)
    stop = d.pop('stop', None)
    step = d.pop('step', 1)

    assert stop is not None
    assert not d, f'Additional entries {d}'

    return slice(start, stop, step)


def to_slices(d: dict) -> Slices:
    return {k: to_slice(v) for k, v in d.items()}


def slice_one(device: InputDevice, device_slices: SlicesDict) -> Slices:
    name = device.name.lower()
    m = [v for k, v in device_slices.items() if name.startswith(k.lower())]
    return to_slices(m[0]) if m else auto_slice(device.channels)


def slice_all(
    devices: t.Sequence[InputDevice], device_slices: SlicesDict
) -> SlicesDict:
    return {d.name: slice_one(d, device_slices) for d in devices}
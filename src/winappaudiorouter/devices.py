from __future__ import annotations

from pycaw.constants import DEVICE_STATE, EDataFlow
from pycaw.pycaw import AudioUtilities

from .com import com_initialized
from .errors import AudioRoutingError
from .models import AudioDeviceInfo


def _list_output_devices_noinit() -> list[AudioDeviceInfo]:
    default_device_id = None
    try:
        default_device_id = AudioUtilities.GetSpeakers().id
    except Exception:
        default_device_id = None

    devices = AudioUtilities.GetAllDevices(
        data_flow=EDataFlow.eRender.value,
        device_state=DEVICE_STATE.ACTIVE.value,
    )
    return [
        AudioDeviceInfo(
            id=device.id,
            name=device.FriendlyName or "",
            is_default=device.id == default_device_id,
        )
        for device in devices
    ]


def list_output_devices() -> list[AudioDeviceInfo]:
    """List active render devices."""
    with com_initialized():
        return _list_output_devices_noinit()


def match_output_device(device: str, candidates: list[AudioDeviceInfo]) -> AudioDeviceInfo:
    if not candidates:
        raise AudioRoutingError("No active output devices were found.")

    lowered = device.lower()
    by_id = [d for d in candidates if d.id.lower() == lowered]
    if by_id:
        return by_id[0]

    by_name_exact = [d for d in candidates if d.name.lower() == lowered]
    if len(by_name_exact) == 1:
        return by_name_exact[0]
    if len(by_name_exact) > 1:
        raise AudioRoutingError(f"Multiple devices match '{device}'. Use device id instead.")

    by_name_contains = [d for d in candidates if lowered in d.name.lower()]
    if len(by_name_contains) == 1:
        return by_name_contains[0]
    if len(by_name_contains) > 1:
        raise AudioRoutingError(f"Multiple devices contain '{device}'. Use full name or id.")

    raise AudioRoutingError(f"Output device '{device}' not found.")


def find_output_device(device: str) -> AudioDeviceInfo:
    with com_initialized():
        return match_output_device(device, _list_output_devices_noinit())

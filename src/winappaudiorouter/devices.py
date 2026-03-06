from __future__ import annotations

from typing import Literal

from pycaw.constants import DEVICE_STATE, EDataFlow, ERole
from pycaw.pycaw import AudioUtilities

from .com import com_initialized
from .errors import AudioRoutingError
from .models import AudioDeviceInfo


AudioFlow = Literal["output", "input"]


def _data_flow_value(flow: AudioFlow) -> int:
    return EDataFlow.eCapture.value if flow == "input" else EDataFlow.eRender.value


def _default_device_id(flow: AudioFlow) -> str | None:
    try:
        enumerator = AudioUtilities.GetDeviceEnumerator()
        endpoint = enumerator.GetDefaultAudioEndpoint(
            _data_flow_value(flow),
            ERole.eMultimedia.value,
        )
        device = AudioUtilities.CreateDevice(endpoint)
        return None if device is None else device.id
    except Exception:
        return None


def _list_devices_noinit(flow: AudioFlow) -> list[AudioDeviceInfo]:
    default_device_id = _default_device_id(flow)
    devices = AudioUtilities.GetAllDevices(
        data_flow=_data_flow_value(flow),
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


def _list_output_devices_noinit() -> list[AudioDeviceInfo]:
    return _list_devices_noinit("output")


def _list_input_devices_noinit() -> list[AudioDeviceInfo]:
    return _list_devices_noinit("input")


def list_output_devices() -> list[AudioDeviceInfo]:
    """List active render devices."""
    with com_initialized():
        return _list_output_devices_noinit()


def list_input_devices() -> list[AudioDeviceInfo]:
    """List active capture devices."""
    with com_initialized():
        return _list_input_devices_noinit()


def _match_device(
    device: str,
    candidates: list[AudioDeviceInfo],
    *,
    flow_label: str,
) -> AudioDeviceInfo:
    if not candidates:
        raise AudioRoutingError(f"No active {flow_label} devices were found.")

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

    raise AudioRoutingError(f"{flow_label.capitalize()} device '{device}' not found.")


def match_output_device(device: str, candidates: list[AudioDeviceInfo]) -> AudioDeviceInfo:
    return _match_device(device, candidates, flow_label="output")


def match_input_device(device: str, candidates: list[AudioDeviceInfo]) -> AudioDeviceInfo:
    return _match_device(device, candidates, flow_label="input")


def find_output_device(device: str) -> AudioDeviceInfo:
    with com_initialized():
        return match_output_device(device, _list_output_devices_noinit())


def find_input_device(device: str) -> AudioDeviceInfo:
    with com_initialized():
        return match_input_device(device, _list_input_devices_noinit())

from __future__ import annotations

from typing import Literal

from pycaw.constants import EDataFlow, ERole

from .com import com_initialized
from .device_ids import pack_capture_device_id, pack_render_device_id, unpack_device_id
from .devices import (
    _list_input_devices_noinit,
    _list_output_devices_noinit,
    match_input_device,
    match_output_device,
)
from .models import AudioDeviceInfo, AudioSessionInfo
from .policy_config import PolicyConfigFactory
from .sessions import (
    _enumerate_input_sessions_noinit,
    _enumerate_output_sessions_noinit,
    _resolve_process_ids_from_sessions,
)

AudioFlow = Literal["output", "input"]


def _data_flow_value(flow: AudioFlow) -> int:
    return EDataFlow.eCapture.value if flow == "input" else EDataFlow.eRender.value


def _pack_device_id(flow: AudioFlow, device_id: str | None) -> str | None:
    if flow == "input":
        return pack_capture_device_id(device_id)
    return pack_render_device_id(device_id)


def _matched_device(flow: AudioFlow, device: str) -> AudioDeviceInfo:
    if flow == "input":
        candidates = _list_input_devices_noinit()
        return match_input_device(device, candidates)
    candidates = _list_output_devices_noinit()
    return match_output_device(device, candidates)


def _sessions_for_flow(flow: AudioFlow) -> list[AudioSessionInfo]:
    if flow == "input":
        return _enumerate_input_sessions_noinit()
    return _enumerate_output_sessions_noinit()


def _set_route_for_processes(
    process_ids: list[int],
    device_id: str | None,
    flow: AudioFlow,
) -> None:
    packed_device_id = _pack_device_id(flow, device_id)
    flow_value = _data_flow_value(flow)
    with PolicyConfigFactory() as factory:
        for pid in process_ids:
            factory.set_persisted_default_endpoint(
                process_id=pid,
                flow=flow_value,
                role=ERole.eConsole.value,
                packed_device_id=packed_device_id,
            )
            factory.set_persisted_default_endpoint(
                process_id=pid,
                flow=flow_value,
                role=ERole.eMultimedia.value,
                packed_device_id=packed_device_id,
            )


def _set_app_device(
    *,
    process_id: int | None,
    process_name: str | None,
    device: str,
    flow: AudioFlow,
) -> dict[int, AudioDeviceInfo]:
    with com_initialized():
        target = _matched_device(flow, device)
        sessions = _sessions_for_flow(flow)
        pids = _resolve_process_ids_from_sessions(process_id, process_name, sessions)
        _set_route_for_processes(pids, target.id, flow)
        return {pid: target for pid in pids}


def _clear_app_device(
    *,
    process_id: int | None,
    process_name: str | None,
    flow: AudioFlow,
) -> list[int]:
    with com_initialized():
        sessions = _sessions_for_flow(flow)
        pids = _resolve_process_ids_from_sessions(process_id, process_name, sessions)
        _set_route_for_processes(pids, None, flow)
        return pids


def _get_app_device(
    *,
    process_id: int | None,
    process_name: str | None,
    flow: AudioFlow,
) -> dict[int, str]:
    with com_initialized():
        sessions = _sessions_for_flow(flow)
        pids = _resolve_process_ids_from_sessions(process_id, process_name, sessions)

        if not pids:
            return {}

        results: dict[int, str] = {}
        with PolicyConfigFactory() as factory:
            for pid in pids:
                policy_device_id = factory.get_persisted_default_endpoint(
                    process_id=pid,
                    flow=_data_flow_value(flow),
                    role=ERole.eMultimedia.value,
                )
                unpacked_device = unpack_device_id(policy_device_id)
                if unpacked_device:
                    results[pid] = unpacked_device

        return results


def set_app_output_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
    device: str,
) -> dict[int, AudioDeviceInfo]:
    """Route one app (or all matching app PIDs) to a specific output device."""
    return _set_app_device(
        process_id=process_id,
        process_name=process_name,
        device=device,
        flow="output",
    )


def clear_app_output_device(
    *, process_id: int | None = None, process_name: str | None = None
) -> list[int]:
    """Clear persisted per-app output routing (app returns to system default)."""
    return _clear_app_device(
        process_id=process_id,
        process_name=process_name,
        flow="output",
    )


def get_app_output_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
) -> dict[int, str]:
    """Return current persisted route for the PID as a plain MMDevice id."""
    return _get_app_device(
        process_id=process_id,
        process_name=process_name,
        flow="output",
    )


def set_app_input_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
    device: str,
) -> dict[int, AudioDeviceInfo]:
    """Route one app (or all matching app PIDs) to a specific input device."""
    return _set_app_device(
        process_id=process_id,
        process_name=process_name,
        device=device,
        flow="input",
    )


def clear_app_input_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
) -> list[int]:
    """Clear persisted per-app input routing (app returns to system default)."""
    return _clear_app_device(
        process_id=process_id,
        process_name=process_name,
        flow="input",
    )


def get_app_input_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
) -> dict[int, str]:
    """Return current persisted input route for the PID as a plain MMDevice id."""
    return _get_app_device(
        process_id=process_id,
        process_name=process_name,
        flow="input",
    )

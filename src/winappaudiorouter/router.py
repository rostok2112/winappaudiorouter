from __future__ import annotations

from pycaw.constants import EDataFlow, ERole

from .com import com_initialized
from .device_ids import pack_render_device_id, unpack_device_id
from .devices import _list_output_devices_noinit, match_output_device
from .models import AudioDeviceInfo
from .policy_config import PolicyConfigFactory
from .sessions import _enumerate_sessions_noinit, _resolve_process_ids_from_sessions


def _set_route_for_processes(process_ids: list[int], device_id: str | None) -> None:
    packed_device_id = pack_render_device_id(device_id)
    with PolicyConfigFactory() as factory:
        for pid in process_ids:
            factory.set_persisted_default_endpoint(
                process_id=pid,
                flow=EDataFlow.eRender.value,
                role=ERole.eConsole.value,
                packed_device_id=packed_device_id,
            )
            factory.set_persisted_default_endpoint(
                process_id=pid,
                flow=EDataFlow.eRender.value,
                role=ERole.eMultimedia.value,
                packed_device_id=packed_device_id,
            )


def set_app_output_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
    device: str,
) -> dict[int, AudioDeviceInfo]:
    """Route one app (or all matching app PIDs) to a specific output device."""
    with com_initialized():
        candidates = _list_output_devices_noinit()
        target = match_output_device(device, candidates)
        sessions = _enumerate_sessions_noinit()
        pids = _resolve_process_ids_from_sessions(process_id, process_name, sessions)
        _set_route_for_processes(pids, target.id)
        return {pid: target for pid in pids}


def clear_app_output_device(
    *, process_id: int | None = None, process_name: str | None = None
) -> list[int]:
    """Clear persisted per-app output routing (app returns to system default)."""
    with com_initialized():
        sessions = _enumerate_sessions_noinit()
        pids = _resolve_process_ids_from_sessions(process_id, process_name, sessions)
        _set_route_for_processes(pids, None)
        return pids


def get_app_output_device(
    *,
    process_id: int | None = None,
    process_name: str | None = None,
) -> dict[int, str]:
    """Return current persisted route for the PID as a plain MMDevice id."""
    with com_initialized():
        sessions = _enumerate_sessions_noinit()

        # Resolve the PID(s) based on process_name or process_id
        pids = _resolve_process_ids_from_sessions(process_id, process_name, sessions)

        if not pids:
            return {}

        results = {}
        with PolicyConfigFactory() as factory:
            for pid in pids:
                policy_device_id = factory.get_persisted_default_endpoint(
                    process_id=pid,
                    flow=EDataFlow.eRender.value,
                    role=ERole.eMultimedia.value,
                )
                unpacked_device = unpack_device_id(policy_device_id)
                if unpacked_device:
                    results[pid] = unpacked_device

        return results

from __future__ import annotations

import comtypes
import psutil
from pycaw.api.audiopolicy import IAudioSessionControl2, IAudioSessionManager2
from pycaw.constants import DEVICE_STATE, EDataFlow
from pycaw.pycaw import AudioUtilities

from .com import com_initialized
from .errors import AudioRoutingError
from .models import AudioSessionInfo


def _enumerate_sessions_noinit() -> list[AudioSessionInfo]:
    devices = AudioUtilities.GetAllDevices(
        data_flow=EDataFlow.eRender.value,
        device_state=DEVICE_STATE.ACTIVE.value,
    )
    sessions: list[AudioSessionInfo] = []
    seen: set[tuple[str, str]] = set()

    for device in devices:
        try:
            manager_iface = device._dev.Activate(  # pylint: disable=protected-access
                IAudioSessionManager2._iid_, comtypes.CLSCTX_ALL, None
            )
            manager = manager_iface.QueryInterface(IAudioSessionManager2)
            enumerator = manager.GetSessionEnumerator()
        except Exception:
            continue

        count = enumerator.GetCount()
        for index in range(count):
            session = enumerator.GetSession(index)
            if session is None:
                continue

            control = session.QueryInterface(IAudioSessionControl2)
            process_id = int(control.GetProcessId())
            instance_id = control.GetSessionInstanceIdentifier() or ""

            key = (device.id, instance_id)
            if key in seen:
                continue
            seen.add(key)

            process_name: str | None = None
            if process_id > 0:
                try:
                    process_name = psutil.Process(process_id).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = None

            sessions.append(
                AudioSessionInfo(
                    process_id=process_id,
                    process_name=process_name,
                    device_id=device.id,
                    device_name=device.FriendlyName or "",
                    session_identifier=control.GetSessionIdentifier() or "",
                    session_instance_identifier=instance_id,
                )
            )

    sessions.sort(key=lambda x: (x.process_name or "", x.process_id, x.device_name))
    return sessions


def list_app_sessions() -> list[AudioSessionInfo]:
    """List current render audio sessions across active output devices."""
    with com_initialized():
        return _enumerate_sessions_noinit()


def _resolve_process_ids_from_sessions(
    process_id: int | None,
    process_name: str | None,
    sessions: list[AudioSessionInfo],
) -> list[int]:
    if process_id is not None:
        return [process_id]
    if not process_name:
        raise AudioRoutingError("Provide either process_id or process_name.")

    name = process_name.lower()
    pids = sorted(
        {
            session.process_id
            for session in sessions
            if session.process_id > 0
            and session.process_name
            and session.process_name.lower() == name
        }
    )
    if not pids:
        raise AudioRoutingError(
            f"No active audio sessions found for process name '{process_name}'."
        )
    return pids


def resolve_process_ids(process_id: int | None, process_name: str | None) -> list[int]:
    with com_initialized():
        sessions = _enumerate_sessions_noinit()
        return _resolve_process_ids_from_sessions(process_id, process_name, sessions)

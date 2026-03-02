from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioDeviceInfo:
    id: str
    name: str
    is_default: bool


@dataclass(frozen=True)
class AudioSessionInfo:
    process_id: int
    process_name: str | None
    device_id: str
    device_name: str
    session_identifier: str
    session_instance_identifier: str

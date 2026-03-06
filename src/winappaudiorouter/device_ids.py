from __future__ import annotations

from .constants import (
    DEVINTERFACE_AUDIO_CAPTURE,
    DEVINTERFACE_AUDIO_RENDER,
    MMDEVAPI_TOKEN,
)


def _pack_device_id(device_id: str | None, interface_id: str) -> str | None:
    if not device_id:
        return None
    return f"{MMDEVAPI_TOKEN}{device_id}{interface_id}"


def pack_render_device_id(device_id: str | None) -> str | None:
    return _pack_device_id(device_id, DEVINTERFACE_AUDIO_RENDER)


def pack_capture_device_id(device_id: str | None) -> str | None:
    return _pack_device_id(device_id, DEVINTERFACE_AUDIO_CAPTURE)


def unpack_device_id(policy_device_id: str | None) -> str | None:
    if not policy_device_id:
        return None
    unpacked = policy_device_id
    if unpacked.startswith(MMDEVAPI_TOKEN):
        unpacked = unpacked[len(MMDEVAPI_TOKEN) :]
    for interface_id in (DEVINTERFACE_AUDIO_RENDER, DEVINTERFACE_AUDIO_CAPTURE):
        if unpacked.endswith(interface_id):
            unpacked = unpacked[: -len(interface_id)]
            break
    return unpacked

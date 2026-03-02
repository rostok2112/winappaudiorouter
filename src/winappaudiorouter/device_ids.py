from __future__ import annotations

from .constants import DEVINTERFACE_AUDIO_RENDER, MMDEVAPI_TOKEN


def pack_render_device_id(device_id: str | None) -> str | None:
    if not device_id:
        return None
    return f"{MMDEVAPI_TOKEN}{device_id}{DEVINTERFACE_AUDIO_RENDER}"


def unpack_device_id(policy_device_id: str | None) -> str | None:
    if not policy_device_id:
        return None
    unpacked = policy_device_id
    if unpacked.startswith(MMDEVAPI_TOKEN):
        unpacked = unpacked[len(MMDEVAPI_TOKEN) :]
    if unpacked.endswith(DEVINTERFACE_AUDIO_RENDER):
        unpacked = unpacked[: -len(DEVINTERFACE_AUDIO_RENDER)]
    return unpacked

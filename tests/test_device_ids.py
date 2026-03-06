from __future__ import annotations

from winappaudiorouter.constants import (
    DEVINTERFACE_AUDIO_CAPTURE,
    DEVINTERFACE_AUDIO_RENDER,
    MMDEVAPI_TOKEN,
)
from winappaudiorouter.device_ids import (
    pack_capture_device_id,
    pack_render_device_id,
    unpack_device_id,
)


def test_pack_render_device_id() -> None:
    raw = "{0.0.0.00000000}.{abc}"
    packed = pack_render_device_id(raw)
    assert packed == f"{MMDEVAPI_TOKEN}{raw}{DEVINTERFACE_AUDIO_RENDER}"


def test_pack_none_returns_none() -> None:
    assert pack_render_device_id(None) is None


def test_pack_capture_device_id() -> None:
    raw = "{0.0.1.00000000}.{def}"
    packed = pack_capture_device_id(raw)
    assert packed == f"{MMDEVAPI_TOKEN}{raw}{DEVINTERFACE_AUDIO_CAPTURE}"


def test_unpack_roundtrip() -> None:
    raw = "{0.0.0.00000000}.{abc}"
    packed = pack_render_device_id(raw)
    assert unpack_device_id(packed) == raw


def test_unpack_capture_roundtrip() -> None:
    raw = "{0.0.1.00000000}.{def}"
    packed = pack_capture_device_id(raw)
    assert unpack_device_id(packed) == raw


def test_unpack_none_returns_none() -> None:
    assert unpack_device_id(None) is None

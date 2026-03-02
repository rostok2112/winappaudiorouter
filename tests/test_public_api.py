from __future__ import annotations

import winappaudiorouter as war


def test_public_exports() -> None:
    assert hasattr(war, "AudioRoutingError")
    assert hasattr(war, "AudioDeviceInfo")
    assert hasattr(war, "AudioSessionInfo")
    assert hasattr(war, "list_output_devices")
    assert hasattr(war, "list_app_sessions")
    assert hasattr(war, "set_app_output_device")
    assert hasattr(war, "clear_app_output_device")
    assert hasattr(war, "get_app_output_device")


def test_version() -> None:
    assert war.__version__ == "1.0.2"

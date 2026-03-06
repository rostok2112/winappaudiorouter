from __future__ import annotations

from contextlib import nullcontext

from pycaw.constants import EDataFlow, ERole

from winappaudiorouter import router
from winappaudiorouter.constants import DEVINTERFACE_AUDIO_CAPTURE, MMDEVAPI_TOKEN
from winappaudiorouter.models import AudioSessionInfo


def test_set_route_for_processes_input_uses_capture_flow(
    monkeypatch,
) -> None:
    calls: list[tuple[int, int, int, str | None]] = []

    class DummyFactory:
        def __enter__(self) -> "DummyFactory":
            return self

        def __exit__(self, *_exc_info: object) -> None:
            return None

        def set_persisted_default_endpoint(
            self,
            process_id: int,
            flow: int,
            role: int,
            packed_device_id: str | None,
        ) -> None:
            calls.append((process_id, flow, role, packed_device_id))

    monkeypatch.setattr(router, "PolicyConfigFactory", lambda: DummyFactory())

    router._set_route_for_processes([1234], "{0.0.1.00000000}.{abc}", "input")

    assert calls == [
        (
            1234,
            EDataFlow.eCapture.value,
            ERole.eConsole.value,
            f"{MMDEVAPI_TOKEN}{{0.0.1.00000000}}.{{abc}}{DEVINTERFACE_AUDIO_CAPTURE}",
        ),
        (
            1234,
            EDataFlow.eCapture.value,
            ERole.eMultimedia.value,
            f"{MMDEVAPI_TOKEN}{{0.0.1.00000000}}.{{abc}}{DEVINTERFACE_AUDIO_CAPTURE}",
        ),
    ]


def test_get_app_input_device_uses_capture_flow(monkeypatch) -> None:
    flows: list[int] = []

    class DummyFactory:
        def __enter__(self) -> "DummyFactory":
            return self

        def __exit__(self, *_exc_info: object) -> None:
            return None

        def get_persisted_default_endpoint(
            self,
            process_id: int,
            flow: int,
            role: int,
        ) -> str:
            assert process_id == 999
            assert role == ERole.eMultimedia.value
            flows.append(flow)
            return f"{MMDEVAPI_TOKEN}mic-id{DEVINTERFACE_AUDIO_CAPTURE}"

    monkeypatch.setattr(router, "com_initialized", nullcontext)
    monkeypatch.setattr(router, "PolicyConfigFactory", lambda: DummyFactory())
    monkeypatch.setattr(
        router,
        "_enumerate_input_sessions_noinit",
        lambda: [
            AudioSessionInfo(
                process_id=999,
                process_name="obs64.exe",
                device_id="session-device",
                device_name="USB Mic",
                session_identifier="session",
                session_instance_identifier="session-instance",
            )
        ],
    )

    routed = router.get_app_input_device(process_name="obs64.exe")

    assert routed == {999: "mic-id"}
    assert flows == [EDataFlow.eCapture.value]

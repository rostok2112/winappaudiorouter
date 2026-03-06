from __future__ import annotations

from contextlib import nullcontext

from pycaw.constants import EDataFlow, ERole

from winappaudiorouter import router
from winappaudiorouter.constants import DEVINTERFACE_AUDIO_CAPTURE, MMDEVAPI_TOKEN
from winappaudiorouter.models import AudioDeviceInfo, AudioSessionInfo


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


def test_helper_dispatchers_cover_input_and_output_paths(monkeypatch) -> None:
    output_device = AudioDeviceInfo(id="out-id", name="Speakers", is_default=True)
    input_device = AudioDeviceInfo(id="in-id", name="Mic", is_default=False)

    monkeypatch.setattr(router, "_list_output_devices_noinit", lambda: ["out-candidates"])
    monkeypatch.setattr(router, "_list_input_devices_noinit", lambda: ["in-candidates"])
    monkeypatch.setattr(router, "match_output_device", lambda device, candidates: output_device)
    monkeypatch.setattr(router, "match_input_device", lambda device, candidates: input_device)
    monkeypatch.setattr(router, "_enumerate_output_sessions_noinit", lambda: ["out-sessions"])
    monkeypatch.setattr(router, "_enumerate_input_sessions_noinit", lambda: ["in-sessions"])

    assert router._pack_device_id("output", "raw-id") == router.pack_render_device_id("raw-id")
    assert router._matched_device("output", "Speakers") == output_device
    assert router._matched_device("input", "Mic") == input_device
    assert router._sessions_for_flow("output") == ["out-sessions"]
    assert router._sessions_for_flow("input") == ["in-sessions"]


def test_set_and_clear_app_device_delegate_to_routing(monkeypatch) -> None:
    target = AudioDeviceInfo(id="device-id", name="Speakers", is_default=True)
    route_calls: list[tuple[list[int], str | None, str]] = []

    monkeypatch.setattr(router, "com_initialized", nullcontext)
    monkeypatch.setattr(router, "_matched_device", lambda flow, device: target)
    monkeypatch.setattr(router, "_sessions_for_flow", lambda flow: ["sessions"])
    monkeypatch.setattr(router, "_resolve_process_ids_from_sessions", lambda process_id, process_name, sessions: [1, 2])
    monkeypatch.setattr(
        router,
        "_set_route_for_processes",
        lambda pids, device_id, flow: route_calls.append((pids, device_id, flow)),
    )

    routed = router._set_app_device(process_name="chrome.exe", process_id=None, device="Speakers", flow="output")
    cleared = router._clear_app_device(process_name="chrome.exe", process_id=None, flow="input")

    assert routed == {1: target, 2: target}
    assert cleared == [1, 2]
    assert route_calls == [
        ([1, 2], "device-id", "output"),
        ([1, 2], None, "input"),
    ]


def test_get_app_device_returns_empty_for_no_pids(monkeypatch) -> None:
    monkeypatch.setattr(router, "com_initialized", nullcontext)
    monkeypatch.setattr(router, "_sessions_for_flow", lambda flow: ["sessions"])
    monkeypatch.setattr(router, "_resolve_process_ids_from_sessions", lambda process_id, process_name, sessions: [])

    assert router._get_app_device(process_name="chrome.exe", process_id=None, flow="output") == {}


def test_get_app_device_skips_empty_unpacked_values(monkeypatch) -> None:
    class DummyFactory:
        def __enter__(self) -> "DummyFactory":
            return self

        def __exit__(self, *_exc_info: object) -> None:
            return None

        def get_persisted_default_endpoint(self, process_id: int, flow: int, role: int) -> str:
            return f"policy:{process_id}"

    monkeypatch.setattr(router, "com_initialized", nullcontext)
    monkeypatch.setattr(router, "_sessions_for_flow", lambda flow: ["sessions"])
    monkeypatch.setattr(
        router,
        "_resolve_process_ids_from_sessions",
        lambda process_id, process_name, sessions: [10, 20],
    )
    monkeypatch.setattr(router, "PolicyConfigFactory", lambda: DummyFactory())
    monkeypatch.setattr(
        router,
        "unpack_device_id",
        lambda policy_id: None if policy_id == "policy:10" else "device-20",
    )

    assert router._get_app_device(process_name="chrome.exe", process_id=None, flow="output") == {20: "device-20"}


def test_public_router_wrappers_delegate_to_internal_helpers(monkeypatch) -> None:
    device = AudioDeviceInfo(id="device-id", name="Speakers", is_default=False)
    monkeypatch.setattr(router, "_set_app_device", lambda **kwargs: {1: device})
    monkeypatch.setattr(router, "_clear_app_device", lambda **kwargs: [1])
    monkeypatch.setattr(router, "_get_app_device", lambda **kwargs: {1: "device-id"})

    assert router.set_app_output_device(process_id=1, device="Speakers") == {1: device}
    assert router.clear_app_output_device(process_id=1) == [1]
    assert router.get_app_output_device(process_id=1) == {1: "device-id"}
    assert router.set_app_input_device(process_id=1, device="Mic") == {1: device}
    assert router.clear_app_input_device(process_id=1) == [1]
    assert router.get_app_input_device(process_id=1) == {1: "device-id"}

from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from winappaudiorouter import devices, sessions
from winappaudiorouter.errors import AudioRoutingError
from winappaudiorouter.models import AudioDeviceInfo, AudioSessionInfo


class _FakeControl:
    def __init__(self, process_id: int, instance_id: str, session_id: str) -> None:
        self._process_id = process_id
        self._instance_id = instance_id
        self._session_id = session_id

    def GetProcessId(self) -> int:
        return self._process_id

    def GetSessionInstanceIdentifier(self) -> str:
        return self._instance_id

    def GetSessionIdentifier(self) -> str:
        return self._session_id


class _FakeSession:
    def __init__(self, control: _FakeControl) -> None:
        self._control = control

    def QueryInterface(self, _iface: object) -> _FakeControl:
        return self._control


class _FakeEnumerator:
    def __init__(self, session_items: list[object | None]) -> None:
        self._session_items = session_items

    def GetCount(self) -> int:
        return len(self._session_items)

    def GetSession(self, index: int) -> object | None:
        return self._session_items[index]


class _FakeManager:
    def __init__(self, session_items: list[object | None]) -> None:
        self._enumerator = _FakeEnumerator(session_items)

    def GetSessionEnumerator(self) -> _FakeEnumerator:
        return self._enumerator


class _FakeManagerIface:
    def __init__(self, session_items: list[object | None]) -> None:
        self._manager = _FakeManager(session_items)

    def QueryInterface(self, _iface: object) -> _FakeManager:
        return self._manager


class _FakeEndpoint:
    def __init__(
        self,
        session_items: list[object | None] | None = None,
        *,
        fails: bool = False,
    ) -> None:
        self._session_items = session_items or []
        self._fails = fails

    def Activate(self, _iid: object, _ctx: object, _reserved: object) -> _FakeManagerIface:
        if self._fails:
            raise RuntimeError("activate failed")
        return _FakeManagerIface(self._session_items)


class _FakeDevice:
    def __init__(
        self,
        device_id: str,
        friendly_name: str | None,
        session_items: list[object | None] | None = None,
        *,
        fails: bool = False,
    ) -> None:
        self.id = device_id
        self.FriendlyName = friendly_name
        self._dev = _FakeEndpoint(session_items, fails=fails)


def test_list_devices_noinit_marks_default_and_handles_input_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []

    class _Enumerator:
        def GetDefaultAudioEndpoint(self, flow: int, role: int) -> str:
            calls.append(flow)
            assert role == devices.ERole.eMultimedia.value
            return "endpoint"

    monkeypatch.setattr(devices.AudioUtilities, "GetDeviceEnumerator", lambda: _Enumerator())
    monkeypatch.setattr(
        devices.AudioUtilities,
        "CreateDevice",
        lambda endpoint: SimpleNamespace(id="default-id") if endpoint == "endpoint" else None,
    )
    monkeypatch.setattr(
        devices.AudioUtilities,
        "GetAllDevices",
        lambda data_flow, device_state: [
            _FakeDevice("default-id", "USB Mic"),
            _FakeDevice("other-id", None),
        ],
    )

    result = devices._list_devices_noinit("input")

    assert calls == [devices.EDataFlow.eCapture.value]
    assert result == [
        AudioDeviceInfo(id="default-id", name="USB Mic", is_default=True),
        AudioDeviceInfo(id="other-id", name="", is_default=False),
    ]


def test_default_device_id_returns_none_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        devices.AudioUtilities,
        "GetDeviceEnumerator",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    assert devices._default_device_id("output") is None


def test_list_device_wrappers_use_internal_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = [AudioDeviceInfo(id="id", name="Speakers", is_default=True)]
    monkeypatch.setattr(devices, "com_initialized", nullcontext)
    monkeypatch.setattr(devices, "_list_output_devices_noinit", lambda: expected)
    monkeypatch.setattr(devices, "_list_input_devices_noinit", lambda: expected)

    assert devices.list_output_devices() == expected
    assert devices.list_input_devices() == expected


def test_find_device_wrappers_use_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = AudioDeviceInfo(id="id", name="Speakers", is_default=True)
    monkeypatch.setattr(devices, "com_initialized", nullcontext)
    monkeypatch.setattr(devices, "_list_output_devices_noinit", lambda: [expected])
    monkeypatch.setattr(devices, "_list_input_devices_noinit", lambda: [expected])

    assert devices.find_output_device("id") == expected
    assert devices.find_input_device("Speakers") == expected


@pytest.mark.parametrize(
    ("matcher", "device", "candidates", "message"),
    [
        (devices.match_output_device, "id", [], "No active output devices"),
        (
            devices.match_output_device,
            "Speakers",
            [
                AudioDeviceInfo(id="a", name="Speakers", is_default=False),
                AudioDeviceInfo(id="b", name="Speakers", is_default=False),
            ],
            "Multiple devices match",
        ),
        (
            devices.match_input_device,
            "Mic",
            [
                AudioDeviceInfo(id="a", name="USB Mic", is_default=False),
                AudioDeviceInfo(id="b", name="Desk Mic", is_default=False),
            ],
            "Multiple devices contain",
        ),
    ],
)
def test_match_device_error_branches(
    matcher: object,
    device: str,
    candidates: list[AudioDeviceInfo],
    message: str,
) -> None:
    with pytest.raises(AudioRoutingError, match=message):
        matcher(device, candidates)


def test_enumerate_sessions_noinit_filters_duplicates_and_lookup_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_items_device_a = [
        _FakeSession(_FakeControl(101, "dup", "session-1")),
        _FakeSession(_FakeControl(101, "dup", "session-2")),
        None,
        _FakeSession(_FakeControl(0, "zero", "session-zero")),
    ]
    session_items_device_b = [
        _FakeSession(_FakeControl(202, "unique", "session-unique")),
    ]

    calls: list[int] = []

    def fake_get_all_devices(data_flow: int, device_state: int) -> list[_FakeDevice]:
        calls.append(data_flow)
        assert device_state == sessions.DEVICE_STATE.ACTIVE.value
        return [
            _FakeDevice("device-b", "Speakers", session_items_device_b),
            _FakeDevice("device-a", "Microphone", session_items_device_a),
            _FakeDevice("device-c", "Broken", fails=True),
        ]

    def fake_process(pid: int) -> SimpleNamespace:
        if pid == 101:
            return SimpleNamespace(name=lambda: "zoom.exe")
        raise sessions.psutil.NoSuchProcess(pid)

    monkeypatch.setattr(sessions.AudioUtilities, "GetAllDevices", fake_get_all_devices)
    monkeypatch.setattr(sessions.psutil, "Process", fake_process)

    result = sessions._enumerate_sessions_noinit("input")

    assert calls == [sessions.EDataFlow.eCapture.value]
    assert [
        (
            item.process_id,
            item.process_name,
            item.device_id,
            item.session_instance_identifier,
        )
        for item in result
    ] == [
        (0, None, "device-a", "zero"),
        (202, None, "device-b", "unique"),
        (101, "zoom.exe", "device-a", "dup"),
    ]


def test_list_and_resolve_session_wrappers(monkeypatch: pytest.MonkeyPatch) -> None:
    session_list = [
        AudioSessionInfo(
            process_id=42,
            process_name="zoom.exe",
            device_id="device-id",
            device_name="Speakers",
            session_identifier="session-id",
            session_instance_identifier="instance-id",
        )
    ]

    monkeypatch.setattr(sessions, "com_initialized", nullcontext)
    monkeypatch.setattr(sessions, "_enumerate_output_sessions_noinit", lambda: session_list)
    monkeypatch.setattr(sessions, "_enumerate_input_sessions_noinit", lambda: session_list)

    assert sessions.list_app_sessions() == session_list
    assert sessions.list_input_sessions() == session_list
    assert sessions.resolve_process_ids(None, "zoom.exe") == [42]
    assert sessions.resolve_input_process_ids(None, "zoom.exe") == [42]


def test_resolve_process_ids_from_sessions_branches() -> None:
    session_list = [
        AudioSessionInfo(
            process_id=10,
            process_name="chrome.exe",
            device_id="device-id",
            device_name="Speakers",
            session_identifier="session-id",
            session_instance_identifier="instance-id-1",
        ),
        AudioSessionInfo(
            process_id=11,
            process_name="CHROME.EXE",
            device_id="device-id",
            device_name="Speakers",
            session_identifier="session-id",
            session_instance_identifier="instance-id-2",
        ),
    ]

    assert sessions._resolve_process_ids_from_sessions(99, None, session_list) == [99]
    assert sessions._resolve_process_ids_from_sessions(None, "chrome.exe", session_list) == [10, 11]

    with pytest.raises(AudioRoutingError, match="Provide either process_id or process_name"):
        sessions._resolve_process_ids_from_sessions(None, None, session_list)

    with pytest.raises(AudioRoutingError, match="No active audio sessions found"):
        sessions._resolve_process_ids_from_sessions(None, "obs64.exe", session_list)

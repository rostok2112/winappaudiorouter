from __future__ import annotations

import ctypes
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from comtypes import GUID

from winappaudiorouter import com, winrt
from winappaudiorouter.constants import (
    BUILD_21H2,
    BUILD_WINDOWS_10_1803,
    IID_POLICY_CONFIG_21H2,
    IID_POLICY_CONFIG_DOWNLEVEL,
)
from winappaudiorouter.errors import AudioRoutingError


def test_com_initialized_calls_initialize_and_uninitialize(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(com.comtypes, "CoInitialize", lambda: calls.append("init"))
    monkeypatch.setattr(com.comtypes, "CoUninitialize", lambda: calls.append("uninit"))

    with com.com_initialized():
        calls.append("body")

    assert calls == ["init", "body", "uninit"]


def test_load_combase_api_configures_functions(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeFunction:
        def __call__(self, *_args: object) -> int:
            return 0

    class FakeCombase:
        WindowsCreateString = FakeFunction()
        WindowsDeleteString = FakeFunction()
        WindowsGetStringRawBuffer = FakeFunction()
        RoGetActivationFactory = FakeFunction()

    winrt._load_combase_api.cache_clear()
    monkeypatch.setattr(winrt.ctypes, "WinDLL", lambda name: FakeCombase())

    api = winrt._load_combase_api()

    assert api.windows_create_string.argtypes[0] is ctypes.c_wchar_p
    assert api.windows_create_string.restype is ctypes.c_long
    assert api.windows_delete_string.argtypes == [ctypes.c_void_p]
    assert api.windows_get_string_raw_buffer.restype is ctypes.c_wchar_p
    assert api.ro_get_activation_factory.restype is ctypes.c_long

    winrt._load_combase_api.cache_clear()


def test_check_hr_raises_on_negative_hresult() -> None:
    with pytest.raises(AudioRoutingError, match="Example failed with HRESULT"):
        winrt.check_hr(-1, "Example")


def test_hstring_none_yields_empty_handle() -> None:
    with winrt.hstring(None) as handle:
        assert not handle


def test_hstring_creates_and_deletes_handle(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []

    def fake_create(value: str, length: int, handle_ptr: object) -> int:
        calls.append((value, length))
        handle_ptr._obj.value = 77
        return 0

    def fake_delete(handle: ctypes.c_void_p) -> int:
        calls.append(handle.value)
        return 0

    api = SimpleNamespace(
        windows_create_string=fake_create,
        windows_delete_string=fake_delete,
    )
    monkeypatch.setattr(winrt, "_load_combase_api", lambda: api)

    with winrt.hstring("abc") as handle:
        assert handle.value == 77

    assert calls == [("abc", 3), 77]


def test_delete_hstring_only_calls_delete_for_truthy_handle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    deleted: list[int] = []
    api = SimpleNamespace(
        windows_delete_string=lambda handle: deleted.append(handle.value),
    )
    monkeypatch.setattr(winrt, "_load_combase_api", lambda: api)

    winrt.delete_hstring(ctypes.c_void_p())
    winrt.delete_hstring(ctypes.c_void_p(11))

    assert deleted == [11]


def test_hstring_to_string_handles_none_and_null_raw(monkeypatch: pytest.MonkeyPatch) -> None:
    assert winrt.hstring_to_string(ctypes.c_void_p()) is None

    api = SimpleNamespace(
        windows_get_string_raw_buffer=lambda _handle, _length_ptr: None,
    )
    monkeypatch.setattr(winrt, "_load_combase_api", lambda: api)

    assert winrt.hstring_to_string(ctypes.c_void_p(5)) is None


def test_hstring_to_string_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    buffer = ctypes.create_unicode_buffer("route")

    def fake_get_buffer(_handle: ctypes.c_void_p, length_ptr: object) -> int:
        length_ptr._obj.value = 5
        return ctypes.addressof(buffer)

    api = SimpleNamespace(windows_get_string_raw_buffer=fake_get_buffer)
    monkeypatch.setattr(winrt, "_load_combase_api", lambda: api)

    assert winrt.hstring_to_string(ctypes.c_void_p(9)) == "route"


@pytest.mark.parametrize(
    ("build", "expected"),
    [
        (BUILD_WINDOWS_10_1803, IID_POLICY_CONFIG_DOWNLEVEL),
        (BUILD_21H2, IID_POLICY_CONFIG_21H2),
    ],
)
def test_resolve_policy_config_iid_selects_expected_guid(
    monkeypatch: pytest.MonkeyPatch,
    build: int,
    expected: GUID,
) -> None:
    monkeypatch.setattr(winrt.sys, "getwindowsversion", lambda: SimpleNamespace(build=build))

    assert winrt.resolve_policy_config_iid() == expected


def test_resolve_policy_config_iid_rejects_old_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        winrt.sys,
        "getwindowsversion",
        lambda: SimpleNamespace(build=BUILD_WINDOWS_10_1803 - 1),
    )

    with pytest.raises(AudioRoutingError, match="Windows 10 1803"):
        winrt.resolve_policy_config_iid()


def test_ro_get_activation_factory_returns_pointer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    iid = GUID("{00000000-0000-0000-0000-000000000000}")

    @contextmanager
    def fake_hstring(value: str):
        assert value == "Class.Id"
        yield ctypes.c_void_p(55)

    def fake_factory(
        class_id_hstring: ctypes.c_void_p,
        iid_ptr: object,
        ptr: object,
    ) -> int:
        assert class_id_hstring.value == 55
        ptr._obj.value = 88
        return 0

    api = SimpleNamespace(ro_get_activation_factory=fake_factory)
    monkeypatch.setattr(winrt, "_load_combase_api", lambda: api)
    monkeypatch.setattr(winrt, "hstring", fake_hstring)

    ptr = winrt.ro_get_activation_factory("Class.Id", iid)

    assert ptr.value == 88

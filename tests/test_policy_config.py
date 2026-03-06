from __future__ import annotations

import ctypes
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from winappaudiorouter import policy_config
from winappaudiorouter.constants import (
    HR_ERROR_NOT_FOUND,
    INDEX_GET_PERSISTED_DEFAULT_ENDPOINT,
    INDEX_RELEASE,
    INDEX_SET_PERSISTED_DEFAULT_ENDPOINT,
    POLICY_CONFIG_CLASS_ID,
)


def _factory_with_ptr(ptr: object = "factory-ptr") -> policy_config.PolicyConfigFactory:
    factory = object.__new__(policy_config.PolicyConfigFactory)
    factory._ptr = ptr
    return factory


def _patch_vtable(
    monkeypatch: pytest.MonkeyPatch,
    functions: dict[int, object],
) -> None:
    size = max(INDEX_RELEASE, INDEX_SET_PERSISTED_DEFAULT_ENDPOINT, INDEX_GET_PERSISTED_DEFAULT_ENDPOINT) + 1
    vtable = [None] * size
    for index in functions:
        vtable[index] = index

    monkeypatch.setattr(
        policy_config.ctypes,
        "cast",
        lambda _ptr, _type: SimpleNamespace(contents=vtable),
    )
    monkeypatch.setattr(
        policy_config.ctypes,
        "WINFUNCTYPE",
        lambda *_sig: (lambda addr: functions[addr]),
    )


def test_policy_config_factory_init_uses_activation_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(policy_config, "resolve_policy_config_iid", lambda: "iid-value")
    monkeypatch.setattr(
        policy_config,
        "ro_get_activation_factory",
        lambda class_id, iid: (class_id, iid, "ptr-value"),
    )

    factory = policy_config.PolicyConfigFactory()

    assert factory._ptr == (POLICY_CONFIG_CLASS_ID, "iid-value", "ptr-value")


def test_policy_config_close_is_noop_for_empty_pointer() -> None:
    factory = _factory_with_ptr(ctypes.c_void_p())
    factory.close()
    assert not factory._ptr


def test_policy_config_close_releases_pointer(monkeypatch: pytest.MonkeyPatch) -> None:
    released: list[object] = []
    _patch_vtable(monkeypatch, {INDEX_RELEASE: lambda ptr: released.append(ptr) or 0})
    factory = _factory_with_ptr("ptr-value")

    factory.close()

    assert released == ["ptr-value"]
    assert not factory._ptr


def test_policy_config_context_manager_exit_calls_close(monkeypatch: pytest.MonkeyPatch) -> None:
    factory = _factory_with_ptr("ptr-value")
    called: list[str] = []
    monkeypatch.setattr(factory, "close", lambda: called.append("close"))

    assert factory.__enter__() is factory
    factory.__exit__(None, None, None)

    assert called == ["close"]


def test_set_persisted_default_endpoint_invokes_vtable_function(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, int, int, int, object]] = []

    @contextmanager
    def fake_hstring(value: str | None):
        assert value == "packed-id"
        yield "device-hstring"

    _patch_vtable(
        monkeypatch,
        {
            INDEX_SET_PERSISTED_DEFAULT_ENDPOINT: (
                lambda ptr, pid, flow, role, device_hstring: calls.append(
                    (ptr, pid, flow, role, device_hstring)
                )
                or 0
            )
        },
    )
    monkeypatch.setattr(policy_config, "hstring", fake_hstring)

    factory = _factory_with_ptr()
    factory.set_persisted_default_endpoint(1234, 1, 2, "packed-id")

    assert calls == [("factory-ptr", 1234, 1, 2, "device-hstring")]


def test_get_persisted_default_endpoint_returns_none_when_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_vtable(
        monkeypatch,
        {INDEX_GET_PERSISTED_DEFAULT_ENDPOINT: lambda *_args: HR_ERROR_NOT_FOUND},
    )

    factory = _factory_with_ptr()

    assert factory.get_persisted_default_endpoint(1234, 1, 2) is None


def test_get_persisted_default_endpoint_returns_none_for_empty_hstring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_vtable(
        monkeypatch,
        {INDEX_GET_PERSISTED_DEFAULT_ENDPOINT: lambda *_args: 0},
    )

    factory = _factory_with_ptr()

    assert factory.get_persisted_default_endpoint(1234, 1, 2) is None


def test_get_persisted_default_endpoint_converts_and_deletes_hstring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    deleted: list[ctypes.c_void_p] = []

    def fake_get(_ptr: object, _pid: int, _flow: int, _role: int, out_ptr: object) -> int:
        out_ptr._obj.value = 44
        return 0

    _patch_vtable(monkeypatch, {INDEX_GET_PERSISTED_DEFAULT_ENDPOINT: fake_get})
    monkeypatch.setattr(policy_config, "hstring_to_string", lambda handle: f"value:{handle.value}")
    monkeypatch.setattr(policy_config, "delete_hstring", lambda handle: deleted.append(handle))

    factory = _factory_with_ptr()
    value = factory.get_persisted_default_endpoint(1234, 1, 2)

    assert value == "value:44"
    assert len(deleted) == 1
    assert deleted[0].value == 44

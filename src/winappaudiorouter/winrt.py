from __future__ import annotations

import ctypes
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterator

from comtypes import GUID

from .constants import (
    BUILD_21H2,
    BUILD_WINDOWS_10_1803,
    IID_POLICY_CONFIG_21H2,
    IID_POLICY_CONFIG_DOWNLEVEL,
)
from .errors import AudioRoutingError


@dataclass(frozen=True)
class _CombaseApi:
    windows_create_string: object
    windows_delete_string: object
    windows_get_string_raw_buffer: object
    ro_get_activation_factory: object


@lru_cache(maxsize=1)
def _load_combase_api() -> _CombaseApi:
    combase = ctypes.WinDLL("combase")

    windows_create_string = combase.WindowsCreateString
    windows_create_string.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    windows_create_string.restype = ctypes.c_long

    windows_delete_string = combase.WindowsDeleteString
    windows_delete_string.argtypes = [ctypes.c_void_p]
    windows_delete_string.restype = ctypes.c_long

    windows_get_string_raw_buffer = combase.WindowsGetStringRawBuffer
    windows_get_string_raw_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    windows_get_string_raw_buffer.restype = ctypes.c_wchar_p

    ro_get_activation_factory = combase.RoGetActivationFactory
    ro_get_activation_factory.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(GUID),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    ro_get_activation_factory.restype = ctypes.c_long

    return _CombaseApi(
        windows_create_string=windows_create_string,
        windows_delete_string=windows_delete_string,
        windows_get_string_raw_buffer=windows_get_string_raw_buffer,
        ro_get_activation_factory=ro_get_activation_factory,
    )


def check_hr(hr: int, context: str) -> None:
    if hr < 0:
        raise AudioRoutingError(f"{context} failed with HRESULT 0x{hr & 0xFFFFFFFF:08X}")


@contextmanager
def hstring(value: str | None) -> Iterator[ctypes.c_void_p]:
    if value is None:
        yield ctypes.c_void_p()
        return

    api = _load_combase_api()
    handle = ctypes.c_void_p()
    hr = api.windows_create_string(value, len(value), ctypes.byref(handle))
    check_hr(hr, "WindowsCreateString")
    try:
        yield handle
    finally:
        api.windows_delete_string(handle)


def delete_hstring(handle: ctypes.c_void_p) -> None:
    if handle:
        _load_combase_api().windows_delete_string(handle)


def hstring_to_string(handle: ctypes.c_void_p) -> str | None:
    if not handle:
        return None
    api = _load_combase_api()
    length = ctypes.c_uint32()
    raw = api.windows_get_string_raw_buffer(handle, ctypes.byref(length))
    if raw is None:
        return None
    return ctypes.wstring_at(raw, length.value)


def resolve_policy_config_iid() -> GUID:
    build = sys.getwindowsversion().build
    if build < BUILD_WINDOWS_10_1803:
        raise AudioRoutingError(
            "Per-app output routing requires Windows 10 1803+ (build 17134 or newer)."
        )
    return IID_POLICY_CONFIG_21H2 if build >= BUILD_21H2 else IID_POLICY_CONFIG_DOWNLEVEL


def ro_get_activation_factory(class_id: str, iid: GUID) -> ctypes.c_void_p:
    api = _load_combase_api()
    with hstring(class_id) as class_id_hstring:
        ptr = ctypes.c_void_p()
        hr = api.ro_get_activation_factory(class_id_hstring, ctypes.byref(iid), ctypes.byref(ptr))
        check_hr(hr, "RoGetActivationFactory")
        return ptr

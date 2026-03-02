from __future__ import annotations

import ctypes

from .constants import (
    HR_ERROR_NOT_FOUND,
    INDEX_GET_PERSISTED_DEFAULT_ENDPOINT,
    INDEX_RELEASE,
    INDEX_SET_PERSISTED_DEFAULT_ENDPOINT,
    POLICY_CONFIG_CLASS_ID,
)
from .winrt import (
    check_hr,
    delete_hstring,
    hstring,
    hstring_to_string,
    resolve_policy_config_iid,
    ro_get_activation_factory,
)


class PolicyConfigFactory:
    """Raw WinRT factory for Windows.Media.Internal.AudioPolicyConfig."""

    def __init__(self) -> None:
        iid = resolve_policy_config_iid()
        self._ptr = ro_get_activation_factory(POLICY_CONFIG_CLASS_ID, iid)

    def close(self) -> None:
        if not self._ptr:
            return
        vtable = ctypes.cast(
            self._ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
        ).contents
        release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(
            vtable[INDEX_RELEASE]
        )
        release(self._ptr)
        self._ptr = ctypes.c_void_p()

    def __enter__(self) -> "PolicyConfigFactory":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def set_persisted_default_endpoint(
        self, process_id: int, flow: int, role: int, packed_device_id: str | None
    ) -> None:
        with hstring(packed_device_id) as device_hstring:
            vtable = ctypes.cast(
                self._ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
            ).contents
            func = ctypes.WINFUNCTYPE(
                ctypes.c_long,
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_void_p,
            )(vtable[INDEX_SET_PERSISTED_DEFAULT_ENDPOINT])
            hr = int(func(self._ptr, process_id, flow, role, device_hstring))
            check_hr(hr, "SetPersistedDefaultAudioEndpoint")

    def get_persisted_default_endpoint(
        self, process_id: int, flow: int, role: int
    ) -> str | None:
        vtable = ctypes.cast(
            self._ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
        ).contents
        func = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
        )(vtable[INDEX_GET_PERSISTED_DEFAULT_ENDPOINT])

        device_hstring = ctypes.c_void_p()
        hr = int(func(self._ptr, process_id, flow, role, ctypes.byref(device_hstring)))
        if hr == HR_ERROR_NOT_FOUND:
            return None
        check_hr(hr, "GetPersistedDefaultAudioEndpoint")
        if not device_hstring:
            return None
        try:
            return hstring_to_string(device_hstring)
        finally:
            delete_hstring(device_hstring)

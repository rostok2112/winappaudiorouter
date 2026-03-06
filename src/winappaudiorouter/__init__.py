from __future__ import annotations

from .devices import (
    find_input_device,
    find_output_device,
    list_input_devices,
    list_output_devices,
)
from .errors import AudioRoutingError
from .models import AudioDeviceInfo, AudioSessionInfo
from .router import (
    clear_app_input_device,
    clear_app_output_device,
    get_app_input_device,
    get_app_output_device,
    set_app_input_device,
    set_app_output_device,
)
from .sessions import (
    list_app_sessions,
    list_input_sessions,
    resolve_input_process_ids,
    resolve_process_ids,
)

__all__ = [
    "AudioRoutingError",
    "AudioDeviceInfo",
    "AudioSessionInfo",
    "list_output_devices",
    "list_input_devices",
    "find_output_device",
    "find_input_device",
    "list_app_sessions",
    "list_input_sessions",
    "resolve_process_ids",
    "resolve_input_process_ids",
    "set_app_output_device",
    "set_app_input_device",
    "clear_app_output_device",
    "clear_app_input_device",
    "get_app_output_device",
    "get_app_input_device",
]

__version__ = "1.1.1"

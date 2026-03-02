from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import comtypes


@contextmanager
def com_initialized() -> Iterator[None]:
    """Initialize COM for the current thread and always uninitialize."""
    comtypes.CoInitialize()
    try:
        yield
    finally:
        comtypes.CoUninitialize()

from __future__ import annotations

import pytest

from winappaudiorouter.devices import match_output_device
from winappaudiorouter.errors import AudioRoutingError
from winappaudiorouter.models import AudioDeviceInfo


def _devices() -> list[AudioDeviceInfo]:
    return [
        AudioDeviceInfo(id="id-default", name="Speakers (Realtek)", is_default=True),
        AudioDeviceInfo(id="id-hdmi", name="HDMI Output", is_default=False),
        AudioDeviceInfo(id="id-cable", name="Virtual Cable", is_default=False),
    ]


def test_match_by_exact_id() -> None:
    found = match_output_device("id-hdmi", _devices())
    assert found.id == "id-hdmi"


def test_match_by_exact_name_case_insensitive() -> None:
    found = match_output_device("speakers (realtek)", _devices())
    assert found.id == "id-default"


def test_match_by_partial_name() -> None:
    found = match_output_device("Cable", _devices())
    assert found.id == "id-cable"


def test_match_missing_raises() -> None:
    with pytest.raises(AudioRoutingError):
        match_output_device("not-found", _devices())

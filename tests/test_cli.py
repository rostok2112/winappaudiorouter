from __future__ import annotations

import pytest

from winappaudiorouter import cli
from winappaudiorouter.models import AudioDeviceInfo


def test_cli_get_system_default(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "get_app_output_device", lambda process_id=None, process_name=None: None)
    exit_code = cli.main(["get", "--pid", "1234"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "<system default>" in output


def test_cli_route_without_pid_or_process_name_exits() -> None:
    with pytest.raises(SystemExit):
        cli.main(["route", "--device", "Speakers"])


def test_cli_get_input_system_default(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli, "get_app_input_device", lambda process_id=None, process_name=None: None)
    exit_code = cli.main(["get", "--flow", "input", "--pid", "1234"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "<system default>" in output


def test_cli_route_input_dispatches_to_input_router(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _set(process_id=None, process_name=None, device=None):
        assert process_name == "obs64.exe"
        assert device == "USB Mic"
        return {4321: AudioDeviceInfo(id="mic-id", name="USB Mic", is_default=False)}

    monkeypatch.setattr(cli, "set_app_input_device", _set)
    exit_code = cli.main(
        ["route", "--flow", "input", "--process-name", "obs64.exe", "--device", "USB Mic"]
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "pid=4321 -> USB Mic (mic-id)" in output


def test_cli_list_input_devices(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "list_input_devices",
        lambda: [AudioDeviceInfo(id="mic-id", name="USB Mic", is_default=True)],
    )
    exit_code = cli.main(["list-devices", "--flow", "input"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "* USB Mic" in output
    assert "mic-id" in output

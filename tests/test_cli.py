from __future__ import annotations

from types import SimpleNamespace

import pytest

from winappaudiorouter import cli
from winappaudiorouter.models import AudioDeviceInfo, AudioSessionInfo


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


def test_cli_list_input_sessions(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "list_input_sessions",
        lambda: [
            AudioSessionInfo(
                process_id=77,
                process_name=None,
                device_id="mic-id",
                device_name="USB Mic",
                session_identifier="session",
                session_instance_identifier="instance",
            )
        ],
    )

    exit_code = cli.main(["list-sessions", "--flow", "input"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "<unknown>" in output
    assert "USB Mic" in output


def test_cli_route_output_dispatches_to_output_router(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "set_app_output_device",
        lambda process_id=None, process_name=None, device=None: {
            100: AudioDeviceInfo(id="speaker-id", name="Speakers", is_default=True)
        },
    )

    exit_code = cli.main(["route", "--pid", "100", "--device", "Speakers"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "pid=100 -> Speakers (speaker-id)" in output


def test_cli_clear_dispatches_and_prints_pids(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli, "clear_app_output_device", lambda process_id=None, process_name=None: [1, 2])

    exit_code = cli.main(["clear", "--process-name", "chrome.exe"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Cleared routes for: 1, 2" in output


def test_cli_get_prints_routed_mapping(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "get_app_output_device",
        lambda process_id=None, process_name=None: {1234: "device-id"},
    )

    exit_code = cli.main(["get", "--pid", "1234"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "{1234: 'device-id'}" in output


def test_cli_clear_without_pid_or_process_name_exits() -> None:
    with pytest.raises(SystemExit):
        cli.main(["clear"])


def test_cli_get_without_pid_or_process_name_exits() -> None:
    with pytest.raises(SystemExit):
        cli.main(["get"])


def test_cli_main_returns_one_for_unknown_command(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_parser = SimpleNamespace(parse_args=lambda argv=None: SimpleNamespace(cmd="unknown"))
    monkeypatch.setattr(cli, "build_parser", lambda: fake_parser)

    assert cli.main([]) == 1

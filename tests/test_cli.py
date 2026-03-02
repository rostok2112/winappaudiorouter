from __future__ import annotations

import pytest

from winappaudiorouter import cli


def test_cli_get_system_default(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "get_app_output_device", lambda process_id=None, process_name=None: None)
    exit_code = cli.main(["get", "--pid", "1234"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "<system default>" in output


def test_cli_route_without_pid_or_process_name_exits() -> None:
    with pytest.raises(SystemExit):
        cli.main(["route", "--device", "Speakers"])

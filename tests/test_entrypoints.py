from __future__ import annotations

import runpy

import pytest

from winappaudiorouter import cli


def test___main___exits_with_cli_return_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "main", lambda: 7)

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("winappaudiorouter.__main__", run_name="__main__")

    assert exc_info.value.code == 7

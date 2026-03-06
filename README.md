# winappaudiorouter

[![CI](https://github.com/rostok2112/winappaudiorouter/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/rostok2112/winappaudiorouter/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/rostok2112/winappaudiorouter/graph/badge.svg?branch=main)](https://app.codecov.io/gh/rostok2112/winappaudiorouter)
[![Docs](https://readthedocs.org/projects/winappaudiorouter/badge/?version=latest)](https://winappaudiorouter.readthedocs.io/en/latest/)
[![PyPI Version](https://img.shields.io/pypi/v/winappaudiorouter.svg)](https://pypi.org/project/winappaudiorouter/)
[![Python Versions](https://img.shields.io/pypi/pyversions/winappaudiorouter.svg)](https://pypi.org/project/winappaudiorouter/)
[![License](https://img.shields.io/pypi/l/winappaudiorouter.svg)](https://github.com/rostok2112/winappaudiorouter/blob/main/LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6)](https://learn.microsoft.com/windows/)

`winappaudiorouter` is a Python library for changing output and input audio devices per app on Windows, without requiring external tools. It follows the same Windows routing path used by EarTrumpet/SoundVolumeView:
`Windows.Media.Internal.AudioPolicyConfig::SetPersistedDefaultAudioEndpoint`.

Full documentation lives at `https://winappaudiorouter.readthedocs.io/`.

## Features

- Enumerate active output and input devices.
- Enumerate active app audio sessions for output or input flows.
- Read persisted app output or input devices by PID or process name.
- Route one app PID (or all active sessions by process name) to a target output or input device.
- Clear persisted app routing (return to system default).
- CLI + Python API.

## Installation

```powershell
pip install winappaudiorouter
```

For local development:

```powershell
pip install -e .[dev]
```

## CLI Usage

```powershell
winappaudiorouter list-devices
winappaudiorouter list-devices --flow input
winappaudiorouter list-sessions
winappaudiorouter list-sessions --flow input
winappaudiorouter route --process-name chrome.exe --device "Headphones"
winappaudiorouter route --flow input --process-name obs64.exe --device "USB Mic"
winappaudiorouter route --pid 1234 --device "{0.0.0.00000000}.{GUID}"
winappaudiorouter clear --process-name chrome.exe
winappaudiorouter clear --flow input --pid 4567
winappaudiorouter get --pid 1234
winappaudiorouter get --flow input --process-name obs64.exe
winappaudiorouter get --process-name chrome.exe  # Get the current device for all chrome.exe processes
```

`--flow` accepts `output` (default) or `input`.

## Python Usage

```python
import winappaudiorouter as war

output_devices = war.list_output_devices()
input_devices = war.list_input_devices()
output_sessions = war.list_app_sessions()
input_sessions = war.list_input_sessions()

war.set_app_output_device(process_name="chrome.exe", device="Headphones")
war.clear_app_output_device(process_name="chrome.exe")
war.get_app_output_device(process_name="chrome.exe")  # {} means <system default>

war.set_app_input_device(process_name="obs64.exe", device="USB Mic")
war.clear_app_input_device(process_name="obs64.exe")
war.get_app_input_device(process_name="obs64.exe")  # {} means <system default>
```

## Running tests

```powershell
python -m pytest -q
python -m pytest --cov=winappaudiorouter --cov-report=term-missing --cov-report=xml
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

## CI and PyPI publish

- CI tests/build run on push and pull requests.
- Coverage is uploaded to Codecov from the `main` branch CI workflow.
- Documentation is published on Read the Docs.
- PyPI publish workflow runs on tag pushes like `v1.0.1`.
- GitHub repo secrets required: `PYPI_API_TOKEN`, `RTD_API_KEY`, and `CODECOV_TOKEN`.

## Contribution guidelines

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Limitations

- Windows 10 1803+ only.
- `process_name` routing requires at least one active audio session for that app in the selected flow.
- Session re-binding can be asynchronous; some apps require playback or recording restart.

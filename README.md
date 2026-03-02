# winappaudiorouter

`winappaudiorouter` is a Python library for changing output audio devices per app on Windows, without requiring external tools. It follows the same Windows routing path used by EarTrumpet/SoundVolumeView:
`Windows.Media.Internal.AudioPolicyConfig::SetPersistedDefaultAudioEndpoint`.

## Features

- Enumerate active output devices.
- Enumerate active app audio sessions.
- Route one app PID (or all active sessions by process name) to a target output.
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
winappaudiorouter list-sessions
winappaudiorouter route --process-name chrome.exe --device "Headphones"
winappaudiorouter route --pid 1234 --device "{0.0.0.00000000}.{GUID}"
winappaudiorouter clear --process-name chrome.exe
winappaudiorouter get --pid 1234
```

## Python Usage

```python
import winappaudiorouter as war

devices = war.list_output_devices()
sessions = war.list_app_sessions()

war.set_app_output_device(process_name="chrome.exe", device="Headphones")
war.clear_app_output_device(process_name="chrome.exe")
```

## Running tests

```powershell
python -m pytest -q
```

## Contribution guidelines

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Limitations

- Windows 10 1803+ only.
- `process_name` routing requires at least one active audio session for that app.
- Session re-binding can be asynchronous; some apps require playback restart.
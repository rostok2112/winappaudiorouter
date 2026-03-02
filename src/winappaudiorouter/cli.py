from __future__ import annotations

import argparse

from .devices import list_output_devices
from .sessions import list_app_sessions
from .router import clear_app_output_device, get_app_output_device, set_app_output_device


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Per-app output audio router for Windows."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-devices", help="List active output devices.")
    sub.add_parser("list-sessions", help="List active render sessions.")

    route = sub.add_parser("route", help="Route app output to a selected device.")
    route.add_argument("--pid", type=int, help="Process ID.")
    route.add_argument("--process-name", help="Process name, e.g. chrome.exe.")
    route.add_argument("--device", required=True, help="Device id or name.")

    clear = sub.add_parser("clear", help="Clear app routing and use system default.")
    clear.add_argument("--pid", type=int, help="Process ID.")
    clear.add_argument("--process-name", help="Process name, e.g. chrome.exe.")

    get_cmd = sub.add_parser("get", help="Get persisted route for one PID.")
    get_cmd.add_argument("--pid", type=int, required=True, help="Process ID.")
    return parser


def _print_devices() -> None:
    for device in list_output_devices():
        marker = "*" if device.is_default else " "
        print(f"{marker} {device.name}\n    {device.id}")


def _print_sessions() -> None:
    for session in list_app_sessions():
        pname = session.process_name or "<unknown>"
        print(
            f"{pname:<30} pid={session.process_id:<7} device={session.device_name} ({session.device_id})"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "list-devices":
        _print_devices()
        return 0

    if args.cmd == "list-sessions":
        _print_sessions()
        return 0

    if args.cmd == "route":
        if args.pid is None and not args.process_name:
            parser.error("route requires --pid or --process-name")
        result = set_app_output_device(
            process_id=args.pid,
            process_name=args.process_name,
            device=args.device,
        )
        for pid, device in result.items():
            print(f"pid={pid} -> {device.name} ({device.id})")
        return 0

    if args.cmd == "clear":
        if args.pid is None and not args.process_name:
            parser.error("clear requires --pid or --process-name")
        pids = clear_app_output_device(process_id=args.pid, process_name=args.process_name)
        print("Cleared routes for:", ", ".join(str(pid) for pid in pids))
        return 0

    if args.cmd == "get":
        routed = get_app_output_device(args.pid)
        if routed:
            print(routed)
        else:
            print("<system default>")
        return 0

    return 1

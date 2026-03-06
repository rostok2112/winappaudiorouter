from __future__ import annotations

import argparse

from .devices import list_input_devices, list_output_devices
from .router import (
    clear_app_input_device,
    clear_app_output_device,
    get_app_input_device,
    get_app_output_device,
    set_app_input_device,
    set_app_output_device,
)
from .sessions import list_app_sessions, list_input_sessions


def _add_flow_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--flow",
        choices=("output", "input"),
        default="output",
        help="Audio flow to target. Defaults to output.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Per-app Windows audio router for output and input devices."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_devices = sub.add_parser("list-devices", help="List active audio devices.")
    _add_flow_argument(list_devices)

    list_sessions = sub.add_parser("list-sessions", help="List active audio sessions.")
    _add_flow_argument(list_sessions)

    route = sub.add_parser("route", help="Route app audio to a selected device.")
    _add_flow_argument(route)
    route.add_argument("--pid", type=int, help="Process ID.")
    route.add_argument("--process-name", help="Process name, e.g. chrome.exe.")
    route.add_argument("--device", required=True, help="Device id or name.")

    clear = sub.add_parser("clear", help="Clear app routing and use system default.")
    _add_flow_argument(clear)
    clear.add_argument("--pid", type=int, help="Process ID.")
    clear.add_argument("--process-name", help="Process name, e.g. chrome.exe.")

    get_cmd = sub.add_parser("get", help="Get persisted route for app.")
    _add_flow_argument(get_cmd)
    get_cmd.add_argument("--pid", type=int, help="Process ID.")
    get_cmd.add_argument("--process-name", help="Process name, e.g. chrome.exe.")
    return parser


def _print_devices(flow: str) -> None:
    devices = list_input_devices() if flow == "input" else list_output_devices()
    for device in devices:
        marker = "*" if device.is_default else " "
        print(f"{marker} {device.name}\n    {device.id}")


def _print_sessions(flow: str) -> None:
    sessions = list_input_sessions() if flow == "input" else list_app_sessions()
    for session in sessions:
        pname = session.process_name or "<unknown>"
        print(
            f"{pname:<30} pid={session.process_id:<7} device={session.device_name} ({session.device_id})"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "list-devices":
        _print_devices(args.flow)
        return 0

    if args.cmd == "list-sessions":
        _print_sessions(args.flow)
        return 0

    if args.cmd == "route":
        if args.pid is None and not args.process_name:
            parser.error("route requires --pid or --process-name")
        router = set_app_input_device if args.flow == "input" else set_app_output_device
        result = router(
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
        clearer = clear_app_input_device if args.flow == "input" else clear_app_output_device
        pids = clearer(process_id=args.pid, process_name=args.process_name)
        print("Cleared routes for:", ", ".join(str(pid) for pid in pids))
        return 0

    if args.cmd == "get":
        if args.pid is None and not args.process_name:
            parser.error("get requires --pid or --process-name")
        getter = get_app_input_device if args.flow == "input" else get_app_output_device
        routed = getter(process_id=args.pid, process_name=args.process_name)
        if routed:
            print(routed)
        else:
            print("<system default>")
        return 0

    return 1

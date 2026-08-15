from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .audit import audit_file, audit_text
from .c2pa_forensics import inspect_c2pa
from .capabilities import get_capabilities


VERSION = __version__


def _dump(data: dict, pretty: bool) -> None:
    print(json.dumps(data, indent=2 if pretty else None, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="provenance-audit",
        description="Inspect provider verification, signed file provenance and observable text forensics without treating style heuristics as proof.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Audit a supported text/document/media file")
    scan.add_argument("path")
    scan.add_argument("--provider", default="anthropic", choices=["anthropic", "google", "none", "auto"])
    scan.add_argument("--pretty", action="store_true")
    scan.add_argument("--no-segments", action="store_true")
    scan.add_argument("--no-c2pa", action="store_true")

    scan_text = sub.add_parser("scan-text", help="Audit literal text")
    scan_text.add_argument("text")
    scan_text.add_argument("--provider", default="anthropic", choices=["anthropic", "google", "none", "auto"])
    scan_text.add_argument("--pretty", action="store_true")
    scan_text.add_argument("--no-segments", action="store_true")

    scan_stdin = sub.add_parser("scan-stdin", help="Audit text read from stdin")
    scan_stdin.add_argument("--provider", default="anthropic", choices=["anthropic", "google", "none", "auto"])
    scan_stdin.add_argument("--pretty", action="store_true")
    scan_stdin.add_argument("--no-segments", action="store_true")

    c2pa = sub.add_parser("verify-c2pa", help="Inspect C2PA Content Credentials on a supported asset")
    c2pa.add_argument("path")
    c2pa.add_argument("--pretty", action="store_true")

    caps = sub.add_parser("capabilities", help="Show detector capabilities")
    caps.add_argument("--pretty", action="store_true")

    web = sub.add_parser("web", help="Launch the local browser interface")
    web.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to local-only 127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    web.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "scan":
            report = audit_file(
                args.path,
                provider=args.provider,
                include_segments=not args.no_segments,
                inspect_file_provenance=not args.no_c2pa,
            )
            _dump(report.to_dict(), args.pretty)
            return 0

        if args.command == "scan-text":
            report = audit_text(
                args.text,
                source="inline",
                provider=args.provider,
                include_segments=not args.no_segments,
            )
            _dump(report.to_dict(), args.pretty)
            return 0

        if args.command == "scan-stdin":
            report = audit_text(
                sys.stdin.read(),
                source="stdin",
                provider=args.provider,
                include_segments=not args.no_segments,
            )
            _dump(report.to_dict(), args.pretty)
            return 0

        if args.command == "verify-c2pa":
            _dump(inspect_c2pa(args.path).__dict__, args.pretty)
            return 0

        if args.command == "capabilities":
            _dump(get_capabilities(), args.pretty)
            return 0

        if args.command == "web":
            from .web import run_web

            run_web(host=args.host, port=args.port, open_browser=not args.no_browser)
            return 0

    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

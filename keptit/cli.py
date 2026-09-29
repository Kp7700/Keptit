import argparse
from pathlib import Path

from keptit.scanner import format_scan_summary, scan_folder


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="keptit",
        description="Local-first photo scanning tool.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a folder for supported images.",
    )

    scan_parser.add_argument(
        "folder",
        type=Path,
        help="Folder to scan.",
    )

    scan_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subdirectories recursively.",
    )

    return parser


def main() -> int:
    """Run the Keptit command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        try:
            result = scan_folder(
                args.folder,
                recursive=args.recursive,
            )
        except NotADirectoryError as error:
            parser.error(str(error))

        print(format_scan_summary(result))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
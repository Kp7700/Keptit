import argparse
from pathlib import Path

from keptit.grouping import group_images
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

    scan_parser.add_argument(
        "--group",
        action="store_true",
        help="Group similar images by perceptual hash.",
    )

    return parser


def format_group_summary(images, groups) -> str:
    """Format image groups for human-readable CLI output."""
    image_filenames = {
        image.id: image.filename
        for image in images
    }

    lines = [f"Groups found: {len(groups)}"]

    for index, group in enumerate(groups, start=1):
        lines.append(f"Group {index}:")

        for image_id in group.image_ids:
            filename = image_filenames.get(image_id, image_id)
            lines.append(f"  {filename}")

    return "\n".join(lines)


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

        if args.group:
            groups = group_images(result.images)
            print(format_group_summary(result.images, groups))

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
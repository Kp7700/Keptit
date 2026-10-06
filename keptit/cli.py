import argparse
from pathlib import Path

from keptit.grouping import group_images
from keptit.quality import analyze_image_quality
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

    scan_parser.add_argument(
        "--quality",
        action="store_true",
        help="Calculate quality metrics for successfully indexed images.",
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


def format_quality_summary(result) -> str:
    """Return a human-readable summary of calculated quality metrics and scores."""
    lines = [
        "",
        "Quality Metrics:",
    ]

    analyzed_images = [
        image
        for image in result.images
        if image.quality_metrics is not None
    ]

    if not analyzed_images:
        lines.append("None")
        return "\n".join(lines)

    for image in sorted(analyzed_images, key=lambda item: item.filename):
        metrics = image.quality_metrics
        score = image.quality_score

        lines.extend([
            "",
            f"- {image.filename}",
            f"  Sharpness variance: {metrics.sharpness_variance}",
            f"  Mean luminance: {metrics.mean_luminance}",
            f"  Dark pixel ratio: {metrics.dark_pixel_ratio}",
            f"  Bright pixel ratio: {metrics.bright_pixel_ratio}",
        ])

        if score is not None:
            lines.extend([
                f"  Sharpness component: {score.sharpness_component}",
                f"  Exposure component: {score.exposure_component}",
                f"  Overall score: {score.overall_score}/100",
            ])

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

        if args.quality:
            try:
                result.images = [
                    analyze_image_quality(image)
                    for image in result.images
                ]
            except RuntimeError as error:
                parser.error(str(error))

        print(format_scan_summary(result))

        if args.group:
            groups = group_images(result.images)
            print(format_group_summary(result.images, groups))

        if args.quality:
            print(format_quality_summary(result))

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

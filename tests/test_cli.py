from pathlib import Path

from PIL import Image

from keptit.cli import build_parser, format_quality_summary
from keptit.quality import analyze_image_quality
from keptit.scanner import format_scan_summary, scan_folder


def test_scan_without_group_flag():
    parser = build_parser()

    args = parser.parse_args(["scan", "photos"])

    assert args.command == "scan"
    assert args.folder == Path("photos")
    assert args.recursive is False
    assert args.group is False


def test_scan_with_group_flag():
    parser = build_parser()

    args = parser.parse_args(["scan", "photos", "--group"])

    assert args.command == "scan"
    assert args.folder == Path("photos")
    assert args.recursive is False
    assert args.group is True


def test_scan_with_recursive_and_group_flags():
    parser = build_parser()

    args = parser.parse_args(
        ["scan", "photos", "--recursive", "--group"]
    )

    assert args.command == "scan"
    assert args.folder == Path("photos")
    assert args.recursive is True
    assert args.group is True


def test_group_flag_runs_grouping(monkeypatch, capsys):
    from keptit import cli

    class FakeResult:
        images = []

    grouping_called = False

    def fake_scan_folder(folder, recursive=False):
        return FakeResult()

    def fake_group_images(images):
        nonlocal grouping_called
        grouping_called = True
        assert images == []
        return []

    monkeypatch.setattr(cli, "scan_folder", fake_scan_folder)
    monkeypatch.setattr(cli, "group_images", fake_group_images)
    monkeypatch.setattr(
        cli,
        "format_scan_summary",
        lambda result: "Scan summary",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["keptit", "scan", "photos", "--group"],
    )

    assert cli.main() == 0
    assert grouping_called is True

    captured = capsys.readouterr()
    assert "Scan summary" in captured.out


def test_group_flag_prints_group_members(monkeypatch, capsys):
    from keptit import cli
    from keptit.grouping import ImageGroup

    class FakeImage:
        def __init__(self, image_id, filename):
            self.id = image_id
            self.filename = filename

    class FakeResult:
        images = [
            FakeImage("image-1", "photo1.jpg"),
            FakeImage("image-2", "photo2.jpg"),
            FakeImage("image-3", "photo3.jpg"),
        ]

    def fake_scan_folder(folder, recursive=False):
        return FakeResult()

    def fake_group_images(images):
        return [
            ImageGroup(image_ids=["image-1", "image-2"]),
            ImageGroup(image_ids=["image-3"]),
        ]

    monkeypatch.setattr(cli, "scan_folder", fake_scan_folder)
    monkeypatch.setattr(cli, "group_images", fake_group_images)
    monkeypatch.setattr(
        cli,
        "format_scan_summary",
        lambda result: "Scan summary",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["keptit", "scan", "photos", "--group"],
    )

    assert cli.main() == 0

    captured = capsys.readouterr()

    assert "Scan summary" in captured.out
    assert "Groups found: 2" in captured.out
    assert "photo1.jpg" in captured.out
    assert "photo2.jpg" in captured.out
    assert "photo3.jpg" in captured.out


def test_scan_without_group_does_not_run_grouping(monkeypatch, capsys):
    from keptit import cli

    class FakeResult:
        images = []

    grouping_called = False

    def fake_scan_folder(folder, recursive=False):
        return FakeResult()

    def fake_group_images(images):
        nonlocal grouping_called
        grouping_called = True
        return []

    monkeypatch.setattr(cli, "scan_folder", fake_scan_folder)
    monkeypatch.setattr(cli, "group_images", fake_group_images)
    monkeypatch.setattr(
        cli,
        "format_scan_summary",
        lambda result: "Scan summary",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["keptit", "scan", "photos"],
    )

    assert cli.main() == 0
    assert grouping_called is False

    captured = capsys.readouterr()

    assert captured.out == "Scan summary\n"


def test_parser_accepts_quality_flag():
    parser = build_parser()

    args = parser.parse_args([
        "scan",
        "photos",
        "--quality",
    ])

    assert args.quality is True


def test_parser_quality_defaults_to_false():
    parser = build_parser()

    args = parser.parse_args([
        "scan",
        "photos",
    ])

    assert args.quality is False


def test_quality_flag_outputs_quality_metrics(tmp_path, capsys):
    image_path = tmp_path / "test.png"

    image = Image.new("L", (100, 100), 128)
    image.save(image_path)

    parser = build_parser()

    args = parser.parse_args([
        "scan",
        str(tmp_path),
        "--quality",
    ])

    result = scan_folder(
        args.folder,
        recursive=args.recursive,
    )

    result.images = [
        analyze_image_quality(image)
        for image in result.images
    ]

    print(format_scan_summary(result))

    if args.quality:
        print(format_quality_summary(result))

    output = capsys.readouterr().out

    assert "Quality Metrics:" in output
    assert "test.png" in output
    assert "Sharpness variance:" in output
    assert "Mean luminance:" in output
    assert "Dark pixel ratio:" in output
    assert "Bright pixel ratio:" in output


def test_quality_metrics_not_output_without_quality_flag(tmp_path, capsys):
    image_path = tmp_path / "test.png"

    image = Image.new("L", (100, 100), 128)
    image.save(image_path)

    parser = build_parser()

    args = parser.parse_args([
        "scan",
        str(tmp_path),
    ])

    result = scan_folder(
        args.folder,
        recursive=args.recursive,
    )

    print(format_scan_summary(result))

    output = capsys.readouterr().out

    assert "Quality Metrics:" not in output

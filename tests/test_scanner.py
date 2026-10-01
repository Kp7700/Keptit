from pathlib import Path

from keptit.hashing import HashingError
from keptit.scanner import (
    discover_images,
    format_scan_summary,
    index_image,
    is_supported_image,
    read_image_info,
    scan_folder,
)
from PIL import Image


def test_supported_jpg():
    assert is_supported_image(Path("photo.jpg"))


def test_supported_jpeg():
    assert is_supported_image(Path("photo.jpeg"))


def test_supported_png():
    assert is_supported_image(Path("photo.png"))


def test_extension_is_case_insensitive():
    assert is_supported_image(Path("photo.JPG"))
    assert is_supported_image(Path("photo.JPEG"))
    assert is_supported_image(Path("photo.PNG"))


def test_unsupported_file():
    assert not is_supported_image(Path("document.pdf"))
    assert not is_supported_image(Path("notes.txt"))


def test_discover_images_non_recursive(tmp_path):
    (tmp_path / "photo1.jpg").touch()
    (tmp_path / "photo2.png").touch()
    (tmp_path / "notes.txt").touch()

    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()
    (subfolder / "photo3.jpg").touch()

    images = discover_images(tmp_path, recursive=False)

    assert len(images) == 2
    assert tmp_path / "photo1.jpg" in images
    assert tmp_path / "photo2.png" in images
    assert subfolder / "photo3.jpg" not in images


def test_discover_images_recursive(tmp_path):
    (tmp_path / "photo1.jpg").touch()

    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()
    (subfolder / "photo2.png").touch()

    images = discover_images(tmp_path, recursive=True)

    assert len(images) == 2
    assert tmp_path / "photo1.jpg" in images
    assert subfolder / "photo2.png" in images


def test_discover_images_empty_directory(tmp_path):
    images = discover_images(tmp_path)

    assert images == []


def test_read_image_info(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    image.save(image_path, format="JPEG")

    width, height, image_format = read_image_info(image_path)

    assert width == 800
    assert height == 600
    assert image_format == "JPEG"


def test_read_png_image_info(tmp_path):
    image_path = tmp_path / "photo.png"

    image = Image.new("RGB", (640, 480))
    image.save(image_path, format="PNG")

    width, height, image_format = read_image_info(image_path)

    assert width == 640
    assert height == 480
    assert image_format == "PNG"


def test_index_corrupted_image(tmp_path):
    image_path = tmp_path / "broken.jpg"
    image_path.write_bytes(b"this is not a real image")

    record = index_image(image_path)

    assert record.filename == "broken.jpg"
    assert record.status == "failed"
    assert record.width is None
    assert record.height is None
    assert record.image_format is None
    assert record.error


def test_scan_folder_empty_directory(tmp_path):
    result = scan_folder(tmp_path)

    assert result.folder == tmp_path.resolve()
    assert result.recursive is False
    assert result.images == []
    assert result.discovered_count == 0
    assert result.successful_count == 0
    assert result.failed_count == 0
    assert result.supported_count == 0
    assert result.unsupported_count == 0


def test_scan_folder_indexes_images(tmp_path):
    jpg_path = tmp_path / "photo.jpg"
    png_path = tmp_path / "photo.png"
    text_path = tmp_path / "notes.txt"

    Image.new("RGB", (800, 600)).save(jpg_path, format="JPEG")
    Image.new("RGB", (640, 480)).save(png_path, format="PNG")
    text_path.write_text("not an image")

    result = scan_folder(tmp_path)

    assert result.discovered_count == 3
    assert result.supported_count == 2
    assert result.unsupported_count == 1
    assert result.successful_count == 2
    assert result.failed_count == 0

    filenames = {image.filename for image in result.images}

    assert filenames == {"photo.jpg", "photo.png"}


def test_scan_folder_handles_corrupted_image(tmp_path):
    valid_path = tmp_path / "valid.jpg"
    broken_path = tmp_path / "broken.jpg"

    Image.new("RGB", (800, 600)).save(valid_path, format="JPEG")
    broken_path.write_bytes(b"not a real image")

    result = scan_folder(tmp_path)

    assert result.discovered_count == 2
    assert result.supported_count == 2
    assert result.unsupported_count == 0
    assert result.successful_count == 1
    assert result.failed_count == 1

    failed_images = [
        image for image in result.images
        if image.status == "failed"
    ]

    assert len(failed_images) == 1
    assert failed_images[0].filename == "broken.jpg"
    assert failed_images[0].error


def test_scan_folder_recursive(tmp_path):
    root_image = tmp_path / "root.jpg"

    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()

    nested_image = subfolder / "nested.png"

    Image.new("RGB", (100, 100)).save(root_image, format="JPEG")
    Image.new("RGB", (200, 150)).save(nested_image, format="PNG")

    result = scan_folder(tmp_path, recursive=True)

    assert result.recursive is True
    assert result.discovered_count == 2

    paths = {image.path for image in result.images}

    assert root_image.resolve() in paths
    assert nested_image.resolve() in paths


def test_scan_folder_non_recursive(tmp_path):
    root_image = tmp_path / "root.jpg"

    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()

    nested_image = subfolder / "nested.png"

    Image.new("RGB", (100, 100)).save(root_image, format="JPEG")
    Image.new("RGB", (200, 150)).save(nested_image, format="PNG")

    result = scan_folder(tmp_path, recursive=False)

    assert result.recursive is False
    assert result.discovered_count == 1
    assert result.images[0].filename == "root.jpg"


def test_scan_folder_rejects_file_path(tmp_path):
    file_path = tmp_path / "not_a_folder.txt"
    file_path.write_text("hello")

    try:
        scan_folder(file_path)
    except NotADirectoryError:
        pass
    else:
        raise AssertionError("Expected NotADirectoryError")


def test_scan_folder_counts_supported_and_unsupported_files(tmp_path):
    Image.new("RGB", (100, 100)).save(
        tmp_path / "photo.jpg",
        format="JPEG",
    )

    Image.new("RGB", (100, 100)).save(
        tmp_path / "image.png",
        format="PNG",
    )

    (tmp_path / "notes.txt").write_text("hello")
    (tmp_path / "document.pdf").write_bytes(b"fake pdf")

    result = scan_folder(tmp_path)

    assert result.discovered_count == 4
    assert result.supported_count == 2
    assert result.unsupported_count == 2
    assert result.successful_count == 2
    assert result.failed_count == 0


def test_format_scan_summary(tmp_path):
    image_path = tmp_path / "photo.jpg"

    Image.new("RGB", (800, 600)).save(
        image_path,
        format="JPEG",
    )

    (tmp_path / "notes.txt").write_text("hello")

    result = scan_folder(tmp_path)

    summary = format_scan_summary(result)

    assert "Keptit Scanner" in summary
    assert f"Folder: {tmp_path.resolve()}" in summary
    assert "Recursive: No" in summary
    assert "Files discovered: 2" in summary
    assert "Supported images: 1" in summary
    assert "Unsupported files: 1" in summary
    assert "Failed images: 0" in summary
    assert "Successfully indexed: 1" in summary
    assert "JPEG: 1" in summary
    assert "Failed:" in summary
    assert "None" in summary
    assert "Scan completed successfully." in summary


def test_format_scan_summary_includes_failed_images(tmp_path):
    broken_path = tmp_path / "broken.jpg"
    broken_path.write_bytes(b"not a real image")

    result = scan_folder(tmp_path)

    summary = format_scan_summary(result)

    assert "Failed images: 1" in summary
    assert "- broken.jpg" in summary
    assert "Reason:" in summary


def test_index_image_extracts_metadata(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[271] = "Canon"
    exif[272] = "EOS R5"
    exif[34855] = 400

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    record = index_image(image_path)

    assert record.status == "success"
    assert record.metadata is not None
    assert record.metadata.camera_make == "Canon"
    assert record.metadata.camera_model == "EOS R5"
    assert record.metadata.iso == 400


def test_index_image_without_exif_still_succeeds(tmp_path):
    image_path = tmp_path / "photo.jpg"

    Image.new("RGB", (800, 600)).save(
        image_path,
        format="JPEG",
    )

    record = index_image(image_path)

    assert record.status == "success"
    assert record.metadata is not None
    assert record.metadata.captured_at is None
    assert record.metadata.camera_make is None
    assert record.metadata.camera_model is None
    assert record.metadata.orientation is None
    assert record.metadata.focal_length is None
    assert record.metadata.iso is None


def test_index_corrupted_image_does_not_extract_metadata(tmp_path):
    image_path = tmp_path / "broken.jpg"
    image_path.write_bytes(b"not a real image")

    record = index_image(image_path)

    assert record.status == "failed"
    assert record.metadata is None
    assert record.width is None
    assert record.height is None
    assert record.image_format is None
    assert record.error is not None


def test_index_image_generates_perceptual_hash(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (100, 100), color="white")
    image.save(image_path, "JPEG")

    record = index_image(image_path)

    assert record.status == "success"
    assert record.perceptual_hash is not None
    assert len(record.perceptual_hash) == 16


def test_index_image_generates_same_hash_for_same_image(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (100, 100), color="white")
    image.save(image_path, "JPEG")

    first = index_image(image_path)
    second = index_image(image_path)

    assert first.perceptual_hash == second.perceptual_hash


def test_index_image_hash_failure_marks_image_as_failed(tmp_path, monkeypatch):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (100, 100), color="white")
    image.save(image_path, "JPEG")

    def failing_hash(_image):
        raise HashingError("hashing failed")

    monkeypatch.setattr("keptit.scanner.compute_dhash", failing_hash)

    record = index_image(image_path)

    assert record.status == "failed"
    assert record.error == "hashing failed"
    assert record.perceptual_hash is None


def test_scan_reports_hash_failure(tmp_path, monkeypatch):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (100, 100), color="white")
    image.save(image_path, "JPEG")

    def failing_hash(_image):
        raise HashingError("hashing failed")

    monkeypatch.setattr("keptit.scanner.compute_dhash", failing_hash)

    result = scan_folder(tmp_path)

    assert result.discovered_count == 1
    assert result.supported_count == 1
    assert result.successful_count == 0
    assert result.failed_count == 1
    assert result.images[0].status == "failed"
    assert result.images[0].perceptual_hash is None

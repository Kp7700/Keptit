from datetime import datetime

from PIL import Image

from keptit.metadata import extract_metadata


def test_extract_metadata_without_exif(tmp_path):
    image_path = tmp_path / "photo.jpg"

    Image.new("RGB", (800, 600)).save(
        image_path,
        format="JPEG",
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.captured_at is None
    assert metadata.camera_make is None
    assert metadata.camera_model is None
    assert metadata.orientation is None
    assert metadata.focal_length is None
    assert metadata.iso is None


def test_extract_captured_at(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[36867] = "2026:09:30 18:45:12"

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.captured_at == datetime(2026, 9, 30, 18, 45, 12)

def test_extract_camera_make_and_model(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[271] = " Canon "
    exif[272] = " EOS R5 "

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.camera_make == "Canon"
    assert metadata.camera_model == "EOS R5"

def test_extract_orientation(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[274] = 6

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.orientation == 6

def test_extract_focal_length(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[37386] = (50, 1)

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.focal_length == 50.0

def test_extract_iso(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[34855] = 400

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.iso == 400

def test_malformed_captured_at_does_not_fail_extraction(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[36867] = "not-a-date"
    exif[271] = "Canon"
    exif[34855] = 400

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.captured_at is None
    assert metadata.camera_make == "Canon"
    assert metadata.iso == 400

def test_malformed_focal_length_does_not_fail_extraction(tmp_path):
    image_path = tmp_path / "photo.jpg"

    image = Image.new("RGB", (800, 600))
    exif = image.getexif()
    exif[37386] = (50, 0)
    exif[34855] = 800

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    with Image.open(image_path) as image:
        metadata = extract_metadata(image)

    assert metadata.focal_length is None
    assert metadata.iso == 800

def test_extracts_captured_at_from_datetime_fallback():
    image = Image.new("RGB", (100, 100))

    exif = image.getexif()
    exif[306] = "2026:09:30 22:14:39"

    metadata = extract_metadata(image)

    assert metadata.captured_at == datetime(2026, 9, 30, 22, 14, 39)
from datetime import datetime
from pathlib import Path

from keptit.models import ImageMetadata, ImageRecord


def test_image_record_creation():
    record = ImageRecord(
        id="test-001",
        filename="photo.jpg",
        path=Path("C:/Photos/photo.jpg"),
        extension=".jpg",
        file_size=1024,
        width=1920,
        height=1080,
        modified_time=datetime(2026, 9, 28, 12, 0, 0),
        image_format="JPEG",
        status="success",
    )

    assert record.id == "test-001"
    assert record.filename == "photo.jpg"
    assert record.path == Path("C:/Photos/photo.jpg")
    assert record.extension == ".jpg"
    assert record.file_size == 1024
    assert record.width == 1920
    assert record.height == 1080
    assert record.image_format == "JPEG"
    assert record.status == "success"
    assert record.error is None
    assert record.metadata is None


def test_image_record_can_store_error():
    record = ImageRecord(
        id="test-002",
        filename="broken.jpg",
        path=Path("C:/Photos/broken.jpg"),
        extension=".jpg",
        file_size=512,
        width=None,
        height=None,
        modified_time=datetime(2026, 9, 28, 12, 0, 0),
        image_format=None,
        status="failed",
        error="Unable to identify image file",
    )

    assert record.status == "failed"
    assert record.width is None
    assert record.height is None
    assert record.image_format is None
    assert record.error == "Unable to identify image file"

def test_image_metadata_defaults_to_none():
    metadata = ImageMetadata()

    assert metadata.captured_at is None
    assert metadata.camera_make is None
    assert metadata.camera_model is None
    assert metadata.orientation is None
    assert metadata.focal_length is None
    assert metadata.iso is None


def test_image_metadata_stores_values():
    captured_at = datetime(2026, 9, 28, 12, 30, 0)

    metadata = ImageMetadata(
        captured_at=captured_at,
        camera_make="Canon",
        camera_model="EOS R5",
        orientation=1,
        focal_length=50.0,
        iso=400,
    )

    assert metadata.captured_at == captured_at
    assert metadata.camera_make == "Canon"
    assert metadata.camera_model == "EOS R5"
    assert metadata.orientation == 1
    assert metadata.focal_length == 50.0
    assert metadata.iso == 400


def test_image_record_can_store_metadata():
    metadata = ImageMetadata(
        camera_make="Canon",
        camera_model="EOS R5",
        iso=400,
    )

    record = ImageRecord(
        id="test-003",
        filename="photo.jpg",
        path=Path("C:/Photos/photo.jpg"),
        extension=".jpg",
        file_size=1024,
        width=1920,
        height=1080,
        modified_time=datetime(2026, 9, 28, 12, 0, 0),
        image_format="JPEG",
        status="success",
        metadata=metadata,
    )

    assert record.metadata is metadata
    assert record.metadata.camera_make == "Canon"
    assert record.metadata.camera_model == "EOS R5"
    assert record.metadata.iso == 400
from datetime import datetime

from PIL import Image

from keptit.models import ImageMetadata


def extract_metadata(image: Image.Image) -> ImageMetadata:
    """Extract supported metadata from an opened image."""
    exif = image.getexif()

    captured_at = None
    camera_make = None
    camera_model = None
    orientation = None
    focal_length = None
    iso = None

    if exif:
        value = exif.get(36867)  # DateTimeOriginal

        if value is None:
            value = exif.get(306)  # DateTime

        if value:
            try:
                captured_at = datetime.strptime(
                    value,
                    "%Y:%m:%d %H:%M:%S",
                )
            except (TypeError, ValueError):
                captured_at = None

        camera_make = exif.get(271)  # Make
        camera_model = exif.get(272)  # Model
        orientation = exif.get(274)  # Orientation

        value = exif.get(37386)  # FocalLength

        if value is not None:
            try:
                if isinstance(value, tuple):
                    focal_length = value[0] / value[1]
                else:
                    focal_length = float(value)
            except (TypeError, ValueError, ZeroDivisionError):
                focal_length = None

        if isinstance(camera_make, str):
            camera_make = camera_make.strip()

        if isinstance(camera_model, str):
            camera_model = camera_model.strip()

        if orientation is not None:
            try:
                orientation = int(orientation)
            except (TypeError, ValueError):
                orientation = None

        value = exif.get(34855)  # ISOSpeedRatings

        if value is not None:
            try:
                iso = int(value)
            except (TypeError, ValueError):
                iso = None

    return ImageMetadata(
        captured_at=captured_at,
        camera_make=camera_make,
        camera_model=camera_model,
        orientation=orientation,
        focal_length=focal_length,
        iso=iso,
    )
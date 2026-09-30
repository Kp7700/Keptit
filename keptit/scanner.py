from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from keptit.models import ImageRecord, ScanResult

from keptit.metadata import extract_metadata


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def is_supported_image(path: Path) -> bool:
    """Return True if the file has a supported image extension."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS

def discover_images(folder: Path, recursive: bool = False) -> list[Path]:
    """Discover supported image files in a folder."""
    if recursive:
        candidates = folder.rglob("*")
    else:
        candidates = folder.glob("*")

    return [
        path
        for path in candidates
        if path.is_file() and is_supported_image(path)
    ]

def read_image_info(path: Path) -> tuple[int, int, str]:
    """Read width, height, and format from an image."""
    with Image.open(path) as image:
        image.verify()

    with Image.open(path) as image:
        return image.width, image.height, image.format

def index_image(path: Path) -> ImageRecord:
    """Create an ImageRecord for a single image."""
    absolute_path = path.resolve()

    try:
        stat = absolute_path.stat()
        width, height, image_format = read_image_info(absolute_path)

        with Image.open(absolute_path) as image:
            metadata = extract_metadata(image)

        return ImageRecord(
            id=str(uuid4()),
            filename=absolute_path.name,
            path=absolute_path,
            extension=absolute_path.suffix.lower(),
            file_size=stat.st_size,
            width=width,
            height=height,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            image_format=image_format,
            status="success",
            error=None,
            metadata=metadata,
        )

    except (OSError, UnidentifiedImageError) as error:
        return ImageRecord(
            id=str(uuid4()),
            filename=absolute_path.name,
            path=absolute_path,
            extension=absolute_path.suffix.lower(),
            file_size=0,
            width=None,
            height=None,
            modified_time=datetime.fromtimestamp(0),
            image_format=None,
            status="failed",
            error=str(error),
            metadata=None,
        )

def scan_folder(folder: Path, recursive: bool = False) -> ScanResult:
    """Scan a folder and index all supported images."""
    folder = folder.resolve()

    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    if recursive:
        candidates = folder.rglob("*")
    else:
        candidates = folder.glob("*")

    files = [
        path
        for path in candidates
        if path.is_file()
    ]

    supported_files = [
        path
        for path in files
        if is_supported_image(path)
    ]

    images = [
        index_image(path)
        for path in supported_files
    ]

    return ScanResult(
        folder=folder,
        recursive=recursive,
        images=images,
        discovered_count=len(files),
        unsupported_count=len(files) - len(supported_files),
    )

def format_scan_summary(result: ScanResult) -> str:
    """Return a human-readable summary of a completed scan."""
    image_types: dict[str, int] = {}

    for image in result.images:
        if image.image_format is not None:
            image_types[image.image_format] = (
                image_types.get(image.image_format, 0) + 1
            )

    lines = [
        "Keptit Scanner",
        "",
        f"Folder: {result.folder}",
        f"Recursive: {'Yes' if result.recursive else 'No'}",
        "",
        f"Files discovered: {result.discovered_count}",
        f"Supported images: {result.supported_count}",
        f"Unsupported files: {result.unsupported_count}",
        f"Failed images: {result.failed_count}",
        f"Successfully indexed: {result.successful_count}",
        "",
        "Image types:",
    ]

    if image_types:
        for image_format, count in sorted(image_types.items()):
            lines.append(f"{image_format}: {count}")
    else:
        lines.append("None")

    lines.extend(["", "Failed:"])

    failed_images = [
        image for image in result.images
        if image.status == "failed"
    ]

    if failed_images:
        for image in failed_images:
            lines.append(f"- {image.filename}")
            if image.error:
                lines.append(f"  Reason: {image.error}")
    else:
        lines.append("None")

    lines.extend([
        "",
        "Scan completed successfully.",
    ])

    return "\n".join(lines)
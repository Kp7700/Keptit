from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

@dataclass
class QualityMetrics:
    """Measurements describing observable image-quality properties."""

    sharpness_variance: float
    mean_luminance: float
    dark_pixel_ratio: float
    bright_pixel_ratio: float

@dataclass
class QualityScore:
    """Deterministic heuristic score derived from quality measurements."""

    sharpness_component: float
    exposure_component: float
    overall_score: int

@dataclass
class ImageMetadata:
    """Metadata extracted from an image."""

    captured_at: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    orientation: Optional[int] = None
    focal_length: Optional[float] = None
    iso: Optional[int] = None

@dataclass
class ImageRecord:
    """Information collected about a single image during scanning."""

    id: str
    filename: str
    path: Path
    extension: str
    file_size: int
    width: Optional[int]
    height: Optional[int]
    modified_time: datetime
    image_format: Optional[str]
    status: str
    error: Optional[str] = None
    metadata: Optional[ImageMetadata] = None
    perceptual_hash: Optional[str] = None
    quality_metrics: QualityMetrics | None = None
    quality_score: QualityScore | None = None

@dataclass
class ScanResult:
    """Result of scanning a folder for supported images."""

    folder: Path
    recursive: bool
    images: list[ImageRecord]
    discovered_count: int
    unsupported_count: int

    @property
    def supported_count(self) -> int:
        """Return the number of supported image files discovered."""
        return len(self.images)

    @property
    def successful_count(self) -> int:
        """Return the number of successfully indexed images."""
        return sum(image.status == "success" for image in self.images)

    @property
    def failed_count(self) -> int:
        """Return the number of supported images that failed to index."""
        return sum(image.status == "failed" for image in self.images)


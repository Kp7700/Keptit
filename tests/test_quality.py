from PIL import Image, ImageFilter

from keptit.quality import (
    MAX_DIMENSION,
    _prepare_grayscale,
    analyze_image_quality,
    calculate_quality_metrics,
)

from keptit.models import ImageMetadata, ImageRecord


def test_black_image():
    image = Image.new("L", (10, 10), 0)

    metrics = calculate_quality_metrics(image)

    assert metrics.mean_luminance == 0.0
    assert metrics.dark_pixel_ratio == 1.0
    assert metrics.bright_pixel_ratio == 0.0
    assert metrics.sharpness_variance == 0.0


def test_white_image():
    image = Image.new("L", (10, 10), 255)

    metrics = calculate_quality_metrics(image)

    assert metrics.mean_luminance == 255.0
    assert metrics.dark_pixel_ratio == 0.0
    assert metrics.bright_pixel_ratio == 1.0
    assert metrics.sharpness_variance == 0.0


def test_middle_gray_image():
    image = Image.new("L", (10, 10), 128)

    metrics = calculate_quality_metrics(image)

    assert metrics.mean_luminance == 128.0
    assert metrics.dark_pixel_ratio == 0.0
    assert metrics.bright_pixel_ratio == 0.0
    assert metrics.sharpness_variance == 0.0


def test_mixed_exposure_ratios():
    image = Image.new("L", (10, 10), 128)

    for x in range(5):
        for y in range(10):
            image.putpixel((x, y), 0)

    for x in range(5, 10):
        for y in range(10):
            image.putpixel((x, y), 255)

    metrics = calculate_quality_metrics(image)

    assert metrics.mean_luminance == 127.5
    assert metrics.dark_pixel_ratio == 0.5
    assert metrics.bright_pixel_ratio == 0.5


def test_high_frequency_image_has_sharpness():
    image = Image.new("L", (20, 20), 0)

    for x in range(20):
        for y in range(20):
            if (x + y) % 2 == 0:
                image.putpixel((x, y), 255)

    metrics = calculate_quality_metrics(image)

    assert metrics.sharpness_variance > 0.0


def test_blurring_reduces_sharpness():
    image = Image.new("L", (50, 50), 0)

    for x in range(10, 40):
        for y in range(10, 40):
            image.putpixel((x, y), 255)

    sharp_metrics = calculate_quality_metrics(image)

    blurred = image.filter(ImageFilter.GaussianBlur(radius=3))
    blurred_metrics = calculate_quality_metrics(blurred)

    assert blurred_metrics.sharpness_variance < sharp_metrics.sharpness_variance


def test_large_image_is_bounded_to_max_dimension():
    image = Image.new("RGB", (3000, 4000), "gray")

    grayscale = _prepare_grayscale(image)

    assert max(grayscale.size) == MAX_DIMENSION
    assert grayscale.size == (768, 1024)


def test_small_image_is_not_resized():
    image = Image.new("RGB", (800, 600), "gray")

    grayscale = _prepare_grayscale(image)

    assert grayscale.size == (800, 600)


def test_quality_calculation_is_deterministic():
    image = Image.new("L", (100, 100), 128)

    for x in range(25, 75):
        for y in range(25, 75):
            image.putpixel((x, y), 255)

    first = calculate_quality_metrics(image)
    second = calculate_quality_metrics(image)

    assert first == second


def make_test_record(path, status="success"):
    return ImageRecord(
        id="test-id",
        filename=path.name,
        path=path,
        extension=path.suffix,
        file_size=path.stat().st_size,
        width=100,
        height=100,
        modified_time=path.stat().st_mtime,
        image_format="PNG",
        status=status,
        error=None,
        metadata=ImageMetadata(),
        perceptual_hash="0123456789abcdef",
    )


def test_analyze_image_quality_populates_metrics(tmp_path):
    path = tmp_path / "test.png"

    image = Image.new("L", (100, 100), 128)
    image.save(path)

    record = make_test_record(path)

    result = analyze_image_quality(record)

    assert result.quality_metrics is not None
    assert result.quality_metrics.mean_luminance == 128.0


def test_analyze_image_quality_does_not_mutate_original_record(tmp_path):
    path = tmp_path / "test.png"

    image = Image.new("L", (100, 100), 128)
    image.save(path)

    record = make_test_record(path)

    result = analyze_image_quality(record)

    assert record.quality_metrics is None
    assert result.quality_metrics is not None


def test_analyze_image_quality_preserves_record_fields(tmp_path):
    path = tmp_path / "test.png"

    image = Image.new("L", (100, 100), 128)
    image.save(path)

    record = make_test_record(path)

    result = analyze_image_quality(record)

    assert result.id == record.id
    assert result.path == record.path
    assert result.filename == record.filename
    assert result.metadata == record.metadata
    assert result.perceptual_hash == record.perceptual_hash


def test_analyze_image_quality_ignores_failed_record(tmp_path):
    path = tmp_path / "broken.png"
    path.write_bytes(b"not an image")

    record = make_test_record(path, status="failed")

    result = analyze_image_quality(record)

    assert result is record
    assert result.quality_metrics is None

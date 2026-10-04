from dataclasses import replace

from PIL import Image

from keptit.models import ImageRecord, QualityMetrics


MAX_DIMENSION = 1024


def _prepare_grayscale(image: Image.Image) -> Image.Image:
    grayscale = image.convert("L")

    if max(grayscale.size) > MAX_DIMENSION:
        grayscale.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

    return grayscale


def _calculate_laplacian_variance(grayscale: Image.Image) -> float:
    width, height = grayscale.size

    if width < 3 or height < 3:
        return 0.0

    pixels = list(grayscale.get_flattened_data())

    laplacian_values = []

    for y in range(1, height - 1):
        row_start = y * width
        previous_row = row_start - width
        next_row = row_start + width

        for x in range(1, width - 1):
            index = row_start + x

            center = pixels[index]
            left = pixels[index - 1]
            right = pixels[index + 1]
            top = pixels[previous_row + x]
            bottom = pixels[next_row + x]

            laplacian_values.append(
                4 * center
                - left
                - right
                - top
                - bottom
            )

    mean = sum(laplacian_values) / len(laplacian_values)

    return sum(
        (value - mean) ** 2
        for value in laplacian_values
    ) / len(laplacian_values)


def calculate_quality_metrics(image: Image.Image) -> QualityMetrics:
    grayscale = _prepare_grayscale(image)
    pixels = list(grayscale.get_flattened_data())

    pixel_count = len(pixels)

    if pixel_count == 0:
        raise ValueError("Cannot calculate quality metrics for an empty image")

    mean_luminance = sum(pixels) / pixel_count

    dark_pixel_ratio = (
        sum(pixel < 32 for pixel in pixels) / pixel_count
    )

    bright_pixel_ratio = (
        sum(pixel > 223 for pixel in pixels) / pixel_count
    )

    sharpness_variance = _calculate_laplacian_variance(grayscale)

    return QualityMetrics(
        sharpness_variance=sharpness_variance,
        mean_luminance=mean_luminance,
        dark_pixel_ratio=dark_pixel_ratio,
        bright_pixel_ratio=bright_pixel_ratio,
    )


def analyze_image_quality(record: ImageRecord) -> ImageRecord:
    """Calculate quality metrics for a successfully indexed image."""

    if record.status != "success":
        return record

    try:
        with Image.open(record.path) as image:
            metrics = calculate_quality_metrics(image)
    except Exception as error:
        raise RuntimeError(
            f"Failed to calculate quality metrics for {record.filename}: {error}"
        ) from error

    return replace(
        record,
        quality_metrics=metrics,
    )

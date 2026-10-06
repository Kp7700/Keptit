import math

from keptit.models import QualityMetrics, QualityScore


SHARPNESS_REFERENCE = 10_000.0


def _validate_quality_metrics(metrics: QualityMetrics) -> None:
    if metrics.sharpness_variance < 0:
        raise ValueError("sharpness_variance cannot be negative")

    if not 0.0 <= metrics.dark_pixel_ratio <= 1.0:
        raise ValueError("dark_pixel_ratio must be between 0.0 and 1.0")

    if not 0.0 <= metrics.bright_pixel_ratio <= 1.0:
        raise ValueError("bright_pixel_ratio must be between 0.0 and 1.0")

    if metrics.dark_pixel_ratio + metrics.bright_pixel_ratio > 1.0:
        raise ValueError(
            "dark_pixel_ratio and bright_pixel_ratio cannot sum to more than 1.0"
        )


def _calculate_sharpness_component(sharpness_variance: float) -> float:
    return min(
        math.log1p(sharpness_variance)
        / math.log1p(SHARPNESS_REFERENCE),
        1.0,
    )


def _calculate_exposure_component(
    dark_pixel_ratio: float,
    bright_pixel_ratio: float,
) -> float:
    clipping_ratio = dark_pixel_ratio + bright_pixel_ratio
    return 1.0 - clipping_ratio


def calculate_quality_score(metrics: QualityMetrics) -> QualityScore:
    """Calculate a deterministic 0–100 heuristic quality score."""

    _validate_quality_metrics(metrics)

    sharpness_component = _calculate_sharpness_component(
        metrics.sharpness_variance
    )

    exposure_component = _calculate_exposure_component(
        metrics.dark_pixel_ratio,
        metrics.bright_pixel_ratio,
    )

    overall = (
        0.5 * sharpness_component
        + 0.5 * exposure_component
    )

    overall_score = round(overall * 100)

    return QualityScore(
        sharpness_component=sharpness_component,
        exposure_component=exposure_component,
        overall_score=overall_score,
    )

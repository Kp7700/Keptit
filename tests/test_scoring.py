import pytest

from keptit.models import QualityMetrics
from keptit.scoring import (
    SHARPNESS_REFERENCE,
    calculate_quality_score,
)


def make_metrics(
    sharpness=0.0,
    dark=0.0,
    bright=0.0,
):
    return QualityMetrics(
        sharpness_variance=sharpness,
        mean_luminance=128.0,
        dark_pixel_ratio=dark,
        bright_pixel_ratio=bright,
    )


def test_zero_sharpness_produces_zero_sharpness_component():
    result = calculate_quality_score(make_metrics(sharpness=0.0))

    assert result.sharpness_component == 0.0


def test_reference_sharpness_produces_full_sharpness_component():
    result = calculate_quality_score(
        make_metrics(sharpness=SHARPNESS_REFERENCE)
    )

    assert result.sharpness_component == 1.0


def test_sharpness_above_reference_is_saturated():
    result = calculate_quality_score(
        make_metrics(sharpness=SHARPNESS_REFERENCE * 100)
    )

    assert result.sharpness_component == 1.0


def test_increasing_sharpness_does_not_decrease_component():
    low = calculate_quality_score(make_metrics(sharpness=100.0))
    high = calculate_quality_score(make_metrics(sharpness=1000.0))

    assert high.sharpness_component >= low.sharpness_component


def test_zero_clipping_produces_full_exposure_component():
    result = calculate_quality_score(
        make_metrics(dark=0.0, bright=0.0)
    )

    assert result.exposure_component == 1.0


def test_all_dark_pixels_produce_zero_exposure_component():
    result = calculate_quality_score(
        make_metrics(dark=1.0, bright=0.0)
    )

    assert result.exposure_component == 0.0


def test_all_bright_pixels_produce_zero_exposure_component():
    result = calculate_quality_score(
        make_metrics(dark=0.0, bright=1.0)
    )

    assert result.exposure_component == 0.0


def test_increasing_clipping_does_not_increase_exposure_component():
    low = calculate_quality_score(
        make_metrics(dark=0.1, bright=0.1)
    )
    high = calculate_quality_score(
        make_metrics(dark=0.3, bright=0.2)
    )

    assert high.exposure_component <= low.exposure_component


def test_final_score_is_bounded():
    cases = [
        make_metrics(),
        make_metrics(sharpness=10000),
        make_metrics(sharpness=1000000),
        make_metrics(dark=1.0),
        make_metrics(bright=1.0),
    ]

    for metrics in cases:
        result = calculate_quality_score(metrics)

        assert 0 <= result.overall_score <= 100


def test_perfect_components_produce_score_100():
    result = calculate_quality_score(
        make_metrics(
            sharpness=SHARPNESS_REFERENCE,
            dark=0.0,
            bright=0.0,
        )
    )

    assert result.overall_score == 100


def test_zero_sharpness_and_total_clipping_produce_score_0():
    result = calculate_quality_score(
        make_metrics(
            sharpness=0.0,
            dark=1.0,
            bright=0.0,
        )
    )

    assert result.overall_score == 0


def test_same_inputs_produce_same_score():
    metrics = make_metrics(
        sharpness=2762.411495,
        dark=0.05,
        bright=0.10,
    )

    first = calculate_quality_score(metrics)
    second = calculate_quality_score(metrics)

    assert first == second


def test_better_sharpness_does_not_decrease_final_score():
    low = calculate_quality_score(
        make_metrics(sharpness=100.0, dark=0.1, bright=0.1)
    )
    high = calculate_quality_score(
        make_metrics(sharpness=1000.0, dark=0.1, bright=0.1)
    )

    assert high.overall_score >= low.overall_score


def test_better_exposure_does_not_decrease_final_score():
    poor = calculate_quality_score(
        make_metrics(sharpness=1000.0, dark=0.3, bright=0.2)
    )
    better = calculate_quality_score(
        make_metrics(sharpness=1000.0, dark=0.1, bright=0.1)
    )

    assert better.overall_score >= poor.overall_score


@pytest.mark.parametrize(
    "metrics",
    [
        make_metrics(sharpness=-1.0),
        make_metrics(dark=-0.1),
        make_metrics(dark=1.1),
        make_metrics(bright=-0.1),
        make_metrics(bright=1.1),
        make_metrics(dark=0.8, bright=0.3),
    ],
)
def test_invalid_metrics_are_rejected(metrics):
    with pytest.raises(ValueError):
        calculate_quality_score(metrics)



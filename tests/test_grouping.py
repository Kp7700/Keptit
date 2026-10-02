from datetime import datetime
from pathlib import Path

from keptit.models import ImageRecord
from keptit.grouping import group_images, hamming_distance


def make_record(
    image_id: str,
    perceptual_hash: str | None,
    status: str = "success",
) -> ImageRecord:
    return ImageRecord(
        id=image_id,
        filename=f"{image_id}.jpg",
        path=Path(f"/photos/{image_id}.jpg"),
        extension=".jpg",
        file_size=1000,
        width=100,
        height=100,
        modified_time=datetime.now(),
        image_format="JPEG",
        status=status,
        perceptual_hash=perceptual_hash,
    )


def test_hamming_distance_identical_hashes():
    assert hamming_distance("0000000000000000", "0000000000000000") == 0


def test_hamming_distance_one_bit_difference():
    assert hamming_distance("0000000000000000", "0000000000000001") == 1


def test_hamming_distance_known_difference():
    assert hamming_distance("0000000000000000", "ffffffffffffffff") == 64


def test_group_images_groups_similar_images():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000001"),
        make_record("c", "ffffffffffffffff"),
    ]

    groups = group_images(images, threshold=1)

    assert [group.image_ids for group in groups] == [
        ["a", "b"],
        ["c"],
    ]


def test_group_images_keeps_singletons():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "ffffffffffffffff"),
    ]

    groups = group_images(images, threshold=1)

    assert [group.image_ids for group in groups] == [
        ["a"],
        ["b"],
    ]


def test_group_images_uses_transitive_connections():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000001"),
        make_record("c", "0000000000000003"),
    ]

    groups = group_images(images, threshold=1)

    assert [group.image_ids for group in groups] == [
        ["a", "b", "c"],
    ]


def test_group_images_ignores_missing_hashes():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", None),
        make_record("c", "0000000000000001"),
    ]

    groups = group_images(images, threshold=1)

    assert [group.image_ids for group in groups] == [
        ["a", "c"],
    ]


def test_group_images_ignores_failed_records():
    images = [
        make_record("a", "0000000000000000"),
        make_record(
            "b",
            "0000000000000001",
            status="failed",
        ),
        make_record("c", "0000000000000001"),
    ]

    groups = group_images(images, threshold=1)

    assert [group.image_ids for group in groups] == [
        ["a", "c"],
    ]


def test_group_images_is_deterministic():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000001"),
        make_record("c", "ffffffffffffffff"),
    ]

    first = group_images(images, threshold=1)
    second = group_images(images, threshold=1)

    assert first == second


def test_group_images_groups_distance_below_threshold():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000001"),
    ]

    groups = group_images(images, threshold=2)

    assert [group.image_ids for group in groups] == [
        ["a", "b"],
    ]


def test_group_images_groups_distance_equal_to_threshold():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000003"),
    ]

    groups = group_images(images, threshold=2)

    assert [group.image_ids for group in groups] == [
        ["a", "b"],
    ]


def test_group_images_does_not_group_distance_above_threshold():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000007"),
    ]

    groups = group_images(images, threshold=2)

    assert [group.image_ids for group in groups] == [
        ["a"],
        ["b"],
    ]


def test_group_images_with_zero_threshold_groups_identical_hashes():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "0000000000000000"),
        make_record("c", "0000000000000001"),
    ]

    groups = group_images(images, threshold=0)

    assert [group.image_ids for group in groups] == [
        ["a", "b"],
        ["c"],
    ]


def test_group_images_uses_default_threshold():
    images = [
        make_record("a", "0000000000000000"),
        make_record("b", "00000000000000ff"),
        make_record("c", "00000000000001ff"),
    ]

    groups = group_images(images)

    assert [group.image_ids for group in groups] == [
        ["a", "b", "c"],
    ]

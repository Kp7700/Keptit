from dataclasses import dataclass

from keptit.models import ImageRecord


@dataclass
class ImageGroup:
    """A group of visually similar images."""

    image_ids: list[str]


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Return the Hamming distance between two 64-bit hexadecimal hashes."""
    value_a = int(hash_a, 16)
    value_b = int(hash_b, 16)

    return (value_a ^ value_b).bit_count()


def group_images(
    images: list[ImageRecord],
    threshold: int = 8,
) -> list[ImageGroup]:
    """Group images whose perceptual hashes are within the given threshold."""

    comparable_images = [
        image
        for image in images
        if image.status == "success" and image.perceptual_hash is not None
    ]

    adjacency: dict[str, set[str]] = {
        image.id: set() for image in comparable_images
    }

    for index, image_a in enumerate(comparable_images):
        for image_b in comparable_images[index + 1:]:
            distance = hamming_distance(
                image_a.perceptual_hash,
                image_b.perceptual_hash,
            )

            if distance <= threshold:
                adjacency[image_a.id].add(image_b.id)
                adjacency[image_b.id].add(image_a.id)

    groups: list[ImageGroup] = []
    visited: set[str] = set()

    for image in comparable_images:
        if image.id in visited:
            continue

        stack = [image.id]
        visited.add(image.id)
        group_ids: list[str] = []

        while stack:
            current_id = stack.pop()
            group_ids.append(current_id)

            for neighbor_id in sorted(adjacency[current_id]):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    stack.append(neighbor_id)

        groups.append(ImageGroup(image_ids=group_ids))

    return groups

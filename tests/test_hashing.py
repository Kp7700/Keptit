from PIL import Image

from keptit.hashing import HashingError, compute_dhash


def test_dhash_is_deterministic():
    image = Image.new("L", (100, 100), color=128)

    first = compute_dhash(image)
    second = compute_dhash(image)

    assert first == second


def test_dhash_returns_64_bit_hex_string():
    image = Image.new("RGB", (100, 100), color="white")

    result = compute_dhash(image)

    assert isinstance(result, str)
    assert len(result) == 16
    assert all(character in "0123456789abcdef" for character in result)


def test_dhash_changes_when_image_structure_changes():
    image_a = Image.new("L", (100, 100), color=0)

    image_b = Image.new("L", (100, 100), color=0)

    for x in range(50, 100):
        for y in range(100):
            image_b.putpixel((x, y), 255)

    result_a = compute_dhash(image_a)
    result_b = compute_dhash(image_b)

    assert result_a != result_b


def test_dhash_accepts_rgb_images():
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    result = compute_dhash(image)

    assert isinstance(result, str)
    assert len(result) == 16

def test_dhash_known_image():
    image = Image.new("L", (8, 8), color=0)

    for x in range(4, 8):
        for y in range(8):
            image.putpixel((x, y), 255)

    assert compute_dhash(image) == "1818181818181818"

def test_dhash_wraps_hashing_failure(monkeypatch):
    image = Image.new("RGB", (100, 100), color="white")

    def failing_convert(_mode):
        raise ValueError("conversion failed")

    monkeypatch.setattr(image, "convert", failing_convert)

    try:
        compute_dhash(image)
    except HashingError as error:
        assert str(error) == "Failed to compute perceptual hash"
    else:
        raise AssertionError("Expected HashingError")


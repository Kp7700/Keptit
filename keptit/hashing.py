from PIL import Image


class HashingError(Exception):
    """Raised when perceptual hashing fails."""


def compute_dhash(image: Image.Image) -> str:
    """Compute a 64-bit perceptual dHash for an image."""
    try:
        grayscale = image.convert("L")
        resized = grayscale.resize((9, 8))

        pixels = list(resized.get_flattened_data())

        hash_bits = []

        for row in range(8):
            row_start = row * 9
            for column in range(8):
                left = pixels[row_start + column]
                right = pixels[row_start + column + 1]
                hash_bits.append(left < right)

        hash_value = 0
        for bit in hash_bits:
            hash_value = (hash_value << 1) | int(bit)

        return f"{hash_value:016x}"
    except (OSError, ValueError, TypeError) as error:
        raise HashingError("Failed to compute perceptual hash") from error
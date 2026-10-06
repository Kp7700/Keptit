# Keptit

Keptit is a local-first, open-source photo culling tool designed to help photographers manage and analyze their photos without sending them to cloud services.

## Current Version

**v0.0.6 — Scoring**

This version extends the v0.0.5 quality-measurement foundation with a deterministic heuristic quality score.

The score combines the existing image-quality measurements into a bounded 0–100 score. It is intended to provide an explainable indication of how favorable the currently implemented measurable signals are under Keptit's scoring configuration.

The score is a heuristic. It is **not** an objective measurement of photographic quality and does not determine which photograph should be kept.

The scoring system currently uses:

- Sharpness variance
- Dark pixel ratio
- Bright pixel ratio

Mean luminance remains available as a quality measurement but does not directly contribute to the current score.

The scoring calculation is deterministic and runs locally without external services or AI/ML inference.

## Features

* Scan a selected folder for images
* Recursive folder scanning
* Supports:

  * JPG
  * JPEG
  * PNG
* Case-insensitive file extensions
* Detect unsupported files
* Detect corrupt or unreadable images
* Continue scanning when an image cannot be read
* Collect basic image information:

  * Filename
  * Absolute path
  * File extension
  * File size
  * Width
  * Height
  * Modification time
  * Image format
  * Scan status
* Extract supported EXIF metadata:

  * Capture date and time
  * Camera make
  * Camera model
  * Orientation
  * Focal length
  * ISO
* Handle missing metadata without failing image indexing
* Handle malformed individual metadata fields without failing image indexing
* Unique ID for each image record
* Structured scan results
* Human-readable scan summary
* Command-line interface
* Automated tests
* Generate a 64-bit perceptual dHash for successfully indexed images
* Group visually similar successfully indexed images using perceptual-hash Hamming distance
* Deterministic similarity grouping
* Display similarity groups through the command-line interface
* Calculate local image-quality measurements:

  * Sharpness variance as a sharpness/focus proxy
  * Mean luminance
  * Dark pixel ratio
  * Bright pixel ratio
* Bound quality analysis to a maximum working dimension of 1024 pixels
* Display quality measurements through the command-line interface
* Enable quality analysis explicitly with `--quality`
* Calculate a deterministic heuristic quality score from existing quality measurements
* Normalize sharpness using a fixed logarithmic transformation
* Combine sharpness and exposure/clipping components using equal weighting
* Bound the resulting heuristic score to 0–100
* Display quality-score components and the overall score through the command-line interface

## Privacy

Keptit is designed as a local-first application.

In v0.0.6:

* Images are processed locally.
* EXIF metadata is extracted locally using Pillow.
* Perceptual hashes are generated locally.
* Quality metrics are calculated locally using Pillow.
* Quality scores are calculated locally from existing quality metrics.
* No images are uploaded to a cloud service.
* No external AI APIs are used.
* No neural-network inference is used.
* The scanner does not modify image files.
* Image grouping is performed locally using stored perceptual hashes.
* Scoring does not require external services or network access.

## Installation

Clone the repository and install Keptit in editable mode:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd keptit
pip install -e .
```

Keptit requires **Python 3.10 or newer**.

## Usage

Scan a folder:

```bash
keptit scan "path/to/folder"
```

Scan a folder recursively:

```bash
keptit scan "path/to/folder" --recursive
```

You can also run the CLI directly through Python:

```bash
python -m keptit.cli scan "path/to/folder"
```

Scan a folder and group similar images:

```bash
keptit scan "path/to/folder" --group
```

Scan a folder recursively and group similar images:

```bash
keptit scan "path/to/folder" --recursive --group
```

You can also enable grouping when running the CLI through Python:

```bash
python -m keptit.cli scan "path/to/folder" --group
```

Scan a folder and calculate quality metrics and scores:

```bash
keptit scan "path/to/folder" --quality
```

Scan a folder recursively and calculate quality metrics and scores:

```bash
keptit scan "path/to/folder" --recursive --quality
```

Quality analysis is opt-in. The normal scan command does not calculate quality metrics or scores.

Quality analysis can also be combined with similarity grouping:

```bash
keptit scan "path/to/folder" --quality --group
```

You can also enable quality analysis when running the CLI through Python:

```bash
python -m keptit.cli scan "path/to/folder" --quality
```

## Quality Metrics and Scoring

Keptit separates **measurement** from **judgment**.

Quality metrics describe observable characteristics of an image.

The quality score combines selected metrics through a documented deterministic heuristic.

The conceptual pipeline is:

```text
QualityMetrics
     ↓
Normalization
     ↓
Weighted combination
     ↓
QualityScore
```

### Sharpness Variance

Sharpness is measured using the variance of a discrete Laplacian response over the grayscale image.

It is a **sharpness/focus proxy**, not a direct measurement of photographic quality. Higher values indicate greater local intensity variation in the analyzed image.

Texture, noise, compression artifacts, scene content, motion blur, defocus blur, resizing, and camera or editor sharpening can all affect the measurement.

The sharpness calculation is performed on a working image whose longest dimension is limited to 1024 pixels. Images smaller than this limit are not enlarged.

### Mean Luminance

Mean luminance is the arithmetic mean of grayscale pixel values.

The value ranges from 0 to 255:

- 0 represents black.
- 255 represents white.
- Higher values indicate a brighter average image.

A higher mean luminance does not mean that an image is better exposed.

Mean luminance is currently reported as a quality measurement but is not directly included in the v0.0.6 quality score.

### Dark Pixel Ratio

Dark pixel ratio is the proportion of analyzed pixels with grayscale luminance below 32.

The value ranges from 0.0 to 1.0.

### Bright Pixel Ratio

Bright pixel ratio is the proportion of analyzed pixels with grayscale luminance above 223.

The value ranges from 0.0 to 1.0.

These measurements describe image characteristics. They do not independently determine whether an image is good or bad.

## Quality Score

The v0.0.6 score is a deterministic heuristic derived from the currently available quality measurements.

It should be understood as:

> A deterministic heuristic indicating how favorable the currently implemented image-quality measurements are under Keptit's scoring configuration.

It should **not** be interpreted as:

- a percentage of photographic quality
- a probability that the image is the best photograph
- a probability that the user should keep the photograph
- an objective measure of artistic or photographic quality

### Sharpness Component

Sharpness variance is unbounded, so it is transformed using a logarithmic normalization.

The fixed reference value is:

```text
SHARPNESS_REFERENCE = 10,000
```

The normalized sharpness component is:

```text
sharpness_component =
    min(
        log1p(sharpness_variance) /
        log1p(10,000),
        1.0
    )
```

This transformation reduces the effect of very large sharpness values while preserving the direction that higher measured sharpness produces a higher component.

Values at or above the reference point are capped at 1.0.

The reference value is an engineering calibration constant for normalization. It is not intended to represent the sharpness of a perfect photograph.

### Exposure Component

The current score uses the measured dark and bright pixel ratios as a clipping-based exposure signal.

The calculation is:

```text
clipping_ratio =
    dark_pixel_ratio + bright_pixel_ratio

exposure_component =
    1.0 - clipping_ratio
```

This treats clipped dark and bright pixels as a penalty.

It does **not** attempt to determine the correct exposure of an arbitrary photograph.

A deliberately dark night photograph or a deliberately bright snow scene may therefore receive a lower exposure component even when the exposure is appropriate for the photographer's intent.

### Overall Score

The sharpness and exposure components currently use equal weighting:

```text
overall =
    0.5 × sharpness_component
  + 0.5 × exposure_component
```

The displayed score is:

```text
overall_score =
    round(overall × 100)
```

The final score is therefore bounded to:

```text
0–100
```

The value does not represent a percentage of photographic quality.

### Absolute Scoring

The v0.0.6 score is **absolute**, not dataset-relative.

The score for an image depends on its own `QualityMetrics` and the fixed scoring configuration.

Adding or removing other images from a scan does not change the mathematical score of an existing image.

This makes the calculation deterministic and comparable across separate scans, subject to the limitations of the underlying measurements.

### Missing and Invalid Data

The scoring function operates on a complete `QualityMetrics` object.

It does not silently replace missing measurements with arbitrary values.

Invalid values are rejected explicitly. For example:

- negative sharpness variance is invalid
- dark pixel ratio outside 0.0–1.0 is invalid
- bright pixel ratio outside 0.0–1.0 is invalid
- dark and bright pixel ratios whose sum exceeds 1.0 are invalid

The scoring layer does not reopen image files or recalculate quality measurements.

## Scoring Limitations

The current score is intentionally simple and explainable.

The underlying sharpness measurement is a high-frequency-detail proxy. It can be influenced by texture, noise, compression artifacts, camera sharpening, resizing, and scene content.

As a result, an image with strong high-frequency patterns can receive a relatively high sharpness measurement even when that high-frequency detail does not correspond to useful photographic sharpness.

Real-image testing has demonstrated this limitation. In particular, a blurred image can sometimes receive a higher score than a visually better image when its measured pixel characteristics produce a more favorable combination of the current components.

This does not indicate that the scoring formula failed mathematically. It demonstrates that the underlying measurements are imperfect proxies for photographic quality.

Similarly, the exposure component is based only on dark and bright pixel ratios. It does not understand photographic intent or scene context.

Therefore, the v0.0.6 score should be treated as an **explainable heuristic**, not as an authoritative photographic-quality judgment.

Quality scoring does not perform ranking, selection, confidence estimation, or deletion.

## Example

A scan produces a summary similar to:

```text
Keptit Scanner

Folder: integration_test_photos
Recursive: Yes

Files discovered: 5
Supported images: 4
Unsupported files: 1
Failed images: 1
Successfully indexed: 3
```

When grouping is enabled, the scan summary is followed by the detected similarity groups:

```text
Groups found: 2
Group 1:
  img1.png
  img2.jpg
Group 2:
  img3.png
```

When quality analysis is enabled, the output also contains quality measurements and scoring information:

```text
Quality Metrics:

- example.jpg
  Sharpness variance: 132.54
  Mean luminance: 74.28
  Dark pixel ratio: 0.3480
  Bright pixel ratio: 0.0054
  Sharpness component: 0.5314
  Exposure component: 0.6465
  Overall score: 59/100
```

Failed or unsupported files do not stop the rest of the scan.

## Testing

Run the test suite with:

```bash
pytest
```

The current v0.0.6 test suite contains **113 tests** covering folder scanning, metadata extraction, perceptual hashing, similarity grouping, Hamming-distance behavior, grouping thresholds, deterministic grouping, missing hashes, failed records, CLI grouping, quality metrics, quality-analysis behavior, quality scoring, scoring edge cases, ImageRecord quality integration, CLI quality output, supported and unsupported files, recursive scanning, corrupt images, path handling, case-insensitive extensions, metadata handling, hashing failures, scan results, and model behavior.

The scoring tests cover:

- deterministic calculations
- sharpness normalization
- sharpness saturation
- exposure/clipping calculation
- score bounds
- minimum and maximum-like inputs
- monotonic behavior
- invalid metric rejection
- deterministic repeated calculations
- integration with `QualityMetrics`
- integration with `ImageRecord`

Real-world integration testing has also been performed using multiple JPEG and PNG images containing balanced, blurred, sharp, underexposed, overexposed, and high-frequency image examples.

## Current Scope

Keptit v0.0.6 covers folder scanning, basic image indexing, selected EXIF metadata extraction, perceptual hashing, deterministic similarity grouping, local image-quality measurements, and deterministic heuristic quality scoring.

Quality measurements currently include:

* Sharpness variance
* Mean luminance
* Dark pixel ratio
* Bright pixel ratio

Quality scoring currently combines:

* Logarithmically normalized sharpness
* Exposure/clipping component derived from dark and bright pixel ratios

Quality analysis and scoring are optional and can be enabled through the `--quality` CLI option.

It does **not** currently perform:

* GPS metadata extraction
* Aperture extraction
* Shutter speed extraction
* Duplicate detection
* Burst grouping
* Image ranking or selection
* Best-photo selection
* Confidence calculation
* Face detection
* Eye detection
* Smile detection
* Image deletion
* RAW image processing
* GUI-based photo culling
* XMP writing
* AI/ML image analysis
* Cloud image processing
* External AI APIs

## Similarity Grouping

Keptit v0.0.4 can group successfully indexed images according to the Hamming distance between their 64-bit perceptual hashes.

A lower Hamming distance means fewer differing bits between two hashes. The grouping threshold determines the maximum distance at which images are considered similar.

The threshold is an engineering heuristic rather than a universal definition of "same photo." Changing the threshold can produce smaller or larger groups.

Images without a valid perceptual hash and failed image records do not participate in similarity grouping.

Similarity grouping does not determine which image is better, does not rank photographs, and does not perform automatic selection or deletion.

## License

Keptit is released under the **MIT License**.

See [`LICENSE`](LICENSE) for the full license text.

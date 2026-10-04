# Keptit

Keptit is a local-first, open-source photo culling tool designed to help photographers manage and analyze their photos without sending them to cloud services.

## Current Version

**v0.0.5 — Quality Metrics**

This version extends the v0.0.4 grouping foundation with local image-quality measurements.

Quality analysis measures observable image characteristics without assigning an overall quality score or selecting a preferred image.

The following quality metrics are currently calculated:

- Sharpness variance
- Mean luminance
- Dark pixel ratio
- Bright pixel ratio

Quality analysis is deterministic and runs locally using Pillow.

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

## Privacy

Keptit is designed as a local-first application.

In v0.0.5:

* Images are processed locally.
* EXIF metadata is extracted locally using Pillow.
* Perceptual hashes are generated locally using Pillow.
* Quality metrics are calculated locally using Pillow.
* No images are uploaded to a cloud service.
* No external AI APIs are used.
* No neural-network inference is used.
* The scanner does not modify image files.
* Image grouping is performed locally using stored perceptual hashes.

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

Scan a folder and calculate quality metrics:

```bash
keptit scan "path/to/folder" --quality
```

Scan a folder recursively and calculate quality metrics:

```bash
keptit scan "path/to/folder" --recursive --quality
```

Quality analysis is opt-in. The normal scan command does not calculate quality metrics.

Quality metrics can also be combined with similarity grouping:

```bash
keptit scan "path/to/folder" --quality --group
```

You can also enable quality analysis when running the CLI through Python:

```bash
python -m keptit.cli scan "path/to/folder" --quality
```

## Quality Metrics

Keptit v0.0.5 reports raw image measurements rather than an overall quality score.

### Sharpness Variance

Sharpness is measured using the variance of a discrete Laplacian response over the grayscale image.

It is a **sharpness/focus proxy**, not a direct measurement of photographic quality. Higher values indicate greater local intensity variation in the analyzed image. Texture, noise, compression artifacts, scene content, motion blur, defocus blur, resizing, and camera or editor sharpening can all affect the measurement.

The sharpness calculation is performed on a working image whose longest dimension is limited to 1024 pixels. Images smaller than this limit are not enlarged.

### Mean Luminance

Mean luminance is the arithmetic mean of grayscale pixel values.

The value ranges from 0 to 255:

- 0 represents black.
- 255 represents white.
- Higher values indicate a brighter average image.

A higher mean luminance does not mean that an image is better exposed.

### Dark Pixel Ratio

Dark pixel ratio is the proportion of analyzed pixels with grayscale luminance below 32.

The value ranges from 0.0 to 1.0.

### Bright Pixel Ratio

Bright pixel ratio is the proportion of analyzed pixels with grayscale luminance above 223.

The value ranges from 0.0 to 1.0.

These measurements describe image characteristics. They do not determine whether an image is good or bad.

Quality analysis does not perform ranking, scoring, selection, or deletion.

## Example

A scan produces a summary similar to:

```text
Keptit Scan Summary
-------------------
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

Failed or unsupported files do not stop the rest of the scan.

## Testing

Run the test suite with:

```bash
pytest
```

The current v0.0.5 test suite contains **91 tests** covering folder scanning, metadata extraction, perceptual hashing, similarity grouping, Hamming-distance behavior, grouping thresholds, deterministic grouping, missing hashes, failed records, CLI grouping, quality metrics, quality-analysis behavior, CLI quality output, supported and unsupported files, recursive scanning, corrupt images, path handling, case-insensitive extensions, metadata handling, hashing failures, scan results, and model behavior.

The quality tests include deterministic synthetic-image tests for:

- Uniform black images
- Uniform white images
- Middle-gray images
- Mixed exposure
- High-frequency image structure
- Blurred images
- Working-resolution limits
- Small-image preservation
- Deterministic calculations
- ImageRecord quality integration
- Failed-image handling

## Current Scope

Keptit v0.0.5 covers folder scanning, basic image indexing, selected EXIF metadata extraction, perceptual hashing, deterministic similarity grouping, and local image-quality measurements.

Quality measurements currently include:

* Sharpness variance
* Mean luminance
* Dark pixel ratio
* Bright pixel ratio

Quality analysis is optional and can be enabled through the `--quality` CLI option.

It does **not** currently perform:

* GPS metadata extraction
* Aperture extraction
* Shutter speed extraction
* Duplicate detection
* Burst grouping
* Overall image quality scoring
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

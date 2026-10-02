# Keptit

Keptit is a local-first, open-source photo culling tool designed to help photographers manage and analyze their photos without sending them to cloud services.

## Current Version

**v0.0.4 — Grouping**

This version extends the v0.0.3 perceptual-hashing foundation with local similarity grouping based on perceptual-hash Hamming distance.

Grouping is deterministic and operates on the perceptual hashes already stored on successfully indexed images.

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

## Privacy

Keptit is designed as a local-first application.

In v0.0.4:

* Images are processed locally.
* EXIF metadata is extracted locally using Pillow.
* Perceptual hashes are generated locally using Pillow.
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

The v0.0.4 test suite contains 70 tests covering folder scanning, metadata extraction, perceptual hashing, similarity grouping, Hamming-distance behavior, grouping thresholds, deterministic grouping, missing hashes, failed records, CLI grouping, supported and unsupported files, recursive scanning, corrupt images, path handling, case-insensitive extensions, metadata handling, hashing failures, and scan results.

## Current Scope

Keptit v0.0.4 covers folder scanning, basic image indexing, selected EXIF metadata extraction, perceptual hashing, and deterministic similarity grouping.

It does **not** currently perform:

* GPS metadata extraction
* Aperture extraction
* Shutter speed extraction
* Duplicate detection
* Burst grouping
* Image quality scoring
* Face detection
* Eye detection
* Image ranking or selection
* Confidence calculation
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

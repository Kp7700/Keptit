# Keptit

Keptit is a local-first, open-source photo culling tool designed to help photographers manage and analyze their photos without sending them to cloud services.

## Current Version

**v0.0.1 — Folder Scanner + Basic Image Indexer**

This version provides the foundation of Keptit by scanning folders and collecting basic information about supported image files.

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
* Unique ID for each image record
* Structured scan results
* Human-readable scan summary
* Command-line interface
* Automated tests

## Privacy

Keptit is designed as a local-first application.

In v0.0.1:

* Images are processed locally.
* No images are uploaded to a cloud service.
* No external AI APIs are used.
* No neural-network inference is used.
* The scanner does not modify image files.

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

Failed or unsupported files do not stop the rest of the scan.

## Testing

Run the test suite with:

```bash
pytest
```

The v0.0.1 test suite covers folder scanning, supported and unsupported files, recursive scanning, corrupt images, image metadata, path handling, case-insensitive extensions, and scan results.

## Current Scope

Keptit v0.0.1 is intentionally limited to folder scanning and basic image indexing.

It does **not** currently perform:

* EXIF analysis
* Perceptual hashing
* Duplicate or similarity detection
* Burst grouping
* Image quality scoring
* Face detection
* Image ranking or selection
* RAW image processing
* GUI-based photo culling
* AI/ML image analysis
* Cloud image processing

## License

Keptit is released under the **MIT License**.

See [`LICENSE`](LICENSE) for the full license text.

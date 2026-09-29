# Changelog

All notable changes to Keptit are documented in this file.

## [0.0.1] - 2026-09-29

### Added

* Added the first working Keptit folder scanner and basic image indexer.
* Added support for JPG, JPEG, and PNG image files.
* Added non-recursive folder scanning.
* Added recursive folder scanning with `--recursive`.
* Added unsupported-file detection and handling.
* Added basic image information extraction:

  * image width
  * image height
  * image format
  * file size
  * file extension
  * absolute file path
  * filesystem modification time
* Added the `ImageRecord` data model for individual indexed images.
* Added the `ScanResult` data model for folder scan results.
* Added unique internal IDs for indexed images.
* Added corrupted and unreadable image handling without terminating the entire scan.
* Added explicit scan status and error information for failed images.
* Added human-readable scan summaries.
* Added scan accounting for:

  * files discovered
  * supported images
  * unsupported files
  * failed images
  * successfully indexed images
* Added the command-line interface:

  * `keptit scan <folder>`
  * `keptit scan <folder> --recursive`
* Added pytest-based unit tests.
* Added temporary-directory and synthetic-image testing using Pillow.
* Added CLI integration testing with valid, unsupported, corrupted, and nested image files.
* Completed the v0.0.1 test suite with 22 passing tests.

### Supported File Extensions

- `.jpg`
- `.jpeg`
- `.png`

### Not Included

The following are intentionally outside the scope of v0.0.1:

* EXIF metadata extraction
* Perceptual hashing
* Similarity detection
* Burst grouping
* Image quality analysis
* Image scoring
* Confidence calculation
* RAW image support
* GUI
* XMP functionality
* AI/ML image analysis
* Cloud image processing
* External AI APIs

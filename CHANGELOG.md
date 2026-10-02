# Changelog

All notable changes to Keptit are documented in this file.

## [0.0.4] - 2026-10-02

### Added

* Added deterministic similarity grouping for successfully indexed images.
* Added perceptual-hash Hamming-distance comparison for grouping.
* Added a configurable similarity threshold for grouping images.
* Added group representation for collections of visually similar images.
* Added handling for images without perceptual hashes so they do not participate in grouping.
* Added handling for failed image records so failed images do not participate in grouping.
* Added deterministic group ordering and membership behavior.
* Added the `--group` CLI option.
* Added grouping output showing the number of detected groups and their image filenames.
* Added grouping unit tests, threshold tests, deterministic grouping tests, missing-hash tests, failed-record tests, and CLI grouping tests.
* Kept Pillow as the only runtime dependency; no additional clustering or hashing library was introduced.

### Grouping Scope

The following are supported in v0.0.4:

* Similarity grouping using 64-bit perceptual hashes
* Hamming-distance comparison between perceptual hashes
* Configurable similarity threshold
* Deterministic grouping of similar images
* Handling of isolated images
* Exclusion of images without valid perceptual hashes
* Exclusion of failed image records
* CLI output for detected groups

The following remain intentionally outside the scope of v0.0.4:

* Duplicate detection
* Image quality analysis
* Face or eye detection
* Smile detection
* Image ranking
* Image selection
* Best-photo selection
* Confidence calculation
* Image deletion
* AI/ML image analysis
* Cloud image processing
* GUI
* Web interface
* Database-backed grouping
* XMP modification
* RAW image support

### Testing

* Completed the v0.0.4 test suite with 70 passing tests.
* Added tests for Hamming-distance calculation.
* Added tests for basic similarity grouping.
* Added tests for multiple independent groups.
* Added tests for threshold behavior.
* Added tests for isolated images.
* Added tests for missing perceptual hashes.
* Added tests for failed image records.
* Added deterministic grouping tests.
* Added scanner and grouping integration tests.
* Added CLI grouping tests.
* Preserved all previous scanner, metadata, and perceptual-hashing regression coverage.

## [0.0.3] - 2026-10-01

### Added

* Added local perceptual hashing using a 64-bit dHash implementation.
* Added the `perceptual_hash` field to `ImageRecord`.
* Added deterministic hexadecimal representation of generated perceptual hashes.
* Added hashing during successful image indexing.
* Added explicit `HashingError` handling so hashing failures produce failed image records without terminating the scan.
* Added hashing unit tests, known-output regression testing, model tests, scanner integration tests, and hashing failure tests.
* Kept Pillow as the only runtime dependency; no additional hashing library was introduced.

### Hashing Scope

The following are supported in v0.0.3:

* 64-bit dHash generation
* Local perceptual hash generation
* Storage of the generated hash on successful `ImageRecord` instances

The following remain intentionally outside the scope of v0.0.3:

* Duplicate detection
* Similarity detection
* Similarity thresholds
* Burst grouping
* Image quality analysis
* Face or eye detection
* Image ranking
* Image selection
* AI/ML image analysis
* Cloud image processing

### Testing

* Completed the v0.0.3 test suite with 49 passing tests.

## [0.0.2] - 2026-09-30

### Added

* Added the `ImageMetadata` data model for supported image metadata.
* Added local EXIF metadata extraction using Pillow.
* Added capture date and time extraction from `DateTimeOriginal`, with `DateTime` as a fallback.
* Added camera make extraction.
* Added camera model extraction.
* Added orientation extraction.
* Added focal length extraction with EXIF rational-value normalization.
* Added ISO extraction.
* Added metadata to successful `ImageRecord` instances.
* Added handling for images without EXIF metadata.
* Added handling for malformed individual metadata fields without failing image indexing.
* Preserved existing corrupted-image failure behavior.
* Added metadata extraction and scanner integration tests.

### Metadata Scope

The following metadata fields are supported in v0.0.2:

* Capture date and time
* Camera make
* Camera model
* Orientation
* Focal length
* ISO

The following are intentionally outside the scope of v0.0.2:

* GPS metadata
* Aperture
* Shutter speed
* XMP
* RAW metadata
* Perceptual hashing
* Similarity detection
* Burst grouping
* Image quality analysis
* Face or eye detection
* Image ranking
* AI/ML image analysis
* Cloud image processing

### Testing

* Completed the v0.0.2 test suite with 37 passing tests.

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

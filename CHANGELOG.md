# Changelog

All notable changes to Keptit are documented in this file.

## [0.0.6] - 2026-10-06

### Added

* Added the `QualityScore` data model.
* Added deterministic quality scoring based on the existing `QualityMetrics`.
* Added logarithmic normalization of sharpness variance.
* Added a fixed sharpness calibration reference of `10,000.0`.
* Added exposure/clipping scoring based on dark and bright pixel ratios.
* Added equal weighting between the normalized sharpness and exposure components.
* Added a bounded overall heuristic score in the range 0–100.
* Added quality-score integration with `ImageRecord`.
* Added quality-score output to the existing `--quality` CLI option.
* Added validation for invalid quality-metric inputs.
* Added deterministic scoring tests.
* Added mathematical boundary and monotonicity tests.
* Added quality-score integration tests.
* Preserved the existing quality measurements without changing their meaning.
* Kept scoring separate from image scanning, grouping, and CLI presentation.
* Kept Pillow as the only runtime dependency.

### Quality Scoring Scope

The following are supported in v0.0.6:

* Deterministic scoring from existing `QualityMetrics`.
* Logarithmic normalization of sharpness variance.
* Sharpness calibration reference of `10,000.0`.
* Exposure/clipping component derived from dark and bright pixel ratios.
* Equal 50/50 weighting between sharpness and exposure components.
* Final score bounded to 0–100.
* Per-image `QualityScore` stored on `ImageRecord`.
* Optional quality-score output through the existing `--quality` CLI option.
* Absolute scoring that does not depend on the other images in the current scan.

The score is defined as a deterministic heuristic indicating how favorable the currently implemented image-quality measurements are under Keptit's scoring configuration.

It is not:

* a percentage of photographic quality
* a probability that an image is the best photograph
* a probability that an image should be kept
* an objective measure of artistic or photographic quality

The scoring calculation is:

```text
sharpness_component =
    min(
        log1p(sharpness_variance) /
        log1p(10000.0),
        1.0
    )

clipping_ratio =
    dark_pixel_ratio + bright_pixel_ratio

exposure_component =
    1.0 - clipping_ratio

overall =
    0.5 * sharpness_component
    + 0.5 * exposure_component

overall_score =
    round(overall * 100)
```

## [0.0.5] - 2026-10-04

### Added

* Added the `QualityMetrics` data model.
* Added local image-quality analysis using Pillow.
* Added sharpness variance as a sharpness/focus proxy.
* Added mean luminance measurement.
* Added dark pixel ratio measurement.
* Added bright pixel ratio measurement.
* Added bounded-resolution quality analysis with a maximum working dimension of 1024 pixels.
* Added optional quality analysis through the `--quality` CLI option.
* Added quality metrics output showing raw measurements without an overall quality score.
* Added optional quality analysis integration with `ImageRecord`.
* Added deterministic quality-analysis tests.
* Added working-resolution and small-image behavior tests.
* Added tests for quality analysis of successful image records.
* Added tests ensuring failed image records are not analyzed.
* Added CLI tests for quality-option parsing and quality output.
* Kept Pillow as the only runtime dependency; no additional image-processing dependency was introduced.

### Quality Metrics Scope

The following are supported in v0.0.5:

* Sharpness variance using a discrete Laplacian response.
* Mean luminance using grayscale pixel values.
* Dark pixel ratio for pixels below luminance 32.
* Bright pixel ratio for pixels above luminance 223.
* Maximum quality-analysis working dimension of 1024 pixels.
* Deterministic quality calculations.
* Optional quality analysis through the CLI.
* Raw metric output without an overall quality score.

Sharpness variance is treated as a sharpness/focus proxy rather than a direct measure of photographic quality. Its value can be affected by texture, noise, compression, scene content, blur, resizing, and sharpening.

The quality metrics describe observable image characteristics. They do not determine which photograph is better.

The following remain intentionally outside the scope of v0.0.5:

* Overall image quality scoring
* Image ranking
* Image selection
* Best-photo selection
* Confidence calculation
* Face detection
* Eye detection
* Smile detection
* Image deletion
* AI/ML image analysis
* Cloud image processing
* GUI
* Web interface
* XMP modification
* RAW image support

### Testing

* Completed the v0.0.5 test suite with **91 passing tests**.
* Added tests for quality metric calculations.
* Added deterministic synthetic-image quality tests.
* Added sharpness behavior tests.
* Added exposure measurement tests.
* Added working-resolution tests.
* Added small-image preservation tests.
* Added deterministic calculation tests.
* Added `ImageRecord` quality-metric integration tests.
* Added failed-image quality-analysis tests.
* Added CLI quality-option tests.
* Added CLI quality-output tests.
* Preserved all previous scanner, metadata, perceptual-hashing, and grouping regression coverage.

### Performance

Quality analysis uses a bounded working resolution to prevent large source images from causing excessive processing time.

During local validation, three test images took approximately 52 seconds with the original full-resolution Python Laplacian implementation and approximately 0.88 seconds after the bounded-resolution and implementation optimization.

A subsequent end-to-end test through image indexing and quality analysis processed the same three images in approximately 1.10 seconds.

These measurements are development-machine benchmarks rather than formal performance guarantees.

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

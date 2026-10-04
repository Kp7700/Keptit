# Keptit Development Guide

## 1. Purpose

This document describes how Keptit should be developed, tested, reviewed, and extended.

Keptit is a local-first, open-source photo culling tool. Development should prioritize privacy, simplicity, deterministic behavior, explainability, maintainability, and incremental progress.

This document is a development guide. It does not replace the README or CHANGELOG.

* `README.md` explains what Keptit is and how to use it.
* `CHANGELOG.md` records what changed in each version.
* `DEVELOPMENT.md` explains how Keptit should be developed.

---

## 2. Current Version

Current version: **v0.0.5**

v0.0.5 is the **Quality Metrics** release.

The v0.0.5 implementation is considered complete.

The Keptit development progression is:

* v0.0.1 — Folder Scanner + Basic Image Indexer
* v0.0.2 — Metadata Extraction
* v0.0.3 — Perceptual Hashing
* v0.0.4 — Similarity Grouping
* v0.0.5 — Quality Metrics

The current repository contains:

```text
Keptit/
├── .gitignore
├── CHANGELOG.md
├── DEVELOPMENT.md
├── LICENSE
├── README.md
├── pyproject.toml
│
├── keptit/
│   ├── cli.py
│   ├── grouping.py
│   ├── hashing.py
│   ├── metadata.py
│   ├── models.py
│   ├── quality.py
│   └── scanner.py
│
└── tests/
    ├── test_cli.py
    ├── test_grouping.py
    ├── test_hashing.py
    ├── test_metadata.py
    ├── test_models.py
    ├── test_quality.py
    └── test_scanner.py
```

Do not assume files or directories exist if they are not present in the repository.

---

## 3. Development Principles

### 3.1 Incremental development

Build Keptit one small, understandable component at a time.

Do not implement several future features together simply because they are related.

Before adding a feature:

1. Inspect the current repository.
2. Determine what already exists.
3. Identify the smallest required change.
4. Implement it.
5. Add or update tests.
6. Run the relevant tests.
7. Run the complete test suite.
8. Verify the actual output.
9. Only then move to the next component.

Do not rewrite working code without a concrete reason.

### 3.2 Stay within the current version

Do not implement features belonging to a later Keptit version unless explicitly requested.

For example, while working on v0.0.5, do not add:

* duplicate detection
* burst grouping
* image quality scoring
* confidence scoring
* face detection
* image ranking
* automatic selection
* RAW support
* GUI
* XMP functionality
* AI/ML image analysis
* cloud processing
* external AI APIs
* overall quality scoring
* quality-based ranking or selection

A future feature may be discussed conceptually, but discussion is not permission to implement it.

### 3.3 Preserve working functionality

Changes should be as small as reasonably possible.

Avoid unnecessary rewrites, abstractions, frameworks, dependencies, or architectural changes.

Existing behavior should remain working unless the change intentionally modifies that behavior.

---

## 4. Architecture

Keptit should keep responsibilities separated.

The basic architecture is:

```text
CLI
 │
 ▼
Scanner
 │
 ├── File discovery
 ├── Image validation
 └── Image indexing
       │
       ▼
   ImageRecord[]
       │
       ├───────────────┐
       ▼               ▼
   Grouping        Quality
       │           Analysis
       ▼               │
 ImageGroup[]          ▼
                  QualityMetrics
```

### Quality Analysis

`keptit/quality.py`

The quality module contains local image-quality measurement logic.

It currently calculates:

* sharpness variance
* mean luminance
* dark pixel ratio
* bright pixel ratio

Quality analysis is independent of grouping. It does not rank images, calculate an overall quality score, select photographs, or modify image files.

Quality calculations use Pillow and operate on image pixel data.

Quality analysis is exposed through the CLI as an optional `--quality` capability.

### CLI

`keptit/cli.py`

The CLI handles command-line arguments and presentation of results.

It should not contain scanner logic.

### Scanner

`keptit/scanner.py`

The scanner contains the core folder-scanning and image-indexing behavior.

The scanner should be usable independently of the CLI.

For example:

```python
from keptit.scanner import scan_folder
```

### Models

`keptit/models.py`

Models represent structured data produced by the scanner.

The current primary models are:

* `ImageRecord`
* `ScanResult`

### Grouping

`keptit/grouping.py`

The grouping module contains similarity-grouping behavior based on the perceptual hashes already stored on successfully indexed `ImageRecord` objects.

Grouping should:

* consume existing perceptual hashes
* compare hashes using Hamming distance
* apply the configured similarity threshold
* construct deterministic groups
* exclude images without valid perceptual hashes
* exclude failed image records

Grouping should not perform image scanning, metadata extraction, or perceptual-hash generation.

The grouping module should be usable independently of the CLI.

### Tests

`tests/`

Tests verify the behavior of the models, scanner, and related functionality.

Tests should not depend on a user's personal photo collection.

---

## 5. Current v0.0.5 Scope

The scanner currently supports:

* JPG
* JPEG
* PNG

File extensions are case-insensitive.

The scanner can:

* scan a selected folder
* scan recursively
* identify supported image files
* identify unsupported files
* validate supported image files
* detect corrupted or unreadable images
* continue scanning after an image failure
* collect basic image information
* create `ImageRecord` objects
* create `ScanResult` objects
* produce a human-readable scan summary
* expose scanning through the CLI

The current implementation also:

* extracts selected EXIF metadata
* generates a 64-bit perceptual dHash for successfully indexed images
* stores the perceptual hash on `ImageRecord` objects
* handles hashing failures as failed image records
* groups successfully indexed images using perceptual-hash Hamming distance
* applies a similarity threshold during grouping
* produces deterministic similarity groups
* excludes images without valid perceptual hashes from grouping
* excludes failed image records from grouping
* calculates local image-quality measurements
* calculates sharpness variance as a sharpness/focus proxy
* calculates mean luminance
* calculates dark pixel ratio
* calculates bright pixel ratio
* limits quality-analysis working resolution to a maximum dimension of 1024 pixels
* stores quality measurements in `QualityMetrics`
* optionally attaches quality measurements to `ImageRecord`
* exposes quality analysis through the `--quality` CLI option

The current `ImageRecord` contains:

* unique ID
* filename
* absolute path
* extension
* file size
* width
* height
* modification time
* image format
* scan status
* error information when applicable
* perceptual hash when hashing succeeds
* quality metrics when quality analysis has been performed

---

## 6. v0.0.5 Quality Analysis

v0.0.5 establishes the first local image-quality measurement layer.

The quality-analysis module is:

```text
keptit/quality.py
```

The module currently provides measurements for:

* sharpness variance
* mean luminance
* dark pixel ratio
* bright pixel ratio

These are measurements rather than quality judgments.

The implementation deliberately does not calculate:

* an overall quality score
* a 0–100 quality rating
* image ranking
* image selection
* confidence
* best-photo determination

### Sharpness

Sharpness is measured using the variance of a discrete Laplacian response over a grayscale working image.

Conceptually:

```text
Image
 ↓
Grayscale
 ↓
Working-resolution image
 ↓
Laplacian response
 ↓
Variance
 ↓
Sharpness measurement
```

The resulting value is a sharpness/focus proxy.

Higher values generally indicate greater local intensity variation, but a higher value does not objectively mean that a photograph is better.

The measurement can be affected by:

* scene texture
* fine detail
* image noise
* compression artifacts
* motion blur
* defocus blur
* resizing
* camera or editor sharpening

### Mean Luminance

Mean luminance is calculated from grayscale pixel values.

The value ranges from approximately:

```text
0 → black
255 → white
```

Higher values indicate a brighter average image.

Higher mean luminance does not mean that an image has better exposure.

### Dark Pixel Ratio

Dark pixel ratio is the proportion of analyzed pixels with grayscale luminance below:

```text
32
```

The value ranges from 0.0 to 1.0.

### Bright Pixel Ratio

Bright pixel ratio is the proportion of analyzed pixels with grayscale luminance above:

```text
223
```

The value ranges from 0.0 to 1.0.

### Working Resolution

Quality analysis uses a bounded working resolution.

The longest image dimension is limited to:

```text
1024 pixels
```

Images smaller than this limit are not enlarged.

The bounded resolution prevents unnecessarily expensive processing of very large photographs.

Because resizing can affect numerical measurements, the working-resolution behavior is explicitly tested.

### Data Model

Quality measurements are represented by:

```python
@dataclass
class QualityMetrics:
    sharpness_variance: float
    mean_luminance: float
    dark_pixel_ratio: float
    bright_pixel_ratio: float
```

`ImageRecord` contains:

```python
quality_metrics: QualityMetrics | None
```

`None` means that quality measurements have not been attached to that record.

Quality metrics are optional data. A valid image does not become invalid merely because quality analysis was not requested.

### CLI Behavior

Quality analysis is opt-in.

Normal scanning:

```text
keptit scan <folder>
```

does not calculate or display quality metrics.

Quality analysis:

```text
keptit scan <folder> --quality
```

calculates and displays the measurements.

Quality analysis can also be combined with existing grouping functionality:

```text
keptit scan <folder> --quality --group
```

The CLI remains a presentation layer. Metric calculations belong in `keptit/quality.py`.

### Dependency Decision

v0.0.5 does not introduce a new runtime dependency for quality analysis.

Pillow is sufficient for the implemented image loading, grayscale conversion, resizing, and pixel-processing requirements.

No OpenCV, NumPy, SciPy, scikit-image, machine-learning library, external API, or cloud service is required.

### Performance

Quality analysis was initially evaluated at full source-image resolution.

Large images caused unnecessarily high processing time, so quality calculations were bounded to a maximum working dimension of 1024 pixels.

Local validation demonstrated a substantial reduction in processing time while preserving deterministic metric behavior.

The 1024-pixel limit is therefore part of the implemented quality-analysis behavior rather than an undocumented optimization.

---

## 7. Dependencies

Keep dependencies minimal.

The current runtime dependency is:

```text
Pillow
```

The project uses Python's standard library wherever practical.

`pytest` is used for testing.

Do not introduce a new dependency merely because it makes a small task more convenient.

Before adding a dependency, determine whether the standard library or an existing dependency is sufficient.

Libraries such as OpenCV, imagehash, NumPy, SQLite, PySide6, or other large dependencies should not be introduced without a concrete requirement and explicit approval when the addition changes the project's intended architecture or scope.

Perceptual hashing is implemented using Pillow. No additional hashing library is required.

---

## 8. Error Handling

Keptit should fail gracefully at the image level.

A corrupted or unreadable supported image should not terminate the entire folder scan.

Instead:

1. Attempt to index the image.
2. If indexing succeeds, create a successful `ImageRecord`.
3. If indexing fails, create a failed `ImageRecord`.
4. Store the error information.
5. Continue processing the remaining files.
6. Include the failure in the final scan result and summary.

Do not use broad silent exception handling such as:

```python
except:
    pass
```

Errors should be explicit and useful for debugging.

Perceptual hashing is part of successful image indexing in v0.0.3. If perceptual hashing fails, the image is represented as a failed `ImageRecord` and the scanner continues processing remaining files.

Hashing failures use the explicit `HashingError` exception rather than broad silent exception handling.

---

## 9. Testing Rules

Every meaningful behavior should have a corresponding test.

Tests should preferably use:

* `pytest`
* temporary directories
* synthetic images
* small controlled test files

Do not require personal photos for automated tests.

Important scanner behaviors to test include:

* supported JPG
* supported JPEG
* supported PNG
* case-insensitive extensions
* unsupported files
* empty directories
* non-recursive scanning
* recursive scanning
* valid image indexing
* image dimensions
* image format
* corrupted images
* failed image records
* invalid folder paths
* supported/unsupported accounting
* scan summary formatting

For perceptual hashing, tests should cover:

* deterministic hashing
* 64-bit hexadecimal output
* structural image differences
* RGB image input
* known-input hash output
* scanner hash generation
* hashing failure handling
* scan-level failure accounting

For similarity grouping, tests should cover:

* Hamming-distance calculation
* identical hashes
* hashes with known bit differences
* basic similarity grouping
* multiple independent groups
* threshold behavior
* isolated images
* missing perceptual hashes
* failed image records
* deterministic group membership
* deterministic group ordering
* transitive grouping behavior where applicable
* scanner-to-grouping integration
* CLI grouping output

For quality analysis, tests should cover:

* black images
* white images
* middle-gray images
* mixed exposure images
* high-frequency images
* blurred images
* sharpness directional behavior
* luminance behavior
* dark-pixel ratios
* bright-pixel ratios
* bounded working resolution
* small-image behavior
* deterministic calculations
* `QualityMetrics` model behavior
* `ImageRecord` quality-metric integration
* quality-analysis behavior on failed records
* CLI quality-option parsing
* CLI quality output

Run:

```bash
pytest
```

before considering a change complete.

A passing test suite is necessary but does not by itself prove that the implementation is correct. Actual CLI behavior and output should also be checked when relevant.

---

## 10. CLI Rules

The CLI should remain a thin wrapper around the core scanner.

Current commands:

```bash
keptit scan <folder>
```

and:

```bash
keptit scan <folder> --recursive
```

Similarity grouping can be enabled with:

```bash
keptit scan <folder> --group
```

and

```bash
keptit scan <folder> --recursive --group
```

Quality analysis can be enabled with:

```bash
keptit scan <folder> --quality
```

and

```bash
keptit scan <folder> --recursive --quality
```

Quality analysis can also be combined with similarity grouping:

```bash
keptit scan <folder> --quality --group
```

The scanner should remain usable without invoking the CLI.

Do not move scanner logic into `cli.py`.

---

## 11. Debugging Workflow

When something fails:

1. Reproduce the failure.
2. Read the actual error message.
3. Identify the actual cause.
4. Explain the cause clearly.
5. Make the smallest reasonable fix.
6. Run the relevant test.
7. Run the complete test suite.
8. Re-run the command that originally failed.
9. Confirm the actual output.

Do not guess at the cause when an actual error message or reproducible behavior is available.

Do not perform large rewrites to fix a localized problem.

---

## 12. Code Style

Prefer:

* clear names
* small functions
* type hints
* useful docstrings
* straightforward control flow
* explicit error handling
* simple data structures

Avoid:

* unnecessary abstractions
* premature optimization
* clever code that reduces readability
* unnecessary frameworks
* unnecessary dependencies
* code that hides important behavior

The code should remain understandable to a beginner/intermediate Python developer.

---

## 13. Privacy and Product Rules

Keptit is local-first.

Images should not be uploaded to cloud services as part of the core application.

The core application should not depend on external AI APIs.

The scanner should not modify the user's original image files.

Keptit should be read-only by default.

Keptit should never silently delete or modify user photographs.

Do not describe a heuristic as objectively determining the "best" photograph.

When future image-analysis features are added, their limitations and reasoning should be explainable to the user.

---

## 14. Repository Rules

The GitHub repository is the source of truth for the current implementation.

Do not assume that a file exists because it was discussed previously.

Before modifying an existing component:

1. Check the current repository state.
2. Read the current file.
3. Understand its existing behavior.
4. Modify the smallest necessary section.
5. Test the change.

Do not recreate, rename, or move files without a concrete reason.

---

## 15. Documentation Rules

Documentation should describe the implementation that actually exists.

Do not document planned features as if they are already implemented.

When functionality is added:

* update `README.md` when user-facing behavior changes
* update `CHANGELOG.md` when a versioned change is completed
* update this file only when development rules, architecture, or workflow change

Do not create documentation solely to make the repository appear larger or more professional.

---

## 16. Version Completion

A version should be considered complete only when:

* its defined scope is implemented
* the implementation works
* relevant tests exist
* the complete test suite passes
* the actual CLI behavior has been checked where applicable
* documentation reflects the implemented behavior
* no unfinished feature is presented as complete

v0.0.5 — Quality Metrics is considered complete when its defined quality-measurement scope is implemented, tested, documented, and verified without introducing later-stage ranking, scoring, selection, or deletion functionality.

For v0.0.5, the completed test suite contains **91 passing tests**.

---

## 17. Working With Future Development Sessions

When continuing Keptit development in a new session:

1. Read this document.
2. Read `README.md`.
3. Read `CHANGELOG.md`.
4. Inspect the current repository tree.
5. Read the relevant source files before proposing changes.
6. Check the current tests.
7. Determine the current version and scope.
8. Continue from the actual repository state.

Do not rely solely on previous conversation context.

The repository is authoritative for what has actually been implemented.

---

## 18. Development Philosophy

Keptit should grow through small verified steps.

The goal is not to add as many features as possible as quickly as possible.

The goal is to build a reliable, understandable, privacy-preserving open-source tool whose behavior can be explained and tested.

When there is a choice between a simple solution and an unnecessarily complex one, prefer the simple solution unless there is a concrete technical reason not to.

When there is uncertainty, inspect the code and test the behavior rather than assuming.

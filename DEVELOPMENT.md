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

Current version: **v0.0.6**

v0.0.6 is the **Quality Scoring** release.

The v0.0.6 implementation is considered complete.

The Keptit development progression is:

* v0.0.1 — Folder Scanner + Basic Image Indexer
* v0.0.2 — Metadata Extraction
* v0.0.3 — Perceptual Hashing
* v0.0.4 — Similarity Grouping
* v0.0.5 — Quality Metrics
* v0.0.6 — Quality Scoring

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
│   ├── scanner.py
│   └── scoring.py
│
└── tests/
    ├── test_cli.py
    ├── test_grouping.py
    ├── test_hashing.py
    ├── test_metadata.py
    ├── test_models.py
    ├── test_quality.py
    ├── test_scanner.py
    └── test_scoring.py
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

For example, while working on v0.0.6, do not add:

* confidence scoring
* image ranking
* automatic selection
* automatic deletion
* face detection
* eye detection
* smile detection
* subject detection
* RAW support
* GUI
* XMP functionality
* AI/ML image analysis
* cloud processing
* external AI APIs
* database storage
* group-level winner selection
* quality-based deletion

A future feature may be discussed conceptually, but discussion is not permission to implement it.

### 3.3 Preserve working functionality

Changes should be as small as reasonably possible.

Avoid unnecessary rewrites, abstractions, frameworks, dependencies, or architectural changes.

Existing behavior should remain working unless the change intentionally modifies that behavior.

---

## 4. Architecture

Keptit should keep responsibilities separated.

The current architecture is:

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
ImageGroup[]           ▼
                  QualityMetrics
                       │
                       ▼
                    Scoring
                       │
                       ▼
                  QualityScore
```

### Quality Analysis

`keptit/quality.py`

The quality module contains local image-quality measurement logic.

It currently calculates:

* sharpness variance
* mean luminance
* dark pixel ratio
* bright pixel ratio

Quality analysis is independent of grouping.

Quality analysis does not determine whether a photograph should be kept.

Quality calculations use Pillow and operate on image pixel data.

Quality analysis is exposed through the CLI as an optional `--quality` capability.

### Scoring

`keptit/scoring.py`

The scoring module converts existing `QualityMetrics` into a deterministic `QualityScore`.

Scoring must consume existing measurements rather than reopening images or recalculating image-quality metrics.

The scoring module is responsible for:

* validating scoring inputs
* normalizing sharpness
* deriving the exposure/clipping component
* combining the components
* producing the final bounded score

Scoring does not:

* scan folders
* open image files
* calculate image-quality measurements
* perform grouping
* rank photographs
* select photographs
* delete photographs
* use AI/ML
* call external services

The scoring module should remain independently testable.

### CLI

`keptit/cli.py`

The CLI handles command-line arguments and presentation of results.

It should not contain scanner logic or scoring mathematics.

The CLI may display `QualityMetrics` and `QualityScore` returned by the underlying modules.

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

Models represent structured data produced by the scanner and later analysis stages.

The current primary models include:

* `ImageRecord`
* `ScanResult`
* `ImageMetadata`
* `QualityMetrics`
* `QualityScore`

`QualityMetrics` represents measurements.

`QualityScore` represents the deterministic heuristic derived from those measurements.

The distinction between the two should remain explicit.

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

Grouping should not perform image scanning, metadata extraction, perceptual-hash generation, quality measurement, or quality scoring.

The grouping module should be usable independently of the CLI.

### Tests

`tests/`

Tests verify the behavior of the models, scanner, metadata extraction, hashing, grouping, quality analysis, scoring, and CLI.

Tests should not depend on a user's personal photo collection.

---

## 5. Current v0.0.6 Scope

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
* calculates a deterministic quality score from existing quality measurements
* stores the score in `QualityScore`
* optionally attaches the score to `ImageRecord`
* exposes quality measurements and scores through the `--quality` CLI option

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
* metadata when metadata extraction has been performed
* perceptual hash when hashing succeeds
* quality metrics when quality analysis has been performed
* quality score when scoring has been performed

---

## 6. v0.0.6 Quality Scoring

v0.0.6 establishes the first deterministic scoring layer on top of Keptit's existing quality measurements.

The central distinction is:

```text
v0.0.5

Image
 ↓
QualityMetrics
```

versus:

```text
v0.0.6

QualityMetrics
 ↓
Normalization
 ↓
Weighted combination
 ↓
QualityScore
```

A score is not a new image measurement.

It is a mathematical transformation of existing measurements.

### QualityScore Model

The scoring result is represented by:

```python
@dataclass
class QualityScore:
    sharpness_component: float
    exposure_component: float
    overall_score: int
```

The components are retained because they make the resulting score inspectable and explainable.

### Score Definition

The v0.0.6 score represents:

> A deterministic heuristic indicating how favorable the currently implemented image-quality measurements are under Keptit's scoring configuration.

It does not represent:

* percentage photographic quality
* probability that an image is the best photograph
* probability that a user should keep the image
* artistic quality
* composition quality
* emotional value
* subject importance
* photographic intent

### Sharpness Component

The existing v0.0.5 `sharpness_variance` measurement is used as the sharpness input.

Because Laplacian variance is unbounded and can have a heavy-tailed distribution, it is transformed logarithmically.

The fixed calibration reference is:

```text
SHARPNESS_REFERENCE = 10,000.0
```

The normalized sharpness component is:

```text
sharpness_component =
    min(
        log1p(sharpness_variance)
        /
        log1p(10,000.0),
        1.0
    )
```

The `log1p` transformation compresses very large values while preserving ordering for non-negative sharpness measurements.

The result is bounded to:

```text
0.0 ≤ sharpness_component ≤ 1.0
```

Values at or above the calibration reference saturate at `1.0`.

The reference value is an engineering calibration point for normalization. It is not a claim that a photograph with a sharpness variance of 10,000 represents perfect photographic sharpness.

### Exposure Component

The current exposure-related component is based on clipping ratios rather than mean luminance.

The clipping ratio is:

```text
clipping_ratio =
    dark_pixel_ratio
    +
    bright_pixel_ratio
```

The exposure component is:

```text
exposure_component =
    1.0 - clipping_ratio
```

The result is bounded to:

```text
0.0 ≤ exposure_component ≤ 1.0
```

This means that a greater proportion of pixels below the dark threshold or above the bright threshold reduces the component.

Mean luminance is intentionally not included directly in the score.

The reason is that mean luminance alone does not establish correct exposure. A deliberately dark night photograph or a bright snow scene may have an appropriate mean luminance even though it is far from the middle of the numerical range.

Therefore the current score treats clipping as a measurable signal rather than claiming to determine the correct exposure of an arbitrary scene.

### Weighting

The v0.0.6 score gives equal weight to the two normalized components:

```text
overall =
    0.5 × sharpness_component
    +
    0.5 × exposure_component
```

The final displayed score is:

```text
overall_score =
    round(overall × 100)
```

Therefore:

```text
0 ≤ overall_score ≤ 100
```

The equal weighting is an explicit baseline heuristic.

It is not presented as scientifically optimal or as universal photographic truth.

The weighting remains hard-coded in v0.0.6 because introducing user-configurable scoring parameters would add configuration complexity without sufficient evidence that it is necessary at this stage.

### Absolute vs Dataset-Relative Behavior

v0.0.6 uses absolute scoring.

The score for an image depends only on:

* its `QualityMetrics`
* the fixed scoring configuration

It does not depend on the other images currently being scanned.

Therefore adding or removing another photograph from a scan does not change an existing image's score.

This preserves:

* determinism
* reproducibility
* cross-scan comparability
* simple testing
* predictable behavior

Dataset-relative normalization is not part of v0.0.6.

### Missing Metrics

Scoring requires a complete `QualityMetrics` object.

`quality_metrics = None` means that quality measurements have not been calculated and therefore no score should be produced.

The scoring function does not silently substitute arbitrary values for missing measurements.

The current `calculate_quality_score()` function accepts a `QualityMetrics` instance and validates its numerical fields.

### Invalid Inputs

The scoring layer rejects invalid measurements.

It rejects:

* negative sharpness variance
* dark-pixel ratios outside `[0.0, 1.0]`
* bright-pixel ratios outside `[0.0, 1.0]`
* dark and bright ratios whose sum exceeds `1.0`

Invalid data should not be silently converted into a valid-looking score.

### Determinism

For the same `QualityMetrics` values and scoring configuration, the result must be identical.

The scoring system uses:

* no randomness
* no machine-learning inference
* no external service
* no time-dependent behavior
* no hidden state
* no dataset-relative normalization

### Performance

Scoring operates on already-calculated `QualityMetrics`.

It does not reopen image files.

It does not recalculate the Laplacian or exposure measurements.

The intended flow is:

```text
Image
 ↓
Quality Analysis
 ↓
QualityMetrics
 ↓
Scoring
 ↓
QualityScore
```

rather than:

```text
QualityScore request
 ↓
reopen image
 ↓
recalculate metrics
 ↓
score
```

This avoids unnecessary duplicate image processing.

### Known Limitations

The v0.0.6 score is a heuristic and has known limitations.

The underlying sharpness measurement is based on Laplacian variance. Laplacian variance measures local high-frequency intensity variation; it does not understand photographic intent or semantic image quality.

Consequently, high-frequency content such as:

* texture
* noise
* compression artifacts
* strong patterns
* artificial sharpening

can increase the sharpness measurement without necessarily indicating a better photograph.

Real-image testing demonstrated this limitation. A visually blurred image can receive a higher score than another visually preferable image when its measured clipping behavior and high-frequency content produce more favorable numerical inputs.

This is not treated as a scoring implementation failure. It is a limitation of the underlying measurement model.

The current v0.0.6 implementation therefore must not claim to identify the objectively best photograph.

Future versions may investigate improved quality measurements, but such work is outside the completed v0.0.6 scoring scope.

---

## 7. Dependencies

Keep dependencies minimal.

The current runtime dependency remains:

```text
Pillow
```

The project uses Python's standard library wherever practical.

`pytest` is used for testing.

The v0.0.6 scoring layer does not introduce a new runtime dependency.

Do not introduce a new dependency merely because it makes a small task more convenient.

Before adding a dependency, determine whether the standard library or an existing dependency is sufficient.

Libraries such as OpenCV, NumPy, SciPy, scikit-image, machine-learning libraries, or other large dependencies should not be introduced without a concrete requirement and explicit approval when the addition changes the project's intended architecture or scope.

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

Perceptual hashing is part of successful image indexing. If perceptual hashing fails, the image is represented as a failed `ImageRecord` and the scanner continues processing remaining files.

Hashing failures use the explicit `HashingError` exception rather than broad silent exception handling.

Quality scoring does not silently replace invalid numerical measurements.

---

## 9. Testing Rules

Every meaningful behavior should have a corresponding test.

Tests should preferably use:

* `pytest`
* temporary directories
* synthetic images
* small controlled test files
* directly constructed numerical inputs where appropriate

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

For quality scoring, tests should cover:

* zero sharpness
* reference sharpness
* sharpness above the reference
* monotonic sharpness behavior
* zero clipping
* complete dark clipping
* complete bright clipping
* monotonic clipping behavior
* score bounds
* perfect component combination
* minimum component combination
* deterministic scoring
* mathematical consistency between `QualityMetrics` and `QualityScore`
* invalid sharpness values
* invalid dark-pixel ratios
* invalid bright-pixel ratios
* invalid combined clipping ratios
* `QualityScore` model behavior
* integration with `ImageRecord`
* integration with quality analysis
* CLI quality-score output

Run:

```bash
pytest
```

before considering a change complete.

A passing test suite is necessary but does not by itself prove that the implementation is correct. Actual CLI behavior and output should also be checked when relevant.

Real-world images may be used for manual validation, but they should not replace deterministic automated tests.

---

## 10. CLI Rules

The CLI should remain a thin wrapper around the core scanner and analysis modules.

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

and:

```bash
keptit scan <folder> --recursive --group
```

Quality analysis and scoring can be enabled with:

```bash
keptit scan <folder> --quality
```

and:

```bash
keptit scan <folder> --recursive --quality
```

Quality analysis can also be combined with similarity grouping:

```bash
keptit scan <folder> --quality --group
```

When `--quality` is used, the CLI displays:

* raw quality measurements
* normalized sharpness component
* exposure component
* overall heuristic score

The CLI should label the result clearly as a quality score or heuristic score.

The CLI should not contain scoring mathematics.

The CLI should consume the `QualityScore` already produced by the scoring layer.

Do not move scanner, quality-analysis, or scoring logic into `cli.py`.

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

The v0.0.6 score is not a keeper recommendation.

It is not a probability that the user should retain the image.

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

All code changes and Git operations are performed locally by the project developer.

The normal Git workflow is:

```text
Local VS Code changes
        ↓
Local tests
        ↓
Diff review
        ↓
Commit
        ↓
Tag
        ↓
Push to GitHub
```

The GitHub repository should only receive a version after the local implementation and documentation have been verified.

---

## 15. Documentation Rules

Documentation should describe the implementation that actually exists.

Do not document planned features as if they are already implemented.

When functionality is added:

* update `README.md` when user-facing behavior changes
* update `CHANGELOG.md` when a versioned change is completed
* update this file only when development rules, architecture, or workflow genuinely change

Do not create documentation solely to make the repository appear larger or more professional.

The v0.0.6 scoring formula, normalization, weighting, score range, deterministic behavior, and limitations should be documented accurately.

Do not describe the score as objective photographic quality.

Do not document future ranking, selection, confidence, or deletion functionality as implemented.

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
* known limitations are documented when they materially affect interpretation

v0.0.6 — Quality Scoring is considered complete when its defined scoring scope is implemented, tested, documented, and verified without introducing later-stage ranking, selection, confidence, deletion, or image-analysis functionality.

The completed v0.0.6 test suite contains **113 passing tests**.

The real-world CLI validation also confirmed that the scoring pipeline operates on actual JPEG and PNG images and produces deterministic measurements and scores.

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

When beginning a new version, first define its scope before modifying code.

Do not assume that a limitation discovered in one version automatically authorizes redesigning that version. Determine whether the issue belongs to the next version's scope.

---

## 18. Development Philosophy

Keptit should grow through small verified steps.

The goal is not to add as many features as possible as quickly as possible.

The goal is to build a reliable, understandable, privacy-preserving open-source tool whose behavior can be explained and tested.

When there is a choice between a simple solution and an unnecessarily complex one, prefer the simple solution unless there is a concrete technical reason not to.

When there is uncertainty, inspect the code and test the behavior rather than assuming.

For scoring specifically, do not mistake mathematical complexity for technical quality.

A simple heuristic with explicit assumptions is preferable to a sophisticated formula whose behavior cannot be defended.

The current v0.0.6 scoring layer establishes:

```text
QualityMetrics
      ↓
Normalization
      ↓
Deterministic weighting
      ↓
QualityScore
```

It deliberately does not establish:

```text
QualityScore
      ↓
Ranking
      ↓
Selection
      ↓
Deletion
```

Those are separate future capabilities and must remain separate unless explicitly introduced in a later version.

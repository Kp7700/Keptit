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

Current version: **v0.0.1**

v0.0.1 is the **Folder Scanner + Basic Image Indexer**.

The v0.0.1 implementation is considered complete.

The current repository contains:

```text
Keptit/
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml
│
├── keptit/
│   ├── cli.py
│   ├── models.py
│   └── scanner.py
│
└── tests/
    ├── test_models.py
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

For example, while working on v0.0.1, do not add:

* EXIF metadata extraction
* perceptual hashing
* duplicate detection
* similarity grouping
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
     Models
```

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

### Tests

`tests/`

Tests verify the behavior of the models, scanner, and related functionality.

Tests should not depend on a user's personal photo collection.

---

## 5. Current v0.0.1 Scope

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

---

## 6. Dependencies

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

---

## 7. Error Handling

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

---

## 8. Testing Rules

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

Run:

```bash
pytest
```

before considering a change complete.

A passing test suite is necessary but does not by itself prove that the implementation is correct. Actual CLI behavior and output should also be checked when relevant.

---

## 9. CLI Rules

The CLI should remain a thin wrapper around the core scanner.

Current commands:

```bash
keptit scan <folder>
```

and:

```bash
keptit scan <folder> --recursive
```

The scanner should remain usable without invoking the CLI.

Do not move scanner logic into `cli.py`.

---

## 10. Debugging Workflow

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

## 11. Code Style

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

## 12. Privacy and Product Rules

Keptit is local-first.

Images should not be uploaded to cloud services as part of the core application.

The core application should not depend on external AI APIs.

The scanner should not modify the user's original image files.

Keptit should be read-only by default.

Keptit should never silently delete or modify user photographs.

Do not describe a heuristic as objectively determining the "best" photograph.

When future image-analysis features are added, their limitations and reasoning should be explainable to the user.

---

## 13. Repository Rules

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

## 14. Documentation Rules

Documentation should describe the implementation that actually exists.

Do not document planned features as if they are already implemented.

When functionality is added:

* update `README.md` when user-facing behavior changes
* update `CHANGELOG.md` when a versioned change is completed
* update this file only when development rules, architecture, or workflow change

Do not create documentation solely to make the repository appear larger or more professional.

---

## 15. Version Completion

A version should be considered complete only when:

* its defined scope is implemented
* the implementation works
* relevant tests exist
* the complete test suite passes
* the actual CLI behavior has been checked where applicable
* documentation reflects the implemented behavior
* no unfinished feature is presented as complete

For v0.0.1, the completed test suite contains **22 passing tests**.

---

## 16. Working With Future Development Sessions

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

## 17. Development Philosophy

Keptit should grow through small verified steps.

The goal is not to add as many features as possible as quickly as possible.

The goal is to build a reliable, understandable, privacy-preserving open-source tool whose behavior can be explained and tested.

When there is a choice between a simple solution and an unnecessarily complex one, prefer the simple solution unless there is a concrete technical reason not to.

When there is uncertainty, inspect the code and test the behavior rather than assuming.

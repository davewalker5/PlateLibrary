[![GitHub issues](https://img.shields.io/github/issues/davewalker5/PlateLibrary)](https://github.com/davewalker5/PlateLibrary/issues)
[![Releases](https://img.shields.io/github/v/release/davewalker5/PlateLibrary.svg?include_prereleases)](https://github.com/davewalker5/PlateLibrary/releases)
[![License: MIT](https://img.shields.io/badge/License-mit-blue.svg)](https://github.com/davewalker5/PlateLibrary/blob/main/LICENSE)
[![Language](https://img.shields.io/badge/language-python-blue.svg)](https://www.python.org)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/davewalker5/PlateLibrary)](https://github.com/davewalker5/PlateLibrary/)

# Plate Library

A simple, SQLite-backed plate library for microscopy work.

This project is deliberately minimal, local-first, and practical. It is not a polished application or a framework — it is a small set of tools that together provide a clean way to:

- Record plates and investigations
- Maintain structured data without spreadsheets
- Explore and query your work
- Export data into a publishing pipeline

It just works.

⸻

## Origin and Use

This project was developed to support a set of ongoing personal microscopy investigations and the associated [Field Notes](https://davidwalker.uk) website.

It provides a structured way to record plates, link them to investigations, and generate consistent outputs for publication. The design reflects that use case: local, iterative, and focused on long-term personal data rather than general-purpose deployment.

⸻

## Philosophy

This project is guided by a few principles:

- SQLite as the source of truth
  No ORM, no abstraction layer — just a well-designed relational schema.
- Small tools, loosely coupled
  Streamlit → data entry
  Datasette → exploration
  Python scripts → import/export
- Readable over clever
  The code is intentionally straightforward and hackable.
- Local-first
  Everything runs locally. No services, no accounts, no cloud dependencies.
- Structured but flexible
  The schema enforces relationships, but the workflow stays lightweight.

⸻

## What this is (and isn’t)

This is:

- A personal data system for microscopy plates
- A replacement for spreadsheet-based tracking
- A foundation for analysis and publishing

This is not:

- A full LIMS
- A multi-user system
- A production-grade web application

⸻

## Architecture

```
SQLite database (source of truth)
↓
Streamlit (data entry / maintenance)
↓
Datasette (exploration / querying)
↓
Export script (CSV)
↓
Field Notes / reports
```

Each layer has a single responsibility.

⸻

## Schema Overview

![Plate Library Database Diagram](https://github.com/davewalker5/PlateLibrary/blob/main/diagrams/database-schema.png)

#### PLATE
A **plate** is the fundamental unit of record. It represents a single observation or preparation (e.g. a slide, section, or specimen view), along with its associated metadata (date, specimen, equipment, notes, etc.).

#### INVESTIGATION
An **investigation** represents a defined piece of work — typically a session or short sequence of related observations. Plates are grouped under investigations to provide context and narrative.

#### SERIES
A **series** is a thematic grouping of investigations. For example, a series might cover a particular type of structure (e.g. leaf epidermis, pollen, stem anatomy) or a class of specimens.

#### SCHEME
A **scheme** is the highest-level organisational structure. It represents an overall programme of work (for example, an annual or seasonal plan), within which multiple series are defined.

#### SPECIES
Represents the biological classification of the specimen being observed. This may be populated to varying levels of precision depending on identification confidence.

#### OBJECTIVE
Represents the microscope objective used for the observation, including magnification and the associated instrument.

#### CAMERA
Represents the imaging setup used (if any), including effective magnification ranges where applicable.

#### STAIN
Represents any staining technique applied to the specimen. This is optional and reflects preparation method.

#### LOCATION
Represents where the specimen was collected or observed. This can include descriptive names and optional grid references.

⸻

## Seed Data

The repository includes initial (“seed”) migrations which populate reference tables such as species, objectives, stains, and programme structure.

These are provided as working examples only.

They reflect a specific set of instruments, locations, and investigative schemes, and are not intended to be universally applicable. If you wish to use this project for your own work, you should review and modify these seed migrations to suit your own:

- Equipment
- Taxonomy
- Locations
- Investigative structure

The schema itself is stable; the seed data is expected to be customised.

⸻

### Setup

1. Create virtual environment, from the project root, and activate it:

```bash
./scripts/make_venv.sh
source ./venv/bin/activate
```

⸻

2. Install dependencies

```bash
pip install -r requirements.txt
```

⸻

3. Create the database by running migrations using yoyo, running the following command from the root of the working copy of the repo:

```bash
yoyo apply -b
```

⸻

## Running the Tools

### Streamlit (data entry / maintenance)

```bash
streamlit run src/maintain_plates.py
```

Provides:

- Add/edit plates
- Add/edit investigations
- Search and browse
- Delete plates (with confirmation)
- Quick links to Datasette

⸻

### Datasette (exploration)

```bash
datasette data/plate_library.db
```

Then open:

```
http://127.0.0.1:8001
```

Use this to:

- Browse tables
- Filter and query
- Inspect relationships
- Validate data

⸻

### Export data

```bash
python src/export_plate_library.py data/plate_library.db output/plates.csv
```

Runs the export query and produces CSV output.

⸻

### Import data

```bash
python src/import_plate_library.py input.xlsx data/plate_library.db
```

Used for initial seeding or bulk updates.

⸻

### Import Script

The import script is intended as a one-off utility to bootstrap the database from an existing spreadsheet.

It is designed specifically around a spreadsheet structure matching the provided index (see Index.xlsx), including column naming and data conventions.

It is not a general-purpose importer and makes a number of assumptions about:

- Date formats
- Species naming
- Reference structure

If you wish to use it with your own data, you will likely need to adapt it to match your spreadsheet format.

⸻

### Typical Workflow

	1.	Enter plates via Streamlit
	2.	Explore and validate in Datasette
	3.	Export to CSV
	4.	Use in analysis / reports

⸻

## Notes

- The UI is intentionally simple — it is a tool, not a product
- The schema is the important part
- Everything is designed to be easy to modify

⸻

# Authors

- **Dave Walker** - _Initial work_

⸻

# Feedback

To file issues or suggestions, please use the [Issues](https://github.com/davewalker5/PlateLibrary/issues) page for this project on GitHub.

⸻

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

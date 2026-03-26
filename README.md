[![GitHub issues](https://img.shields.io/github/issues/davewalker5/PlateLibrary)](https://github.com/davewalker5/PlateLibrary/issues)
[![Releases](https://img.shields.io/github/v/release/davewalker5/PlateLibrary.svg?include_prereleases)](https://github.com/davewalker5/PlateLibrary/releases)
[![License: MIT](https://img.shields.io/badge/License-mit-blue.svg)](https://github.com/davewalker5/PlateLibrary/blob/main/LICENSE)
[![Language](https://img.shields.io/badge/language-python-blue.svg)](https://www.python.org)
[![Language](https://img.shields.io/badge/database-SQLite-blue.svg)](https://github.com/davewalker5/ADS-B-BaseStationReader/)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/davewalker5/PlateLibrary)](https://github.com/davewalker5/PlateLibrary/)

# Plate Library

This project is a simple, SQLite-backed plate library for microscopy work, developed to support a set of ongoing personal microscopy investigations and the associated [Field Notes](https://davidwalker.uk) website.

It is is deliberately minimal, local-first, and practical and consists of a small set of tools that together provide a simple personal data system for recording plates, linking them to investigations, and exporting the data:

A typical workflow with the tool looks like this:

1.	Enter and edit plates via Streamlit
2.	Explore and validate the data in Datasette
3.	Export the data to CSV
4.	Use the exported data in analysis / reports

An import script is also provided to import data from a spreadsheet.

## Database Schema

![Plate Library Database Diagram](https://github.com/davewalker5/PlateLibrary/blob/main/diagrams/database-schema.png)

| Table         | Description                                                                                                                                                                                                             |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PLATE         | A **plate** is the fundamental unit of record. It represents a single observation or preparation (e.g. a slide, section, or specimen view), along with its associated metadata (date, specimen, equipment, notes, etc.) |
| INVESTIGATION | An **investigation** represents a defined piece of work — typically a session or short sequence of related observations. Plates are grouped under investigations to provide context and narrative                       |
| SERIES        | A **series** is a thematic grouping of investigations. For example, a series might cover a particular type of structure (e.g. leaf epidermis, pollen, stem anatomy) or a class of specimens                             |
| SCHEME        | A **scheme** is the highest-level organisational structure. It represents an overall programme of work (for example, an annual or seasonal plan), within which multiple series are defined                              |
| SPECIES       | Represents the biological classification of the specimen being observed. This may be populated to varying levels of precision depending on identification confidence                                                    |
| MICROSCOPE    | Represents the instrument used to examine the speciment and record the plate                                                                                                                                            |
| OBJECTIVE     | Represents the microscope objective used for the observation, including magnification and an association with the instrument                                                                                            |
| CAMERA        | Represents the imaging setup used, including effective magnification ranges where applicable                                                                                                                            |
| STAIN         | Represents any staining technique applied to the specimen. This is optional and reflects preparation method                                                                                                             |
| LOCATION      | Represents where the specimen was collected or observed. This can include descriptive names and optional grid references                                                                                                |

### Seed Data

The repository includes initial (“seed”) migrations which populate reference tables such as species, objectives, stains, and programme structure.

These are provided as working examples only.

They reflect a specific set of instruments, locations, and investigative schemes, and are not intended to be universally applicable. If you wish to use this project for your own work, you should review and modify these seed migrations to suit your own:

- Equipment
- Taxonomy
- Locations
- Investigative structure

### Database Creation

To create the database, run the following script at the root of the project folder:

```bash
yoyo apply -b
```

This will create a SQLite database called *plate_library.db* in the data folder.

## Running the Tools

### Virtual Environment

To run the tools, first create and activate a virtual environment by running the following at the root of the project:

```bash
python -m venv venv
source ./venv/bin/activate
```

This assumes a Mac or Linux-based setup and should be modified if running on Windows.

### Streamlit (Data Entry and Maintenance)

Open a terminal window and run the following script to start streamlit:

```bash
streamlit run src/maintain_plates.py
```

Use this to:

- Add/edit plates
- Add/edit investigations
- Search and browse the data
- Delete plates
- Quick links to Datasette

Plates and investigations are considered the fastest-moving data in need of a maintenance UI. The remaining data is likely to be relatively static and the expectation is this will be maintained in SQLite itself.

The Streamlit UI includes a link to Datasette and if you want to use this then Datasette should also be started (see below)

### Datasette (Data Exploration)

Open a terminal window and run the following script to start Datasette:

```bash
datasette data/plate_library.db
```

Then open:

```
http://127.0.0.1:8001
```

Use this to browse, filter and query the data.

## Data Import and Export

### Export

The data can be exported in CSV format by running the following at the root of the poject:

```bash
python src/export_plate_library.py --db data/plate_library.db --csv output/plates.csv
```

This form of the export command reads the export query from the *sql/export.sql* file. If required, an alternative can be specified using the *--sql* argument.

### Import

The import script is intended as a one-off utility to bootstrap the database from an existing spreadsheet (XLSX). It is not a general-purpose importer and makes a number of assumptions about:

- Date formats
- Species naming
- Reference structure

Use the following syntax to run the import:

```bash
python src/import_plate_library.py --db data/plate_library.db --xlsx input.xlsx --truncate-plate
```

The *--truncate-plate* argument is optional and should be used with care as it truncates the PLATE table before importing.

#### File Format

It is designed around an input spreadsheet (XLSX) with the following columns:

| Column Name                   | Required | Type      | Description                                                                                                  |
| ----------------------------- | -------- | --------- | ------------------------------------------------------------------------------------------------------------ |
| Date                          | Yes      | Input     | The date the observation or plate was recorded, typically in DD/MM/YY format.                                |
| Series                        | Yes      | Lookup    | The series identifier used to resolve the associated scheme and series structure.                            |
| Scientific Name               | No       | Reference | The scientific (Latin) name of the specimen (not used directly in import logic but retained for reference).  |
| Common Name                   | Yes*     | Lookup    | The common name used to look up the corresponding species record. Required if Species_Id is to be populated. |
| Specimen                      | Yes      | Input     | A short description of the specimen or material observed.                                                    |
| Plate                         | Yes      | Input     | The plate identifier, corresponding to a physical slide or preparation.                                      |
| Reference                     | Yes      | Input     | A unique or semi-structured reference for the plate.                                                         |
| Location                      | No       | Lookup    | The location where the specimen was collected or observed.                                                   |
| Investigation                 | Yes      | Lookup    | The investigation reference used to link the plate to a specific investigation record.                       |
| Preparation                   | No       | Input     | Details of specimen preparation (e.g. sectioning, mounting).                                                 |
| Microscope                    | No       | Lookup    | The microscope used for the observation.                                                                     |
| Objective                     | No       | Lookup    | The specific objective lens used.                                                                            |
| Objective Magnification       | No       | Derived   | Nominal magnification of the objective; typically implied by the objective lookup.                           |
| Camera                        | No       | Lookup    | The camera or imaging device used, if applicable.                                                            |
| Lower Effective Magnification | No       | Input     | Lower bound of effective magnification when imaging.                                                         |
| Upper Effective Magnification | No       | Input     | Upper bound of effective magnification when imaging.                                                         |
| Software                      | No       | Input     | Software used for image capture or processing.                                                               |
| Notebook Reference            | No       | Input     | Reference to the corresponding notebook entry.                                                               |
| Notes                         | No       | Input     | Free-text notes describing the observation.                                                                  |
| Verified                      | No       | Input     | Indicates whether the record has been reviewed or confirmed (e.g. TRUE/FALSE).                               |

#### Column Types

| Type      | Meaning                                                                                                    |
| --------- | ---------------------------------------------------------------------------------------------------------- |
| Input     | Stored directly in the PLATE table                                                                         |
| Lookup    | Used to resolve a foreign key (e.g. Species, Investigation, Objective). Values must match existing records |
| Reference | Informational only — not used directly in import logic but retained for context                            |
| Derived   | Implied by another field or lookup and not strictly required                                               |

#### Notes

- Fields marked Yes* are conditionally required depending on whether you want that relationship populated.
- Lookup fields must match existing seed data (or your customised equivalents).
- The import script is intentionally strict in places to avoid introducing inconsistent data.

#### Example Row

| Date     | Series                         | Scientific Name | Common Name     | Specimen                               | Plate         | Reference | Location | Investigation | Preparation | Microscope        | Objective | Objective Magnification | Camera     | Lower Effective Magnification | Upper Effective Magnification | Software             | Notebook Reference | Notes | Verified |
| -------- | ------------------------------ | --------------- | --------------- | -------------------------------------- | ------------- | --------- | -------- | ------------- | ----------- | ----------------- | --------- | ----------------------- | ---------- | ----------------------------- | ----------------------------- | -------------------- | ------------------ | ----- | -------- |
| 23/03/26 | SI II – Support and Conduction | Galium aparine  | Common cleavers | Galium aparine stem, T.S., focus merge | SI-II-018.png | SI-II-018 |          | IN-2026-001   | Unstained   | Ernst Leitz, 1912 | No. 3     | 10                      | Swift EC5R | 26                            | 39                            | Swift Imaging 3, OBS | Vol. IV, p. 10     |       | Yes      |

# Authors

- **Dave Walker** - _Initial work_

# Feedback

To file issues or suggestions, please use the [Issues](https://github.com/davewalker5/PlateLibrary/issues) page for this project on GitHub.

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

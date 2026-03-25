# Plate Library

A simple, SQLite-backed plate library for microscopy work.

This project is deliberately **minimal, local-first, and practical**. It is not a polished application or a framework — it is a small set of tools that together provide a clean way to:

- record plates and investigations
- maintain structured data without spreadsheets
- explore and query your work
- export data into a publishing pipeline

It *just works*.

---

## Philosophy

This project is guided by a few principles:

- **SQLite as the source of truth**  
  No ORM, no abstraction layer — just a well-designed relational schema.

- **Small tools, loosely coupled**
  - Streamlit → data entry
  - Datasette → exploration
  - Python scripts → import/export

- **Readable over clever**  
  The code is intentionally straightforward and hackable.

- **Local-first**
  Everything runs locally. No services, no accounts, no cloud dependencies.

- **Structured but flexible**
  The schema enforces relationships, but the workflow stays lightweight.

---

## What this is (and isn’t)

This is:

- a personal data system for microscopy plates  
- a replacement for spreadsheet-based tracking  
- a foundation for analysis and publishing  

This is not:

- a full LIMS  
- a multi-user system  
- a production-grade web application  

---

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

---

## Schema Overview

The schema is defined in the initial migration:

```
migrations/0001_initial_schema.py
```

At its core is the **PLATE** table, supported by a small number of relational tables.

---

### Core Tables

#### `PLATE`

The central record.

Fields include:

- Date  
- Specimen  
- Plate  
- Reference  
- Notebook_Reference  
- Notes  

Foreign keys:

- `Species_Id` → `SPECIES`  
- `Objective_Id` → `OBJECTIVE`  
- `Camera_Id` → `CAMERA`  
- `Stain_Id` → `STAIN`  
- `Location_Id` → `LOCATION`  
- `Investigation_Id` → `INVESTIGATION`  

---

#### `INVESTIGATION`

Represents a structured piece of work.

- Reference  
- Title  
- Series_Id  

---

#### `SERIES` and `SCHEME`

Define the programme of work:

- `SCHEME` → top-level structure (e.g. annual plan)  
- `SERIES` → thematic grouping  

---

### Lookup Tables

These change infrequently:

- `SPECIES`  
- `OBJECTIVE` (linked to `MICROSCOPE`)  
- `CAMERA`  
- `STAIN`  
- `LOCATION`  

---

### Relationships

The schema forms a natural hierarchy:

```
Scheme → Series → Investigation → Plate
```

---

## Setup

### 1. Create virtual environment

From the project root:

```
./scripts/make_venv.sh
```

Activate it:

```
source .venv/bin/activate
```

---

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Create the database

Run migrations using yoyo:

```
yoyo apply --database sqlite:///data/plate_library.db migrations
```

---

## Running the Tools

### Streamlit (data entry / maintenance)

```
streamlit run scripts/maintain_plates.py
```

Provides:

- add/edit plates  
- add/edit investigations  
- search and browse  
- delete plates (with confirmation)  
- quick links to Datasette  

---

### Datasette (exploration)

```
datasette data/plate_library.db
```

Open:

http://127.0.0.1:8001

Use this to:

- browse tables  
- filter and query  
- inspect relationships  
- validate data  

---

### Export data

```
python scripts/export_plate_library.py data/plate_library.db output/plates.csv
```

Runs the export query and produces CSV output.

---

### Import data

```
python scripts/import_plate_library.py input.xlsx data/plate_library.db
```

Used for initial seeding or bulk updates.

---

## Typical Workflow

1. Enter plates via Streamlit  
2. Explore and validate in Datasette  
3. Export to CSV  
4. Use in analysis / reports  

---

## Notes

- The UI is intentionally simple — it is a tool, not a product  
- The schema is the important part  
- Everything is designed to be easy to modify  

---

## Future Ideas

- image support for plates  
- richer Datasette views  
- tighter publishing integration  
- maintenance screens for lookup tables  

---

## Final Word

This project exists because spreadsheets eventually stop scaling for structured work.

SQLite doesn’t.

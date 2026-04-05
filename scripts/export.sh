#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

python "$PROJECT_ROOT/src/export_plate_library.py" \
  --db "$PROJECT_ROOT/data/plate_library.db" \
  --csv "$PROJECT_ROOT/data/export.csv" \
  --plate-sql "$PROJECT_ROOT/src/plate_library/queries/export-plates.sql" \
  --investigation-sql "$PROJECT_ROOT/src/plate_library/queries/export-investigations.sql"
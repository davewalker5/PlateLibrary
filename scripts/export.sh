#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

python "$PROJECT_ROOT/src/export_plate_library.py" \
  --db "$PROJECT_ROOT/data/plate_library.db" \
  --csv "$PROJECT_ROOT/data/leitz_plates.csv" \
  --sql "$PROJECT_ROOT/sql/export.sql"
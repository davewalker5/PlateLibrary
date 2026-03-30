#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

python "$PROJECT_ROOT/src/import_plate_library.py" \
  --db "$PROJECT_ROOT/data/plate_library.db" \
  --xlsx "$MICROSCOPY_PLATE_LIBRARY/Index.xlsx" \
  --truncate-plate

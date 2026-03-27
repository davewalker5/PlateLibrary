#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

# If the MICROSCOPY_PLATE_LIBRARY environment variable is set, the database is in the
# folder specified in that variable. Otherwise, the database in the data folder of the
# repository is used
DB_PATH="$PROJECT_ROOT/data/plate_library.db"

# The metadata is visible in the Datasette UI, so this has the effect of showing the
# path to the current database (useful if switching between development and live databases)
datasette "$DB_PATH" \
  --metadata <(cat <<EOF
{
  "databases": {
    "plate_library": {
      "description": "Database Path: $DB_PATH"
    }
  }
}
EOF
) \
  --open

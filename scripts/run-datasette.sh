#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

DB_PATH="${MICROSCOPY_PLATE_LIBRARY:-$PROJECT_ROOT/data}/plate_library.db"
datasette "$DB_PATH" --open

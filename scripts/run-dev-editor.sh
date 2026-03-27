#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

streamlit run "$PROJECT_ROOT/src/main.py" -- --db "$PROJECT_ROOT/data/plate_library.db"
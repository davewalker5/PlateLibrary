#!/usr/bin/env bash

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

export PYTHONPATH="$PROJECT_ROOT/src"

streamlit run "$PROJECT_ROOT/src/streamlit_app.py" -- "$@"
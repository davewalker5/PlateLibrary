#!/usr/bin/env bash

# For older versions of MacOS, pip may not find the proj wheel and will build it from source. The
# environment then won't be set correctly to run proj, resulting in errors in the application. Set
# the PROJ_DATA manually if it's present on the machine. The following assumes a MacPorts install
# of proj9
if [ -d "/opt/local/lib/proj9/share/proj" ]; then
    export PROJ_DATA=/opt/local/lib/proj9/share/proj
fi

export PROJECT_ROOT=$( cd "$( dirname "$0" )/.." && pwd )
. $PROJECT_ROOT/venv/bin/activate

export PYTHONPATH="$PROJECT_ROOT/src"

streamlit run "$PROJECT_ROOT/src/streamlit_app.py" -- "$@"
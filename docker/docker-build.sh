#!/bin/sh -f

if [[ $# -ne 3 ]]; then
    echo Usage: docker-build.sh major minor patch
    exit 1
fi

# Setup
VERSION=$1.$2.$3
DEVELOPMENT_FOLDER=~/Dropbox/Development
PROJECT_FOLDER=$DEVELOPMENT_FOLDER/Projects/PlateLibrary
PUBLISH_FOLDER=$DEVELOPMENT_FOLDER/Docker/platelibrary/platelibrary-$VERSION.0

# Publish the application
cd $PROJECT_FOLDER
rm -fr dist
rm -fr src/plate_library.egg-info
source venv/bin/activate
pip install build
python -m build

# Docker build folder setup
mkdir -p $PUBLISH_FOLDER
cp $PROJECT_FOLDER/dist/plate_library-$VERSION-py3-none-any.whl $PUBLISH_FOLDER
cp $PROJECT_FOLDER/src/streamlit_app.py $PUBLISH_FOLDER
cp $PROJECT_FOLDER/docker/Dockerfile $DEVELOPMENT_FOLDER/Docker/platelibrary

# # Docker build
cd $DEVELOPMENT_FOLDER/Docker/platelibrary
docker buildx build --platform linux/amd64  -t "davewalker5/platelibrary:$VERSION.0" -t davewalker5/platelibrary:latest -f Dockerfile .

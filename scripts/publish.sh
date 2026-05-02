#!/bin/bash
# Build and upload furqan-lint to PyPI.
#
# This script is documented but NOT to be run by automation. PyPI
# credentials are held only by the project lead. Run from the repo
# root after a clean checkout of the tag you intend to publish.
#
# Prereqs:
#   pip install --upgrade build twine
#
# Usage:
#   1. git checkout v0.X.Y      (a tagged release commit)
#   2. ./scripts/publish.sh     (prompts for PyPI token via twine)
#
# Verify the upload at https://pypi.org/project/furqan-lint/ and
# install in a fresh virtualenv before announcing the release.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if ! python -c "import build" 2>/dev/null; then
    echo "Missing 'build'. Run: pip install --upgrade build twine"
    exit 1
fi
if ! python -c "import twine" 2>/dev/null; then
    echo "Missing 'twine'. Run: pip install --upgrade build twine"
    exit 1
fi

rm -rf dist/ build/ src/*.egg-info
python -m build
python -m twine check dist/*
python -m twine upload dist/*

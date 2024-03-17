#!/usr/bin/env bash

# Fail on error
set -e

# Create a virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Download requirements
pip3 install -r ./src/requirements.txt

#!/usr/bin/env bash

set -ex

VENV_DIR=".pyvenv"

mkdir -p ${VENV_DIR}
virtualenv ${VENV_DIR}
source "${VENV_DIR}/bin/activate"
pip install -U pip
pip install -r requirements.txt.lock

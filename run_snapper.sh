#!/bin/bash

CONFIG_FILE="autobloomer_snapper_cfg.json"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROG_DIR="${SCRIPT_DIR}/src"
PROTO_DIR="${SCRIPT_DIR}/AutoBloomer-Protobuf/python"
APP="autobloomer_snapper.py"


pushd ${SCRIPT_DIR}

export PYTHONPATH=${PROG_DIR}:${PROTO_DIR}
python3 "${PROG_DIR}/${APP}" -c "${SCRIPT_DIR}/${CONFIG_FILE}"

echo "${CWD}"

popd

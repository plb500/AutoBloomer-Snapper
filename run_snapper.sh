#!/bin/bash

CONFIG_FILE="autobloomer_snapper_cfg.json"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROG_DIR="${SCRIPT_DIR}/src"
PROTO_DIR="${SCRIPT_DIR}/AutoBloomer-Protobuf/python"
APP="autobloomer_snapper.py"
VENV="snapper-env"


# Virtual environment stuff
VENV_PATH=`realpath "${SCRIPT_DIR}/${VENV}"`
if [[ -z "${VIRTUAL_ENV}" ]]; then
	# We are not running in ANY virtual environment. Turn ours on
	if [[ -d ${VENV_PATH} ]]; then
		echo "Activating virtual environment"
		source "${VENV_PATH}/bin/activate"
	else
		echo "You have not configured the virtual environment requried for AutoBloomer-Snapper"
		exit
	fi
else
	# Detect if we are running in the CORRECT virtual environment
	DETECT_VENV=`realpath -q ${VIRTUAL_ENV}`
	if [ "${DETECT_VENV}" == "${VENV_PATH}" ]; then
		echo "Detected virtual environment"
	else
		echo "Running in the wrong virtual environment. This won't work"
		exit
	fi
fi

# We should be good at this point

pushd ${SCRIPT_DIR}

export PYTHONPATH=${PROG_DIR}:${PROTO_DIR}
python3 "${PROG_DIR}/${APP}" -c "${SCRIPT_DIR}/${CONFIG_FILE}"


popd

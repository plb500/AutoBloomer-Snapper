#!/bin/bash

# This should be the only thing you would ever change, if you are using a config file in a different location
CONFIG_FILE="autobloomer_snapper_cfg.json"

# Don't change these (usually)
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
		echo "You have not configured the virtual environment required for AutoBloomer-Snapper"
		echo "To do this please run the following commands:"
		echo "    python3 -m venv ${VENV}"
		echo "    source ${VENV_PATH}/bin/activate"
		echo "    pip3 install -r ${SCRIPT_DIR}/requirements.txt"
		exit
	fi
else
	# Detect if we are running in the CORRECT virtual environment
	DETECT_VENV=`realpath -q ${VIRTUAL_ENV}`
	if [ "${DETECT_VENV}" == "${VENV_PATH}" ]; then
		echo "Detected virtual environment"
	else
		echo "Running in the wrong virtual environment. This won't work"
		echo "Please exit the current virtual environment and run this script again"
		exit
	fi
fi

# We should be good at this point, run the actual script
pushd ${SCRIPT_DIR} "$@" > /dev/null

export PYTHONPATH=${PROG_DIR}:${PROTO_DIR}
python3 "${PROG_DIR}/${APP}" -c "${SCRIPT_DIR}/${CONFIG_FILE}"

popd "$@" > /dev/null

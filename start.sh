#!/bin/sh

VENV=".venv"
PID_FILE="pycmdb.pid"
LOG_FILE="log/uvicorn.log"
WORK_DIR=$(realpath $(dirname "${BASH_SOURCE[0]}"))

cd ${WORK_DIR}
if [ -d ${VENV} ];then
  source ${VENV}/bin/activate
else
  echo "Creating python virtual environment for first running..."
  python3 -m venv ${VENV}
  source ${VENV}/bin/activate
  python3 -m pip install -r requirements.txt
fi

echo "Starting/Restarting pycmdb..."
mkdir -p log
if [ -f ${PID_FILE} ];then
  kill -9 `cat ${PID_FILE}`
fi

python3 ${WORK_DIR}/main.py >> ${WORK_DIR}/${LOG_FILE} 2>&1 &

echo $! > ${PID_FILE}
PID=$(cat ${PID_FILE})

sleep 3
if [ -d /proc/${PID} ]; then
  echo "Process running on pid ${PID} !"
  echo "VENV: $(which python3)"
else
  echo "Process failed on pid ${PID} !"
fi

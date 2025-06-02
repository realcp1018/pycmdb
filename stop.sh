#!/bin/sh

PID_FILE="pycmdb.pid"
WORK_DIR=$(dirname "${BASH_SOURCE[0]}")

cd ${WORK_DIR}
echo "Stoping pycmdb..."
if [ -f ${PID_FILE} ];then
  kill -9 `cat ${PID_FILE}`
else
  echo "PID file ${PID_FILE} not exist, exit!"
  exit 1
fi

echo "Process pid $(cat ${PID_FILE}) killed!"

#!/bin/sh

VENV=".venv"
WORK_DIR=$(dirname "${BASH_SOURCE[0]}")

cd ${WORK_DIR}
source ../${VENV}/bin/activate

if [ "$1" == "--run" ];then
  python3 codegen.py ${1}
else
  python3 codegen.py --help
  exit 1
fi

# Format files in the model directory
for f in `ls ../model|grep -v __pycache__`
do
  echo "Formatting models code: ${f}"
  autopep8 -i ../model/${f}
done

# 备份并清空new.SDL文件
mv new.model new.model.bak
touch new.model
echo "Done!"
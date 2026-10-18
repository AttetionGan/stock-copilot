#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")/.."
if [[ ! -x .venv/bin/python ]]; then
  print '尚未安装项目环境，请先按 README 中的安装步骤操作。'
  read '?按回车关闭…'
  exit 1
fi
exec .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.headless false

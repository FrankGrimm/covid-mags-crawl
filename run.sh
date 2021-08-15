#!/bin/bash
set -xe

source .venv/bin/activate

python download.py
python extract.py
python combine.py

git add "./data"
git commit -m "data update"
git push

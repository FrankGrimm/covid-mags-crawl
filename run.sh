#!/bin/bash
set -xe

python download.py
python extract.py
python combine.py

git add "./data"
git commit -m "data update"
git push

import sys
import os
from glob import glob
from datetime import datetime
import csv

import pandas as pd
import camelot

DOWNLOAD_DIR = "./data/raw"
EXTRACT_DIR = "./data/extracted"

DATE_FORMAT = "%y%m%d"
FILENAME_SUFFIX = "_matrix.pdf"

def filename_to_date(f):
    return datetime.strptime(os.path.basename(f).replace(FILENAME_SUFFIX, ""), DATE_FORMAT)

def extract(date, filename):
    bname = os.path.basename(filename)
    print(f"[extract] {date} {bname}")

    tables = camelot.read_pdf(filename, stream=True, pages="1-end")
    dfs = [table.df for table in tables]

    df = dfs[0]
    if len(dfs) > 1:
        df = pd.concat(dfs)

    extract_filename = os.path.join(EXTRACT_DIR, bname.replace(".pdf", ".csv"))

    df.to_csv(extract_filename,
              sep=",",
              encoding="utf-8",
              quoting=csv.QUOTE_ALL)

    print(f"[extract/complete] {date}")

def main():
    all_files = list(glob(os.path.join(DOWNLOAD_DIR, "*.pdf")))
    all_files = [[filename_to_date(f), f] for f in all_files]
    all_files = sorted(all_files, key=lambda f: f[0])

    for date, filename in all_files:
        extract(date, filename)

if __name__ == "__main__":
    main()

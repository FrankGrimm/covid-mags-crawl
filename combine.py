import sys
import os
from glob import glob
from datetime import datetime
import csv

import numpy as np
import pandas as pd

EXTRACT_DIR = "./data/extracted"

DATE_FORMAT = "%y%m%d"
FILENAME_SUFFIX = "_matrix.csv"

def filename_to_date(f):
    return datetime.strptime(os.path.basename(f).replace(FILENAME_SUFFIX, ""), DATE_FORMAT)

def main():
    all_files = list(glob(os.path.join(EXTRACT_DIR, "*.csv")))
    all_files = [[filename_to_date(f), f] for f in all_files]
    all_files = sorted(all_files, key=lambda f: f[0])

    dfs = []
    dfs_totals = []
    for date, filename in all_files:
        df = pd.read_csv(filename)
        df['date'] = date
        df = df[['date'] + [c for c in df.columns if c != 'date']]
        df = df.drop(columns=["Unnamed: 0"])

        df.columns = ['date',
                      'subregion',
                      'Inzidenzstufe 0 (höchstens 10)',
                      'Inzidenzstufe 1 (von 10,1 bis 35)',
                      'Inzidenzstufe 2 (von 35,1 bis 50)',
                      'Inzidenzstufe 3 (über 50)']
        inci_columns = [c for c in df.columns if c.startswith("Inzidenz")]
        remove_explanation = "Aufgrund der geringen"

        for col in inci_columns:
            df[col] = df[col].astype(str).str.strip()
            df.loc[df[col].str.contains(remove_explanation), col] = np.nan

        # remove header row
        df = df[~df.subregion.isna()]

        df_total = df[df.subregion.str.contains("gesamt")].copy()
        df = df[~df.subregion.str.contains("gesamt")].copy()

        for col in inci_columns:
            df.loc[~(df[col] == "X"), col] = np.nan
            df[col] = df[col].map({np.nan: 0, "X": 1})
            df[col] = df[col].astype(int)

        dfs.append(df)
        dfs_totals.append(df_total)

    # merge all days
    df = pd.concat(dfs)
    df_totals = pd.concat(dfs_totals).drop(columns=['subregion'])

    # export totals
    df_totals.to_csv("./data/totals.csv",
                     sep=",",
                     encoding="utf-8",
                     index=False,
                     quoting=csv.QUOTE_ALL)

    df['subregion'] = df.subregion.str.replace("\n", "")

    # make sure that the lowest incidence case is the only one active per row
    for index, row in df.iterrows():
        rowsum = row[inci_columns].sum()
        if rowsum != 1:
            print("row sum != 1 in ", row)

    df.to_csv("./data/full.csv",
                     sep=",",
                     encoding="utf-8",
                     index=False,
                     quoting=csv.QUOTE_ALL)

if __name__ == "__main__":
    main()

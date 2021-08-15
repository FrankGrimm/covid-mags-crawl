import sys
import os
from glob import glob
from datetime import datetime, timedelta

import requests

force_downloads = "-f" in sys.argv

DOWNLOAD_DIR="./data/raw"
START_DATE = "210724"
DATE_FORMAT = "%y%m%d"

START_DATE = datetime.strptime(START_DATE, DATE_FORMAT)

URL_PREFIX = "https://www.mags.nrw/sites/default/files/asset/document/"
URL_SUFFIX = "_matrix.pdf"

def filename_for_date(d):
    formatted = datetime.strftime(d, DATE_FORMAT)
    return f"{formatted}{URL_SUFFIX}"

def requires_download(filename):
    target_file = os.path.join(DOWNLOAD_DIR, filename)
    status_file = os.path.join(DOWNLOAD_DIR, filename + ".status")

    if force_downloads:
        return True

    if not os.path.exists(status_file):
        return True

    prev_status = None
    if os.path.exists(status_file):
        with open(status_file, "rt") as infile:
            prev_status = infile.read().strip()
            if prev_status == "404":
                # target does not exist
                return False
            if prev_status == "200" and os.path.exists(target_file):
                # target already downloaded
                return False

    return True

def last_download_success():
    all_downloads = []
    cur_date = START_DATE

    while cur_date <= datetime.now():
        cur_file = filename_for_date(cur_date)
        all_downloads.append(cur_file)
        cur_date += timedelta(days=1)

    all_downloads = [f for f in all_downloads if os.path.exists(os.path.join(DOWNLOAD_DIR, f))]
    last_success = all_downloads[-1]

    return last_success

def download_file(filename):
    cur_uri = URL_PREFIX + filename
    target_filename = os.path.join(DOWNLOAD_DIR, filename)
    status_filename = os.path.join(DOWNLOAD_DIR, filename + ".status")

    print("[download] " + filename)

    with requests.get(cur_uri, stream=True) as r:
        r_status = r.status_code
        if r_status == 200:
            with open(target_filename, "wb") as outfile:
                for chunk in r.iter_content(chunk_size=1024*10):
                    outfile.write(chunk)
        with open(status_filename, "wt") as outfile:
            if r_status is None:
                r_status = "500"
            outfile.write(str(r_status) + "\n")

    print("[download/complete] " + filename)


if __name__ == "__main__":
    cur_date = START_DATE
    last_success = last_download_success()
    seen_last_success = False

    while cur_date <= datetime.now():
        cur_file = filename_for_date(cur_date)
        if cur_file == last_success:
            seen_last_success = True

        if not requires_download(cur_file) and not seen_last_success:
            print("[skip] " + cur_file, file=sys.stderr)
            cur_date += timedelta(days=1)
            continue

        download_file(cur_file)
        cur_date += timedelta(days=1)


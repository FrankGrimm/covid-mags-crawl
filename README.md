# covid-mags-crawl

Machine readable (automatically extracted) tables published by [MAGS NRW](https://www.mags.nrw/) on the current incidence rules for counties and cities in NRW, Germany.

# setup

```bash
pip install -r requirements.txt
# if that missed anything try pip install "camelot-py[cv]"
python download.py
python extract.py
python combine.py # writes the final output into ./data/full.csv and ./data/totals.csv
```

## cusp-df-miscfiles

miscellaneous scripts at CUSP data facility, so far includes:

1. "download-lehd.py" - which get's a URL's full table list and iterates through to:
  * save data to local directory
2. "dlnoad-parse-add-lehd.py" - also gets full list of "...csv.gz" files from site and:
  * save data to local directory
  * add data to master file (<dataset>_<st>.csv)
  * remove data from local directory
3. "download-lehd-xwalks.py" - stripped down version of above to simply iterate through all states/territories included on the LEHD LODES data site to download and locally save all "<st>_xwalk.csv.gz" files


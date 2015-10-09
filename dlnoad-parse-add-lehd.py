import os
import sys
import requests
from bs4 import BeautifulSoup
import pysftp
import json
# import csv, gzip #, io
import pandas as pd

def get_all_files(url):
    soup = BeautifulSoup(requests.get(url).text)
    url_list = []
    for a in soup.find_all('a'):
        href = a['href']
        if href.split('.')[-1]=='gz':
            url_list.append(files_url + href)
    return url_list

def download_file(url, fname):
    print 'starting data download...'
    ### a) save, 
    fname = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(fname, 'wb') as fd:
        for chunk in r.iter_content(1000):
            fd.write(chunk)
    print 'file written to local'

def parse_add_data(masterFileName, addFileName):
    file_yts = addFileName.split('_')
    file_yts[4] = file_yts[4][:4]
    yts_lines = [file_yts[4], file_yts[3], file_yts[2]]
    print "'YEAR,TYPE,SEG' are: ", yts_lines
    # with csv.reader(io.BufferedReader(gzip.open(addFileName, 'rb'))) as reader:
    print 'opening ', addFileName, ' with pandas'
    df=pd.read_csv(addFileName)
    file_yts= addFileName.split('_')
    yts_lines = [file_yts[4][:4], file_yts[3], file_yts[2]]
    # check if master file exists
    if (not os.path.isfile(masterFileName)):
        # with open(masterFileName) as f:
        df['YEAR'] = yts_lines[0]
        df['TYPE'] = yts_lines[1]
        df['SEG'] = yts_lines[2]
        df.to_csv(masterFileName, encoding='utf-8', index_label=False, index=False)
    else:
        with open(masterFileName, 'a') as f:
            df['YEAR'] = yts_lines[0]
            df['TYPE'] = yts_lines[1]
            df['SEG'] = yts_lines[2]
            df.to_csv(f, encoding='utf-8', index_label=False, index=False, header=False)
    return addFileName

if __name__=='__main__':
    files_url = sys.argv[1] # input "http://path/to/data/" at command line
    print files_url
    # get all file names
    all_files = get_all_files(files_url) #http://lehd.ces.census.gov/data/lodes/LODES7/ny/rac/ny_rac_S000_JT00_2003.csv.gz
    # file_url = files_url + 'ny_rac_S000_JT00_2003.csv.gz'
    print 'Files found: ', len(all_files)
    
    # keep track of parsed and added table list
    i = 0
    completed_tables = ["" for x in range(len(all_files))]
    for file_url in all_files[300:303]:
        fileName = file_url.split('/')[-1]
        # master file name is <st>_<dataset>
        masterFile = file_url.split('/')[-2]+'_'+file_url.split('/')[-3]+'.csv'
        download_file(file_url, fileName)
        completed_tables[i] = parse_add_data(masterFile, fileName)
        print 'completed download and parse of: ', fileName
        i += 1
    
    print 'finished. ', len(completed_tables), ' tables appended'
 

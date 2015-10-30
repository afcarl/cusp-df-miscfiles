'''
    Author: Clayton
    Date: Oct 8, 2015
    
    usage:
    python dnload-parse-add-lehd.py <url-to-data-files>
    
    details:
    program get's a full list of "...".gz files from an input URL contained in any <a href=""> html element, then iterates through the list to:
        a) download the .gz file,
        b) add data to master file, and
        c) removes file from local directory
        
'''
import os
import sys
import requests
from bs4 import BeautifulSoup
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
    # get and edit file name components for this file
    file_yts= addFileName.split('_')
    yts_lines = [file_yts[4][:4], file_yts[3], file_yts[2]]
    print 'opening ', addFileName, ' with pandas'
    df=pd.read_csv(addFileName)
    # check if master file exists
    if (not os.path.isfile(masterFileName)):
        # set up data frame for write
        df['YEAR'] = yts_lines[0]
        df['TYPE'] = yts_lines[1]
        df['SEG'] = yts_lines[2]
        # write first dataset to master file
        df.to_csv(masterFileName, encoding='utf-8', index_label=False, index=False)
    else:
        with open(masterFileName, 'a') as f:
            # set up header line
            df['YEAR'] = yts_lines[0]
            df['TYPE'] = yts_lines[1]
            df['SEG'] = yts_lines[2]
            # write next dataset to master file
            df.to_csv(f, encoding='utf-8', index_label=False, index=False, header=False)
    return addFileName

def remove_local_file(localFile):
    try:
        os.remove(localFile)
    except OSError:
        raise # raise if error
    print 'done removing file: ', localFile


if __name__=='__main__':
    files_url = sys.argv[1] # input "http://path/to/data/" at command line
    print files_url
    # get all file names
    all_files = get_all_files(files_url) #http://lehd.ces.census.gov/data/lodes/LODES7/ny/rac/ny_rac_S000_JT00_2003.csv.gz
    # file_url = files_url + 'ny_rac_S000_JT00_2003.csv.gz'
    print 'Files found: ', len(all_files)
    
    # keep track of parsed and added table list
    completed_tables = ["" for x in range(len(all_files))]
    for file_url in all_files:
        fileName = file_url.split('/')[-1]
        # master file name is <st>_<dataset>.csv
        masterFile = file_url.split('/')[-2]+'_'+file_url.split('/')[-3]+'.csv'
        # download and save this file
        download_file(file_url, fileName)
        # add saved file to master
        fileAdded = parse_add_data(masterFile, fileName)
        # remove temporary file
        remove_local_file(fileName)
        print 'completed download and parse of: ', fileName
    
    print 'finished.'
 

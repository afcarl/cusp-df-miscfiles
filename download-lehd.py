'''
    Author: Clayton
    Date: Oct 7, 2015
    
    usage:
    python download-test.py <url-to-data-files>
    
    details:
    program get's a full list of "...".gz files from an input URL contained in any <a href=""> html element, then iterates through the list to download and save the .gz file
'''
import sys
import requests
from bs4 import BeautifulSoup

# http://lehd.ces.census.gov/data/lodes/LODES7/ny/rac/

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
    #fname = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(fname, 'wb') as fd:
        for chunk in r.iter_content(1000):
            fd.write(chunk)
    print 'file written to local'

if __name__=='__main__':
    files_url = sys.argv[1] # input "http://path/to/data/" at command line
    
        # get all file names
    all_files = get_all_files(files_url)
    print 'Files found: ', len(all_files)
    
    i = 0 # counter
    for file_url in all_files[0:2]:
        fileName = file_url.split('/')[-1]
        # master file name is <st>_<dataset>
        # masterFile = file_url.split('/')[-2]+'_'+file_url.split('/')[-3]+'.csv'
        download_file(file_url, fileName)
        # remove_local_file(fileName)
        i += 1
        print 'completed download and save of: ', fileName
    
    print 'finished. saved %s files' % (i)


'''
    Author: Clayton
    Date: Oct 10, 2015
    
    usage:
    python download-us-geogs.py <url-to-data-files>
    
    details:
    program downloads geography files from <url-to-data-files> and adjusted based on hardcoded "tbl" format and FIPS codes
'''
import sys
import requests

def download_file(url, fname):
    # download then locally write file
    r = requests.get(url, stream=True)
    with open(fname, 'wb') as fd:
        for chunk in r.iter_content(1000):
            fd.write(chunk)

if __name__=='__main__':
    baseURL = sys.argv[1] # input "http://path/to/data/" at command line
    
    fips = ['09', '34', '36'] # download geographies for CT, NJ, and NY    
    
    for i, fip in enumerate(fips):
        tbl = 'tl_2010_%s_tabblock10.zip' % (fip)
        print 'starting download of', tbl
        
        # set download url
        file_url = baseURL + tbl

        print 'at url', file_url
        download_file(file_url, tbl)
        
        print 'completed download and save of', tbl
        print 'now {0:.2f}% complete'.format((i+1)*100./len(fips))
    
    print 'finished. saved %s files' % (i+1)


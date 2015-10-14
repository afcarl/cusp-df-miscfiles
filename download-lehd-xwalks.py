'''
    Author: Clayton
    Date: Oct 14, 2015
    
    usage:
    python download-lehd-xwalks.py
    
    details:
    program iterates through the list of states to download all <st>_xwalk.csv.gz files from the LEHD data server, for example ny_xwalk.csv.gz here: http://lehd.ces.census.gov/data/lodes/LODES7/ny/
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
    baseURL = 'http://lehd.ces.census.gov/data/lodes/LODES7/'
    # files_url = sys.argv[1] # input "http://path/to/data/" at command line
    states = ['ak', 'al', 'ar', 'az', 'ca', 'co', 'ct', 'dc', 'de', 'fl', 'ga', 
              'hi', 'ia', 'id', 'il', 'in', 'ks', 'ky', 'la', 'ma', 'md', 'me', 
              'mi', 'mn', 'mo', 'ms', 'mt', 'nc', 'nd', 'ne', 'nh', 'nj', 'nm', 
              'nv', 'ny', 'oh', 'ok', 'or', 'pa', 'pr', 'ri', 'sc', 'sd', 'tn', 
              'tx', 'ut', 'va', 'vi', 'vt', 'wa', 'wi', 'wv', 'wy']
    print 'downloding xwalk fiels for %s states or territories' % (len(states))
    
    for i, state in enumerate(states):
        # fileName = file_url.split('/')[-1]
        fileName = state + '_xwalk.csv.gz'
        fileURL = baseURL + state + '/' + fileName
        print 'starting download of', fileName
        print 'from url', fileURL
        download_file(fileURL, fileName)
        print 'completed download and save of', fileName
        print 'now {0:.2f}% complete'.format((i+1)*100./len(states))
    
    print 'finished. saved %s files' % (i+1)


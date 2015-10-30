'''
    Author: Clayton
    Date: Oct 7, 2015
    
    usage:
    python download-test.py <url-to-data-files> <sftp creds>
    
    details:
    program get's a full list of "...".gz files from an input URL contained in any <a href=""> html element, then iterates through the list to:
        a) download the .gz file,
        b) upload file to sftp site (given in <sftp creds> argument), and
        c) removes file from local directory
        
    Note: for sftp credentals (<sftp creds>), can either 
        a) link to a saved JSON file with line 45 or 
        b) paste/type in JSON string directly to command line using line 46
'''
import os
import sys
import requests
from bs4 import BeautifulSoup
import pysftp
import json
import csv, gzip, io

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
    fname = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(fname, 'wb') as fd:
        for chunk in r.iter_content(1000):
            fd.write(chunk)
    print 'file written to local'
    # b) call sftp transfer function and c) delete local file

# psuedo code as of 11am
def parse_add_data(masterFileName, addFileName):
    file_yts = addFileName.split('_')
    file_yts[4] = file_yts[4][:4]
    # yts_lines = ',' + ','.join([file_yts[4], file_yts[3], file_yts[2]])
    yts_lines = ','.join([file_yts[4], file_yts[3], file_yts[2]])
    print "'YEAR,TYPE,SEG' are: ", yts_lines
    # with csv.reader(io.BufferedReader(gzip.open(addFileName, 'rb'))) as reader:
    print 'opening ', addFileName, ' with gzip'
    with gzip.open(addFileName, 'rb') as f:
        # check if master file exists
        if (not os.path.isfile(masterFileName)):
            # write column names to first line
            with open(masterFileName, 'wb') as masterFile:
                writer = csv.writer(masterFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                # strip newline character and
                # add year, type, seg and type column names
                line = f.readline()
                lineAdd = ','.join([''.join(line[:-1]), 'YEAR,TYPE,SEG'])
                writer.writerow(lineAdd)
                # writer.next()
                print 'wrote header line: ', lineAdd
                # writer.close()
        with open(masterFileName, 'wb') as masterFile:
            # masterFile.seek(-1,2) # go to end of existing file
            # masterFile.readline()
            writer = csv.writer(masterFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for line in f:
                # i = 1
                #while True:
                try: 
                    # line = reader.next() # get subsequent lines of file
                    # strip newline character and
                    # add file's YEAR,TYPE,SEG to line
                    lineAdd = ','.join([''.join(line[:-1]), yts_lines])
                    writer.writerow(lineAdd)
                    # i += 1
                #    if not line:
                #        break
                except error as e:
                    print "Error ", e
                except csv.Error:
                    print "CSV Error"
                except StopIteration:
                    print "Iteration End"
                    break
            # writer.close()
        print 'File ', addFileName, ' appended successfully'
    return addFileName

def upload_to_sftp(localFile):
    creds = json.load(sys.argv[2])
    # creds = json.loads(sys.argv[2])
    # Create SFTP connection
    sftp = pysftp.Connection(host=creds['host'], username=creds['username'], password=creds['password'])
    with sftp.cd('upload'):
	    print 'pre-existing files on sftp: ', sftp.listdir()
	    sftp.put(localFile)
	    print 'now existing files: ', sftp.listdir()
    print 'upload file: ', localFile
    
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
    all_files = get_all_files(files_url)
    print 'Files found: ', len(all_files)
    
    # keep track of parsed and added table list
    completed_tables = []
    for file_url in all_files[0:2]:
        fileName = file_url.split('/')[-1]
        # master file name is <st>_<dataset>
        masterFile = file_url.split('/')[-2]+'_'+file_url.split('/')[-3]+'.csv'
        download_file(file_url, fileName)
        completed_tables = completed_tables.append(parse_add_data(masterFile, fileName))
    #    upload_to_sftp(fileName)
        remove_local_file(fileName)
        print 'completed download and parse of: ', fileName
    # parse file name for functions
    #fileName = all_files[0].split('/')[-1]
    #download_file(all_files[0], fileName)
    #completed_tables = completed_tables.append(parse_add_data(all_files[0], fileName))
    #upload_to_sftp(fileName)
    #remove_local_file(fileName)
    
    print 'finished. ', len(completed_tables), ' tables appended'
    


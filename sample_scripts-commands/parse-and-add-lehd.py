import os
import sys
import requests
from bs4 import BeautifulSoup
import pysftp
import json
# import csv, gzip #, io
import pandas as pd


def parse_add_data(masterFileName, addFileName):
    file_yts = addFileName.split('_')
    file_yts[4] = file_yts[4][:4]
    # yts_lines = ',' + ','.join([file_yts[4], file_yts[3], file_yts[2]])
    # yts_lines = ','.join([file_yts[4], file_yts[3], file_yts[2]])
    yts_lines = [file_yts[4], file_yts[3], file_yts[2]]
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
                print 'line before joins: ', line
                # join = ','.lineAdd([''.join(line[:-1]), 'YEAR,TYPE,SEG' + line[-1]])
                # lineAdd = [line[:-1] + ',' + ','.join(['YEAR', 'TYPE', 'SEG'])]#, line[-1]]
                lineAdd = [line[:-1].split(','), 'YEAR', 'TYPE', 'SEG']
                writer.writerow(lineAdd)
                # writer.next()
                print 'wrote header line: ', lineAdd
                # writer.close()
        with open(masterFileName, 'wb') as masterFile:
            # masterFile.seek(-1,2) # go to end of existing file
            # masterFile.readline()
            writer = csv.writer(masterFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # for line in f:
                # i = 1
            while True:
                try: 
                    line = f.readline() # get subsequent lines of file
                    # strip newline character and
                    # add file's YEAR,TYPE,SEG to line
                    # lineAdd = ','.join([''.join(line[:-1]), yts_lines + line[-1]])
                    lineAdd = [line[:-1]+ ',' + ','.join(yts_lines)]
                    lineAdd = [line[:-1].split(','), yts_lines]
                    writer.writerow(lineAdd)
                    # i += 1
                #    if not line:
                #        break
                except csv.Error:
                    print "CSV Error"
                except StopIteration:
                    print "Iteration End"
                    break
                except: # error:
                    print "Error "
                    break
            # writer.close()
        print 'File ', addFileName, ' appended successfully'
    return addFileName

if __name__=='__main__':
    files_url = sys.argv[1] # input "http://path/to/data/" at command line
    print files_url
    # get all file names
    # all_files = get_all_files(files_url) http://lehd.ces.census.gov/data/lodes/LODES7/ny/rac/ny_rac_S000_JT00_2003.csv.gz
    file_url = files_url + 'ny_rac_S000_JT00_2003.csv.gz'
    # print 'Files found: ', len(all_files)
    
    # keep track of parsed and added table list
    completed_tables = []
    # for file_url in all_files[0:2]:
    fileName = file_url.split('/')[-1]
    # master file name is <st>_<dataset>
    masterFile = file_url.split('/')[-2]+'_'+file_url.split('/')[-3]+'.csv'
    # download_file(file_url, fileName)
    completed_tables = completed_tables.append(parse_add_data(masterFile, fileName))
#    upload_to_sftp(fileName)
    # remove_local_file(fileName)
    print 'completed download and parse of: ', fileName
    # parse file name for functions
    #fileName = all_files[0].split('/')[-1]
    #download_file(all_files[0], fileName)
    #completed_tables = completed_tables.append(parse_add_data(all_files[0], fileName))
    #upload_to_sftp(fileName)
    #remove_local_file(fileName)
    
    print 'finished. '#, len(completed_tables), ' tables appended'
 

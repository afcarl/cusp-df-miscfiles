'''
    Author: Clayton
    Date: Oct 22, 2015
    
    usage:
    python parse-add-lehd.py <st> <dataset>
    
    details:
    program iterates through selected counties' "...".gz files from working directory, then extracts the listed counties and adds data to master file named <st>c_<dataset>.csv
        
'''
import os
import sys
import pandas as pd

# add DataFrame to state's master file
def add_data(masterFileName, df):
    # check if master file exists
    if (not os.path.isfile(masterFileName)):
        # write first dataset to master file
        df.to_csv(masterFileName, encoding='utf-8', index_label=False, index=False)
    else:
        with open(masterFileName, 'a') as f:
            # append next dataset to master file
            df.to_csv(f, encoding='utf-8', index_label=False, index=False, header=False)
    # return addFileName

if __name__=='__main__':
    # set up parameters for download
    st = sys.argv[1] # which state? 'ny'
    part = sys.argv[2] # which dataset? valid inputs are rac, wac, od
    cnty_list = ['36005', '36047', '36061', '36081', '36085']
    
    files = filter(os.path.isfile, os.listdir('.')) # get list of files
    # check they start in <st>_<part> and end in .gz
    all_files = [f for f in files if (f.split('.')[-1]=='gz' and f.split('_')[0]==st and f.split('_')[1]==part)]
    print 'file list is:', all_files
    
    masterFile = st + 'c_' + part + '.csv'
    
    for fileName in all_files:
        # get and edit file name components for this file
        file_yts= fileName.split('_')
        yts_lines = [file_yts[4][:4], file_yts[3], file_yts[2]]
        print 'opening ', fileName, ' with pandas'
        df=pd.read_csv(fileName)
        # set up data frame for write
        df['YEAR'] = yts_lines[0]
        df['TYPE'] = yts_lines[1]
        df['SEG'] = yts_lines[2]
        
        # select just blocks in cnty_list
        df.iloc[:, [0]] = df.iloc[:, [0]].astype(str)
        fips = df.iloc[:, [0]]
        print 'subsetted and converted fips to string'
        toSelect = fips.apply(lambda c: True if c.iloc[0][0:5] in cnty_list else False, axis=1)
        print 'created toSelect'
        df = df[toSelect]
        
        # print df.info()
        # print 'cnty len is', len(cnty)
        # add saved file to master
        # fileAdded = 
        add_data(masterFile, df)
        print 'completed:', fileName
    
    print 'finished.'
 

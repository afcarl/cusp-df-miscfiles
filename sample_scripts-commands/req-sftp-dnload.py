
import sys
import requests
import pysftp

## read in credentials from file
# creds = json.load(open(sys.argv[1]))
## or read in credentials from string argument: '{"host": "<hostname>", "username": "<username>", "password": "<password>"}'
creds = json.loads(sys.argv[1])
# Create SFTP connection
sftp = pysftp.Connection(host=creds['host'], username=creds['username'], password=creds['password'])

# 'http://lehd.ces.census.gov/data/lodes/LODES7/ny/rac/ny_rac_SI03_JT05_2013.csv.gz'
with sftp.cd('upload'):
    file = sys.argv[1]
    r = requests.get(file, stream=True)
    fname = file.split('/')[-1]
    putFile = r.content
    # this is only for data transfer I think... so would need to first save, then transfer
    sftp.put(putFile) 
#    with open(fname, 'wb') as fd:
#        for chunk in r.iter_content(1000):
#            fd.write(chunk)
    # check if it uploaded...
    print 'files now uploaded: ', sftp.listdir()

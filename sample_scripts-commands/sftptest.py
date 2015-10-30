import pysftp
import sys
import json

## read in credentials from file
# creds = json.load(open(sys.argv[1]))
## or read in credentials from string argument: '{"host": "<hostname>", "username": "<username>", "password": "<password>"}'
creds = json.loads(sys.argv[1])
# Create SFTP connection
sftp = pysftp.Connection(host=creds['host'], username=creds['username'], password=creds['password'])

with sftp.cd('upload'):
	print sftp.listdir()

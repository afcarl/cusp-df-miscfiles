add NYC lehd-lodes data to postgres database
--------------------------------------------

#### try reshaping wide data to long (or "record") format so easier to interact with programmatically
+ geog/year/seg/type are already long format
using ipython on compute:
```python
import pandas as pd
rac = pd.read_csv('nyc_rac.csv')
rac.drop('createdate', axis=1, inplace=True) # don't bother with that field
df = pd.melt(rac, id_vars=['h_geocode', 'YEAR', 'TYPE', 'SEG'])
```
+ BUT: data size? wide format = memory usage: 5.0+ GB, long format = memory usage: 31.2+ GB

#### see how larger data file works in postgres
+ first compare file sizes: ls -lh nyc_rac*
  * 
```
psql df_spatial 
CREATE TABLE nyc_rac_long (blkfips varchar(15), year integer, job_type varchar(4), segment varchar(4), variable varchar(4), value numeric);
\copy nyc_rac_long FROM 'nyc_rac_long.csv' CSV HEADER
\d+ nyc_rac_long
```

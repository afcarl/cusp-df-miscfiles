add NYC lehd-lodes data to postgres database
--------------------------------------------

#### reshape wide data to long or "record" format so easier to interact with programmatically
> mostly, as geog/year/seg/type are already long format
> using ipython on compute:
import pandas as pd
rac = pd.read_csv('nyc_rac.csv')
rac.drop('createdate', axis=1)

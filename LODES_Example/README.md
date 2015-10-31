Notes to access LODES data on CUSP servers
-------------------------------------------

#### Log in to CUSP servers
+ NOTE 1: to be updated with in progress work by Data Facility
+ NOTE 2: below is a walk through that works using Ubuntu 15.04

1. Open a terminal
2. SSH to compute:
  * need to go via shell: `ssh <cuspID>@shell.cusp.nyu.edu` replace <cuspID> with your CUSP ID (eg mine is crh278, so the command for me is `ssh crh278@shell.cusp.nyu.edu`)
  * and then you can get to compute: `ssh compute.cusp.nyu.edu`
3. check you have access to the PostgreSQL database and see what tables exist
  * open an instance of [psql](http://www.postgresql.org/docs/9.4/static/app-psql.html): `psql df_spatial`
  * list all tables `\dt` and/or view the details of a specific table, eg `\d+ nyc_rac`
  * exit psql `\q`
  
#### Two easy(ish) ways to play with data

1. psql - already used above, you can enter any SQL statement and there are many other commands. For example
  * Sum RAC workers (total and by age group) for all private/federal primary jobs by year: `SELECT year, type, sum(c000) c000, sum(ca01) ca01, sum(ca02) ca02, sum(ca03) ca03 FROM nyc_rac r WHERE type IN ('JT03', 'JT05') GROUP BY year, type ORDER BY type, year;`
  * Save above (but also by county) out to a .csv in your workspace (NOTE: takes ~2.3 minutes): `\copy (SELECT county_fips, year, type, sum(c000) c000, sum(ca01) ca01, sum(ca02) ca02, sum(ca03) ca03 FROM (SELECT left(h_geocode, 5) county_fips, year, type, c000, ca01, ca02, ca03 FROM nyc_rac r WHERE type IN ('JT03', 'JT05')) q GROUP BY year, type, county_fips ORDER BY type, county_fips, year) TO './county_rac_worker_age.csv' CSV HEADER`
2. Python, here's two examples
  1. using psycopg2 which gives more DB functionality (and [here's](http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries) their "basic module usage" examples for more detail)
  2. using pandas to get the result of a query directly into a dataframe
```python
#### example 1: pyscopg2 to list tables
import psycopg2 as pg

# define connection
conn = pg.connect("dbname=df_spatial host=compute.cusp.nyu.edu user=<username> password=<password>")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: get list of tables then print them
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type='BASE TABLE'")
print cur.fetchall()

##### example 2: get resulting query directly into pandas DataFrame
# get the same annual and by county summary of workers for all private and federal primary jobs in NYC
# BUT, pass in the job types as paramaters
import pandas as pd

# set query
qry = "SELECT county_fips, year, type, sum(c000) c000, sum(ca01) ca01, sum(ca02) ca02, sum(ca03) ca03 FROM (SELECT left(h_geocode, 5) county_fips, year, type, c000, ca01, ca02, ca03 FROM nyc_rac r WHERE type IN ('%s', '%s')) q GROUP BY year, type, county_fips ORDER BY type, county_fips, year;" % ('JT03', 'JT05')

# get query results into a pandas DataFrame, a bit slower than psql but not terribly
df = pd.read_sql_query(qry, conn)

# view dataframe info
df.info()
```

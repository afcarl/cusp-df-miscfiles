## data manipulation to extract some LEHD LODES data for a visualization proof of concept, all below run on CUSP compute

#### create empty table (in psql) and add to "df_spatial" postgres DB
+ `CREATE TABLE bg2010_nhood (geoid varchar(12), ntacode varchar(4), ntaname varchar(100), lat double precision, lon double precision);`
+ `\copy bg2010_nhood FROM '/home/cusp/crh278/lehd/geogs/bg2010_lookup.csv' CSV HEADER`

#### compile geography data for NY-NJ-CT blocks, plus some DB admin stuff
+ `SELECT * INTO tristate_blocks FROM (SELECT * FROM tl_2010_09_tabblock10 UNION ALL SELECT * FROM tl_2010_34_tabblock10 UNION ALL SELECT * FROM tl_2010_36_tabblock10) as q;` - create table from 3 state level block tables
+ `ALTER TABLE tristate_blocks ADD PRIMARY KEY (geoid10);` - set primary key to block FIPS code
+ `CREATE INDEX tristate_blocks_geom_gist ON tristate_blocks USING gist (geom);` - add gist index to polygon data
+ `ALTER TABLE tristate_blocks ADD COLUMN geom_pntwgs geometry('Point', 4326);`
+ `UPDATE tristate_blocks SET geom_pntwgs = ST_Transform(ST_Centroid(geom), 4326);`
+ `CREATE INDEX tristate_blocks_geompntwgs_gist ON tristate_blocks USING gist (geom_pntwgs);` - best practice to have GiST index on geometry columns
+ `ALTER TABLE tristate_blocks ADD COLUMN blkgrp10 varchar(12);` - create block group column for faster matching to neighborhood lookup file
+ `UPDATE tristate_blocks SET blkgrp10 = left(geoid10, 12);` - populate
+ `CREATE INDEX ON tristate_blocks (blkgrp10);` - create index for faster searching
+ `VACUUM ANALYZE tristate_blocks` - clean up and recalculate table stats
+ `ALTER TABLE bg2010_nhood ADD PRIMARY KEY (geoid);` - add primary key to lookup table
+ `VACUUM ANALYZE VERBOSE bg2010_nhood;` - how to see what VACUUM ANALYZE does

#### select DUBMO blocks' point coordinates (psql)
+ `SELECT geoid10 as blockid10, ST_Y(ST_Centroid(geom_pntwgs)) as lat, ST_X(ST_Centroid(geom_pntwgs)) as lon INTO dumbo_blocks FROM tristate_blocks t JOIN bg2010_nhood b ON t.blkgrp10 = b.geoid WHERE b.ntacode = 'BK38';` - select blocks and lat/lon coordinates in DUMBO neighborhood
+ `SELECT count(*) FROM dumbo_lodes_odunique WHERE lat IS NULL;` - unassigned records confirmed outside of NY-NJ-CT
+ `\copy (select * from dumbo_lodes_odunique WHERE lat IS NOt NULL) TO './dumbo_od_wCoords.csv' CSV HEADER` - save out data

#### get LEHD datasets with records in DUMBO (ipython)
+ `import pandas as pd`
+ `dumbo = pd.read_csv('dumbo_blocks.csv')`
+ `rac = pd.read_csv('rac/nyc_rac.csv')`
+ `indx = rac.h_geocode.isin(dumbo.blockid10)`
+ `df = rac[indx]`
+ `df = pd.merge(df, dumbo, left_on='h_geocode', right_on='blockid10')`
+ `df.to_csv('dumbo_rac.csv', index=False, index_label=False)`
+ `wac = pd.read_csv('wac/nyc_wac.csv')`
+ `indx = wac.w_geocode.isin(dumbo.blockid10)`
+ `df = wac[indx]`
+ `df = pd.merge(df, dumbo, left_on='w_geocode', right_on='blockid10')`
+ `df.to_csv('dumbo_wac.csv', index=False, index_label=False)`
+ `od = df.read_csv('od/nyc_od.csv)`
+ `indxh = od.h_geocode.isin(dumbo.blockid10)` - is there a residential match
+ `indxw = od.w_geocode.isin(dumbo.blockid10)` - is there a workplace match
+ `df = od[indxh | indxw]` - grab those that match either workplace or home (2676642 entries)
+ `df.to_csv('dumbo_od.csv', index=False, index_label=False)`
> NOTE: for Lat/Lon data need blocks outside of DUMBO, that step in postgres DB (below)
+ `import numpy as np`
+ `dumbo_od_geocodes = np.append(df.w_geocode.unique(), df.h_geocode.unique())`
+ `dumbo_od_geocodes = pd.DataFrame(dumbo_od_geocodes)`
+ `dumbo_od_geocodes = dumbo_od_geocodes.rename(columns={0: 'geocode'})`
+ `dumbo_od_geocodes = dumbo_od_geocodes.geocode.unique()`
+ `dumbo_od_geocodes = pd.DataFrame(dumbo_od_geocodes)`
+ `dumbo_od_geocodes = dumbo_od_geocodes.rename(columns={0: 'geocode'})`
+ `dumbo_od_geocodes.to_csv('dumbo_od_geo.csv', index=False, index_label=False)`

##### get DUMBO O-D lat/lon (psql)
+ `CREATE TABLE dumbo_lodes_odunique (geocode varchar(15));`
+ `\copy dumbo_lodes_odunique FROM './dumbo_od_geo.csv' CSV HEADER`
+ `UPDATE dumbo_lodes_odunique SET geocode = CASE WHEN length(geocode) < 15 THEN '0' || geocode ELSE geocode END;` - update when pandas dropped leading '0' of block FIPS (Connecticut = '09')
+ `ALTER TABLE dumbo_lodes_odunique ADD PRIMARY KEY (geocode);`
+ `VACUUM ANALYZE dumbo_lodes_odunique;`
+ `ALTER TABLE dumbo_lodes_odunique ADD COLUMN lat double precision, ADD COLUMN lon double precision;`
+ `UPDATE dumbo_lodes_odunique d SET (lat, lon) = (ST_Y(ST_Centroid(geom_pntwgs)), ST_X(ST_Centroid(geom_pntwgs))) FROM tristate_blocks t WHERE d.geocode = t.geoid10;`
+ check if records didn't match in NY-NJ-CT `SELECT * FROM dumbo_lodes_odunique WHERE lat IS NULL AND left(geocode, 2) IN ('09', '34', '36');`
+ total pairs outside NY-NJ-CT (= 8465): `SELECT count(*) FROM dumbo_lodes_odunique WHERE lat IS NULL;` of total pairs (= 122698, 6.9%): `SELECT count(*) FROM dumbo_lodes_odunique;`
+ write to file `\copy (select * from dumbo_lodes_odunique WHERE lat IS NOt NULL) TO './dumbo_od_wCoords.csv' CSV HEADER`

#### get data back to laptop for testing / dev
+ `scp crh278@shell.cusp.nyu.edu:/home/cusp/crh278/lehd/lodes_tmp/dumbo_wac.csv ./`
+ `scp crh278@shell.cusp.nyu.edu:/home/cusp/crh278/lehd/lodes_tmp/dumbo_rac.csv ./`
+ `scp crh278@shell.cusp.nyu.edu:/home/cusp/crh278/lehd/lodes_tmp/dumbo_od.csv ./`
+ `scp crh278@shell.cusp.nyu.edu:/home/cusp/crh278/lehd/lodes_tmp/dumbo_od_wCoords.csv ./` - a bit of a misnomer file name, simply 3 columns: geocode (block id), lat, lon

#### files generated for testing and dev, need to trim these down more
(size, date, name)
+ 182M Oct 28 18:59 `dumbo_od.csv` - either O/D in DUMBO
+ 5.6M Oct 28 18:55 `dumbo_od_wCoords.csv` - any block id (O-D, plus lat/lon) from above in NY-NJ-CT
+ 9.8M Oct 28 13:27 `dumbo_rac.csv`
+ 12M Oct 28 13:27 `dumbo_wac.csv`

### other stuff done but not necessary for this step, maybe useful in future
#### get unique blocks from full NYC LODES LEHD O-D table (ipython)
+ `import pandas as pd`
+ `import numpy as np`
+ `df = pd.read_csv('./nyc_od.csv')` - 11G file takes a bit to load...
+ `df.info()` - print out removed, but note <|>_geocode read in as int
+ `w_geo = df.w_geocode.unique()` - get unique workplace codes
+ `h_geo = df.h_geocode.unique()` - get unique residential codes
+ `all_geo = np.append(w_geo, h_geo)` - combine workplace and residential
+ `geodf = pd.DataFrame(all_geo)`
+ `geodf = geodf.rename(columns={0: 'geocode'})`
+ `uni_geo = geodf.geocode.unique()` - keep only unique codes
+ `uni_geo = pd.DataFrame(uni_geo)`
+ `uni_geo = uni_geo.rename(columns={0: 'geocode'})` - 543190 non-null int64
#### create table and load unique O-D block list to database (psql)
+ `CREATE TABLE nyc_lodes_odunique (geocode varchar(15))`
+ `\copy nyc_lodes_odunique FROM './nyc_lodes_od_geogs.csv' CSV HEADER`


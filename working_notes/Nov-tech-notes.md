#### November 2nd data cleaning / testing

```SQL
----------------------
-- test some queries
-- note performed in psql, thus \copy... is psql form of COPY <query> TO <file>
---------------------
SELECT year, type, sum(c000) c000, sum(ca01) ca01, sum(ca02) ca02, sum(ca03) ca03 FROM nyc_rac r WHERE type IN ('JT03', 'JT05') AND r.seg = 'S000' GROUP BY year, type ORDER BY type, year;

-- summarize RAC/WAC by tract and copy out to local --
\copy (SELECT left(h_geocode, 11) tract_fips, year, type, seg, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03, sum(r.ce01) ce01, sum(r.ce02) ce02, sum(r.ce03) ce03, sum(r.cns01) cns01, sum(r.cns02) cns02, sum(r.cns03) cns03, sum(r.cns04) cns04, sum(r.cns05) cns05, sum(r.cns06) cns06, sum(r.cns07) cns07, sum(r.cns08) cns08, sum(r.cns09) cns09, sum(r.cns10) cns10, sum(r.cns11) cns11, sum(r.cns12) cns12, sum(r.cns13) cns13, sum(r.cns14) cns14, sum(r.cns15) cns15, sum(r.cns16) cns16, sum(r.cns17) cns17, sum(r.cns18) cns18, sum(r.cns19) cns19, sum(r.cns20) cns20, sum(r.cr01) cr01, sum(r.cr02) cr02, sum(r.cr03) cr03, sum(r.cr04) cr04, sum(r.cr05) cr05, sum(r.cr07) cr07, sum(r.ct01) ct01, sum(r.ct02) ct02, sum(r.cd01) cd01, sum(r.cd02) cd02, sum(r.cd03) cd03, sum(r.cd04) cd04, sum(r.cs01) cs01, sum(r.cs02) cs02 FROM nyc_rac r GROUP BY tract_fips, year, type, seg ORDER BY type, seg, year, tract_fips) TO './tract_rac_nyc.csv' CSV HEADER
-- 15 ish minutes?

\copy (SELECT left(w_geocode, 11) tract_fips, year, type, seg, sum(w.c000) c000, sum(w.ca01) ca01, sum(w.ca02) ca02, sum(w.ca03) ca03, sum(w.ce01) ce01, sum(w.ce02) ce02, sum(w.ce03) ce03, sum(w.cns01) cns01, sum(w.cns02) cns02, sum(w.cns03) cns03, sum(w.cns04) cns04, sum(w.cns05) cns05, sum(w.cns06) cns06, sum(w.cns07) cns07, sum(w.cns08) cns08, sum(w.cns09) cns09, sum(w.cns10) cns10, sum(w.cns11) cns11, sum(w.cns12) cns12, sum(w.cns13) cns13, sum(w.cns14) cns14, sum(w.cns15) cns15, sum(w.cns16) cns16, sum(w.cns17) cns17, sum(w.cns18) cns18, sum(w.cns19) cns19, sum(w.cns20) cns20, sum(w.cr01) cr01, sum(w.cr02) cr02, sum(w.cr03) cr03, sum(w.cr04) cr04, sum(w.cr05) cr05, sum(w.cr07) cr07, sum(w.ct01) ct01, sum(w.ct02) ct02, sum(w.cd01) cd01, sum(w.cd02) cd02, sum(w.cd03) cd03, sum(w.cd04) cd04, sum(w.cs01) cs01, sum(w.cs02) cs02, sum(w.cfa01) cfa01, sum(w.cfa02) cfa02, sum(w.cfa03) cfa03, sum(w.cfa04) cfa04, sum(w.cfa05) cfa05, sum(w.cfs01) cfs01, sum(w.cfs02) cfs02, sum(w.cfs03) cfs03, sum(w.cfs04) cfs04, sum(w.cfs05) cfs05 FROM nyc_wac w GROUP BY tract_fips, year, type, seg ORDER BY type, seg, year, tract_fips) TO './tract_wac_nyc.csv' CSV HEADER

-----------------------
-----------------------

------ make O-D data more useful ----------
-- first create unique block-block table for NYC O-D
SELECT h_geocode, w_geocode INTO nyc_od_unique FROM nyc_od GROUP BY h_geocode, w_geocode;

-- NOTE: takes a long time, summarizing 153,094,477 rows
---- first version created 31,176,321 rows, but laptop disconnected during process so runing a 2nd version to confirm...
```
+ v1 command above got killed on laptop disconnect, but as noted did produce a big table
+ v2 command used to run in background is below, going to test resulting table length
  * `nohup psql -d df_spatial -c "SELECT h_geocode, w_geocode INTO nyc_od_unique_v2 FROM nyc_od GROUP BY h_geocode, w_geocode" &`
  * note, above gave "nohup: ignoring input and appending output to `nohup.out'" warning...
  * completed with same number (31,176,321) of total rows as v1, dropped v2 table

```SQL
-- update table, pg administrative stuff
ALTER TABLE nyc_od_unique ADD COLUMN uid serial NOT NULL; ALTER TABLE nyc_od_unique ADD PRIMARY KEY (uid); CREATE INDEX ON nyc_od_unique (h_geocode); CREATE INDEX ON nyc_od_unique (w_geocode);

-- add geometry columns for distance calculation
-- nyc_od_unique includes any combination where EITHER home or work is in NYC
-- tristate_blocks as all block info for NY / NJ / CT
-- so, resulting distance calculations will have any commuters entering / leaving NYC 
-- with origins/destinations in one of those three states, but will throw an error if do not include 
-- "WHERE [h/w]_geocode IS NOT NULL"
ALTER TABLE nyc_od_unique ADD COLUMN h_geom geometry('Point', 4326), ADD COLUMN w_geom geometry('Point', 4326);
UPDATE nyc_od_unique n SET h_geom = geom_pntwgs FROM tristate_blocks t WHERE n.h_geocode = t.geoid10; UPDATE nyc_od_unique n SET w_geom = geom_pntwgs FROM tristate_blocks t WHERE n.w_geocode = t.geoid10;

-- add distance column and calculate, cast to geography to calculate distance on spheroid
ALTER TABLE nyc_od_unique ADD COLUMN dist_meters double precision; 

-- calculate table stats
VACUUM ANALYZE nyc_od_unique;
```

#### (November 3rd++) Given time to calculate above, run next chunk in background
+ first create a file (od_update_1103.sql) which simple contains the below
```SQL
UPDATE nyc_od_unique SET dist_meters = ST_Distance(h_geom::geography, w_geom::geography) WHERE h_geom IS NOT NULL AND w_geom IS NOT NULL;
-- add start and end neighborhood codes
ALTER TABLE nyc_od_unique ADD COLUMN h_ntacode varchar(4), ADD COLUMN w_ntacode varchar(4);
UPDATE nyc_od_unique o SET h_ntacode = ntacode FROM bg2010_nhood b WHERE left(o.h_geocode, 12) = b.geoid;
UPDATE nyc_od_unique o SET w_ntacode = ntacode FROM bg2010_nhood b WHERE left(o.w_geocode, 12) = b.geoid;
-- recalculate table statistics
VACUUM ANALYZE VERBOSE nyc_od_unique;
```
+ then from the terminal run
`nohup psql -d df_spatial -f od_update_1103.sql > od_update_1103_out.txt &`
+ this notice: `nohup: ignoring input and redirecting stderr to stdout` is due to [not explicitly directing the error to an output](http://unix.stackexchange.com/questions/105840/nohup-ignoring-input-and-redirecting-stderr-to-stdout)

> SIDE NOTE: had a couple typos (table and column name) in the above query that caused it to fail and hang up a bit, here's some useful things to diagnose/clean up that situation:
>> 1. `SELECT * FROM pg_stat_activity WHERE datname = 'df_spatial';` list query processes for this database
>> 2. `SELECT pg_cancel_backend(<pid>) FROM pg_stat_activity WHERE datname = 'df_spatial'` - cancel specific process that doesn't need to run, pulled from [here](http://www.postgresql.org/docs/9.2/static/functions-admin.html)

```SQL
-- now we can more directly calculate some distance metrics by neighborhood --
\copy (SELECT d.h_ntacode, d.w_ntacode, f.year, f.type, sum(f.s000) s000, sum(f.sa01) sa01, sum(f.sa02) sa02, sum(f.sa03) sa03, sum(f.se01) se01, sum(f.se02) se02, sum(f.se03) se03, sum(f.si01) si01, sum(f.si02) si02, sum(f.si03) si03 FROM nyc_od f JOIN nyc_od_unique d ON f.h_geocode = d.h_geocode AND f.w_geocode = d.geocode GROUP BY d.h_ntacode, d.w_ntacode, f.year, f.type ORDER BY f.year, d.h_ntacode, d.w_ntacode, f.type) TO './nyc_nhood_od.csv' CSV HEADER

```

#### (Nov 10) datasets for SOM 
[NYC City Planning LION Street Layer File](http://www.nyc.gov/html/dcp/html/bytes/dwnlion.shtml)
+ Download and unzip File Geodatabase
+ use ogr2ogr to convert to shapefile: `ogr2ogr -f "ESRI Shapefile" ./ ./lion/lion.gdb`
  * get warning of shortened fields (**NEED TO UPDATE IN POSTGIS LATER**): `Normalized/laundered field name:` X
  * Permission denied to add spatial reference [NY_STATE_PLANE](http://spatialreference.org/ref/esri/102718/postgis/), transform (aka reproject) data using geopandas:
```Python
import geopandas as gpd
lion = gpd.read_file('lion.shp') # takes a while since loading a big shapefile
lion.crs # confirm read in correctly
lion.to_crs(epsg=4326, inplace=True)
lion.crs # confirm transformed correctly
lion.to_file('./lion_wgs.shp')
```
+ Try loading to shapefile: `shp2pgsql -s 4326 lion_wgs public.lion_wgs | psql -d df_spatial` (successful)
+ test a few lines with `SELECT gid, ST_AsText(geom) wkt_geom FROM lion_wgs WHERE gid IN (15, 60, 700, 8923, 30928, 201555);` in psql and view [in CartoDB](http://bit.ly/1MVom9s) - these look good
+ do the same steps above for the "node.*" shapefile

#### (Nov 11) SOM continued
Get Deptartment of Finance [RPAD](http://www1.nyc.gov/site/finance/taxes/property-assessments.page) data

From the target location location, run `wget <url>` for the below datasets (all on RPAD page):
1. Tax Class 1
2. Tax Classes 2, 3, and 4
3. Data Dictionary
> NOTE: in MS Access, still need to reformat/extract to make useful.

Add NY State Plane (feet) to PostGIS (updated from [spatialreference.org](http://spatialreference.org/ref/esri/102718/postgis/))
```SQL
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) 
    values ( 102718, 'esri', 102718, '+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs ', 'PROJCS["NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["False_Easting",984249.9999999999],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",-74],PARAMETER["Standard_Parallel_1",40.66666666666666],PARAMETER["Standard_Parallel_2",41.03333333333333],PARAMETER["Latitude_Of_Origin",40.16666666666666],UNIT["Foot_US",0.30480060960121924],AUTHORITY["EPSG","102718"]]');
```

Get [Parks Properties](https://data.cityofnewyork.us/City-Government/Parks-Properties/rjaj-zgq7) data
+ downloaded as shapefile ("export" -> "Shapefile")
+ transfer to cusp server with `scp Parks_Properties.zip crh278@shell.cusp.nyu.edu:/home/cusp/crh278/parks/.`
+ load to postgis with `shp2pgsql -s 102718 DPR_ParksProperties_001 public.dpr_parks | psql -d df_spatial`

Get [Selected Facilities](http://www.nyc.gov/html/dcp/html/bytes/dwnselfac.shtml) data
+ [metadata](http://www.nyc.gov/html/dcp/pdf/bytes/selfac_metadata.pdf?r=1)
+ download with `wget http://www.nyc.gov/html/dcp/download/bytes/nyc_facilities2015_shp.zip`
+ load to postgis with `shp2pgsql -s 102718 Facilities public.facilities | psql -d df_spatial`

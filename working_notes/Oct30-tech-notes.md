### notes for Friday, October 30
* load compiled RAC, WAC, and OD data
  * use each sets' data dictionary to create `CREATE TABLE` query (see [Query_prep_example.ods] (https://github.com/crusselsh/cusp-df-miscfiles/tree/master/data_notes/Query_prep_example.ods))
  * load into df_spatial with `\copy nyc_<dataset> FROM ./<dataset>/nyc_<dataset>.csv CSV HEADER`
* add unique identifier as primary key, and btree search indexes to category variables, then VACUUM ANALYZE table:
```SQL
ALTER TABLE nyc_<dataset> ADD COLUMN uid serial NOT NULL; -- add unique ID
ALTER TABLE nyc_<dataset> ADD PRIMARY KEY (uid); -- set uid as primary key
CREATE INDEX ON nyc_<dataset> (year); -- add btree index for faster searching
CREATE INDEX ON nyc_<dataset> (type);
CREATE INDEX ON nyc_<dataset> (seg);
CREATE INDEX ON nyc_<dataset> (*_geocode); -- index for location columns h_geocode and w_geocode
VACUUM ANALYZE nyc_<dataset>; -- get database caught up with all the data changes

-- in psql above can also be run all at once, as for WAC here:
ALTER TABLE nyc_wac ADD COLUMN uid serial NOT NULL; ALTER TABLE nyc_wac ADD PRIMARY KEY (uid); CREATE INDEX ON nyc_wac (year); CREATE INDEX ON nyc_wac (type); CREATE INDEX ON nyc_wac (seg); VACUUM ANALYZE nyc_wac;
```
* Test data speed - sum some columns, then create neighborhood level summaries of RAC
```SQL
-- test query plan and execution time with summary of NYC primary jobs by year for each of the 3 age buckets
EXPLAIN ANALYZE SELECT year, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03 FROM nyc_rac r GROUP BY year ORDER BY year;
-- output:
                                                       QUERY PLAN                                                              
--------------------------------------------------------------------------------------------------------------------------------------
 Sort  (cost=751468.17..751468.20 rows=12 width=20) (actual time=31855.030..31855.031 rows=12 loops=1)
   Sort Key: year
   Sort Method: quicksort  Memory: 25kB
   ->  HashAggregate  (cost=751467.83..751467.95 rows=12 width=20) (actual time=31854.975..31854.990 rows=12 loops=1)
         ->  Seq Scan on nyc_rac r  (cost=0.00..568811.26 rows=14612526 width=20) (actual time=0.104..7852.398 rows=14612332 loops=1)
 Total runtime: 31855.302 ms
(6 rows)

-- view results
SELECT year, r.type, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03 FROM nyc_rac r GROUP BY year ORDER BY type, year;
 year |   c000   |   ca01   |   ca02   |  ca03   
------+----------+----------+----------+---------
 2002 | 41229416 | 11161352 | 24023804 | 6044260
 2003 | 40868916 | 10762368 | 23912516 | 6194032
 2004 | 40764300 | 10929340 | 23472980 | 6361980
 2005 | 41457300 | 11233672 | 23553992 | 6669636
 2006 | 42368032 | 11654908 | 23791392 | 6921732
 2007 | 42617200 | 11697632 | 23772740 | 7146828
 2008 | 43641784 | 12170824 | 24132308 | 7338652
 2009 | 44389572 | 11414216 | 25405360 | 7569996
 2010 | 45427328 | 11345008 | 25945264 | 8137056
 2011 | 46446320 | 11517372 | 26314936 | 8614012
 2012 | 46645956 | 11125488 | 26453336 | 9067132
 2013 | 47574964 | 11253416 | 26854944 | 9466604

-- difference when also by private/federall primary jobs
EXPLAIN ANALYZE SELECT year, r.type, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03 FROM nyc_rac r WHERE r.type IN ('JT03', 'JT05') GROUP BY year, type ORDER BY type, year;
                                                           QUERY PLAN                                                   
                                                                                 
-------------------------------------------------------------------------------------------------------------------------------------
----------------------
 Sort  (cost=598743.19..598743.24 rows=19 width=25) (actual time=19058.673..19058.675 rows=16 loops=1)
   Sort Key: type, year
   Sort Method: quicksort  Memory: 26kB
   ->  HashAggregate  (cost=598742.60..598742.79 rows=19 width=25) (actual time=19058.545..19058.566 rows=16 loops=1)
         ->  Bitmap Heap Scan on nyc_rac r  (cost=70478.65..541154.63 rows=3839198 width=25) (actual time=1323.597..13029.349 rows=37
44503 loops=1)
               Recheck Cond: ((type)::text = ANY ('{JT03,JT05}'::text[]))
               Rows Removed by Index Recheck: 5679
               ->  Bitmap Index Scan on nyc_rac_type_idx  (cost=0.00..69518.85 rows=3839198 width=0) (actual time=1318.609..1318.609 
rows=3744503 loops=1)
                     Index Cond: ((type)::text = ANY ('{JT03,JT05}'::text[]))
 Total runtime: 19058.981 ms

-- also view this data
SELECT year, r.type, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03 FROM nyc_rac r WHERE r.type IN ('JT03', 'JT05') GROUP BY year, type ORDER BY type, year;
 year | type |   c000   |  ca01   |  ca02   |  ca03   
------+------+----------+---------+---------+---------
 2002 | JT03 |  9322536 | 2601388 | 5398440 | 1322708
 2003 | JT03 |  9213384 | 2513360 | 5336952 | 1363072
 2004 | JT03 |  9262864 | 2536792 | 5315072 | 1411000
 2005 | JT03 |  9404112 | 2615444 | 5328124 | 1460544
 2006 | JT03 |  9601476 | 2705964 | 5370928 | 1524584
 2007 | JT03 |  9577416 | 2711380 | 5308504 | 1557532
 2008 | JT03 |  9979112 | 2822064 | 5506972 | 1650076
 2009 | JT03 |  9887652 | 2645928 | 5599980 | 1641744
 2010 | JT03 |  9974276 | 2613288 | 5633028 | 1727960
 2011 | JT03 | 10244888 | 2663252 | 5740328 | 1841308
 2012 | JT03 | 10302112 | 2577608 | 5785368 | 1939136
 2013 | JT03 | 10596016 | 2613788 | 5929340 | 2052888
 2010 | JT05 |    77144 |   12416 |   45772 |   18956
 2011 | JT05 |    79936 |   12680 |   47356 |   19900
 2012 | JT05 |    75912 |   10764 |   45136 |   20012
 2013 | JT05 |    76292 |   11024 |   45396 |   19872


-- create neighborhood level summary of full table
SELECT n.ntacode, n.ntaname, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03, sum(r.ce01) ce01, sum(r.ce02) ce02, sum(r.ce03) ce03, sum(r.cns01) cns01, sum(r.cns02) cns02, sum(r.cns03) cns03, sum(r.cns04) cns04, sum(r.cns05) cns05, sum(r.cns06) cns06, sum(r.cns07) cns07, sum(r.cns08) cns08, sum(r.cns09) cns09, sum(r.cns10) cns10, sum(r.cns11) cns11, sum(r.cns12) cns12, sum(r.cns13) cns13, sum(r.cns14) cns14, sum(r.cns15) cns15, sum(r.cns16) cns16, sum(r.cns17) cns17, sum(r.cns18) cns18, sum(r.cns19) cns19, sum(r.cns20) cns20, sum(r.cr01) cr01, sum(r.cr02) cr02, sum(r.cr03) cr03, sum(r.cr04) cr04, sum(r.cr05) cr05, sum(r.cr07) cr07, sum(r.ct01) ct01, sum(r.ct02) ct02, sum(r.cd01) cd01, sum(r.cd02) cd02, sum(r.cd03) cd03, sum(r.cd04) cd04, sum(r.cs01) cs01, sum(r.cs02) cs02, r.year, r.type, r.seg
INTO nyc_nhood_rac
FROM nyc_rac r JOIN bg2010_nhood n ON left(r.h_geocode, 12) = n.geoid -- join on blockgroup FIPS
GROUP BY r.year, r.type, r.seg, n.ntacode, n.ntaname
ORDER BY r.year, n.ntacode;

-- check how query plan and long it took to run
EXPLAIN ANALYZE SELECT n.ntacode, n.ntaname, sum(r.c000) c000, sum(r.ca01) ca01, sum(r.ca02) ca02, sum(r.ca03) ca03, sum(r.ce01) ce01, sum(r.ce02) ce02, sum(r.ce03) ce03, sum(r.cns01) cns01, sum(r.cns02) cns02, sum(r.cns03) cns03, sum(r.cns04) cns04, sum(r.cns05) cns05, sum(r.cns06) cns06, sum(r.cns07) cns07, sum(r.cns08) cns08, sum(r.cns09) cns09, sum(r.cns10) cns10, sum(r.cns11) cns11, sum(r.cns12) cns12, sum(r.cns13) cns13, sum(r.cns14) cns14, sum(r.cns15) cns15, sum(r.cns16) cns16, sum(r.cns17) cns17, sum(r.cns18) cns18, sum(r.cns19) cns19, sum(r.cns20) cns20, sum(r.cr01) cr01, sum(r.cr02) cr02, sum(r.cr03) cr03, sum(r.cr04) cr04, sum(r.cr05) cr05, sum(r.cr07) cr07, sum(r.ct01) ct01, sum(r.ct02) ct02, sum(r.cd01) cd01, sum(r.cd02) cd02, sum(r.cd03) cd03, sum(r.cd04) cd04, sum(r.cs01) cs01, sum(r.cs02) cs02, r.year, r.type, r.seg
FROM nyc_rac r JOIN bg2010_nhood n ON left(r.h_geocode, 12) = n.geoid -- join on blockgroup FIPS
GROUP BY r.year, r.type, r.seg, n.ntacode, n.ntaname
ORDER BY r.year, n.ntacode;
-- output (14.05 minutes to complete):
                                                  QUERY PLAN                                                                  
----------------------------------------------------------------------------------------------------------------------------------------------
 GroupAggregate  (cost=8952966.27..10674470.47 rows=453240 width=174) (actual time=630143.009..842880.280 rows=105824 loops=1)
   ->  Sort  (cost=8952966.27..8989497.58 rows=14612526 width=174) (actual time=630142.012..714846.701 rows=14563744 loops=1)
         Sort Key: r.year, n.ntacode, r.type, r.seg, n.ntaname
         Sort Method: external merge  Disk: 2966144kB
         ->  Hash Join  (cost=208.64..970864.36 rows=14612526 width=174) (actual time=5.881..52349.951 rows=14563744 loops=1)
               Hash Cond: ("left"((r.h_geocode)::text, 12) = (n.geoid)::text)
               ->  Seq Scan on nyc_rac r  (cost=0.00..568811.26 rows=14612526 width=166) (actual time=0.161..17956.973 rows=14612332 loops=1)
               ->  Hash  (cost=129.95..129.95 rows=6295 width=37) (actual time=5.610..5.610 rows=6295 loops=1)
                     Buckets: 1024  Batches: 1  Memory Usage: 429kB
                     ->  Seq Scan on bg2010_nhood n  (cost=0.00..129.95 rows=6295 width=37) (actual time=0.014..2.397 rows=6295 loops=1)
 Total runtime: 842961.036 ms
(11 rows)

```


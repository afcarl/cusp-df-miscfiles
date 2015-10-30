### notes for Friday, October 30
1. load compiled RAC, WAC, and OD data
  * use each sets' data dictionary to create `CREATE TABLE` query (see [Query_prep_example.ods] (https://github.com/crusselsh/cusp-df-miscfiles/tree/master/data_notes/Query_prep_example.ods))
  * load into df_spatial with `psql df_spatial` then `\copy nyc_<dataset> FROM ./<dataset>/nyc_<dataset>.csv CSV HEADER`
2. add unique identifier as primary key, and btree search indexes to category variables, then VACUUM ANALYZE table:
``` SQL
ALTER TABLE nyc_<dataset> ADD COLUMN uid serial NOT NULL; -- add unique ID
ALTER TABLE nyc_<dataset> ADD PRIMARY KEY (uid); -- set uid as primary key
CREATE INDEX ON nyc_<dataset> (year); -- add btree index for faster searching
CREATE INDEX ON nyc_<dataset> (type);
CREATE INDEX ON nyc_<dataset> (seg);
VACUUM ANALYZE nyc_<dataset>
```
3. Test data speed - create neighborhood level summaries of RAC

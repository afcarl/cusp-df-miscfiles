-- create table for compiled LEHD RAC data
CREATE TABLE nyc_rac (h_geocode Varchar(15), c000 numeric, ca01 numeric, ca02 numeric, ca03 numeric, ce01 numeric, ce02 numeric, ce03 numeric, cns01 numeric, cns02 numeric, cns03 numeric, cns04 numeric, cns05 numeric, cns06 numeric, cns07 numeric, cns08 numeric, cns09 numeric, cns10 numeric, cns11 numeric, cns12 numeric, cns13 numeric, cns14 numeric, cns15 numeric, cns16 numeric, cns17 numeric, cns18 numeric, cns19 numeric, cns20 numeric, cr01 numeric, cr02 numeric, cr03 numeric, cr04 numeric, cr05 numeric, cr07 numeric, ct01 numeric, ct02 numeric, cd01 numeric, cd02 numeric, cd03 numeric, cd04 numeric, cs01 numeric, cs02 numeric, createdate Varchar(8), year Int, type Varchar(4), seg Varchar(4));

-- WAC 
CREATE TABLE nyc_wac (w_geocode Varchar(15), c000 numeric, ca01 numeric, ca02 numeric, ca03 numeric, ce01 numeric, ce02 numeric, ce03 numeric, cns01 numeric, cns02 numeric, cns03 numeric, cns04 numeric, cns05 numeric, cns06 numeric, cns07 numeric, cns08 numeric, cns09 numeric, cns10 numeric, cns11 numeric, cns12 numeric, cns13 numeric, cns14 numeric, cns15 numeric, cns16 numeric, cns17 numeric, cns18 numeric, cns19 numeric, cns20 numeric, cr01 numeric, cr02 numeric, cr03 numeric, cr04 numeric, cr05 numeric, cr07 numeric, ct01 numeric, ct02 numeric, cd01 numeric, cd02 numeric, cd03 numeric, cd04 numeric, cs01 numeric, cs02 numeric, cfa01 numeric, cfa02 numeric, cfa03 numeric, cfa04 numeric, cfa05 numeric, cfs01 numeric, cfs02 numeric, cfs03 numeric, cfs04 numeric, cfs05 numeric, createdate Varchar(8), year numeric, type Varchar(4), seg Varchar(4));

-- OD
CREATE TABLE nyc_od (w_geocode Varchar(15), h_geocode Varchar(15), s000 numeric, sa01 numeric, sa02 numeric, sa03 numeric, se01 numeric, se02 numeric, se03 numeric, si01 numeric, si02 numeric, si03 numeric, createdate Varchar(8), year Int, type Varchar(4));


-- summarize WAC by nhood
SELECT n.ntacode, n.ntaname, sum(w.c000) c000, sum(w.ca01) ca01, sum(w.ca02) ca02, sum(w.ca03) ca03, sum(w.ce01) ce01, sum(w.ce02) ce02, sum(w.ce03) ce03, sum(w.cns01) cns01, sum(w.cns02) cns02, sum(w.cns03) cns03, sum(w.cns04) cns04, sum(w.cns05) cns05, sum(w.cns06) cns06, sum(w.cns07) cns07, sum(w.cns08) cns08, sum(w.cns09) cns09, sum(w.cns10) cns10, sum(w.cns11) cns11, sum(w.cns12) cns12, sum(w.cns13) cns13, sum(w.cns14) cns14, sum(w.cns15) cns15, sum(w.cns16) cns16, sum(w.cns17) cns17, sum(w.cns18) cns18, sum(w.cns19) cns19, sum(w.cns20) cns20, sum(w.cr01) cr01, sum(w.cr02) cr02, sum(w.cr03) cr03, sum(w.cr04) cr04, sum(w.cr05) cr05, sum(w.cr07) cr07, sum(w.ct01) ct01, sum(w.ct02) ct02, sum(w.cd01) cd01, sum(w.cd02) cd02, sum(w.cd03) cd03, sum(w.cd04) cd04, sum(w.cs01) cs01, sum(w.cs02) cs02, sum(w.cfa01) cfa01, sum(w.cfa02) cfa02, sum(w.cfa03) cfa03, sum(w.cfa04) cfa04, sum(w.cfa05) cfa05, sum(w.cfs01) cfs01, sum(w.cfs02) cfs02, sum(w.cfs03) cfs03, sum(w.cfs04) cfs04, sum(w.cfs05) cfs05
FROM nyc_wac w JOIN bg2010_nhood n ON left(w.w_geocode, 12) = n.geoid
GROUP BY w.year, w.type, w.seg, n.ntacode, n.ntaname
ORDER BY w.year, w.ntacode;

-- summarzie OD distances by nhood
SELECT 

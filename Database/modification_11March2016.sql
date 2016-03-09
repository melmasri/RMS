--------------------------------------------------
--- load Prod_2016March09.db from dropbox

-- show values of current settings
.show
-- Setting certain variables.
.headers on
-- Turn command echo on or off
.echo on
-- Enable or disable automatic EXPLAIN QUERY PLAN
.eqp on
-- Stop after hitting an error.  Default OFF
--.bail on
-- Turning loggin on
.log log_sqlite.log

.tables


--- Empty indicator tables
delete from edu_indicator_aid;
delete from edu_indicator_est;
delete from indicator_audit_trail;

-- inserting EDU_INDICATOR_AID
-- cvs mode to set the separators before inserting data
.mode csv                       
.import "Inserted data/EDU_INDICATOR_AID.csv" EDU_INDICATOR_AID
--removing the headers (a bit of a hack but sqlite has no direct way)
delete FROM EDU_INDICATOR_AID WHERE IND_ID = 'IND_ID';


-- change RM_Mapping
delete from RM_Mapping;
delete from EDU_METER_AID;

-- Adding regular EDU_METER_AID
.mode csv                       
.import "Inserted data/EDU_METER_AID(data).csv" EDU_METER_AID
delete FROM EDU_METER_AID WHERE EMC_ID = 'EMC_ID';
-- Adding new labels to EDU_METER_AID
.import "Inserted data/NEW AC CODES inserted in EDU_METER_AID.csv" EDU_METER_AID
delete FROM EDU_METER_AID WHERE EMC_ID = 'EMC_ID';


DROP TABLE IF EXISTS RM_TEMP;
-- Creating table
CREATE TABLE RM_TEMP(
	Tab nvarchar(50)  NOT NULL, -- Sheet name in the questionnaire.
	RM_TABLE  nvarchar(50) NOT NULL, -- Table name and number in the Questionniare
    RM_TABLE_NAME  nvarchar(250) NOT NULL, -- Table FULL NAME
	Col int(10) ,                    -- Col number.
    AC varchar(100),            -- Alphanumeric codeing scheme.
    EXL_REF varchar(10),
    CUR_YEAR int(2));        -- EXCEL cell address. Firtst cell in the column.

-- Importing data
.mode csv
.import "Inserted data/RM_Mapping.csv" RM_TEMP
--removing the headers
DELETE FROM RM_TEMP WHERE Tab= 'Tab';

-- Extracting EMC_IDs and Inserting the mapping and EMC_IDs to RM_Mapping table
INSERT INTO RM_Mapping 
       select EDU_METER_AID.EMC_ID, RM_Temp.* from RM_Temp 
       left join  EDU_METER_AID on EDU_METER_AID.AC = RM_Temp.AC;
-- Dropping unwanted tables
DROP TABLE IF EXISTS RM_TEMP;



DROP TABLE IF EXISTS RM_TEMP;
-- Creating table
CREATE TABLE RM_TEMP(
    co_code int(10) not null,
    old_year int(10) not null,
    new_year int(10) not null,
    old_mc_id int (10) not null,
    new_mc_id int (10) not null);

.mode csv
.import "Inserted data/rm_mapping_new_old.csv" RM_TEMP
--removing the headers
DELETE FROM RM_TEMP WHERE co_code = 'co_code';


-- Temp table for meter data
CREATE TABLE EDU_METER_TEMP(
	EMC_ID int(10) NOT NULL,
	CO_CODE int(10) NOT NULL,
    ADM_CODE int(10) NOT NULL, 
	EMCO_YEAR int(4) NOT NULL,
	EAG_AGE int(3) ,    -- not sure what is this : in our case NULL.
	ST_ID int(5) ,      -- SOURCE_TITLE : exported: in our case 1.
	ABE_ID char(1) ,    -- EC_AB_EXPENDITURE: A - Actual : B - Budget: in our case NULL.
	MQ_ID char(1) ,     -- EDU_QUAL: already have the create script.
	MG_ID char(1) ,     -- MAGNITUDE: already have the create script.
	EM_FIG float ,
	EC_TD_ID decimal(3, 0) NOT NULL, -- EC_TYPE_DATA: exported.
	NOTEYESNO char(1) ,              -- in out case NULL.
PRIMARY KEY (EMC_ID ASC,CO_CODE ASC,ADM_CODE ASC, EMCO_YEAR ASC));

-- storing similar data
-- EDU_METER97_REP
insert into EDU_METER_TEMP
select b.new_mc_id as EMC_ID, a.co_code, a.adm_code, b.new_year as EMCO_YEAR, a.EAG_AGE, a.ST_ID, a.ABE_ID, a.MQ_ID, a.MG_ID, a.EM_FIG, a.EC_TD_ID, a.NOTEYESNO from edu_meter97_rep as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;
--deleting it from original table
DELETE from EDU_METER97_REP
where exists(select * from RM_TEMP as b 
      where b.co_code = EDU_METER97_REP.co_code and
            b.old_mc_id = EDU_METER97_REP.emc_id and
            b.old_year = EDU_METER97_REP.emco_year);
-- insertingn new data
insert into EDU_METER97_REP
select * from EDU_METER_TEMP;
-- emptying temp table
delete from EDU_METER_TEMP;


-- EDU_METER97_OBS
-- storing similar data
insert into EDU_METER_TEMP
select b.new_mc_id as EMC_ID, a.co_code, a.adm_code, b.new_year as EMCO_YEAR, a.EAG_AGE, a.ST_ID, a.ABE_ID, a.MQ_ID, a.MG_ID, a.EM_FIG, a.EC_TD_ID, a.NOTEYESNO from edu_meter97_obs as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;
--deleting it from original table
DELETE from EDU_METER97_OBS
where exists(select * from RM_TEMP as b 
      where b.co_code = EDU_METER97_OBS.co_code and
            b.old_mc_id = EDU_METER97_OBS.emc_id and
            b.old_year = EDU_METER97_OBS.emco_year);
-- insertingn new data
insert into EDU_METER97_OBS
select * from EDU_METER_TEMP;
-- emptying temp table
delete from EDU_METER_TEMP;


-- EDU_METER97_EST
-- storing similar data
insert into EDU_METER_TEMP
select b.new_mc_id as EMC_ID, a.co_code, a.adm_code, b.new_year as EMCO_YEAR, a.EAG_AGE, a.ST_ID, a.ABE_ID, a.MQ_ID, a.MG_ID, a.EM_FIG, a.EC_TD_ID, a.NOTEYESNO from edu_meter97_est as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;
--deleting it from original table
DELETE from EDU_METER97_EST
where exists(select * from RM_TEMP as b 
      where b.co_code = EDU_METER97_EST.co_code and
            b.old_mc_id = EDU_METER97_EST.emc_id and
            b.old_year = EDU_METER97_EST.emco_year);
-- insertingn new data
insert into EDU_METER97_EST
select * from EDU_METER_TEMP;
-- emptying temp table
delete from EDU_METER_TEMP;

DROP TABLE IF EXISTS EDU_METER_TEMP;


--- FTN
CREATE TABLE EDU_FTN_TEMP(
	CO_CODE int  NOT NULL,
    ADM_CODE int NOT NULL,
	EMCO_YEAR int NOT NULL,
	EMC_ID int   NOT NULL,
	FTN_CODE int  NOT NULL,
	FTN_DATA varchar(1500),
	NTABLE decimal(2, 0) NOT NULL, -- Table numbe is 1.1, 1.2, ...
	QUESTNAME char(1) NOT NULL,
	USERNAME varchar(255),
	DATE_ADDED DATETIME DEFAULT (datetime('now','localtime')),
PRIMARY KEY (CO_CODE ASC, ADM_CODE ASC,  EMCO_YEAR ASC, EMC_ID ASC ));


-- storing similar data
-- EDU_FTN97_REP
insert into EDU_FTN_TEMP
select a.co_code, a.adm_code, b.new_year as EMCO_YEAR,  b.new_mc_id as EMC_ID, a.FTN_CODE,a.FTN_DATA, a.NTABLE, a.QUESTNAME, a.USERNAME, a.DATE_ADDED from edu_ftn97_rep as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;
--- EMPTY

delete from EDU_FTN_TEMP;

-- storing similar data
-- EDU_FTN97_OBS
insert into EDU_FTN_TEMP
select a.co_code, a.adm_code, b.new_year as EMCO_YEAR,  b.new_mc_id as EMC_ID, a.FTN_CODE,a.FTN_DATA, a.NTABLE, a.QUESTNAME, a.USERNAME, a.DATE_ADDED from edu_ftn97_obs as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;
--- EMPTY

delete from EDU_FTN_TEMP;

-- storing similar data
-- EDU_FTN97_EST
insert into EDU_FTN_TEMP
select a.co_code, a.adm_code, b.new_year as EMCO_YEAR,  b.new_mc_id as EMC_ID, a.FTN_CODE,a.FTN_DATA, a.NTABLE, a.QUESTNAME, a.USERNAME, a.DATE_ADDED from edu_ftn97_est as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;
--- EMPTY
select distinct co_code, emco_year from EDU_FTN97_EST;

delete from EDU_FTN_TEMP;
drop table EDU_FTN_TEMP;

--- Inclusions
CREATE TABLE EDU_INCLUSION_TEMP(
       CO_CODE decimal(6, 0) NOT NULL,
       EMCO_YEAR decimal(4, 0) NOT NULL,
       ADM_CODE INT NOT NULL,
       EMC_ID decimal(6, 0) NOT NULL,
       DESC_INCLU varchar(32),  -- Where the inlcusion code XC and XR exist.
       EC_TD_ID decimal(3, 0) NOT NULL,
PRIMARY KEY ( CO_CODE ASC,  EMCO_YEAR ASC,    EMC_ID ASC, ADM_CODE ASC));



-- storing similar data
-- EDU_INCLUSION_REP
insert into EDU_INCLUSION_TEMP
select a.co_code, b.new_year as EMCO_YEAR,a.adm_code, b.new_mc_id as EMC_ID, a.DESC_INCLU, a.EC_TD_ID from edu_inclusion_rep as a
inner join RM_TEMP as b on a.co_code = b.co_code and b.old_year = a.emco_year and b.old_mc_id = a.EMC_ID;

--empty
-- for OBS and EST as well.

delete from EDU_INCLUSION_TEMP;
drop table EDU_INCLUSION_TEMP;

select distinct co_code, emco_year from edu_inclusion_obs;

select distinct co_code, emco_year from edu_inclusion_rep;

select distinct co_code, emco_year from edu_inclusion_est;

select * from EDU_INCLUSION_OBS;


-- Audit Trail
select count(*) from METER_AUDIT_TRAIL as a
inner join RM_TEMP as b on a.co_code = b.co_code and a.MC_YEAR = b.old_year and a.MC_ID = b.old_mc_id;



--select distinct co_code, mc_year from meter_audit_trail;

--- Output regoins
.mode csv
.once regions.csv
select * from regions where adm_code >0 order by co_code;

-- REGIONS TABLE
-- Deleting table
DROP TABLE IF EXISTS REGIONS;
-- Creating table
CREATE TABLE REGIONS(
	CO_CODE INT NOT NULL CHECK (CO_CODE>= 0),
	ADM_CODE INT NOT NULL,
    ADM_NAME TEXT NOT NULL,
    MC_YEAR INT NOT NULL, 
PRIMARY KEY (CO_CODE ASC,ADM_CODE ASC, MC_YEAR));


--inserting REGIONS
--cvs mode to set the separators before inserting data
.mode csv
.import "Inserted data/regions.csv" REGIONS

--removing the headers ( a bit of a hack but sqlite has no direct way)
delete FROM REGIONS WHERE CO_CODE = 'CO_CODE';

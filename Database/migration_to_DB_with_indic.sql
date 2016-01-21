-- This script creates all the needed tables in create_tables.sql
-- Also it inserts all the data from insert_data.sql
--------------------------------------------------
--------------------------------------------------

-- Settings
--------------------------------------------------
-- show values of current settings
.show
-- Setting certain variables.
.headers on
-- Turn command echo on or off
.echo on
-- Enable or disable automatic EXPLAIN QUERY PLAN
.eqp on
-- Stop after hitting an error.  Default OFF
.bail on
-- Turning loggin on
.log migrate.log

--- Modfying FTN table for date
--------------------------------------------------
--------------------------------------------------
--------------------------------------------------
DROP TABLE IF EXISTS EDU_FTN97_OBS_temp;
---- Creating table
CREATE TABLE EDU_FTN97_OBS_temp(
	CO_CODE int  NOT NULL,
    ADM_CODE int NOT NULL,
	EMCO_YEAR int NOT NULL,
	EMC_ID int   NOT NULL,
	FTN_CODE int  NOT NULL,
	FTN_DATA varchar(1500),
	NTABLE decimal(2, 0) NOT NULL, -- Table numbe is 1.1, 1.2, ...
	QUESTNAME char(1) NOT NULL,
	USERNAME varchar(255),
	DATE_ADDED datetime DEFAULT (datetime('now','localtime')),
PRIMARY KEY (CO_CODE ASC, ADM_CODE ASC,  EMCO_YEAR ASC, EMC_ID ASC ));



---- EDU_FTN_ASSO97_EST TABLE
---- Deleting table
DROP TABLE IF EXISTS EDU_FTN97_EST_temp;
---- Creating table
CREATE TABLE EDU_FTN97_EST_temp(
	CO_CODE int  NOT NULL,
    ADM_CODE int NOT NULL,
	EMCO_YEAR int NOT NULL,
	EMC_ID int   NOT NULL,
	FTN_CODE int  NOT NULL,
	FTN_DATA varchar(1500),
	NTABLE decimal(2, 0) NOT NULL, -- Table numbe is 1.1, 1.2, ...
	QUESTNAME char(1) NOT NULL,
	USERNAME varchar(255),
	DATE_ADDED datetime DEFAULT (datetime('now','localtime')),
PRIMARY KEY (CO_CODE ASC, ADM_CODE ASC,  EMCO_YEAR ASC, EMC_ID ASC ));

---- EDU_FTN_ASSO97_REP TABLE
---- Deleting table
DROP TABLE IF EXISTS EDU_FTN97_REP_temp;
---- Creating table
CREATE TABLE EDU_FTN97_REP_temp(
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


INSERT INTO EDU_FTN97_REP_temp SELECT * from EDU_FTN97_REP;
INSERT INTO EDU_FTN97_OBS_temp SELECT * from EDU_FTN97_OBS;
INSERT INTO EDU_FTN97_EST_temp SELECT * from EDU_FTN97_EST; 


DROP TABLE IF EXISTS EDU_FTN97_OBS;
---- Creating table
CREATE TABLE EDU_FTN97_OBS(
	CO_CODE int  NOT NULL,
    ADM_CODE int NOT NULL,
	EMCO_YEAR int NOT NULL,
	EMC_ID int   NOT NULL,
	FTN_CODE int  NOT NULL,
	FTN_DATA varchar(1500),
	NTABLE decimal(2, 0) NOT NULL, -- Table numbe is 1.1, 1.2, ...
	QUESTNAME char(1) NOT NULL,
	USERNAME varchar(255),
	DATE_ADDED datetime DEFAULT (datetime('now','localtime')),
PRIMARY KEY (CO_CODE ASC, ADM_CODE ASC,  EMCO_YEAR ASC, EMC_ID ASC ));

---- EDU_FTN_ASSO97_EST TABLE
---- Deleting table
DROP TABLE IF EXISTS EDU_FTN97_EST;
---- Creating table
CREATE TABLE EDU_FTN97_EST(
	CO_CODE int  NOT NULL,
    ADM_CODE int NOT NULL,
	EMCO_YEAR int NOT NULL,
	EMC_ID int   NOT NULL,
	FTN_CODE int  NOT NULL,
	FTN_DATA varchar(1500),
	NTABLE decimal(2, 0) NOT NULL, -- Table numbe is 1.1, 1.2, ...
	QUESTNAME char(1) NOT NULL,
	USERNAME varchar(255),
	DATE_ADDED datetime DEFAULT (datetime('now','localtime')),
PRIMARY KEY (CO_CODE ASC, ADM_CODE ASC,  EMCO_YEAR ASC, EMC_ID ASC ));

---- EDU_FTN_ASSO97_REP TABLE
---- Deleting table
DROP TABLE IF EXISTS EDU_FTN97_REP;
---- Creating table
CREATE TABLE EDU_FTN97_REP(
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



INSERT INTO EDU_FTN97_REP SELECT * from EDU_FTN97_REP_temp;
INSERT INTO EDU_FTN97_OBS SELECT * from EDU_FTN97_OBS_temp;     
INSERT INTO EDU_FTN97_EST SELECT * from EDU_FTN97_EST_temp;


DROP TABLE IF EXISTS EDU_FTN97_REP_temp;
DROP TABLE IF EXISTS EDU_FTN97_OBS_temp;
DROP TABLE IF EXISTS EDU_FTN97_EST_temp;


--------------------------------------------------
--------------------------------------------------
--------------------------------------------------

----------- Audit trial tables
--  METER_AUDIT_TRAIL TABLE
DROP TABLE IF EXISTS METER_AUDIT_TRAIL_T;
-- Creating table
CREATE TABLE METER_AUDIT_TRAIL_T(
	Audit_ID Integer , -- Based on ROWID definition in SQLite, this should do the same job as autoincrement
	MC_ID decimal(6, 0) NOT NULL,
    CO_CODE decimal(6, 0) NOT NULL,
    ADM_CODE INT NOT NULL, -- Administrative Division code.
	MC_YEAR decimal(4, 0) NOT NULL,
	EM_FIG_NEW varchar(4000) NULL,
	EM_FIG_OLD varchar(4000) NULL,
	MQ_ID_NEW char(1) NULL,
	MQ_ID_OLD char(1) NULL,
	MG_ID_NEW char(1) NULL,
	MG_ID_OLD char(1) NULL,
	TYPE_MOD char(1) NULL, --- I don't know what is this
	USER_NAME varchar(20) NOT NULL,
	SYS_DATE datetime DEFAULT (datetime('now','localtime')),
	SERIES varchar(10) NOT NULL,
	SURVEY_ID char(2) NULL, --- Regional model default is set to 'RM'
    PRIMARY KEY (Audit_ID ASC));



INSERT INTO METER_AUDIT_TRAIL_T SELECT * from METER_AUDIT_TRAIL;


DROP TABLE IF EXISTS METER_AUDIT_TRAIL;
-- Creating table
CREATE TABLE METER_AUDIT_TRAIL(
	Audit_ID Integer , -- Based on ROWID definition in SQLite, this should do the same job as autoincrement
	MC_ID decimal(6, 0) NOT NULL,
    CO_CODE decimal(6, 0) NOT NULL,
    ADM_CODE INT NOT NULL, -- Administrative Division code.
	MC_YEAR decimal(4, 0) NOT NULL,
	EM_FIG_NEW varchar(4000) NULL,
	EM_FIG_OLD varchar(4000) NULL,
	MQ_ID_NEW char(1) NULL,
	MQ_ID_OLD char(1) NULL,
	MG_ID_NEW char(1) NULL,
	MG_ID_OLD char(1) NULL,
	TYPE_MOD char(1) NULL, --- I don't know what is this
	USER_NAME varchar(20) NOT NULL,
	SYS_DATE datetime DEFAULT (datetime('now','localtime')),
	SERIES varchar(10) NOT NULL,
	SURVEY_ID char(2) NULL, --- Regional model default is set to 'RM'
    PRIMARY KEY (Audit_ID ASC));




INSERT INTO METER_AUDIT_TRAIL SELECT * from METER_AUDIT_TRAIL_T;



DROP TABLE IF EXISTS METER_AUDIT_TRAIL_T;


--------------------------------------------------
--------------------------------------------------
--------------------------------------------------

----------- Indicator table
--  EDU_INDICATOR_EST
DROP TABLE IF EXISTS EDU_INDICATOR_EST;
-- Creating table
CREATE TABLE EDU_INDICATOR_EST(
       IND_ID varchar(50) NOT NULL,
       CO_CODE int NOT NULL,
       ADM_CODE INT NOT NULL, -- Administrative Division code.
       IND_YEAR smallint NOT NULL,
       FRM_ID smallint NOT NULL,
       FIG float NULL,
       QUAL smallint NULL,
       MAGN smallint NULL,
       CALC_DATE datetime DEFAULT (datetime('now','localtime')),
       PRIMARY KEY ( IND_ID ASC,  CO_CODE ASC, ADM_CODE ASC , IND_YEAR ASC,   FRM_ID ASC));
       
--  EDU_INDICATOR_AID
DROP TABLE IF EXISTS EDU_INDICATOR_AID;
-- Creating table
CREATE TABLE EDU_INDICATOR_AID(
       IND_ID varchar(50) NOT NULL,
       LABEL_ENG  varchar(2048),
       PRIMARY KEY ( IND_ID ASC));

----------- Audit trial tables
--  METER_AUDIT_TRAIL TABLE
DROP TABLE IF EXISTS INDICATOR_AUDIT_TRAIL;
-- Creating table
CREATE TABLE INDICATOR_AUDIT_TRAIL(
	Audit_ID Integer , -- Based on ROWID definition in SQLite, this should do the same job as autoincrement
	IND_ID varchar(50) NOT NULL,
    CO_CODE decimal(6, 0) NOT NULL,
    ADM_CODE INT NOT NULL, -- Administrative Division code.
	IND_YEAR decimal(4, 0) NOT NULL,
	FIG_NEW varchar(4000) NULL,
	FIG_OLD varchar(4000) NULL,
	QUAL_NEW char(1) NULL,
	QUAL_OLD char(1) NULL,
	MAGN_NEW char(1) NULL,
	MAGN_OLD char(1) NULL,
	USER_NAME varchar(20) NOT NULL,
	SYS_DATE datetime DEFAULT (datetime('now','localtime')),
	SERIES varchar(10) NOT NULL,
    PRIMARY KEY (Audit_ID ASC));


-- inserting EDU_INDICATOR_AID
-- cvs mode to set the separators before inserting data
.mode csv                       
.import "Inserted data/EDU_INDICATOR_AID.csv" EDU_INDICATOR_AID

--removing the headers (a bit of a hack but sqlite has no direct way)
delete FROM EDU_INDICATOR_AID WHERE IND_ID = 'IND_ID';


-- Logging off
--------------------------------------------------
-- Turn logging off
.log off

-- Exist this program
.quit

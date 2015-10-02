-- Turning loggin on
-- .log insert_data.log

-- inserting data

-- inserting EDU_QUAL
-- cvs mode to set the separators before inserting data
                  
.mode csv
.import "Inserted data/Qualifier.csv" EDU_QUAL

--removing the headers ( a bit of a hack but sqlite has no direct way)
DELETE FROM EDU_QUAL WHERE MQ_ID = 'MQ_ID';


--column mode to view the data better.
-- .mode column                    
-- select * from EDU_QUAL;

-- inserting COUNTRY
-- cvs mode to set the separators before inserting data
.mode csv                       
.import "Inserted data/Country.csv" COUNTRY

--removing the headers ( a bit of a hack but sqlite has no direct way)
DELETE FROM COUNTRY WHERE CO_CODE = 'CO_CODE';

--column mode to view the data better.
-- .mode column                    
-- select * from COUNTRY limit 2

-- DELETE from COUNTRY


-- inserting MAGNITUDE
-- cvs mode to set the separators before inserting data
.mode csv                       
.import "Inserted data/Magnitude(data).csv" MAGNITUDE

--removing the headers ( a bit of a hack but sqlite has no direct way)
delete FROM MAGNITUDE WHERE MG_ID = 'MG_ID';

--column mode to view the data better.
-- .mode column                    
-- select * from MAGNITUDE

-- DELETE from MAGNITUDE


-- inserting EDU_METER_AID
-- cvs mode to set the separators before inserting data
.mode csv                       
.import "Inserted data/EDU_METER_AID(data).csv" EDU_METER_AID

--removing the headers ( a bit of a hack but sqlite has no direct way)
delete FROM EDU_METER_AID WHERE EMC_ID = 'EMC_ID';

-- Distinguishing new AC_CODEs from existing ones.
-- Deleting table
DROP TABLE IF EXISTS AC_TEMP;
CREATE TABLE AC_TEMP(AC varchar(100), LABEL_INT_EN varchar(2048));

.mode csv   
.import "Inserted data/All AC CODES.csv" AC_TEMP
--removing the headers
DELETE FROM AC_TEMP WHERE AC= 'AC';

-- Creating the NEW AC CODES
DROP TABLE IF EXISTS AC_TEMP_NEW;
CREATE TABLE AC_TEMP_NEW(
	EMC_ID integer  primary key AUTOINCREMENT,    -- Numeric coding scheme.
	AC varchar(100),            -- Alphanumeric codeing scheme.
	LABEL_INT_EN varchar(2048));

-- Inserting new AC CODES.
INSERT  INTO AC_TEMP_NEW (AC, LABEL_INT_EN) 
select DISTINCT  AC, LABEL_INT_EN  from (select EDU_METER_AID.EMC_ID, AC_TEMP.* from AC_TEMP
       left join EDU_METER_AID on AC_TEMP.AC = EDU_METER_AID.AC)
       where EMC_ID is null;

-- Inserting new AC_CODES to EDU_METER_AID
INSERT INTO EDU_METER_AID(EMC_ID, AC, LABEL_INT_EN)
select EMC_ID + 900000 as EMC_ID, AC, LABEL_INT_EN from AC_TEMP_NEW;

--  Exporting new AC_CODE
.header on
.echo off
.eqp off
.mode csv
.once "Inserted data/NEW AC CODES inserted in EDU_METER_AID.csv"
select * from EDU_METER_AID where EMC_ID >  900000;

-- Dropping unwanted tables
DROP TABLE IF EXISTS AC_TEMP;
DROP TABLE IF EXISTS AC_TEMP_NEW;

.echo on
.eqp on
--column mode to view the data better.
-- .mode column
-- select * from EDU_METER_AID limit 3;


-- inserting RM_mapping
-- Creating a temproraty table to hold data
-- Deleting table
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

-- Extracting EMC_IDs andInserting the mapping and EMC_IDs to RM_Mapping table
INSERT INTO RM_Mapping 
       select EDU_METER_AID.EMC_ID, RM_Temp.* from RM_Temp 
       left join  EDU_METER_AID on EDU_METER_AID.AC = RM_Temp.AC;

-- Dropping unwanted tables
DROP TABLE IF EXISTS RM_TEMP;

-- inserting REGIONS
-- cvs mode to set the separators before inserting data
.mode csv
.import "Inserted data/ADM_table.csv" REGIONS

--removing the headers ( a bit of a hack but sqlite has no direct way)
delete FROM REGIONS WHERE CO_CODE = 'CO_CODE';


-- inserting RM_Mapping_NonNumeric
-- cvs mode to set the separators before inserting data
.mode csv                       
.import "Inserted data/RM_Mapping_NonNumeric.csv" RM_Mapping_NonNumeric

--removing the headers (a bit of a hack but sqlite has no direct way)
delete FROM RM_Mapping_NonNumeric WHERE Tab = 'Tab';

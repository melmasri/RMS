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
.log log_sqlite.log


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


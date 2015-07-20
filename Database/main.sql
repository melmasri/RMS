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
.log log_sqlite.log

.tables
-- A file to run functions from

-- Creating tables
--------------------------------------------------
-- Creating the sql tables in file create_tables.sql
.read create_tables.sql

-- making sure the tables are inserted (you should see the created tables)
.tables

-- Inserting data
--------------------------------------------------
-- Inserting data in the created tables
.read insert_data.sql


-- Logging off
--------------------------------------------------
-- Turn logging off
.log off

-- Exist this program
.quit


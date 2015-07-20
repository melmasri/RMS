/* This is a library of collective usefull functions to use in sql */


--- Printing all tables with a given column name
--- For MS SQL (SQLite might have different formulation)
DECLARE  @MyColumn nvarchar(50)
SET @MyColumn = N'%EAG_AGE%'
SELECT c.name AS ColName, t.name AS TableName FROM sys.columns c 
	JOIN sys.tables t ON c.object_id = t.object_id
WHERE c.name LIKE @MyColumn



--------------------------------------------------
-- show values of current settings
.show
-- Setting certain variables.
.headers on
-- Turn command echo on or off
.echo on
-- Enable or disable automatic EXPLAIN QUERY PLAN
.eqp on

.tables



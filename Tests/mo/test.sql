

.show
.headers on 
.echo on 

.table

.schema EDU_METER97_REP

.schema RM_Mapping
                
.mode csv
.import "../imported_data/4180_regions.csv" REGIONS


select distinct CO_CODE,  ADM_CODE from REGIONS where ADM_CODE <>0;


select distinct CO_CODE from EDU_METER97_REP;


.mode column
--------------------------------------------------
--  What is writing to get a function
select b.ADM_CODE,
       case
       when b.MG_ID ='1' then 'n'
       when b.MG_ID ='3' then d.DESC_INCLU
       when b.MG_ID ='6' then 'Z'
       when b.MG_ID ='D' then 'm'
       else b.EM_FIG end as cell,
       a.Col, a.EXL_REF from RM_Mapping as a
left join EDU_METER97_REP as b on a.EMC_ID = b.EMC_ID
left join REGIONS as c on b.CO_CODE = c.CO_CODE and b.ADM_CODE = c.ADM_CODE
left join EDU_INCLUSION_REP as d on d.CO_CODE =b.CO_CODE and d.EMCO_YEAR = b.EMCO_YEAR
     and d.ADM_CODE = b.ADM_CODE and d.EMC_ID = b.EMC_ID
left join MAGNITUDE as e on e.MG_ID = b.MG_ID
where a.Tab = 'Teachers ISCED 1' and b.CO_CODE = 4180
union
select a.ADM_CODE, a.ADM_NAME as cell , b.col, b.EXL_REF from REGIONS as a
left join RM_Mapping as b on b.Tab = 'Teachers ISCED 1'
                   and b.AC = 'ADM_NAME'
where a.co_code = 4180
union
-- columns number
select -1 as ADM_CODE, a.Col as cell, a.Col, a.EXL_REF from RM_Mapping as a 
where a.Tab = 'Teachers ISCED 1' and a.RM_TABLE = 'Table 1.1'
union
-- AC Codes 
select -2 as ADM_CODE, AC as cell, Col, EXL_REF from RM_Mapping 
       where Tab = 'Teachers ISCED 1' and RM_TABLE = 'Table 1.1'
union
-- AC LABEL
select -3 as ADM_CODE, b.LABEL_INT_EN as cell, a.Col, a.EXL_REF from RM_Mapping as a
       left join EDU_METER_AID as b on a.EMC_ID = b.EMC_ID
where a.Tab = 'Teachers ISCED 1' and a.RM_TABLE = 'Table 1.1' limit 10;

.show

.mode csv

select a.AC, b.LABEL_INT_EN, a.Col, a.EXL_REF from RM_Mapping as a
       left join EDU_METER_AID as b on a.EMC_ID = b.EMC_ID
where a.Tab = 'Teachers ISCED 1' and a.RM_TABLE = 'Table 1.1' limit 10;


                   
.schema RM_Mapping

.schema EDU_METER_AID

select * from EDU_METER_AID where AC = 'ADM_NAME';

select * from RM_Mapping as a
       left join REGIONS 
where a.Tab = 'Teachers ISCED 1'
and a.AC = 'ADM_NAME' limit 10;

x
       where a.AC ='ADM_NAME' limit 10;


select * from REGIONS as a
       left 
                left join RM_Mapping as b on a.

.schema Edu_Comment_Table_Rep

.schema RM_Mapping_NonNumeric




select -5 as ADM_CODE, b.COM_DATA, -1 as Col, a.EXL_REF from RM_Mapping_NonNumeric as a
   left join EDU_COMMENT_TABLE_REP as b on b.WT_NAME = a.RM_TABLE
       where a.RM_TABLE = 'Table 2.1' and b.CO_CODE = 4180 and  b.EMCO_YEAR = 2012;


select distinct ADM_CODE from;

.schema EDU_COMMENT_TABLE_REP

INSERT OR REPLACE INTO EDU_COMMENT_TABLE_REP VALUES (4180, 2012, 'Table 2.1', 'Testing table comment.');


select distinct RM_TABLE from RM_Mapping_NonNumeric;

select * from EDU_COMMENT_TABLE_REP;

.schema RM_Mapping_NonNumeric

select a.RM_TABLE, b.COM_DATA, a.EXL_REF
       from RM_Mapping_NonNumeric as a
       left join EDU_COMMENT_TABLE_REP as b
       on b.WT_NAME = a.RM_TABLE where a.Table 2.2 and b.CO_CODE = 4180 and  b.EMCO_YEAR = 2012;


select a.ADM_CODE, a.ADM_NAME as cell, b.col, b.EXL_REF from REGIONS as a 
       left join RM_Mapping as b on  b.AC = 'ADM_NAME'               
       and b.AC= 'T.1' where a.co_code =4180;



select a.ADM_CODE, a.ADM_NAME as cell, b.col, b.EXL_REF from REGIONS as a 
       left join RM_Mapping as b on  b.AC = 'ADM_NAME'               
       and b.Rm_Table= (select RM_TABLE from RM_Mapping as b where b.AC = 'T.1' limit 1)   where a.co_code =4180;



select -1 as ADM_CODE, a.Col as cell, a.Col, a.EXL_REF
       from RM_Mapping as a where a.AC='T.2.GPV.Pu.Math'
       union
       select -2 as ADM_CODE, AC as cell, Col, EXL_REF from RM_Mapping
       where AC='T.2.GPV.Pu.Math'
       union
       select -3 as ADM_CODE, b.LABEL_INT_EN as cell, a.Col, a.EXL_REF
       from RM_Mapping as a
       left join EDU_METER_AID as b on a.EMC_ID = b.EMC_ID
       where a.AC='T.2.GPV.Pu.Math'
       union

       select a.ADM_CODE, a.ADM_NAME as cell, b.col, b.EXL_REF
       from REGIONS as a
       left join RM_Mapping as b on b.AC = 'ADM_NAME' and b.AC='T.2.GPV.Pu.Math'
       where a.co_code =4180;


-- Comments
.table

a.ADM_CODE, a.FTN_DATA,b. b.Col, b. EXL_REF

select c.ADM_CODE, c.FTN_DATA, a.Col, a.EXL_REF from RM_Mapping as a
        left join EDU_METER_AID as b on b.AC = a.AC
        join EDU_FTN97_REP as c on b.EMC_ID = c.EMC_ID
 where a.AC = 'E.1.Pr' and a.CUR_YEAR = 0
 and c.CO_CODE = 4180 and c.EMCO_YEAR = 2012;



 and b.CO_CODE = 4180 and b.EMCO_YEAR = 2012;

select a.ADM_CODE, a.FTN_DATA, b.Col, b.EXL_REF from EDU_FTN97_REP as a
       left join RM_Mapping as b on a.EMC_ID = b.EMC_ID
       where a.CO_CODE = 4180 and a.EMCO_YEAR = 2012;
       
select * from EDU_FTN97_REP as a 
left join EDU_METER_AID as b on b.EMC_ID = a.EMC_ID;

.schema RM_Mapping

.schema EDU_FTN97_REP


select * from RM_Mapping where AC = 'E.1.Pr'






SELECT C.ADM_CODE, c.FTN_DATA, a.Col, a.EXL_REF F
ROM RM_Mapping AS a LEFT JOIN EDU_METER_AID AS b ON b.AC = a.ACec
JOIN EDU_FTN97_REP AS c ON b.EMC_ID = c.EMC_ID
WHERE a.RM_TABLE = 'Table 1.1' AND a.CUR_YEAR = 0
AND c.CO_CODE = 4180 AND c.EMCO_YEAR = 2012;

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
	SYS_DATE datetime DEFAULT CURRENT_TIMESTAMP,
	SERIES varchar(10) NOT NULL,
	SURVEY_ID char(2) NULL, --- Regional model default is set to 'RM'

DELETE FROM METER_AUDIT_TEMP;

INSERT INTO METER_AUDIT_TEMP (MC_ID, CO_CODE, ADM_CODE, MC_YEAR, EM_FIG_OLD, MQ_ID_OLD, MG_ID_OLD, USER_NAME, SERIES)
SELECT c.EMC_ID,c.CO_CODE, c.ADM_CODE, c.EMCO_YEAR, c.EM_FIG, c.MQ_ID, c.MG_ID, 'mo', 'est' from RM_MAPPING as a
LEFT JOIN EDU_METER_AID AS b ON b.AC = a.AC
JOIN EDU_METER97_REP as c  ON b.EMC_ID = c.EMC_ID
WHERE a.Tab='Teachers ISCED 1' AND  c.CO_CODE = 4180 AND (( c.EMCO_YEAR= 2012 AND a.CUR_YEAR=0 ) OR ( c.EMCO_YEAR= 2011 AND a.CUR_YEAR=-1));


select * from METER_AUDIT_TEMP limit 1;

INSERT INTO METER_AUDIT_TRAIL (MC_ID, CO_CODE, ADM_CODE, MC_YEAR, EM_FIG_OLD, MQ_ID_OLD, MG_ID_OLD, USER_NAME, SERIES, SURVEY_ID, EM_FIG_NEW, MQ_ID_NEW, MG_ID_NEW) 
SELECT a.MC_ID, a.CO_CODE, a.ADM_CODE, a.MC_YEAR,
a.EM_FIG_OLD, a.MQ_ID_OLD, a.MG_ID_OLD,
a.USER_NAME, a.SERIES, a.SURVEY_ID,
b.EM_FIG, b.MQ_ID, b.MG_ID from  METER_AUDIT_TEMP as a
join EDU_METER97_REP as b on a.MC_ID = b.EMC_ID
and a.CO_CODE = b.CO_CODE and a.ADM_CODE = b.ADM_CODE
and a.MC_YEAR = b.EMCO_YEAR AND
(a.EM_FIG_OLD !=b.EM_FIG OR a.MQ_ID_OLD != b.MQ_ID OR a.MG_ID_OLD != b.MG_ID);




select * from EDU_METER97_REP 
WHERE CO_CODE = 4180 and EMCO_YEAR = 2012 and EMC_ID = 900083 and ADM_CODE = 18;

UPDATE EDU_METER97_REP SET EM_FIG=99 WHERE CO_CODE = 4180 and EMCO_YEAR = 2012 and EMC_ID = 900083 and ADM_CODE = 18;



DELETE FROM METER_AUDIT_TEMP  WHERE EM_FIG_NEW=EM_FIG_OLD AND MQ_ID_NEW=MQ_ID_OLD AND MG_ID_NEW=MG_ID_OLD;]

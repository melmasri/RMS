

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

.schema REGIONS

select distinct CO_CODE, ADM_CODE from EDU_METER97_REP;

.show


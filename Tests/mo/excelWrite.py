import sys
sys.path.append('../../Librairies')
from rmsqlfunctions  import *
from rmfunctions import *
import xlsxwriter

    
def getTable(ext, co_code, year, var_type):
    """ A function that returns METER data and labels  for a specific CO_CODE and year
        ext could either be 'AC = somAC', RM_TABLE = someTableName'.
        The function returns the a list of tuples of thre data
        tuple ( ADM_CODE, DATA, CELL.NO , EXL_REF)
    """
    data = []
    for offset in [0,-1]:
        sql_data = ("select b.ADM_CODE, case when b.MG_ID ='1' then 'n' "
                    "when b.MG_ID ='3' then d.DESC_INCLU "
                   "when b.MG_ID ='6' then 'Z' "
                   "when b.MG_ID ='D' then 'm' "
                   "else b.EM_FIG end as cell, "
                   "a.Col, a.EXL_REF from EDU_METER97_REP as b "
                   "left join RM_Mapping as a on a.EMC_ID = b.EMC_ID "
                   "left join REGIONS as c on b.CO_CODE = c.CO_CODE "
                   "and b.ADM_CODE = c.ADM_CODE "
                   "left join EDU_INCLUSION_REP as d on d.CO_CODE =b.CO_CODE "
                   "and d.EMCO_YEAR = b.EMCO_YEAR and d.ADM_CODE = b.ADM_CODE "
                   "and d.EMC_ID = b.EMC_ID "
                   "left join MAGNITUDE as e on e.MG_ID = b.MG_ID "
                   "where b.CO_CODE ={1} and b.EMCO_YEAR ={2} "
                   "and a.{0} and "
                    "a.CUR_YEAR = {3}".format(ext, co_code, year+offset , offset))
        data = data + sql_query(sql_data)
        # Table header/label
    label_adm = ("select -1 as ADM_CODE, a.Col as cell, a.Col, a.EXL_REF "
                 "from RM_Mapping as a where a.{0} "
                 "union "
                 "select -2 as ADM_CODE, AC as cell, Col, EXL_REF from "         
                 "RM_Mapping  where {0} "
                 "union "
                 "select -3 as ADM_CODE, b.LABEL_INT_EN as cell, a.Col, "
                 "a.EXL_REF from RM_Mapping as a "
                 "left join EDU_METER_AID as b on a.EMC_ID = b.EMC_ID "
                 "where a.{0} "
                 "union ".format(ext, co_code, year))
        # Regions
    if (var_type == 'AC'):
        ext = ("RM_TABLE= (select RM_TABLE from RM_Mapping "
               "as b where b.{0} limit 1)".format(ext))
    label_adm = label_adm +("select a.ADM_CODE, a.ADM_NAME as cell, "
                            "b.col, b.EXL_REF from REGIONS as a "
                            "left join RM_Mapping as b on "
                            "b.AC = 'ADM_NAME' "              
                            "and b.{0} where a.co_code ={1};".format(ext, co_code, year))
    data =  data + sql_query(label_adm)
    return(data)

def getTable_comment(ext, co_code, year):
    """ A function that returns a list of tuples for table comments.
    """
    sql_str =("select a.RM_TABLE, b.COM_DATA, a.EXL_REF "
              "from RM_Mapping_NonNumeric as a "
              "left join EDU_COMMENT_TABLE_REP as b on b.WT_NAME = a.RM_TABLE "
              "where a.{0} and b.CO_CODE = {1} "
              "and  b.EMCO_YEAR = {2};".format(ext, co_code, year)) 
    data = sql_query(sql_str)
    return(data)


def write_var(var, wb, co_code, year, var_type):
    view_type='ReadOnly'
    if var_type == "AC":
        var_list = ["AC='{0}'".format(var)]
        worksheet = wb.add_worksheet()
    elif var_type == "table":
        var_list = ["RM_TABLE='{0}'".format(var)]
        worksheet = wb.add_worksheet()
    elif var_type == "sheet":
        view_type = 'Edit'
        var_list = sql_query("SELECT DISTINCT RM_TABLE FROM RM_Mapping  WHERE Tab ='{0}'".format(var))
        var_list = ["RM_TABLE='{0}'".format(x[0]) for x in var_list]
        worksheet = wb.add_worksheet(var)
    else :
        sys.exit("Only types AC, table, sheet are accepted")

    co_name = getCO_NAME(co_code)
    no_ADM = getADM_DISTINCT(co_code)
    header_dict= {'A1': 'Country','B1': co_name,'A2': 'CO_CODE',
                  'B2': co_code,'A3': 'Year','B3': year,
                  'A4': 'Data','B4': var, 'A5': 'No.ADM', 'B5': no_ADM}

    # A loop over all tables all tables
    for ext in var_list:
        data = getTable(ext, co_code, year, var_type)

        if(var_type != "AC"):
            write_table_comment(worksheet,
                                getTable_comment(ext, co_code, year),
                                view_type)
        
        write_data(worksheet, data, view_type)
        write_data(worksheet , header_dict)
           
        
        
def write_data(worksheet, data, view_type = 'ReadOnly'):
    """ A function that writes tables to a given sheet.
        Mapping should follow the following convention
        EXL_REF | COL | AC |LABEL_INT_EN
              A function that writes a dictionary of keys and values, 
        where keys are the excel rel and values are the data
        """
    if(type(data)==list):
        uni_ids = sorted(list(set([x[0] for x in data])))
        uni_ids = {uni_ids[y]:y for y in range(len(uni_ids))}
        uni_ids[0] = len(uni_ids)+1
        if view_type =="Edit":
            for i in data:
                ind = indexes(i[3])
                worksheet.write(uni_ids[i[0]] + ind[0]-3 -1*(i[0]>=0), ind[1], i[1] )
        elif view_type == "ReadOnly":
            data.sort(key=lambda tup: tup[2]) # Sorting the data by column no.
            left_top_corner = 3               # the index of the first column.
            rc_ids = [indexes(x[3]) for x in data]
            uni_cols = sorted(list(set([x[1] for x in rc_ids] )))
            uni_cols = {uni_cols[i]:i + left_top_corner for i in range(len(uni_cols))}
            for i in range(len(data)):
                worksheet.write(uni_ids[data[i][0]] + rc_ids[i][0]-3
                                -1*(data[i][0]>=0), uni_cols[rc_ids[i][1]], data[i][1])
    elif(type(data)==dict):
        for key, value in data.items():
            worksheet.write(key, value)



def write_table_comment(worksheet, data, view_type = 'ReadOnly'):
    """ A function that writes table commnets by using write_dict.
    Basically it creates a dictionary of excel ref as keys and data as values.
    It write The name of the table and the 'Comment' header thatn the cooment """
    if(data):
        data= data[0]
        ind = indexes(data[2])
        if (view_type == 'ReadOnly'):
            ind[1] = 3
        dict_table = {indexes_inverse([ind[0]-1, ind[1]]): 'Table comments:',
                      indexes_inverse(ind): data[1]}
        write_data(worksheet, dict_table)
            
set_database_file("../../Database/UISProd.db")


co_code = 4180
co_name = getCO_NAME(co_code)
year = 2012

filename = "{0}_{1}.xlsx".format(co_name, 2012)
wb = xlsxwriter.Workbook(filename)

var ='Teachers ISCED 2'
# view_type = 'edit'              #  or readonly
write_var('Teachers ISCED 2', wb, co_code, year, var_type = "sheet")
write_var('Table 2.1', wb, co_code, year, var_type = "table")
write_var('T.2.GPV.Pu.Math', wb, co_code, year, var_type = "AC")

write_var('Table 1.4', wb, co_code, year, var_type = "table")
write_var('T.1', wb, co_code, year, var_type = "AC")

wb.close()

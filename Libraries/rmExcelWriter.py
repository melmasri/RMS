import sys
sys.path.append('../../Libraries')
from rmsqlfunctions  import *
from rmfunctions import *
import xlsxwriter

    
def getTable(var, co_code, year, var_type,serie):
    """ A function that returns AC or Table data and labels for a specific CO_CODE and year.
        var : is either  
                "AC = 'somAC'" ( i.e. "AC =' T.1'") 
                "RM_TABLE = 'someTableName' 
        it depends if you want to extract a specific AC code and its labels or a whole table.
        serie : is either 'REP', 'OBS', 'EST.
        The function returns the a list of tuples, where each tuple is an SQL record. 
        The tuple is organized as ( ADM_CODE, DATA, CELL.NO , EXL_REF)
    """
    data = []
    # The bellow offset is to accord for the data in the questionnaire from the previous year.
    for offset in [0,-1]:
        sql_data = ("select b.ADM_CODE, case when b.MG_ID ='1' then 'n' "
                    "when b.MG_ID ='3' then d.DESC_INCLU "
                    "when b.MG_ID ='6' then 'Z' "
                    "when b.MG_ID ='D' then 'm' "
                    "else b.EM_FIG end as cell, "
                    "a.Col, a.EXL_REF from EDU_METER97_{4} as b "
                    "left join RM_Mapping as a on a.EMC_ID = b.EMC_ID "
                    "left join REGIONS as c on b.CO_CODE = c.CO_CODE "
                    "and b.ADM_CODE = c.ADM_CODE "
                    "left join EDU_INCLUSION_{4} as d on d.CO_CODE =b.CO_CODE "
                    "and d.EMCO_YEAR = b.EMCO_YEAR and d.ADM_CODE = b.ADM_CODE "
                    "and d.EMC_ID = b.EMC_ID "
                    "left join MAGNITUDE as e on e.MG_ID = b.MG_ID "
                    "where b.CO_CODE ={1} and b.EMCO_YEAR ={2} "
                    "and a.{0} and "
                    "a.CUR_YEAR = {3}".format(var, co_code, year+offset , offset, serie))
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
                 "union ".format(var, co_code, year))
        # Regions
    if (var_type == 'AC'):
        var = ("RM_TABLE= (select RM_TABLE from RM_Mapping "
               "as b where b.{0} limit 1)".format(var))
    label_adm = label_adm +("select a.ADM_CODE, a.ADM_NAME as cell, "
                            "b.col, b.EXL_REF from REGIONS as a "
                            "left join RM_Mapping as b on "
                            "b.AC = 'ADM_NAME' "              
                            "and b.{0} where a.co_code ={1};".format(var, co_code, year))
    data =  data + sql_query(label_adm)
    return(data)

def getCell_comment(var, co_code, year,serie):
    """ Returns the cell comments of a specific variable (var) if exist.
        var : is either  
                "AC = 'somAC'" ( i.e. "AC =' T.1'") 
                "RM_TABLE = 'someTableName' 
    """
    ntable_adm_divi_offset = ''
    if var != "RM_TABLE='Table i'":
        ntable_adm_divi_offset = "AND c.NTABLE<>-1"
        
    data = []
    # The bellow offset is to accord for the data in the questionnaire from the previous year.
    for offset in [0,-1]:
        sql_str = ("SELECT c.ADM_CODE, '[' || c.DATE_ADDED || '] ' || c.FTN_DATA, a.Col, a.EXL_REF, c.USERNAME FROM RM_Mapping AS a "
                   "LEFT JOIN EDU_METER_AID AS b ON b.AC = a.AC "
                   "JOIN EDU_FTN97_{4} AS c ON b.EMC_ID = c.EMC_ID "
                   "WHERE a.{0} AND a.CUR_YEAR = {3} "
                   "AND c.CO_CODE = {1} "
                   "AND c.EMCO_YEAR = {2} {5};".format(var,co_code, year+ offset, offset,serie, ntable_adm_divi_offset))
        data = data + sql_query(sql_str)
    if data:
        return(data)
                

def getTable_comment(var, co_code, year, view_type,serie):
    """ A function that returns table comments for a specific table.
        var : is either  
                "AC = 'somAC'" ( i.e. "AC =' T.1'") 
                "RM_TABLE = 'someTableName' 
        Return value is a dictionary of Excel references as keys and data as values.
    """
    sql_str =("select a.RM_TABLE || ': ' || a.RM_TABLE_NAME, b.COM_DATA, a.EXL_REF "
              "from RM_Mapping_NonNumeric as a "
              "left join EDU_COMMENT_TABLE_{3} as b on b.WT_NAME = a.RM_TABLE "
              "and b.CO_CODE = {1} and  b.EMCO_YEAR = {2} "
              "where a.{0} ;".format(var, co_code, year,serie)) 
    data = sql_query(sql_str)
    if(data):
        data= data[0]
        ind = indexes(data[2])
        ind[1] = 3 if view_type == 'ReadOnly' else ind[1]
        data = {indexes_inverse(ind): data[1], indexes_inverse([ind[0]-3, ind[1]]): data[0], indexes_inverse([ind[0]-1, ind[1]]): 'Table comments:'}
        return(data)


def export_var(var, wb, co_code, year, var_type, serie= 'REP'):
    """ A function that exports to an Excel workbook a data defined in var.
        var in  {Table name, Sheet name, AC} as in the questionnaire
        var_type in {'AC', 'table', 'sheet'}
        wb is the workbook object from xlsxwriter.
    """
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
    no_ADM = getADM_DISTINCT(co_code) -1
    # Header to write to each worksheet
    header_dict= {'A1': 'Country','B1': co_name,'A2': 'CO_CODE',
                  'B2': co_code,'A3': 'Year','B3': year,
                  'A4': 'Data','B4': var, 'A5': 'No.ADM', 'B5': no_ADM,
                  'A6': 'Series', 'B6': serie,
                  'A7': 'Mode', 'B7': view_type}

    # header format
    format_header = wb.add_format({'bold' : True, 'align' : 'left'})
    format_data  = wb.add_format({'align' : 'right'})
    # A loop over all tables all tables
    for ext in var_list:
        data = getTable(ext, co_code, year, var_type, serie)
        data = [l + (format_data,) if l[0]>=0 else l + (format_header,) for l in data]
        data_comment = getCell_comment(ext, co_code, year, serie)
        write_data(worksheet, header_dict)
        if data_comment:
            write_data(worksheet, data, view_type, data_comment = data_comment, fmt=True)
        else:
            write_data(worksheet, data, view_type, fmt=True)
        if(var_type != "AC"):
            table_comment  =  getTable_comment(ext, co_code, year, view_type, serie)
            write_data(worksheet,table_comment) if table_comment  else None

           

def write_data(worksheet, data, view_type = 'ReadOnly', **op):
    """ A function that writes data and labels to a given worksheet.
        There are two ways to write the data. 
        1) data is a list of tuples of the format (ADM_CODE, datum, Table Col no., EXL_REF)
                For example (00, 'National level', 2, H18) which is 
                (ADM_CODE for national level, label , Table column 2, Excel ref H18)
                Note that the EXL_REF need to be the reference of the first datum in the column.
                For example, if first region label is in H18 and there are 10 regions, 
                than National level Excel reference is H30 ( 18 + 10 +2),
                but in the tuple EXL_REF is H18 not H30 as in the tuple example above. 
                This is the same for all datum, EXL_REF is Excel reference for the first datum 
                in that column. 
                To pass table headers, alphanumeric codes (AC) and column numbers, you can 
                use ADM_CODE as an offset.
                Basically,  ADM_CODE for table headers is -3, for AC codes is -2 and for 
                Col numbers is -1.,
                i.e., (-2, 'Administrative divisions', 2, 'H18'), this would place the 
                label 'Administrative divisions' above
                region names by an offset of 2 rows above the first name.
        2) data is a dictionary where keys are EXL_REF and values are the datum.
                For example {'A1': 'Country name', 'B1': Canada}

        view_type: 'ReadOnly' would shift all the Excel references to the right of the worksheet for easier viewing.
                   'Edit' would place them as is, in their original location in the questionnaire.
    """
    if(type(data)==list):
        uni_ids = sorted(list(set([x[0] for x in data])))
        uni_ids = {uni_ids[y]:y for y in range(len(uni_ids))}
        uni_ids[0] = len(uni_ids)+1
        if view_type =="Edit":
            if (op.get('fmt')):
                for i in data:
                    ind = indexes(i[3])
                    worksheet.write(uni_ids[i[0]] + ind[0]-3 -1*(i[0]>=0), ind[1], i[1],i[4] )
            else:
                for i in data:
                    ind = indexes(i[3])
                    worksheet.write(uni_ids[i[0]] + ind[0]-3 -1*(i[0]>=0), ind[1], i[1])     

            if(op.get('data_comment')):
                worksheet.show_comments() # to make comments visibile once workbook is opened
                for i in op.get('data_comment'):
                    ind = indexes(i[3])
                    worksheet.write_comment(uni_ids[i[0]]+ind[0]-3 -1*(i[0]>=0),ind[1],i[1], {'author': i[4]})
        elif view_type == "ReadOnly":
            data.sort(key=lambda tup: tup[2]) # Sorting the data by column no.
            left_top_corner = 3               # the index of the first column.
            rc_ids = [indexes(x[3]) for x in data]
            uni_cols = sorted(list(set([x[1] for x in rc_ids] )))
            uni_cols = {uni_cols[i]:i + left_top_corner for i in range(len(uni_cols))}
            if (op.get('fmt')):
                for i in range(len(data)):
                    worksheet.write(uni_ids[data[i][0]] + rc_ids[i][0]-3
                                    -1*(data[i][0]>=0), uni_cols[rc_ids[i][1]], data[i][1], data[i][4])
            else:
                for i in range(len(data)):  
                    worksheet.write(uni_ids[data[i][0]] + rc_ids[i][0]-3
                                    -1*(data[i][0]>=0), uni_cols[rc_ids[i][1]], data[i][1])
                    
            if(op.get('data_comment')):
                worksheet.show_comments() # to make comments visible once workbook is opened
                dc = op.get('data_comment')
                for i in range(len(dc)):
                    worksheet.write_comment(uni_ids[dc[i][0]] + rc_ids[i][0]-3
                                            -1*(dc[i][0]>=0), uni_cols[indexes(dc[i][3])[1]], dc[i][1],{'author': dc[i][4]})
    elif(type(data)==dict):
        for key, value in data.items():
            worksheet.write(key, value)


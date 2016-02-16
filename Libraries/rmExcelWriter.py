import sys
sys.path.append('../../Libraries')
from rmsqlfunctions  import *
from rmfunctions import *
import xlsxwriter

    
def getTable(var, co_code, year, var_type,serie):
    """ SQL extraction of an AC or RM table, with labels and ADM names.

        var : is either  
                "AC = 'somAC'" ( i.e. "AC =' T.1'"),
                "RM_TABLE = 'someTableName' (i.e. "RM_TABLE=Table 1.3").
        it depends if you want to extract a specific AC code and its labels or a whole table.
        serie : is either 'REP', 'OBS', 'EST.
        The function returns a list of tuples, where each tuple is a SQL record. 
        The tuple is organized as ( ADM_CODE, DATA, CELL.NO , EXL_REF).
    """
    data = []
    # The bellow offset is to accord for the data in the questionnaire from the previous year.
    #for offset in [0,-1]:
    offset = 0
    sql_data = ("select b.ADM_CODE, case when b.MG_ID ='1' then 'n' "
                "when b.MG_ID ='3' then d.DESC_INCLU "
                    "when b.MG_ID ='6' then 'Z' "
                "when b.MG_ID ='D' then 'm' "
                "else b.EM_FIG end as cell, "
                "a.Col, a.EXL_REF from EDU_METER97_{4} as b "
                "left join RM_Mapping as a on a.EMC_ID = b.EMC_ID "
                "left join REGIONS as c on b.CO_CODE = c.CO_CODE "
                "and b.ADM_CODE = c.ADM_CODE and b.EMCO_YEAR = c.MC_YEAR "
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
                            "and b.{0} where a.co_code ={1} and a.mc_year={2};".format(var, co_code, year))
    data =  data + sql_query(label_adm)
    return(data)

def getCell_comment(var, co_code, year,serie):
    """ SQL extraction of cell comments of a specific AC or a RM table.

        var: is either  
                "AC = 'somAC'" ( i.e. "AC =' T.1'"),
                "RM_TABLE = 'someTableName' (i.e. "RM_TABLE=Table 1.2").
    """
    ntable_adm_divi_offset = ''
    if var != "RM_TABLE='Table i'":
        ntable_adm_divi_offset = "AND c.NTABLE<>-1"
        
    data = []
    # The bellow offset is to accord for the data in the questionnaire from the previous year.
    ##for offset in [0,-1]:
    offset=0
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
    """ SQL extraction of RM table comments for a specific table.
        
        var : is either  
                "AC = 'somAC'" ( i.e. "AC =' T.1'"),
                "RM_TABLE = 'someTableName'  (i.e. "RM_TABLE=Table 3.2").
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

def getIndic(co_code, year, ind):
    """ SQL extraction of indicators and their labels for a specific CO_CODE and year.

        ind is either:
                'All' for all indicators,
                indicator name as 'NTP.1',
                or a regular expression as '%T.1%' for all indicators for ISCED 1.
        The function returns a list of tuples, where each tuple is a SQL record. 
        The tuple is organized as (ADM_CODE, DATA, CELL.NO , EXL_REF).
    """
    ind = ' ' if ind =='All' else " and a.IND_ID like '{0}'".format(ind)
    #coalesce(a.FIG,a.MAGN)  ## Try this in the future.
    sql_data = ("select a.ADM_CODE, case when a.MAGN = 'value' then a.FIG else a.MAGN end as FIG, a.IND_ID, b.LABEL_ENG from EDU_INDICATOR_EST as a "
                "left join EDU_INDICATOR_AID as b on a.IND_ID = b.IND_ID "
                "where a.CO_CODE = {0} and a.IND_YEAR = {1}{2}"
                "group by a.IND_ID, a.ADM_CODE".format(co_code, year, ind))
    data = sql_query(sql_data)
    ## Adding indexes to where to write the data
    indic_ids = list(map(lambda x: x[2], data))
    indic_ids = sorted(set(indic_ids))
    dLabel = {x[2]:x[3] for x in data}
    d = {indic_ids[i]: [i+3,indexes_inverse([17, i+3])]  for i in range(len(indic_ids))}
    data  = list(map(lambda x: x[:2] + tuple(d[x[2]]),data ))
    ## Creating IND labels and column numbers 
    col_num = list(map(lambda x:(-1, d[x][0], d[x][0], d[x][1]), indic_ids))
    label_en = list(map(lambda x:(-3, dLabel[x], d[x][0], d[x][1]), indic_ids))
    indic_ids =  list(map(lambda x:(-2, x)+ tuple(d[x]) , indic_ids))
    ## Creating ADM column
    label_adm = ("select a.ADM_CODE, a.ADM_NAME as cell, "
                 "2 as Cell, 'C18' as EXL_REF from REGIONS as a "
                 "where co_code ={0} and mc_year={1};".format(co_code, year))
    data = data + sql_query(label_adm) +  [(-2, 'ADM_NAME', 2, 'C18'),(-1, 2, 2, 'C18')]
    ## Adding everything
    data = data + col_num + indic_ids +label_en
    return(data)

def export_var(var, wb, co_code, year, var_type, serie= 'REP'):
    """  Exports to a xlsx file the whole RM questionniare, a sheet, a table or an AC.

        var:     in  {Table name, Sheet name, AC} as in the questionnaire
        var_type: in {'AC', 'table', 'sheet'}
        wb:      is the workbook object from xlsxwriter.
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
    no_ADM = getADM_DISTINCT(co_code,year) -1
    # Header to write to each worksheet
    header_dict= {'A1': 'Country','B1': co_name,'A2': 'CO_CODE',
                  'B2': co_code,'A3': 'Year','B3': year,
                  'A4': 'Data','B4': var, 'A5': 'No.ADM', 'B5': no_ADM,
                  'A6': 'Series', 'B6': serie,
                  'A7': 'Mode', 'B7': view_type}

    # header format
    format_header = wb.add_format({'bold' : True, 'align' : 'left'})
    format_data  = wb.add_format({'align' : 'right'})
    worksheet.set_column('D:DV', 12)
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

            
def export_indc(ind, wb, co_code, year, serie = 'EST'):
    """ Exports to an xlsx file a list of indicator(s).
        
        ind:    is either 'All' for all indicators or an IND_ID as 'NTP.1'.
        wb:     is the workbook object from xlsxwriter.
        serie:  is always set to EST since there is only EDU_INDICATOR_EST table.
        co_cod: country code.
        year:    data reference year.
    """
    co_name = getCO_NAME(co_code)
    no_ADM = getADM_DISTINCT(co_code, year) -1
    view_type = 'ReadOnly'
    # Header to write to each worksheet
    header_dict= {'A1': 'Country','B1': co_name,'A2': 'CO_CODE',
                  'B2': co_code,'A3': 'Year','B3': year,
                  'A4': 'Data','B4': ind, 'A5': 'No.ADM', 'B5': no_ADM,
                  'A6': 'Series', 'B6': serie,
                  'A7': 'Mode', 'B7': view_type}
    # header format
    format_header = wb.add_format({'bold' : True, 'align' : 'left'})
    format_data  = wb.add_format({'align' : 'right'})
    ## Extract data
    data = getIndic(co_code, year, ind)
    ## Adding formating
    data = [l + (format_data,) if l[0]>=0 else l + (format_header,) for l in data]
    ## Writing
    worksheet = wb.add_worksheet()
    worksheet.set_column('D:DV', 12)
    write_data(worksheet, data, view_type, fmt=True)
    write_data(worksheet, header_dict)

  
def write_data(worksheet, data, view_type = 'ReadOnly', **op):
    """ Writes to xlsx worksheet the given data in specific formats.
        
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
                For example {'A1': 'Country name', 'B1': Canada}.

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


def direct_extraction(s, loc):
    """ Writes record format to Excel.
    
    s must be in the format TYPE-SERIES[co_code1(adm1, adm2,..);co_code2;..;year;AC]
    where 
    TYPE        = raw of indic
    year        = 'yyyy' for a specific year
                = 'yyyy:yyyy' for a range of years
                = '' left empty for all years
    co_code     = xxx for a specific country and all regions
                = xxx(x1,x2,..) for a specific country and a list of regions, x1, x2, ..
                = '' empty for all countries and regions
    AC          = a specific indicator or AC, wildcards of % and _ are accepted.
    SERIES      = rep, obs, or est, by default is est.
    
    loc is where the file location should be.
    """
    s = s.replace(' ','')
    gen_format = '(raw|indic)(-rep|-obs|-est)?\[([A-Za-z0-9\.\(\):,%_]*;?)+\]$'
    if not re.match(gen_format, s):
        print("Error: wrong format.")
        return None
    if re.match('^\[\]$',s):
        print("Error: empty string.")
        return None
    if s.count(';')<2:
        print("Error: minimum of three separators ';'. ")
        return
    extract_type =re.search('(raw|indic)',s).group(0)
    series = 'est'
    if re.search('(rep|obs|est)',s):
        series = re.search('(rep|obs|est)',s).group(0)

    s = s.replace(series, '')
    s = s[s.find('[')+1:s.find(']')]
    s= s.split(';')
    n = len(s)
    ## Testing AC
    AC_reg = '^[A-Za-z0-9\.%_]+$'
    if not re.match(AC_reg, s[n-1]):
        print('Error: wrong format for AC code, only A-Z, a-z, 0-9 and . are acceptable.')
        return None
    ac = s[n-1]
    ##Testing year
    year_reg = '^([0-9]{4}$|[0-9]{4}:[0-9]{4}|\b)$'
    if not re.match(year_reg, s[n-2]) and not s[n-2]=='':
        print("Error: wrong year format, only YYYY, YYYY:YYYY, and '' are allowed.")
        return None
    if s[n-2].count(':')>0:
        aux = s[n-2].split(':')
        year_str = "AND b.EMCO_YEAR >={0} and b.EMCO_YEAR<={1}".format(aux[0], aux[1])
    elif s[n-2]=='':
        year_str=''
    else:
        year_str = 'AND b.EMCO_YEAR='+ s[n-2]

    if extract_type=='indic':
        year_str = year_str.replace('EMCO', 'IND')

    data = []
    filename = loc + 'record_format_' + extract_type + '-' + ac.replace('%','xx')+'.xlsx'
    print('writing: '+filename, end='')
    wb = xlsxwriter.Workbook(filename)
    
    for x in s[0:n-2]:
        if re.match('([0-9]+\([0-9,]+\)|[0-9]+)',x) :
            paran  = x.find('(')
            if paran == -1:
                co_code = 'AND b.CO_CODE=' + x
                regions = ''
            else:       
                co_code = 'AND b.CO_CODE=' + x[0:paran]
                regions = 'AND b.ADM_CODE in ' + x[paran:x.index(')')+1]
        elif x=='':
            co_code = ''
            regions = ''
        else:
            print("Error: wrong format for co_code, expects co_code(adm_code's), co_code, or '', got {0} ".format(x))
            pass
        if extract_type =='raw':
            query = ("select f.CO_SHORT_NAME, b.CO_CODE, "
                     "c.ADM_NAME, b.ADM_CODE, b.EMCO_YEAR, b.EMC_ID, g.AC, "
                     "case when b.MG_ID ='1' then 'n' "
                     "when b.MG_ID ='3' then d.DESC_INCLU "
                     "when b.MG_ID ='6' then 'Z' "
                     "when b.MG_ID ='D' then 'm' "
                     "else b.EM_FIG end as cell, "
                     "h.USERNAME || '[' || h.DATE_ADDED || '] ' || h.FTN_DATA "
                     "from EDU_METER97_{4} as b "
                     "left join COUNTRY as f on b.CO_CODE = f.CO_CODE "
                     "left join EDU_METER_AID as g on b.EMC_ID = g.EMC_ID "
                     "left join REGIONS as c on b.CO_CODE = c.CO_CODE "
                     "and b.ADM_CODE = c.ADM_CODE and b.EMCO_YEAR = c.MC_YEAR "
                     "left join EDU_FTN97_{4} AS h ON b.EMC_ID = h.EMC_ID AND "
                     "b.CO_CODE = h.CO_CODE "
                     "AND b.ADM_CODE = h.ADM_CODE AND b.EMCO_YEAR = h.EMCO_YEAR "
                     "left join EDU_INCLUSION_{4} as d on d.CO_CODE =b.CO_CODE "
                     "and d.EMCO_YEAR = b.EMCO_YEAR and d.ADM_CODE = b.ADM_CODE "
                     "and d.EMC_ID = b.EMC_ID "
                     "left join MAGNITUDE as e on e.MG_ID = b.MG_ID "
                     "where g.AC LIKE '{0}' {3} {1} {2} "
                     "ORDER BY b.CO_CODE, b.ADM_CODE, "
                     "b.EMCO_YEAR, g.AC ASC;".format(ac,co_code, year_str,regions,      series))
        elif extract_type =='indic':
            query = ("select f.CO_SHORT_NAME, b.CO_CODE, "
                     "c.ADM_NAME, b.ADM_CODE, b.IND_YEAR, b.IND_ID, "
                     "case when b.MAGN = 'value' then b.FIG "
                     "else b.MAGN end "
                     "from EDU_INDICATOR_EST as b "
                     "left join COUNTRY as f on b.CO_CODE = f.CO_CODE "
                     "left join REGIONS as c on b.CO_CODE = c.CO_CODE "
                     "and b.ADM_CODE = c.ADM_CODE and c.MC_YEAR = b.IND_YEAR "
                     "where b.IND_ID like '{0}' {1} {2} {3}"
                     "ORDER BY b.CO_CODE, b.ADM_CODE, "
                     "b.IND_YEAR, b.IND_ID ASC".format(ac, co_code, year_str, regions))
        data = data + sql_query(query)
        
    worksheet = wb.add_worksheet(ac.replace('%', 'xx'))
    worksheet.show_comments() # to make comments visibile once workbook is
    format_wb  = wb.add_format({'align' : 'left'})
    worksheet.set_column('A:J', 12, format_wb)
    if data:
        row=0
        col=0
        worksheet.write(row, col,'CO_SHORT_NAME')
        worksheet.write(row, col + 1, 'CO_CODE')
        worksheet.write(row, col + 2, 'ADM_NAME')
        worksheet.write(row, col + 3, 'ADM_CODE')
        worksheet.write(row, col + 4, 'YEAR')
        if extract_type =='raw':
            worksheet.write(row, col + 5, 'MC_ID')
            worksheet.write(row, col + 6, 'AC')
            worksheet.write(row, col + 7, 'FIG')
        else:
            worksheet.write(row, col + 5, 'AC')
            worksheet.write(row, col + 6, 'FIG')
        row += 1
        if extract_type=='raw':
            for co_name, co, ad_name, ad, year, mc_id, ac, fig,comm in (data): 
                worksheet.write(row, col,co_name)
                worksheet.write(row, col + 1, co)
                worksheet.write(row, col + 2, ad_name)
                worksheet.write(row, col + 3, ad)
                worksheet.write(row, col + 4, year)
                worksheet.write(row, col + 5, mc_id)
                worksheet.write(row, col + 6, ac)
                worksheet.write(row, col + 7, fig)
                if comm:
                    worksheet.write_comment(row, col+7, comm)
                row += 1
        else:
            for co_name, co, ad_name, ad, year, ac, fig in (data): 
                worksheet.write(row, col,co_name)
                worksheet.write(row, col + 1, co)
                worksheet.write(row, col + 2, ad_name)
                worksheet.write(row, col + 3, ad)
                worksheet.write(row, col + 4, year)
                worksheet.write(row, col + 5, ac)
                worksheet.write(row, col + 6, fig)
                row += 1
    wb.close()
    print('...Done.')
    return filename

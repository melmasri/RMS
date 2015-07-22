# import sqlite3 #sql connection
import xlrd #to read excel file
from xlrd import open_workbook
import re
import collections #enable namedtuple: varname = collections.namedtuple('varname','val1, val2, val3..') and ordered dic
import sys, json
from rmsqlfunctions import *
import os
from functools import reduce
import shutil
import datetime
from itertools import chain
import time

#Global variables
# conn = sqlite3.connect('../../Database/UISProd.db')
# #Uncomment the line below for creating virtual database
# #createDb = sqlite3.connect(":memory:")
# #creates the cursor object for SQL queries
# database_cursor = conn.cursor()
# # Path to the variable mapping file(json) format.
# mapping_file_json="./variables_for_preprocessing.json"
# # Read the json file and put the contents in the dictionary pre_vars

# with open(mapping_file_json) as f:
#     pre_vars=json.loads(f.read())

if ( re.search('\\\\Tests\\\\mo$',os.getcwd()) or re.search('/Tests/os$',os.getcwd()) or re.search('/Tests/mo$',os.getcwd())   ):
    with open("../../Librairies/variables_for_preprocessing.json") as f:
        pre_vars=json.loads(f.read())
else:
    with open("Librairies/variables_for_preprocessing.json") as f:
        pre_vars=json.loads(f.read())



####DATA INSERTION
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------


####DATA LOOKUP
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

####MISC
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

def indexes(cellname):
    """This function returns a vector with the indices of a cell given its name

    For example if cellname='A1' it returns [0,0].
    """
    match1 = re.search('[A-Z]+',cellname)
    col_name = match1.group()
    N = len(col_name)
    col_index = 0
    for index in range(N):
        col_index = col_index+(ord(col_name[index])-ord('A')+1)*26**(N-1-index)
    match2 = re.search('[0-9]+',cellname)
    row_index = int(match2.group())
    return [row_index-1,col_index-1]

def indexes_inverse(xlrd_coordinates):
    """Returns excel coordinates given a vector with xlrd coordinates.

    It works for a maximumn of two letters in the column name.
    """
    # The following gives the number of letters
    column_letter=""
    quotient=int(xlrd_coordinates[1] / 26  )
    letter_number= xlrd_coordinates[1] % 26
    if(quotient):
        column_letter= chr(ord('A')+ (quotient-1))
    column_letter = column_letter + chr( ord('A') + letter_number )
    xl_reference=column_letter + str( xlrd_coordinates[0] + 1 )
    return(xl_reference)

def is_reference(cell_value):
    """Checks if a value is a reference to another cell.

    This functions receives a string, and checks if it has the form
    X[a:b]. If yes, it returns [a,b], else it returns None. 
    If it has the form X[:b] it returns [None,b].
    """
    if type(cell_value) in [int,float]:
        return(None)
    match=re.search('[Xx]\[([0-9]*):([0-9]+)\]$',cell_value)
    if not (match==None):
        reference=list(match.groups())
        if reference[0]=='':
            reference[0]=None
        else:
            reference[0]=int(reference[0])
        reference[1]=int(reference[1])
        return( reference  )
    else:
        return(None)

def ec_td_id(sheet_name):
    """Returns the EC_TD_ID given the sheet name.
    """
    if sheet_name == "Administrative divisions":
        return(1)
    elif sheet_name == "Pupils":
        return(3)
    else:
        return(2)


def mg_id(cell_value):
    """This function gets the MG_ID for the read data

    This works for the meters table only. Reading a number will return 0.
    """
    if type(cell_value) in [int,float]:
        return("")
    elif is_reference(cell_value):
        return(3)
    elif cell_value in ["Z","z"]:
        return(6)
    elif cell_value in ["M","m"]:
        return("D")
    else:
        return("\"\"")



## Error class for a country name that is not found in the database
class CountryNameError(Exception):
    pass



####DATA EXTRACTION
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
def getADM_CODE(co_code):
    """ A function that returns the ADM codes for a specific country"""
    sql_str = 'Select ADM_CODE from REGIONS where CO_CODE ={0}'.format(co_code)
    sql_str = sql_query(sql_str)[0]


def getADM_DISTINCT(co_code):
    """ A function that return the distinct number of ADM"""
    sql_str = 'SELECT COUNT(ADM_CODE) FROM REGIONS WHERE CO_CODE={0}'.format(co_code)
    query = sql_query(sql_str)[0]
    return(query[0])
    
def getCO_CODE(country_name):
    """This function returns a country code given the long name.
    If the exact country name is found, it gives back the code,
    otherwise it returns None.
    """
    name = country_name.upper().replace("'", "''")
    sql_str = ("SELECT CO_CODE FROM COUNTRY "
               " WHERE UPPER(CO_LONG_NAME) IS '{0}' "
               " OR UPPER(CO_SHORT_NAME) IS '{0}' ".format(name))
    code = sql_query(sql_str)
    if code:
        return(code[0][0])

    
def getCO_NAME(co_code, short=True):
    """This function returns a country name given the country code
    If the  country name is found it returns it  otherwise it returns None.
    """
    if short:
        var = 'CO_SHORT_NAME'
    else:
        var = 'CO_LONG_NAME'
    sql_str = ("SELECT {0} FROM COUNTRY "
               " WHERE CO_CODE ={1} ".format(var , co_code))
    code = sql_query(sql_str)
    if code:
        return(code[0][0])

def getAvailable_countries():
    """ Returns a tuple of the available countries"""
    sql_str = ("SELECT DISTINCT b.CO_SHORT_NAME FROM REGIONS as a "
               "left join COUNTRY as b on a.CO_CODE = b.CO_CODE "
               "where a.ADM_CODE >0")
    res = sql_query(sql_str)
    if res:
        return(res)

def getAvailable_year(co_name):
    """ Returns the data year of the submitted questionnaires"""
    name = co_name.upper().replace("'", "''")

    sql_str = ("SELECT DISTINCT A.EMCO_YEAR FROM EDU_METER97_REP AS A "
               "LEFT JOIN COUNTRY AS B ON B.CO_CODE = A.CO_CODE "
               "WHERE UPPER(B.CO_SHORT_NAME) IS '{0}' ".format(name))
    code = sql_query(sql_str)   
    if code:
        return(list(chain.from_iterable(code)))

class questionnaire:
    """Defines questionnaire properties and methods
    
    Attributes:
      wb = the workbook that correspond to the class.
      conn = connection object to the database
      emco_year = the emco_year read from the workbook.
      nadm1 =  number of administrative divisions in the file
      country_name = the name of the country that filled the questionnaire.
      country_code = the code of the country.
      edit_mode = True or False, wether the class if going to be used for editing existing data.
    """
    def set_workbook(self,excel_file):
        """Setw the workbook

        excel_file should be the full path to the excel file.
        """
        self.wb=open_workbook(excel_file)

    def set_database_connection(self,database_file):
        """Sets the connection to the database"""
        self.conn=sqlite3.connect(database_file)

    def get_emco_year(self):
        """Sets the attribute emco_year"""
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            self.emco_year= int( sheet.cell(2,1).value)
        else:
            front_page_variables = pre_vars['fixed_sheets']['Front Page']
            sheet = self.wb.sheet_by_name('Front Page')
            self.emco_year = int(sheet.cell( *indexes( front_page_variables['school_year_ending'][0]  )   ).value)
        
    def get_nadm1(self):
        """Sets the attribute nadm1 based on the questionnaire"""
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            self.nadm1= int(sheet.cell(4,1).value)
        else:
            administrative_divisions_variables = pre_vars['fixed_sheets']['Administrative divisions']
            sheet = self.wb.sheet_by_name('Administrative divisions')
            self.nadm1 = int(sheet.cell( *indexes( administrative_divisions_variables['adm1_number'][0]  )   ).value)

    def get_country_name(self):
        """Sets the country name based on the front page of the questionnaire."""
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            self.country_name = sheet.cell( 0,1   ).value
        else:
            front_page_variables = pre_vars['fixed_sheets']['Front Page']
            sheet = self.wb.sheet_by_name('Front Page')
            self.country_name = sheet.cell( *indexes( front_page_variables['country_name'][0]  )   ).value

    def get_country_code(self):
        """Sets the country code by looking in the COUNTRY table.

        This function searches the country code in the COUNTRY table
        using the self.country_name variable of the class. It assumes
        that there will be an exact match up to case. If this is not
        the case it returns None.
        """
        name=self.country_name.upper()
        # The following is necessary for compatibility with sql syntax
        name="'"+re.sub("'","''",name)+"'"
        cursor=self.conn.cursor()
        #The following is not working so I am using .format, but this is not secure
#        cursor.execute(u'SELECT CO_CODE FROM COUNTRY  WHERE UPPER(CO_LONG_NAME) IS ?', (name,) )
        cursor.execute("SELECT CO_CODE FROM COUNTRY  WHERE UPPER(CO_LONG_NAME) IS {0};".format(name) )        
        country_code=cursor.fetchone()
        if(country_code==None):
            raise CountryNameError("Country name \'{0}\' not found in the COUNTRY database.".format(self.country_name))
        else:
            self.country_code=country_code[0]
        cursor.close()

    def emc_id(self,table_name,column):
        """Returns the emc_id given then table and column number.
        """
        cursor=self.conn.cursor()
        cursor.execute("SELECT EMC_ID  FROM RM_MAPPING WHERE RM_TABLE=\"{0}\" AND Col={1};".format(table_name,column ) )
        return(cursor.fetchone()[0])

    def print_log(self,text_string):
        """Puts the text in the log file and in stdout.
        """
        print(text_string)
        self.log_file.write(text_string)
        self.log_file.flush()
        os.fsync(self.log_file.fileno())
        
    def preprocessing(self):
        """Checks the consistency of the questionnaire.

        This variable reads the Checking sheets and writes in the log
        if there is any NO.  

        If in edit mode, it checks that the meter values of the
        administrative divisions add to the country total and also
        checks that the female columns are less or equal than the
        total of both sexes.
        """
        if (not self.edit_mode):
            check_variables=pre_vars["Checking sheet"]
            sheet=self.wb.sheet_by_name("Checking sheet")
            self.print_log("Date: "+ time.strftime("%x") + "\n")
            self.print_log("Questionnaire path: " + self.excel_file + "\n")
            ## Check the number of sheets
            if pre_vars['nsheets']==self.wb.nsheets:
                self.print_log("The correct number of sheets has been submited.\n")
            printed_main_message=False
            for sheet_name in check_variables.keys():
                for var in [[x, check_variables[sheet_name][1] ] for x in check_variables[sheet_name][0] ]:
                    if( sheet.cell( *var ).value == 'No' ):
                        if(not printed_main_message):                                                        
                            self.print_log("The following items have No in the Checking sheet:\n")
                            printed_main_message=True
                        var[1]-=5
                        self.print_log("{0} : {1}\n".format( sheet_name, sheet.cell(*var).value ))
            if (not  printed_main_message ):
                self.print_log("All the checks passes. QUESTIONNAIRE CAN BE PROCESSED\n")
        else:
            ## For each sheet name, the following dictionary has a
            ## list of pairs. For each pair, the first entry should be
            ## smaller than the second one
            check_less_dictionary={
                'Pupils' : [ [16,14], [17,15], [13,12] ],
                'Teachers ISCED 1' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ],
                'Teachers ISCED 2' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ],
                'Teachers ISCED 3' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ],
                'Teachers ISCED 23' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ]
                }
            # The following variable has the sheets that are being
            # imported.
            edit_sheets_names=self.wb.sheet_names()            
            def check_less():
                """Checks that the pairs from the
                check_less_dictionary satisfy that the first one is
                smaller than the second one"""
                cursor=self.conn.cursor()
                pass_test=True
                for sheet_name,pairs_list in check_less_dictionary.items():
                    if sheet_name not in self.wb.sheet_names():
                        continue
                    sheet=self.wb.sheet_by_name(sheet_name)
                    for pairs in pairs_list:
                        cursor.execute("SELECT EXL_REF FROM RM_MAPPING WHERE Tab=\'{}\' AND Col={}".format(sheet_name,pairs[0]))
                        ref_smaller=cursor.fetchone()[0]
                        cursor.execute("SELECT EXL_REF FROM RM_MAPPING WHERE Tab=\'{}\' AND Col={}".format(sheet_name,pairs[1]))
                        ref_bigger=cursor.fetchone()[0]
                        smaller_meter_starting_coordinates = indexes(ref_smaller)
                        bigger_meter_starting_coordinates = indexes(ref_bigger)
                        smaller_meter_values=sheet.col_values(smaller_meter_starting_coordinates[1],
                                                              smaller_meter_starting_coordinates[0],
                                                              smaller_meter_starting_coordinates[0]+self.nadm1)
                        bigger_meter_values=sheet.col_values(bigger_meter_starting_coordinates[1],
                                                              bigger_meter_starting_coordinates[0],
                                                              bigger_meter_starting_coordinates[0]+self.nadm1)
                        for i in range(self.nadm1):
                            ## Error para el log
                            small_value=smaller_meter_values[i]
                            big_value=bigger_meter_values[i]
                            if  (type(small_value) in [int,float] and type(big_value) in [int,float] and small_value > big_value):
                                self.print_log("{}: In row {} the value of column {} is bigger than the value in column {}.\n".format(sheet_name,i+1,pairs[0],pairs[1]))
                                pass_test=False
                cursor.close()
                return(pass_test)
                                
            def check_regions_exist():
                """Checks that all the regions in the sheet exist and
                are in the same order than in the database."""
                pass_test=True
                cursor=self.conn.cursor()
                cursor.execute("SELECT ADM_NAME FROM REGIONS WHERE CO_CODE=?;",(self.country_code,))
                regions=list(map( lambda x: x[0], cursor.fetchall() ))
                query="SELECT Tab, EXL_REF FROM RM_MAPPING WHERE Tab in (" + ','.join('?'*len(edit_sheets_names)) + ") AND AC='ADM_NAME';"
                cursor.execute(query, edit_sheets_names )
                regions_excel=cursor.fetchall()
                database_regions=self.get_regions()
                if (not database_regions):
                    return(False)
                for sheet_name,coordinates in regions_excel:
                    sheet=self.wb.sheet_by_name(sheet_name)
                    regions_starting_coordinates = indexes(coordinates)
                    sheet_region_names = sheet.col_values(regions_starting_coordinates[1],
                                                    regions_starting_coordinates[0],
                                                    regions_starting_coordinates[0]+self.nadm1)
                    for region in sheet_region_names:
                        if (not region in database_regions.keys()):
                            self.print_log("Region {} in sheet {} is not in the database.\n".format(region,sheet_name ))
                            pass_test=False
                        elif(sheet_region_names[database_regions[region]-1] != region  ):
                            self.print_log("The order of the regions in the sheet does not match the order in the database..\n")
                            pass_test=False
                cursor.close()
                return(pass_test)
            
            def check_region_totals():
                """Check that the regional numbers match the total."""                
                cursor=self.conn.cursor()
                pass_test=True
                cursor.execute("SELECT Tab,EXL_REF,RM_TABLE,Col FROM RM_MAPPING;") 
                mapping_info=cursor.fetchall()
                for variables in mapping_info:                
                    tab=variables[0]
                    if tab not in edit_sheets_names:
                        continue
                    exl_ref=variables[1]
                    table=variables[2]
                    col=variables[3]
                    sheet = self.wb.sheet_by_name(tab)
                    meter_starting_coordinates = indexes(exl_ref)
                    ## Regional values
                    meter_values = sheet.col_values(meter_starting_coordinates[1],\
                                                        meter_starting_coordinates[0],\
                                                        meter_starting_coordinates[0]+self.nadm1)
                    ## Country value
                    meter_value_country=sheet.cell( meter_starting_coordinates[0]+self.nadm1+1,\
                                                        meter_starting_coordinates[1]).value
                    ## If there are missing values or references we do not
                    ## make any check.
                    all_numbers = reduce(lambda x,y: x and y,
                        map( lambda x: x in [int,float], 
                             map(lambda x: type(x) , meter_values))
                        )
                    if (all_numbers):
                        regions_sum=reduce(lambda x,y : x+y, meter_values)
                        if (regions_sum != meter_value_country):
                            ## Error para el log
                            self.print_log("The regional figures do not add up to the country total in {0} column {1}\n".format(table,col))
                            pass_test=False
                cursor.close()
                return(pass_test) 

        return( check_regions_exist() and check_less() and  check_region_totals() )
            
                           
    def emc_id_from_cell_info(self,sheet_name,xlrd_vector_coordinates):
        """Returns the emc_id given cell xlrd coordinates.

        xlrd_vector_coordinates should be a list with the xlrd
        coordinates.
        sheet_name is the name of the sheet in wich the cell is.
        """
        excel_ref=indexes_inverse(xlrd_vector_coordinates)
        row=xlrd_vector_coordinates[0]
        col_ref=None
        # col_ref contains the EXL_REF that can be found in the
        # Rm_Mapping table.
        if (sheet_name=="Pupils" and ( (row>= 17 and row<=17+self.nadm1) or row==19+self.nadm1)  ):
            col_ref=re.sub("[0-9]+","18",excel_ref )            
        elif ( (row>= 18 and row<=18+self.nadm1) or row==20+self.nadm1)   :
            col_ref=re.sub("[0-9]+","19", excel_ref )
        cursor=self.conn.cursor()
        cursor.execute("SELECT EMC_ID FROM RM_Mapping WHERE EXL_REF = '{0}' AND Tab = '{1}' ;".format(col_ref,sheet_name ) )
        emc_id=cursor.fetchone()
        if emc_id:
            emc_id=emc_id[0]
        cursor.close()
        return(emc_id)

    def extract_comments(self):
        """Writes the cell comments to the comments table
        """
        # Tuple of tuples with the information of the data Each entry
        # will be (emc_id,co_code,adm_code,emco_year,comments)

        # Missing: Check that the comment sould be in the meters
        cursor=self.conn.cursor()
        comments_table_tupple=()        
        for sheet in self.wb.sheets():
            for xlrd_coord in sheet.cell_note_map.keys():
                emc_id=self.emc_id_from_cell_info(sheet.name, xlrd_coord )
                if emc_id:
                    emco_year=self.emco_year
                    cursor.execute("SELECT RM_TABLE FROM RM_Mapping WHERE EMC_ID={0} limit 1;".format(emc_id))
                    table=float( cursor.fetchone()[0][5:] )
                    if (sheet.name== "Pupils"):
                        adm_code=xlrd_coord[0]-16
                    else:
                        adm_code=xlrd_coord[0]-17
                        if (emc_id in [20162,20166,20172,20184]  and  xlrd_coord ==  21 ):
                            emco_year= emco_year - 1
                    comment=sheet.cell_note_map[xlrd_coord].text
    #                comments_table_tupple=comments_table_tupple + ( (emc_id,self.country_code,adm_code,emco_year,comment) , )
                    comments_table_tupple=comments_table_tupple + ( (self.country_code,adm_code,emco_year, emc_id,comment,table) , )
        if comments_table_tupple:
            cursor.executemany("INSERT OR REPLACE INTO EDU_FTN97_REP VALUES(?,?,?,?,1,?,?,'R',NULL,NULL);", comments_table_tupple )
            self.conn.commit()
        cursor.close()
                
    
    def create_region_codes(self):
        """Writes the region codes to the regions database.
        """
        # LOG DATABASE
        cursor=self.conn.cursor()
        administrative_divisions_variables=pre_vars['fixed_sheets']['Administrative divisions']
        sheet=self.wb.sheet_by_name('Administrative divisions')
        id_start_coordinates=indexes( administrative_divisions_variables['id_start'][0])    
        regions_index=list(map(int,sheet.col_values(id_start_coordinates[1],\
                                                        id_start_coordinates[0],\
                                                        id_start_coordinates[0]+self.nadm1)))
        regions_names=sheet.col_values(id_start_coordinates[1]+1,\
                                           id_start_coordinates[0],\
                                           id_start_coordinates[0]+self.nadm1)
        sql_values=tuple(map(lambda x,y,z: (x,y,z), [self.country_code] * self.nadm1 , regions_index, regions_names  ))
        cursor.executemany("INSERT OR REPLACE INTO REGIONS VALUES(?,?,?);",sql_values)
        self.conn.commit()
        cursor.close()
        
    def get_regions(self):
        """Returns a dictionary with region name and code as key and value respectively.

        The regions are read from the database. If no regions are
        found in the database, this function returns False.
        """
        cursor=self.conn.cursor()
        cursor.execute("SELECT ADM_NAME,ADM_CODE FROM REGIONS WHERE CO_CODE=? AND ADM_CODE!=0 ;",(self.country_code,) )
        sql_return=cursor.fetchall()        
        cursor.close()
        if sql_return:
            return(dict(sql_return))
        else:
            return(False)
 
    def extract_table_comments(self):
        """Extract the comments from the top of each table.
        
        This function cannot be used with the edit mode.
        """
        cursor=self.conn.cursor()
        comments_data=()
        cursor.execute("SELECT * FROM RM_Mapping_NonNumeric WHERE AC=\"Table_COMM\"")
        comments_info=cursor.fetchall()
        for variables in comments_info:
            tab=variables[0]
            rm_table=variables[1]
            exl_ref=variables[3]
            sheet = self.wb.sheet_by_name(tab)
            comments=sheet.cell(*indexes(exl_ref)).value
            if comments not in ["Emter commemt here","Enter comment here"]:
                comments_data=comments_data + ( (self.country_code,self.emco_year,rm_table,comments  ),   )
        cursor.executemany("INSERT OR REPLACE INTO EDU_COMMENT_TABLE_REP VALUES(?,?,?,?);",comments_data)
        self.conn.commit()
        cursor.close()

    def extract_data(self,write_csv_files=False,write_sql=True):
        """Reads and exports the data of the questionnaire

        If the argument write_sql is True, it will import all the data
        to the sql database.
        
        If the argument write_csv_files is True, it will write 3
        files. All of them in the folder imported_data. Let C be the
        country code. The files will be: C_meters_data.csv,
        C_inclu_data.csv and C_references.sql. 

        C_meters_data.csv will have a csv files with the entries to
        the meters table that correspond to the data being read.

        C_inclu_data.csv will have the entries that go to the inclu
        table, i.e., the fields that are begin referenced.

        C_references.sql will have sql code that sets the mg_id of the
        referenced cells to 4. 

        If both csv files are imported in the sql tables and then the
        sql code in C_references.sql was run it would be equivalent to
        what this function adds to the sql tables when write_sql is
        set to True.
        """
        cursor=self.conn.cursor()
        # Tupples that will contain all the data
        meters_data=()
        inclu_data=()
        # For the sql file we use a set in order to avoid repetitions
        referenced_sql_code=set()
        ## The following local function writes the csv files
        def export_to_csv_files():
            meters_file=open("imported_data/"+str(self.country_code)+"_meters_data.csv",'w')
            inclu_file=open("imported_data/"+str(self.country_code)+"_inclu_data.csv",'w')
            sql_file=open("imported_data/"+str(self.country_code)+"_references.sql",'w')            
            inclu_file.write("CO_CODE,EMCO_YEAR,ADM_CODE,EMC_ID,DESC_INCLU,EC_TD_ID\n")
            meters_file.write("EMC_ID,CO_CODE, ADM_CODE, EMCO_YEAR,EAG_AGE,ST_ID,ABE_ID,MQ_ID,MG_ID,EM_FIG,EC_TD_ID,NOTEYESNO\n")
            for var in meters_data:
                meters_file.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(*var))
            for var in inclu_data:
                inclu_file.write("{0},{1},{2},{3},{4},{5}\n".format(*var))
            for var in referenced_sql_code:
                sql_file.write(var)    
            meters_file.close()
            inclu_file.close()
            sql_file.close()

        def export_to_sqlite():
            # LOG DATABASE
            cursor=self.conn.cursor()
            cursor.executemany("INSERT OR REPLACE INTO EDU_METER97_REP VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",meters_data)
            cursor.executemany("INSERT OR REPLACE INTO EDU_INCLUSION_REP VALUES(?,?,?,?,?,?);",inclu_data)
            for var in referenced_sql_code:
                cursor.execute(var)
            self.conn.commit()
            cursor.close()

        def backup_imported_questionnaire():
            """Puts a copy of the questionnaire in the imports folder.
            """
            import_folder="./import"
            if (not os.path.exists(import_folder)):
                os.makedirs(import_folder)
            shutil.copy(self.excel_file,"./import/RM_{}_{}_{}.xlsx".format(self.country_name,self.emco_year,datetime.datetime.now().strftime("%y-%m-%d-%H-%M")))
            

        # RM_TABLE is necessary for finding the xlrd coordinates
        cursor.execute("SELECT TAB, EXL_REF, EMC_ID,RM_TABLE,Col FROM RM_MAPPING;") 
        mapping_table = cursor.fetchall()
        if self.edit_mode:
            edit_sheets_names=self.wb.sheet_names()
        else:
            self.create_region_codes()
        for variables in mapping_table:
            # When we edit we are only interested in certain sheets
            if self.edit_mode and variables[0] not in edit_sheets_names:
                continue
            # No region names in the meters table:
            if variables[2]==900002:
                continue
            ## The emco_year that is entered is the one of the table
            ## minus 1 for certain fields:
            if variables[2] in [20162,20166,20172,20184] and variables[4]==15:
                emco_year=self.emco_year - 1
            else:
                emco_year=self.emco_year
            sheet = self.wb.sheet_by_name(variables[0])
            # We read the starting excel coordinates
            meter_starting_index = variables[1]
            # We get the starting coordinates for xlrd
            meter_starting_coordinates = indexes(meter_starting_index)
            # We read the figures for all the regions
            meter_values = sheet.col_values(meter_starting_coordinates[1],\
                                          meter_starting_coordinates[0],\
                                          meter_starting_coordinates[0]+self.nadm1)
            # We read the figure for the country
            meter_value_country=sheet.cell( meter_starting_coordinates[0]+self.nadm1+1,\
                                            meter_starting_coordinates[1]).value
            # We put the country value at the beginning so it can be
            # imported to sql in a natural way (the adm code of the
            # country is 0).
            meter_values=[meter_value_country]+meter_values
            for i in range(self.nadm1+1):
                adm_code=i
                reference=is_reference(meter_values[i])
                if reference!=None: # If there is a reference
                    em_fig=""
                    inclu_data=inclu_data+((self.country_code,\
                                            emco_year,\
                                            adm_code,\
                                            variables[2],\
                                            meter_values[i],\
                                            ec_td_id(variables[0]) ),)
                    if reference[0]==None: # First reference coordinate empty
                        ## Same row if a=None in X[a:b]
                        referenced_row=adm_code
                    else:
                        referenced_row=reference[0]
                    referenced_sql_code= referenced_sql_code | {"UPDATE EDU_METER97_REP SET MG_ID=4 WHERE EMC_ID={0} AND CO_CODE={1} AND ADM_CODE={2} AND EMCO_YEAR={3};\n".format(self.emc_id(variables[3],reference[1]),self.country_code,referenced_row,emco_year)}
                else: # If we did not read a reference
                    em_fig=meter_values[i]
                # The following if might not be necessary in the final version
                if type(em_fig)==str:
                    em_fig=""
                meters_data=meters_data + (( variables[2],\
                                             self.country_code,\
                                             adm_code,\
                                             emco_year,\
                                             "",\
                                             1,\
                                             "",\
                                             "",\
                                             mg_id(meter_values[i]),\
                                             em_fig,\
                                             ec_td_id(variables[0]),\
                                             ""),)
        if write_csv_files:
            export_to_csv_files()
        if write_sql:
            export_to_sqlite()
        backup_imported_questionnaire()
        cursor.close()
        
    def __init__(self,excel_file,database_file="../Database/UISProd.db",log_folder="/tmp/log"):
        """Set up variables for questionnaire and database reading"""                
        self.excel_file=excel_file
        self.set_workbook(excel_file)
        self.edit_mode= not 'Checking sheet' in self.wb.sheet_names()
        self.set_database_connection(database_file)
        self.get_emco_year()
        self.get_nadm1()
        self.get_country_name()
        self.get_country_code()
        if (not os.path.exists(log_folder)):
            os.makedirs(log_folder)
        self.log_file=open( log_folder + "/{}".format(self.country_name) + ".log",'a')

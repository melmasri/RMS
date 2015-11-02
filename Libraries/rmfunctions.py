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
# conn = sqlite3.connect('../../Database/Prod.db')
# #Uncomment the line below for creating virtual database
# #createDb = sqlite3.connect(":memory:")
# #creates the cursor object for SQL queries
# database_cursor = conn.cursor()
# # Path to the variable mapping file(json) format.
# mapping_file_json="./variables_for_preprocessing.json"
# # Read the json file and put the contents in the dictionary pre_vars

# with open(mapping_file_json) as f:
#     pre_vars=json.loads(f.read())

# if ( re.search('\\\\Tests\\\\mo$',os.getcwd()) or re.search('/Tests/os$',os.getcwd()) or
     # re.search('/Tests/mo$',os.getcwd())   ):
#     with open("../../Libraries/variables_for_preprocessing.json") as f:
#         pre_vars=json.loads(f.read())
# else:
with open("Libraries/variables_for_preprocessing.json") as f:
    pre_vars=json.loads(f.read())

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
    """This function returns a country code given the long or short name.
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
    If the  country name is found it returns it, otherwise it returns None.
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
               "WHERE UPPER(B.CO_SHORT_NAME) IS '{0}' and A.EMC_ID= 900001".format(name)) #900001 == Pop.Ag0t99
    code = sql_query(sql_str)   
    if code:
        return(list(chain.from_iterable(code)))

####DATA INSERTION
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
def moveSerie(co_code, year, from_serie, to_serie):
    """A function that moves data between series. From REP to OBS for example. 
       So far, it modifies the following 3 SQL table:
        1 - EDU_METER97_{}
        2 - EDU_INCLUSION{}
        3 - EDU_FTN97_{}
        4 - EDU_COMMENT_TABLE_{}
"""
    ### Move EDU_METER97
    ## Current year
    print('Moving data for {0}-{1}'.format(co_code, year))
    ### Deleting existing data
    sql_query("DELETE FROM EDU_FTN97_{0} where CO_CODE ={1} and EMCO_YEAR = {2} and EMC_ID in (select EMC_ID from RM_Mapping)".format(to_serie, co_code,year))
    sql_query("DELETE FROM EDU_INCLUSION_{0} where CO_CODE ={1} and EMCO_YEAR = {2} and EMC_ID in (select EMC_ID from RM_Mapping)".format(to_serie, co_code,year))
    for ind in [0,-1]:
        meter = ("INSERT OR REPLACE INTO EDU_METER97_{3} "
                 "SELECT a.* FROM RM_Mapping as b "
                 "left join EDU_METER97_{2} as a on a.EMC_ID = b.EMC_ID and b.CUR_YEAR ={4} "
                 "where a.co_code ={0} "
                 "and a.EMCO_YEAR ={1}".format(co_code, year + ind, from_serie, to_serie,ind))
        ### Moving EDU_INCLUSION
        ### Current year
        inclu= ("INSERT OR REPLACE INTO EDU_INCLUSION_{3} "
                "SELECT a.* FROM RM_Mapping as b "
                "join EDU_INCLUSION_{2} as a on a.EMC_ID = b.EMC_ID and b.Cur_Year = {4} "
                "where a.co_code ={0} "
                "and a.EMCO_YEAR ={1}".format(co_code, year + ind, from_serie, to_serie,ind))
        ### Current year
        ftn = ("INSERT OR REPLACE INTO EDU_FTN97_{3} "
               "SELECT a.* FROM RM_Mapping as b "
               "left join EDU_FTN97_{2} as a on a.EMC_ID = b.EMC_ID and b.CUR_YEAR = {4} "
               "where a.co_code = {0} "
               "and a.EMCO_YEAR = {1}".format(co_code, year + ind, from_serie, to_serie,ind))
        sql_query(meter,False)
        sql_query(inclu, False)
        sql_query(ftn,False)

    print("Moved METER, INCLU and FTN tables from {0} to {1}".format(from_serie, to_serie))

    ### Moving EDU_COMMENT_TABLE
    ### Current year
    sql_query("DELETE FROM EDU_COMMENT_TABLE_{0} where CO_CODE ={1} and EMCO_YEAR = {2} and WT_NAME in (select RM_TABLE from RM_Mapping_NonNumeric)".format(to_serie, co_code,year))
    table_com = ("INSERT OR REPLACE INTO EDU_COMMENT_TABLE_{3} "
                 "SELECT a.* FROM RM_Mapping_NonNumeric as b "
                 "join EDU_COMMENT_TABLE_{2} as a on a.WT_NAME = b.RM_TABLE "
                 "where a.co_code = {0} "
                 "and a.EMCO_YEAR = {1}".format(co_code, year, from_serie, to_serie))
    sql_query(table_com, False)

    print("Moved COMMENT_TABLE table from {0} to {1}".format(from_serie, to_serie))
     

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

    It works for a maximum of two letters in the column name.
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
    match=re.search('[Xx]\[([0-9]*):([0-9]+)\]$|[Xx]',cell_value)
    if not (match==None):
        reference=list(match.groups())
        if reference[1]==None:
            return("empty_reference")
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


####DATA EXTRACTION CLASS
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------


class questionnaire:
    """Defines questionnaire properties and methods
    
    Attributes:
      wb = the workbook that correspond to the class.
      conn = connection object to the database
      emco_year = the emco_year read from the workbook.
      nadm1 =  number of administrative divisions in the file
      country_name = the name of the country that filled the questionnaire.
      country_code = the code of the country.
      edit_mode = True or False, whether the class if going to be used for editing existing data.
    """
    def set_workbook(self,excel_file):
        """Set the workbook

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
            try:
                self.nadm1 = sheet.cell( *indexes( administrative_divisions_variables['adm1_number'][0]  )   ).value
            except(IndexError):
                self.nadm1 = False
                
            if (type(self.nadm1) in [int,float] and self.nadm1>0 ):
                self.nadm1=int(self.nadm1)
            else:
                self.nadm1=False

    def get_country_name(self):
        """Sets the country name based on the front page of the questionnaire."""
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            self.country_name = sheet.cell( 0,1   ).value
        else:
            front_page_variables = pre_vars['fixed_sheets']['Front Page']
            sheet = self.wb.sheet_by_name('Front Page')
            self.country_name = sheet.cell( *indexes( front_page_variables['country_name'][0]  )   ).value
    
    def get_database_type(self):
        """Sets the database type (OBS,REP,EST) from the questionnaire."""
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            self.database_type = sheet.cell( 5,1 ).value
        else:
            self.database_type='REP'
            
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
            self.country_code=0
        else:
            self.country_code=country_code[0]
        cursor.close()

    def emc_id(self,table_name,column):
        """Returns the emc_id given then table and column number.
        """
        cursor=self.conn.cursor()
        cursor.execute("SELECT EMC_ID  FROM RM_MAPPING WHERE RM_TABLE=\"{0}\" AND Col={1};".format(table_name,column ) )
        return(cursor.fetchone()[0])
        
    def check_nadm1(self):
        """Checks that number of administrative divisions is filled with a positive integer. 
        """
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            nadm1= sheet.cell(4,1).value
            #print("nadm1: {0}\n".format(nadm1))
        else:
            administrative_divisions_variables = pre_vars['fixed_sheets']['Administrative divisions']
            sheet = self.wb.sheet_by_name('Administrative divisions')
            try:
                nadm1 = sheet.cell( *indexes( administrative_divisions_variables['adm1_number'][0]  )   ).value
            except(IndexError):
                nadm1 = False
        if( (type(nadm1) == int or type(nadm1) == float) and int(nadm1)==nadm1 and nadm1 > 0 ):
            self.print_log("Number of administrative divisions: {0}\n".format(nadm1))
            return(True)
        else:
            self.print_log("Error: Wrong value for number of administrative divisions.\n")
            return(False)

    def check_adm1_label(self):
        """Checks that the name of administrative divisions is given. """
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            nadm1= sheet.cell(4,1).value
            return(True)
        else:
            administrative_divisions_variables = pre_vars['fixed_sheets']['Administrative divisions']
            sheet = self.wb.sheet_by_name('Administrative divisions')            
            adm1_label = sheet.cell( *indexes( administrative_divisions_variables['adm1'][0]  )   ).value
        if( (type(adm1_label) == str) and adm1_label ):
            self.print_log("ADM1 name provided: {0}\n".format(adm1_label))
            return(True)
        else:
            self.print_log("Error: ADM1 name not provided.\n")
            return(False)

        
    def check_adm1_names(self):
        """Checks that the region names are filled.
        """
        if (self.edit_mode):
            return(True)
        elif (not self.nadm1):
            return(False)
        else:
            administrative_divisions_variables = pre_vars['fixed_sheets']['Administrative divisions']
            sheet=self.wb.sheet_by_name('Administrative divisions')
            id_start_coordinates=indexes( administrative_divisions_variables['id_start'][0])
            regions_names=sheet.col_values(id_start_coordinates[1]+1,\
                                           id_start_coordinates[0],\
                                           id_start_coordinates[0]+self.nadm1)
            all_regions_good=reduce( lambda x,y: x and y,
                                     ##The following line tests wether it is not empty and different that ...
                                     map( lambda region_name: region_name and region_name != "..." , 
                                          regions_names))
            if (all_regions_good):
                self.print_log("Administrative divisions:\n")
                for region in regions_names:
                    self.print_log("                  {}\n".format(region))
                self.print_log("\n")
            else:
                self.print_log("Error: Empty names for administrative divisions.")
            return(all_regions_good)

    def check_reference_year(self):
        """Checks that the reference year is filled with the right value"""
        if (self.edit_mode):
            return(True)
        else:
            sheet=self.wb.sheet_by_name('Policy information')
            reference_year=sheet.cell(*indexes('M15')).value
            test_value= type(reference_year) == float or type(reference_year) == int
            if (test_value):
                self.print_log("Reference year: {0}\n".format(int(reference_year)))
            else:
                self.print_log("Error: Reference year not filled.\n")
            return(test_value)

    def check_country_name(self):
        """Checks if the country name is filled"""
        if (self.edit_mode):
            return(True)
        else:
            front_page_variables=pre_vars['fixed_sheets']['Front Page']
            cellname=front_page_variables['country_name'][0]
            sheet=self.wb.sheet_by_name('Front Page')
            country_name=sheet.cell(*indexes(cellname)).value
            test_value=sheet.cell_type( *indexes(cellname) ) == front_page_variables['country_name'][1]
            code_test=self.country_code
            if (not test_value ):
                self.print_log("Error: Country name is not filled or has a wrong format.\n")
            elif(not code_test ):
                self.print_log("Error: Country name was not found in the database.\n")
            else:
                self.print_log("Country name is filled: {0}\n".format(country_name))
            return(test_value and code_test)
        
    def check_number_of_sheets(self):
        if (self.edit_mode):
            return(True)
        else:
            if pre_vars['nsheets']==self.wb.nsheets:
                self.print_log("The correct number of sheets"+ "({})".format(self.wb.nsheets) +"has been submited.\n")
                return(True)
            else:
                self.print_log("Error: Incorrect number of sheets submited\n")
                return(False)
            
    def check_edited_configuration_part(self):
        """This functions checks that the table in the top left corner of
        the sheet exists in an edited questionnaire.
        """
        if (self.edit_mode):
            sheet=self.wb.sheets()[0]
            configuration_names=sheet.col_values(0,0,6) # names in the configuration (country, co_code, year,etc.). i.e. first column
            configuration_values=sheet.col_values(1,0,6) # values of the configuration, i.e. second column
            # test1 is to check if the names coincide with the exported ones
            test1= configuration_names == ['Country', 'CO_CODE', 'Year', 'Data', 'No.ADM', 'Series']
            # test2 os to check that the values are not empty (May be it could be improved). 
            test2=reduce( lambda x,y: x and y, configuration_values)
            test_value=test1 and test2
            if (test_value):
                self.print_log("Configuration section of edited questionnaire is properly filled\n")
            else:
                self.print_log("Error: Configuration section has wrong values.")
            return(test_value)
        else:
            return(True)


    def check_one_value(self,value):
        """Checks that value (the argument) is proper.
        
        This function can return three values:
        0 if there is an error.
        1 if the value is OK.
        2 accept but write error (A or N).
        3 if there is an X with no reference.
        4 if there is a missing value.
        """
        return_value=0
        if((type(value) == int or type(value) == float)  and value >=0  ):
            return_value=1
        elif(type(value) == str):
            #Accept regexp
            match1=re.search('[Xx]\[[0-9]*:[0-9]+\]|^ +$|^[Zz]$',value)
            # Accept with error regexp
            match2=re.search('[Aa]$|^[Nn]$',value)
            # Undefined reference
            match3=re.search('^[Xx] *$',value)
            # Missing value
            match4=re.search('^ *$|^[Mm] *',value)            
            if ( not (match1==None) ):
                return_value=1 
            elif ( not (match2==None) ):
                return_value=2
            elif ( not (match3==None) ):
                return_value=3
            elif ( not (match4==None) ):
                return_value=4                
        return(return_value)
    
    def add_missing_column(self,sheet_name,table,column):
        """Adds a columns to the missing values dictionary."""
        if (sheet_name in self.missing_data_dictionary.keys()):
            existing_tables_dict=self.missing_data_dictionary[sheet_name]
            if (table in existing_tables_dict):
                ## Checks go column by column, so it is not necessary
                ## to check if a column has already been added ot to
                ## use sets.
                existing_tables_dict[table]= existing_tables_dict[table] + [column]
            else:
                existing_tables_dict[table]=[column]
        else:
            self.missing_data_dictionary[sheet_name]={table:[column]}

    def add_data_issues(self,sheet_name,table,issue_type,relevant_data):
        """Adds information to the data issues dictionary.
        

        There are 4 types of data issues: 'undefined_reference','check_less','column_sums','region_totals'.
        
        For 'check_less' relevant_data is [smaller_column bigger_column [ list of rows with problems] ].
        For 'undefined_reference' it is the column number.
        For 'column_sums' [[summands_columns],total_column,[row_problems]]
        For 'region_totals' it is the column number
        """
        if (sheet_name in self.data_issues_dictionary.keys()):
            existing_tables_dict=self.data_issues_dictionary[sheet_name]
            if (table in existing_tables_dict.keys()):
                existing_issues_dict=existing_tables_dict[table]
                if (issue_type in existing_issues_dict.keys() ):
                    existing_issues_dict[issue_type] = existing_issues_dict[issue_type] + [relevant_data]
                else:
                    existing_issues_dict[issue_type] = [relevant_data]
            else:                
                existing_tables_dict[table] = {issue_type : [relevant_data]}
        else:## sheet_name in dictionay
            self.data_issues_dictionary[sheet_name] = {table : { issue_type: [relevant_data]}}

        
    def check_values(self):
        edit_sheets_names=self.wb.sheet_names()
        cursor=self.conn.cursor()
        query="SELECT Tab,EXL_REF,RM_TABLE,Col FROM RM_MAPPING WHERE Tab in (" + ','.join('?'*len(edit_sheets_names)) + ") AND AC!='ADM_NAME';"
        #self.print_log("Checking that all the values are proper...") 
        cursor.execute(query, edit_sheets_names )
        mapping_table = cursor.fetchall()
        overall_test=1
        overall_missing=False
        overall_undefined_references=False
        for variables in mapping_table:
            table=variables[2]
            col_number=variables[3]
            sheet = self.wb.sheet_by_name(variables[0])
            meter_starting_index = variables[1]
            meter_starting_coordinates = indexes(meter_starting_index)
            ## We read the values for the regions
            meter_values = sheet.col_values(meter_starting_coordinates[1],\
                                            meter_starting_coordinates[0],\
                                            meter_starting_coordinates[0]+self.nadm1)
            ## We read the country value.
            meter_value_country=sheet.cell( meter_starting_coordinates[0]+self.nadm1+1,\
                                            meter_starting_coordinates[1]).value
            meter_values=[meter_value_country]+meter_values
            # The following will be zero if there is at least one
            # error. 1 if everything is ok and 2 id there is at least one A or N.
            values_test=list(map( self.check_one_value,meter_values ))
            no_errors_test= 0 not in values_test
            if (0 in values_test):
                self.print_log("Error: Column {0} in table {1} has improper values.\n".format(col_number,table))
            if (2 in values_test):
                self.print_log("Error: Column {0} in table {1} has at least one A or N.\n".format(col_number,table))
            if (3 in values_test):
                #self.print_log("Error: Column {0} in table {1} has at least one undefined reference.\n".format(col_number,table))
                overall_undefined_references=True
                self.add_data_issues(variables[0],table,'undefined_reference',col_number )
            if (4 in values_test):
                #self.print_log("Error: Column {0} in table {1} has at least one missing value.\n".format(col_number,table))
                overall_missing=True
                self.add_missing_column(variables[0],table,col_number)
                # Next, add option for X.
                
            overall_test=overall_test and no_errors_test
        if overall_missing:
            self.print_log("Warning: The questionnaire contains missing values.\n")
        if overall_undefined_references:
            self.print_log("Warning: The questionnaire contains undefined references.\n")
        return(overall_test)
    
    def print_log(self,text_string,log_type=False):
        """Puts the test in log and stdout.

        if log_type=False, it writes to the validation log
        if log_type=True (the default) , it writes sys.stdout using print
        """
        print(text_string,end='')
        if (not log_type):            
            self.validation_log_file.write(text_string)
            self.validation_log_file.flush()
            os.fsync(self.validation_log_file.fileno())
        # else:
            # self.error_log_file.write(text_string)
            # self.error_log_file.flush()
            # os.fsync(self.error_log_file.fileno())

                

    def validation(self):
        check_variables=pre_vars["Checking sheet"]
        self.print_log("----------"+"Date: "+datetime.datetime.now().strftime("%B %d, %Y")+"----------\n")
        self.print_log("VALIDATION STEP\n\n")
        if (not self.edit_mode):
            self.print_log("Original questionnaire submited with path:\n")
            self.print_log(self.excel_file+"\n\n")
            administrative_divisions_variables=pre_vars['fixed_sheets']['Administrative divisions']
        else:
            self.print_log("Edited questionnaire submited with path:\n")
            self.print_log(self.excel_file+"\n\n")

        nadm1_test=self.check_nadm1()
        adm1_label_test=self.check_adm1_label()
        adm1_names_test=self.check_adm1_names()
        reference_year_test=self.check_reference_year()
        country_name_test=self.check_country_name()
        number_of_sheets_test=self.check_number_of_sheets()
        edited_configuration_part_test=self.check_edited_configuration_part()
        values_test=self.check_values()
        print("\n----------Questionnaire Validation finished.----------.\n")
        self.validation_log_file.close()
        return ( nadm1_test and adm1_label_test and adm1_names_test and reference_year_test and country_name_test and number_of_sheets_test and edited_configuration_part_test and values_test )

    def check_region_totals(self):
        """Check that the regional numbers match the total."""                
        cursor=self.conn.cursor()
        edit_sheets_names=self.wb.sheet_names()
        pass_test=True
        self.print_log("Checking that region values add to the country value...", True)
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
                    if pass_test:
                            self.print_log("\n", True)
                    self.add_data_issues(tab,table,'region_totals',col)
                    self.print_log("The regional figures do not add up to the country total in {0} column {1}\n".format(table,col), True)
                    pass_test=False
        cursor.close()
        if  pass_test :
            self.print_log("Test passed.\n", True)                        
        return(pass_test)

    def check_less(self):
        """Checks that the pairs from the
        check_less_dictionary satisfy that the first one is
        smaller than the second one"""
        check_less_dictionary={
            ## All the inequalities correspond to the first table
            'Table 0.1' : [ [16,14], [17,15], [13,12] ],
            'Table 1.1' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ],
            'Table 2.1' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ],
            'Table 3.1' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ],
            'Table 4.1' :[ [4,3], [6,5],[8,7],[10,9],[12,11],[14,13] ]
        }
        table_sheet_dictionary={
            'Table 0.1' : 'Pupils' ,
            'Table 1.1' : 'Teachers ISCED 1' ,
            'Table 2.1' : 'Teachers ISCED 2' ,
            'Table 3.1' : 'Teachers ISCED 3' ,
            'Table 4.1' : 'Teachers ISCED 23'
        }
        cursor=self.conn.cursor()
        pass_test=True
        self.print_log("Checking that parts are less than the totals...", True)
        for table,pairs_list in check_less_dictionary.items():
            sheet_name=table_sheet_dictionary[table]
            if sheet_name not in self.wb.sheet_names():
                continue
            sheet=self.wb.sheet_by_name(sheet_name)
            for pairs in pairs_list:
                cursor.execute("SELECT EXL_REF FROM RM_MAPPING WHERE RM_TABLE=\'{}\' AND Col={}".format(table,pairs[0]))
                ref_smaller=cursor.fetchone()[0]
                cursor.execute("SELECT EXL_REF FROM RM_MAPPING WHERE RM_TABLE=\'{}\' AND Col={}".format(table,pairs[1]))
                ref_bigger=cursor.fetchone()[0]
                smaller_meter_starting_coordinates = indexes(ref_smaller)
                bigger_meter_starting_coordinates = indexes(ref_bigger)
                smaller_meter_values=sheet.col_values(smaller_meter_starting_coordinates[1],
                                                      smaller_meter_starting_coordinates[0],
                                                      smaller_meter_starting_coordinates[0]+self.nadm1)
                bigger_meter_values=sheet.col_values(bigger_meter_starting_coordinates[1],
                                                      bigger_meter_starting_coordinates[0],
                                                      bigger_meter_starting_coordinates[0]+self.nadm1)
                rows_with_problem=[]
                for i in range(self.nadm1):
                    ## Error para el log
                    small_value=smaller_meter_values[i]
                    big_value=bigger_meter_values[i]
                    if  (type(small_value) in [int,float] and type(big_value) in [int,float] and small_value > big_value):
                        rows_with_problem=rows_with_problem+[i+1]
                        if pass_test:
                            self.print_log("\n", True)
                        self.print_log("{}: In row {} the value of column {} is bigger than the value in column {}.\n".format(sheet_name,i+1,pairs[0],pairs[1]), True)
                        pass_test=False
                if rows_with_problem:
                    self.add_data_issues(sheet_name, table,'check_less',[pairs[0],pairs[1],rows_with_problem ])
                    
        cursor.close()
        if  pass_test :
            self.print_log("Test passed.\n", True)                        
        return(pass_test)


    def add_values(self,x,y):
        """If both x and y are numbers returns their sum. Otherwise the value of one of them."""        
        if ( type(x) in [int,float] and type(y) in [int,float]):
            return(x+y)
        elif( type(x) not in [int,float] ):
            return(x)
        else:
            return(y)

    def are_equal(self,x,y):
        """Checks is x and y are equal numbers. 

        Returns True if both x and y are numbers and they are equal or
        if at least one of the values is not a number. Otherwise it
        returns False.
        """
        if ( ( (type(x) in [int,float] ) and (type(y) in [int,float]) and x==y) or ( (type(x) not in [int,float] ) or (type(y) not in [int,float])    )   ):
            return(True)
        else:
            return(False)
        
    def check_column_sums(self):
        """Checks columns that have to add up to other columns"""
        check_columns_sums_dictionary={
            ## Each item has two items. The first item is a list whose
            ## terms have to add up to the second item
            'Table 1.1' : [ [[20,21,22],3 ],[[23,24,25],7]  ],
            'Table 2.1' : [ [[26,27,28],3] , [[29,30,31],7 ] ],
            'Table 3.1' : [ [[26,27,28],3] , [[29,30,31],7 ] ],
            'Table 4.1' : [ [[26,27,28],3] , [[29,30,31],7 ] ],
            'Table 1.2' : [ [[3,4,5,6,7,8,9,10],3 ],[[11,12,13,14,15,16,17,18],7 ],[ [19,20,21,22,23,24,25,26],11 ]  ],
            'Table 2.2' : [ [[3,4,5,6,7,8,9,10],3 ],[[11,12,13,14,15,16,17,18],7 ],[ [19,20,21,22,23,24,25,26],11 ]  ],
            'Table 3.2' : [ [[3,4,5,6,7,8,9,10],3 ],[[11,12,13,14,15,16,17,18],7 ],[ [19,20,21,22,23,24,25,26],11 ]  ],
            'Table 4.2' : [ [[3,4,5,6,7,8,9,10],3 ],[[11,12,13,14,15,16,17,18],7 ],[ [19,20,21,22,23,24,25,26],11 ]  ],
            'Table 1.3' : [ [[3,5,6,7,8,9,10],3  ] , [[11,13,14,15,16,17,18],7] , [[19,21,22,23,24,25,26 ],11   ]  ],
            'Table 2.3' : [ [[3,5,6,7,8,9,10],3  ] , [[11,13,14,15,16,17,18],7] , [[19,21,22,23,24,25,26 ],11   ]  ],
            'Table 3.3' : [ [[3,5,6,7,8,9,10],3  ] , [[11,13,14,15,16,17,18],7] , [[19,21,22,23,24,25,26 ],11   ]  ],
            'Table 4.3' : [ [[3,5,6,7,8,9,10],3  ] , [[11,13,14,15,16,17,18],7] , [[19,21,22,23,24,25,26 ],11   ]  ],
            'Table 1.4' : [ [[3,4,5,6,7,8,9],3], [ [10,11,12,13,14,15,16],7], [[17,18,19,20,21,22,23],11 ]  ],
            'Table 2.4' : [ [[3,4,5,6,7,8,9],3], [ [10,11,12,13,14,15,16],7], [[17,18,19,20,21,22,23],11 ]  ],
            'Table 3.4' : [ [[3,4,5,6,7,8,9],3], [ [10,11,12,13,14,15,16],7], [[17,18,19,20,21,22,23],11 ]  ],
            'Table 4.4' : [ [[3,4,5,6,7,8,9],3], [ [10,11,12,13,14,15,16],7], [[17,18,19,20,21,22,23],11 ]  ],
            }
        cursor=self.conn.cursor()
        pass_test=True
        self.print_log("Checking sums of columns...", True)
        for table_name,columns_sum_list in check_columns_sums_dictionary.items():
            cursor.execute("SELECT Tab  FROM RM_Mapping WHERE RM_TABLE=\'{}\' LIMIT 1".format(table_name))
            sheet_name=cursor.fetchone()[0]
            if sheet_name not in self.wb.sheet_names():
                continue
            sheet=self.wb.sheet_by_name(sheet_name)
            for columns_sum_info in columns_sum_list:
                summands_columns=columns_sum_info[0]
                total_column=columns_sum_info[1]
                ## We start by finding the totals
                
                ## First we accumulate the sums of the summans columns in a list
                accumulated_sum=[0]*self.nadm1
                for column_number in summands_columns:
                    cursor.execute("SELECT EXL_REF FROM RM_Mapping WHERE RM_TABLE=\'{}\' and Col=\'{}\'".format(table_name,column_number))
                    ref=cursor.fetchone()[0]
                    column_starting_coordinates= indexes(ref)
                    column_meter_values=sheet.col_values(column_starting_coordinates[1],
                                                         column_starting_coordinates[0],

                                                         column_starting_coordinates[0]+self.nadm1)
                    accumulated_sum=map(self.add_values, accumulated_sum,column_meter_values )
                ## Now we get the total values
                ## The total column is always in the first table of the sheet.
                total_table_name=table_name[0:8]+"1" 
                cursor.execute("SELECT EXL_REF FROM RM_Mapping WHERE RM_TABLE=\'{}\' and Col=\'{}\'".format(total_table_name,total_column))
                ref=cursor.fetchone()[0]
                column_starting_coordinates= indexes(ref)
                total_column_values=sheet.col_values(column_starting_coordinates[1],
                                                     column_starting_coordinates[0],
                                                     column_starting_coordinates[0]+self.nadm1)
                list_accumulated_sum=list(accumulated_sum)
                tests_vector=list(map( self.are_equal , list_accumulated_sum  , total_column_values ))
                rows_problem=[]
                for i in range(1,self.nadm1+1):
                    if (not tests_vector[i-1]):
                        rows_problem=rows_problem+[i]
                if rows_problem:
                    ## We need to add a second argument to print_log here.
                    self.add_data_issues(sheet_name,table_name,'column_sums',[summands_columns,total_column,rows_problem])
                    self.print_log("Columns {} in  {} do not add to column {} in {}. Problems in row(s) {}.\n".format(summands_columns,table_name,total_column,total_table_name,rows_problem), True)
                pass_test= (not rows_problem) and pass_test
        return(pass_test)

    def write_data_report(self):
        cursor=self.conn.cursor()
        data_report_path=self.log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+"_data_report.csv"
        self.data_report_file=data_report_path
        file=open(data_report_path,'a')
        if ( not (self.missing_data_dictionary or self.data_issues_dictionary ) ):
            file.write('No data issues were found.,')
        else:
            if self.missing_data_dictionary:
                file.write("1. Missing data:,\n\n")
                sheet_names_list=list(self.missing_data_dictionary.keys())
                sheet_names_list.sort()
                for sheet_name in sheet_names_list:                    
                    file.write("Sheet: {},\n".format(sheet_name))
                    table_list=list(self.missing_data_dictionary[sheet_name].keys())
                    table_list.sort()
                    for table in table_list :
                        cursor.execute("SELECT RM_TABLE_NAME FROM RM_Mapping WHERE RM_TABLE=?", (table,) )
                        table_name=cursor.fetchone()[0]
                        file.write(",\"{0}: {1}\",\n".format(table,table_name))
                        file.write(",\"Missing data in column(s) {}\",\n".format( self.missing_data_dictionary[sheet_name][table] ))
            file.write("\n\n")
            if self.data_issues_dictionary:
                file.write("2. Data Issues:,\n\n")
                for sheet_name in self.data_issues_dictionary.keys():
                    file.write("Sheet: {},\n".format(sheet_name))
                    for table in self.data_issues_dictionary[sheet_name].keys():
                        cursor.execute("SELECT RM_TABLE_NAME FROM RM_Mapping WHERE RM_TABLE=?", (table,) )
                        table_name=cursor.fetchone()[0]
                        file.write(",\"{0}: {1}\",\n".format(table,table_name))
                        for issue in self.data_issues_dictionary[sheet_name][table].keys():
                            if 'undefined_reference' == issue:
                                file.write(",\"Undefined reference(s) in column(s) {}.\",\n".format(self.data_issues_dictionary[sheet_name][table][issue]) )
                            elif 'region_totals' == issue:
                                file.write(",\"Regional values do not add up to country value in column(s) {}.\",\n".format(self.data_issues_dictionary[sheet_name][table][issue]) )
                            elif 'column_sums' == issue:
                                for relevant_data in self.data_issues_dictionary[sheet_name][table][issue]:
                                    summands=relevant_data[0]
                                    total_column=relevant_data[1]
                                    rows=relevant_data[2]
                                    file.write(",\"Column(s) {0} do not add up to column {1} on row(s) {2}.\",\n".format(summands,total_column,rows))
                            elif 'check_less' == issue:
                                for relevant_data in self.data_issues_dictionary[sheet_name][table][issue]:
                                    smaller_column=relevant_data[0]
                                    bigger_column=relevant_data[1]
                                    rows=relevant_data[2]
                                    file.write(",\"Value in column {0} is greater than value in column {1} on row(s) {2}.\",\n".format(smaller_column,bigger_column,rows))
        ## If it is an original questionnaire print in the data reports if there are nos.
        if(not self.edit_mode):
            check_variables=pre_vars["Checking sheet"]
            sheet=self.wb.sheet_by_name("Checking sheet")
            printed_main_message=False
            for sheet_name in check_variables.keys():
                for var in [[x, check_variables[sheet_name][1] ] for x in check_variables[sheet_name][0] ]:
                    if( sheet.cell( *var ).value == 'No' ):
                        if(not printed_main_message):                                                        
                            file.write("\n\nThe following items have No in the Checking sheet:\n")
                            printed_main_message=True
                        var[1]-=5
                        file.write("\"{0}:\", \"{1}\"\n".format( sheet_name, sheet.cell(*var).value ))
        cursor.close()
        file.close()
                           
    def emc_id_from_cell_info(self,sheet_name,xlrd_vector_coordinates):
        """Returns the emc_id given cell xlrd coordinates.

        xlrd_vector_coordinates should be a list with the xlrd
        coordinates.
        sheet_name is the name of the sheet in which the cell is.
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

        # Missing: Check that the comment should be in the meters
        cursor=self.conn.cursor()
        edu_table_name="EDU_FTN97_"+self.database_type
        for sheet in self.wb.sheets():
            cursor.execute("SELECT  {0}.CO_CODE,{0}.EMCO_YEAR,{0}.EMC_ID,RM_Mapping.Tab FROM {0} LEFT JOIN RM_MAPPING ON {0}.EMC_ID=RM_MAPPING.EMC_ID WHERE RM_Mapping.Tab=\"{3}\" AND ( ( {0}.EMCO_YEAR={1} AND RM_MAPPING.CUR_YEAR=0 ) OR ( {0}.EMCO_YEAR={2} AND RM_MAPPING.CUR_YEAR=-1) )".format(edu_table_name,self.emco_year,self.emco_year-1,sheet.name) )
            things_to_erase=cursor.fetchall()
            for values_to_erase in things_to_erase:
                cursor.execute("DELETE FROM EDU_FTN97_"+self.database_type+" WHERE CO_CODE={0} AND EMCO_YEAR={1} AND EMC_ID={2}".format(values_to_erase[0],values_to_erase[1],values_to_erase[2]))
                self.conn.commit()
                                       
        #delete from Authors where AuthorId=1        
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
                        if (emc_id in [20162,20166,20172,20184]  and  xlrd_coord[1] ==  21 ):
                            emco_year= emco_year - 1
                    comment=sheet.cell_note_map[xlrd_coord].text
                    if not self.edit_mode:
                        author=self.country_name
                    else:
                        author=sheet.cell_note_map[xlrd_coord].author
                    match=re.search('\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.*)',comment, re.MULTILINE|re.DOTALL)
                    if match==None:
                        date_string=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # We are not forced to use this format
                    else:
                        date_string=match.group(1)
                        comment=match.group(2)

                        
                    comments_table_tupple=comments_table_tupple + ( (self.country_code,adm_code,emco_year, emc_id,comment,table,author,date_string) , )
        if comments_table_tupple:
            cursor.executemany("INSERT OR REPLACE INTO EDU_FTN97_"+self.database_type+"(CO_CODE,ADM_CODE,EMCO_YEAR,EMC_ID,FTN_CODE,FTN_DATA,NTABLE,QUESTNAME,USERNAME,DATE_ADDED)" + " VALUES(?,?,?,?,1,?,?,'R',?,?);", comments_table_tupple )
            self.conn.commit()
        cursor.close()

    def read_regions_from_sheet(self):
        """Reads region names from the questionnaire.
        
        It reads the  region names from the  questoinnaire and creates
        the attribute self.regions_from_sheet containing the read names.
        """
        administrative_divisions_variables=pre_vars['fixed_sheets']['Administrative divisions']
        sheet=self.wb.sheet_by_name('Administrative divisions')
        id_start_coordinates=indexes( administrative_divisions_variables['id_start'][0])
        self.regions_from_sheet=sheet.col_values(id_start_coordinates[1]+1,\
                                                 id_start_coordinates[0],\
                                                 id_start_coordinates[0]+self.nadm1)

        
    def compare_region_names(self):
        """Compares region names in sheet and database.
        
        Returns 1 if regions do not exist in the database.  If they
        exist, returns True if names in the database are the same than
        in the sheet and False otherwise.

        """
        if (self.regions_from_sheet==None):
            self.read_regions_from_sheet()
        regions_from_database=self.get_regions()
        if (not regions_from_database):
            return(1)
        else:
            regions_from_database=list(map(str.upper,regions_from_database ))
            regions_from_sheet=list(map(str.upper, self.regions_from_sheet ))
            return ( regions_from_database == regions_from_sheet )
                            
    def insert_region_codes(self):
        """Writes the regions from the sheet to the regions database.

        If the regions exist already in the database they are rewriten.
        """
        cursor=self.conn.cursor()
        administrative_divisions_variables=pre_vars['fixed_sheets']['Administrative divisions']
        sheet=self.wb.sheet_by_name('Administrative divisions')
        id_start_coordinates=indexes( administrative_divisions_variables['id_start'][0])    
        regions_index=list(map(int,sheet.col_values(id_start_coordinates[1],\
                                                        id_start_coordinates[0],\
                                                        id_start_coordinates[0]+self.nadm1)))

        sql_values=tuple(map(lambda x,y,z: (x,y,z), [self.country_code] * self.nadm1 , regions_index, self.regions_from_sheet  ))
        cursor.executemany("INSERT OR REPLACE INTO REGIONS VALUES(?,?,?);",sql_values)
        self.conn.commit()
        cursor.close()
        
    def get_regions(self):
        """Returns a dictionary with region name and code as key and value respectively.

        The regions are read from the database. If no regions are
        found in the database, this function returns False.
        """
        cursor=self.conn.cursor()
        cursor.execute("SELECT ADM_NAME FROM REGIONS WHERE CO_CODE=? AND ADM_CODE>0 ORDER BY ADM_CODE ASC;",(self.country_code,) )
        sql_return=cursor.fetchall()
        cursor.close()
        if sql_return:
            sql_return=reduce(lambda x,y: x+y,sql_return)
            return(sql_return)
        else:
            return(False)
 
    def extract_table_comments(self):
        """Extract the comments from the top of each table.
        
        This function can also be used with the edit mode.
        """
        cursor=self.conn.cursor()
        comments_data=()
        cursor.execute("SELECT Tab,RM_TABLE,AC,EXL_REF FROM RM_Mapping_NonNumeric WHERE AC=\"Table_COMM\"")
        comments_info=cursor.fetchall()
        for variables in comments_info:
            tab=variables[0]
            if tab in self.wb.sheet_names():
                rm_table=variables[1]
                exl_ref=variables[3]
                sheet = self.wb.sheet_by_name(tab)
                comments=sheet.cell(*indexes(exl_ref)).value
                if comments not in ["Enter comment here","Enter comment here"]:
                    comments_data=comments_data + ( (self.country_code,self.emco_year,rm_table,comments  ),   )
                    cursor.executemany("INSERT OR REPLACE INTO EDU_COMMENT_TABLE_"+self.database_type+" VALUES(?,?,?,?);",comments_data)
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
            ## Copy old values from
            
            if self.edit_mode:
                cursor.execute("DELETE FROM METER_AUDIT_TEMP")
                for Table in self.wb.sheet_names():
                    cursor.execute(("INSERT INTO METER_AUDIT_TEMP (MC_ID, CO_CODE, ADM_CODE, MC_YEAR, "
                                   "EM_FIG_OLD, MQ_ID_OLD, MG_ID_OLD, USER_NAME, SERIES, SURVEY_ID) "
                                   "SELECT c.EMC_ID,c.CO_CODE, c.ADM_CODE, c.EMCO_YEAR,"
                                    "c.EM_FIG, c.MQ_ID, c.MG_ID, '{4}', '{5}', 'RM' from RM_MAPPING as a "
                                   "LEFT JOIN EDU_METER_AID AS b ON b.AC = a.AC "
                                    "JOIN EDU_METER97_{5} as c  ON b.EMC_ID = c.EMC_ID "
                                   "WHERE a.Tab='{0}' AND  c.CO_CODE = {1} AND "
                                   "(( c.EMCO_YEAR= {2} AND a.CUR_YEAR=0 ) OR ( c.EMCO_YEAR= {3} AND a.CUR_YEAR=-1))".format(Table,self.country_code, self.emco_year,self.emco_year-1,self.username, self.database_type)))
            
            cursor.executemany("INSERT OR REPLACE INTO EDU_METER97_"+ self.database_type +" VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",meters_data)
            for var in referenced_sql_code:
                cursor.execute(var)
            self.conn.commit()
                         
            if self.edit_mode:
                cursor.execute(("INSERT INTO METER_AUDIT_TRAIL " 
                               "(MC_ID, CO_CODE, ADM_CODE, MC_YEAR, EM_FIG_OLD, MQ_ID_OLD, "
                               "MG_ID_OLD, USER_NAME, SERIES, SURVEY_ID, EM_FIG_NEW, MQ_ID_NEW, MG_ID_NEW) " 
                               "SELECT a.MC_ID, a.CO_CODE, a.ADM_CODE, a.MC_YEAR," 
                               "a.EM_FIG_OLD, a.MQ_ID_OLD, a.MG_ID_OLD," 
                               "a.USER_NAME, a.SERIES, a.SURVEY_ID," 
                               "b.EM_FIG, b.MQ_ID, b.MG_ID from  METER_AUDIT_TEMP as a "
                               "join EDU_METER97_"+ self.database_type +" as b on a.MC_ID = b.EMC_ID "
                               "and a.CO_CODE = b.CO_CODE and a.ADM_CODE = b.ADM_CODE "
                               "and a.MC_YEAR = b.EMCO_YEAR AND "
                               "(a.EM_FIG_OLD !=b.EM_FIG OR a.MQ_ID_OLD != b.MQ_ID OR a.MG_ID_OLD != b.MG_ID)"))
                cursor.execute("DELETE FROM METER_AUDIT_TEMP")
                self.conn.commit()
            #               for Table in self.wb.sheet_names():
                    # query="INSERT INTO METER_AUDIT_TEMP (MC_ID, CO_CODE, ADM_CODE, MC_YEAR,EM_FIG_OLD, USER_NAME, SERIES, SURVEY_ID) SELECT c.EMC_ID,c.CO_CODE, c.ADM_CODE, c.EMCO_YEAR,c.DESC_INCLU, '{4}', '{5}', 'RM' from RM_MAPPING as a LEFT JOIN EDU_METER_AID AS b ON b.AC = a.AC JOIN EDU_INCLUSION_{5} as c  ON b.EMC_ID = c.EMC_ID WHERE a.Tab='{0}' AND  c.CO_CODE = {1} AND (( c.EMCO_YEAR={2} AND a.CUR_YEAR=0) OR (c.EMCO_YEAR={3} AND a.CUR_YEAR=-1))".format(Table,self.country_code, self.emco_year,self.emco_year-1,self.username, self.database_type )
                    # cursor.execute(query)
                    # self.conn.commit() 

            
            cursor.executemany("INSERT OR REPLACE INTO EDU_INCLUSION_"+self.database_type+" VALUES(?,?,?,?,?,?);",inclu_data)
            self.conn.commit()
            
            # if self.edit_mode:
            #     cursor.execute(("INSERT INTO METER_AUDIT_TRAIL " 
            #                     "(MC_ID, CO_CODE, ADM_CODE, MC_YEAR, EM_FIG_OLD, "
            #                     "USER_NAME, SERIES, SURVEY_ID, EM_FIG_NEW) " 
            #                     "SELECT a.MC_ID, a.CO_CODE, a.ADM_CODE, a.MC_YEAR," 
            #                     "a.EM_FIG_OLD, a.USER_NAME, a.SERIES, a.SURVEY_ID," 
            #                     "b.DESC_INCLU from  METER_AUDIT_TEMP as a "
            #                     "join EDU_INCLUSION_{0} as b on a.MC_ID = b.EMC_ID "
            #                     "and a.CO_CODE = b.CO_CODE and a.ADM_CODE = b.ADM_CODE "
            #                     "and a.MC_YEAR = b.EMCO_YEAR AND "
            #                     "(a.EM_FIG_OLD !=b.DESC_INCLU)".format(self.database_type)))
            #     cursor.execute("DELETE FROM METER_AUDIT_TEMP")
            #     self.conn.commit()
                    
            cursor.close()

        def backup_imported_questionnaire():
            """Puts a copy of the questionnaire in the imports folder.
            """
            import_folder="./Import"
            if (not os.path.exists(import_folder)):
                os.makedirs(import_folder)
            shutil.copy(self.excel_file,"./Import/RM_{}_{}_{}.xlsx".format(self.country_name,self.emco_year,datetime.datetime.now().strftime("%y-%m-%d-%H-%M")))
            

        # RM_TABLE is necessary for finding the xlrd coordinates
        cursor.execute("SELECT TAB, EXL_REF, EMC_ID,RM_TABLE,Col FROM RM_MAPPING;") 
        mapping_table = cursor.fetchall()
        if self.edit_mode:            
            edit_sheets_names=self.wb.sheet_names()
            ## Before exporting the entries in the inclusion table of
            ## the sheets being imported are erased.
            inclu_table_name="EDU_INCLUSION_"+self.database_type
            for sheet in self.wb.sheets():
                cursor.execute("SELECT  {0}.CO_CODE,{0}.EMCO_YEAR,{0}.EMC_ID,RM_Mapping.Tab FROM {0} LEFT JOIN RM_MAPPING ON {0}.EMC_ID=RM_MAPPING.EMC_ID WHERE RM_Mapping.Tab=\"{3}\" AND ( ( {0}.EMCO_YEAR={1} AND RM_MAPPING.CUR_YEAR=0 ) OR ( {0}.EMCO_YEAR={2} AND RM_MAPPING.CUR_YEAR=-1) )".format(inclu_table_name,self.emco_year,self.emco_year-1,sheet.name) )
                things_to_erase=cursor.fetchall()
                for values_to_erase in things_to_erase:
                    cursor.execute("DELETE FROM EDU_INCLUSION_"+self.database_type+" WHERE CO_CODE={0} AND EMCO_YEAR={1} AND EMC_ID={2}".format(values_to_erase[0],values_to_erase[1],values_to_erase[2]))
                    self.conn.commit()
        else:
            names_test=self.compare_region_names()
            ## names_test==False if the names do not match.
            if ( names_test==1 or self.force_import ):
                self.insert_region_codes()
            else:
                file=open(self.data_report_file,'a')
                self.validation_log_file=open(self.validation_full_path ,'a')
                print("\nError: Unmatching region names between sheet and database.",end='')
                file.write("General errors,\n")
                file.write("\nError: Unmatching region names between sheet and database.,")
                database_regions=self.get_regions()
                ## number of regions in database:
                dnr=len(database_regions)
                ## number of regions in sheet
                snr=len(self.regions_from_sheet)
                nregions=max(dnr,snr)
                print("\nDatabase region names:       Sheet region names:\n",end='')
                file.write("\nDatabase region names:,       Sheet region names:\n")
                for i in range(0,nregions):
                    if (i<dnr):                        
                        print("  {}".format(database_regions[i]),end='')
                        file.write("{}".format(database_regions[i]))
                    file.write(",")
                    if (i<snr):
                       nspaces=30-len(database_regions[i])
                       print(" "*nspaces + "{}".format( self.regions_from_sheet[i]),end='')
                       file.write( "{}".format( self.regions_from_sheet[i]))
                    print("\n",end='')
                    file.write("\n")
                file.close()
                if(self.force_import):
                    print("\nImporting forced.",end='')
                    self.insert_region_codes()
                else:
                    print("\nImporting aborted.",end='')
                self.validation_log_file.close()
                
                
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
                    if reference!="empty_reference":
                        if reference[0]==None: # First reference coordinate empty
                        ## Same row if a=None in X[a:b]
                            referenced_row=adm_code
                        else:
                            referenced_row=reference[0]                    
                            referenced_sql_code= referenced_sql_code | {"UPDATE EDU_METER97_"+self.database_type+" SET MG_ID=4 WHERE EMC_ID={0} AND CO_CODE={1} AND ADM_CODE={2} AND EMCO_YEAR={3} AND MG_ID IS NULL;\n".format(self.emc_id(variables[3],reference[1]),self.country_code,referenced_row,emco_year)}                            
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
        
    def __init__(self,excel_file,database_file="../Database/Prod.db",log_folder="/tmp/log",username="user",force_import=False):
        """Set up variables for questionnaire and database reading"""
        self.excel_file=excel_file
        self.set_workbook(excel_file)
        self.edit_mode= not 'Checking sheet' in self.wb.sheet_names()
        self.set_database_connection(database_file)
        self.get_emco_year()
        self.get_nadm1()
        self.get_country_name()
        self.get_country_code()
        self.get_database_type()
        self.username=username
        self.log_folder=log_folder
        if (not os.path.exists(log_folder)):
            os.makedirs(log_folder)
        self.validation_full_path=log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+"_validation.txt"
        self.validation_log_file=open(self.validation_full_path,'a')
        self.force_import=force_import
        self.missing_data_dictionary={}
        self.data_issues_dictionary={}
        self.regions_from_sheet=None
#        self.log_file=open( log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+".log",'a')

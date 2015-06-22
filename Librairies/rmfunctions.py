# import sqlite3 #sql connection
import xlrd #to read excel file
from xlrd import open_workbook
import re
import collections #enable namedtuple: varname = collections.namedtuple('varname','val1, val2, val3..') and ordered dic
import sys, json
from rmsqlfunctions import *
import os
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
    with open("../Librairies/variables_for_preprocessing.json") as f:
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
    name = country_name.upper()
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

    def preprocessing(self):
        """Checks the consistency of the questionnaire.

        This variable reads the Checking sheets and writes in the log
        if there is any NO.
        """
        check_variables=pre_vars["Checking sheet"]
        sheet=self.wb.sheet_by_name("Checking sheet")
        printed_main_message=False
        for sheet_name in check_variables.keys():
            for var in [[x, check_variables[sheet_name][1] ] for x in check_variables[sheet_name][0] ]:
                if( sheet.cell( *var ).value == 'No' ):
                    if(not printed_main_message):
                        print("The following items have No in the Checking sheet:")
                        printed_main_message=True
                    var[1]-=5
                    print("{0} : {1}".format( sheet_name, sheet.cell(*var).value ))
    
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

        # RM_TABLE is necessary for finding the xlrd coordinates
        cursor.execute("SELECT TAB, EXL_REF, EMC_ID,RM_TABLE,Col FROM RM_MAPPING;") 
        mapping_table = cursor.fetchall()
        if self.edit_mode:
            edit_sheets_names=self.wb.sheet_names()
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
        cursor.close()
        
    def __init__(self,excel_file,database_file="../Database/UISProd.db",edit_mode=False):
        """Set up variables for questionnaire and database reading"""
        self.edit_mode=edit_mode
        self.set_workbook(excel_file)
        self.set_database_connection(database_file)
        self.get_emco_year()
        self.get_nadm1()
        self.get_country_name()
        self.get_country_code()

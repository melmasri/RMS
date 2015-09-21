import sys, getpass, os

os.chdir('/home/oscar/RMS')
sys.path.append('Libraries')

from rmquestionnaire import *

class questionnaire_test(questionnaire):
    def check_nadm1(self):
        """Checks that number of administrative divisions is filled with a positive integer. 
        """
        if self.edit_mode:
            sheet=self.wb.sheets()[0]
            nadm1= sheet.cell(4,1).value
        else:
            administrative_divisions_variables = pre_vars['fixed_sheets']['Administrative divisions']
            sheet = self.wb.sheet_by_name('Administrative divisions')
            nadm1 = sheet.cell( *indexes( administrative_divisions_variables['adm1_number'][0]  )   ).value
        if( (type(nadm1) == int or type(nadm1) == float) and int(nadm1)==nadm1 and nadm1 > 0 ):
            return(True)
        else:
            return(False)
        
    def check_adm1_names(self):
        """Checks that the region names are filled.
        """
        sheet=self.wb.sheet_by_name('Administrative divisions')
        id_start_coordinates=indexes( administrative_divisions_variables['id_start'][0])
        regions_names=sheet.col_values(id_start_coordinates[1]+1,\
                                       id_start_coordinates[0],\
                                       id_start_coordinates[0]+self.nadm1)
        all_regions_good=reduce( lambda x,y: x and y,
                                 ##The following line tests wether it is not empty and different that ...
                                 map( lambda region_name: region_name and region_name != "..." , 
                                      regions_names))
        return(all_regions_good)

    def check_reference_year(self):
        if (self.edit_mode):
            pass # or True?
        else:
            front_page_variables=pre_vars['fixed_sheets']['Front Page']
            cellname=front_page_variables['academic_year'][0]
            sheet=self.wb.sheet_by_name('Front Page')
            academic_year_value=sheet.cell(*indexes(cellname)).value
            return (academic_year_value >0 and academic_year_value <=2015 )

    def check_country_name(self):
        if (self.edit_mode):
            pass # or True?
        else:
            front_page_variables=pre_vars['fixed_sheets']['Front Page']
            cellname=front_page_variables['country_name'][0]
            sheet=self.wb.sheet_by_name('Front Page')
            return( sheet.cell_type( *indexes(cellname) ) == front_page_variables['country_name'][1] )
    def check_number_of_sheets(self):
        if (self.edit_mode):
            pass
        else:
            if pre_vars['nsheets']==self.wb.nsheets:
                self.print_log("The correct number of sheets"+ "({})".format(self.wb.nsheets) +"has been submited.\n")
    def check_edited_configuration_part(self):
        """This functions checks that the table in the top left corner of
        the sheet exists in an edite questionnaire.
        """
        if (self.edit_mode):
            sheet=self.wb.sheets()[0]
            configuration_names=sheet.col_values(0,0,6) # names in the configuration (country, co_code, year,etc.). i.e. first column
            configuration_values=sheet.col_values(1,0,6) # values of the configuration, i.e. second column
            # test1 is to check if the names coincide with the exported ones
            test1= configuration_names == ['Country', 'CO_CODE', 'Year', 'Data', 'No.ADM', 'Series']
            # test2 os to check that the values are not empty (May be it could be improved). 
            test2=reduce( lambda x,y: x and y, configuration_values)
            return(test1 and test2)
        else:
            pass

    def check_one_value(self,value):
        """Checks that value (the argument) is proper.
        
        This function can return three values:
        0 if there is an error.
        1 if the value is OK.
        2 accept but write error (A or N).
        """
        return_value=0
        if((type(value) == int or type(value) == float)  and value >=0  ):
            return_value=1
        elif(type(value) == str):
            match1=re.search('[Xx]\[[0-9]*:[0-9]+\]|^ +$|^[Zz]$|^[Mm]|^[Xx]',value) #Accept regexp
            match2=re.search('[Aa]$|^[Nn]$',value) # Accept with error regexp
            if ( not (match1==None) ):
                return_value=1 
            elif ( not (match2==None) ):
                return_value=2 
        return(return_value)
    
    def check_values(self):
        edit_sheets_names=self.wb.sheet_names()
        cursor=self.conn.cursor()
        query="SELECT Tab,EXL_REF,RM_TABLE,Col FROM RM_MAPPING WHERE Tab in (" + ','.join('?'*len(edit_sheets_names)) + ") AND AC!='ADM_NAME';"
        #self.print_log("Checking that all the values are proper...") 
        cursor.execute(query, edit_sheets_names )
        mapping_table = cursor.fetchall()
        overall_test=1
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
            self.print_log("{}".format(meter_values))
            meter_values=[meter_value_country]+meter_values
            # The following will be zero if there is at least one
            # error. 1 if everything is ok and 2 id there is at least one A or N.
            column_test=reduce( lambda x,y: x * y , map( self.check_one_value,meter_values ) ) 
            if(not column_test):
                self.print_log("Column {0} in table {1} has improper values.\n".format(col_number,table))
            elif(column_test==2):
                self.print_log("Column {0} in table {1} has at least one A or N.\n".format(col_number,table))
            overall_test=overall_test and column_test
        return(overall_test)
    def print_log_new(self,log_type=False,text_string):
        """Puts the test in log and stdout.

        if log_type=True (the default), it writes to the validation log
        if log_type=False (the default), it writes to the error log
        """
        print(text_string,end='')
        if (log_type):            
            self.validation_log_file.write(text_string)
            self.validation_log_file.flush()
            os.fsync(self.validation_log_file.fileno())
        else:
            self.error_log_file.write(text_string)
            self.error_log_file.flush()
            os.fsync(self.error_log_file.fileno())

                

    def validation(self):
        check_variables=pre_vars["Checking sheet"]
        self.print_log("----------"+"Date: "+datetime.datetime.now().strftime("%B %d, %Y")+"----------\n\n\n")

    def init(self):
        self.validation_log_file=open( log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+"_validation.log",'a')
        self.error_log_file=open( log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+"_error.log",'a')
            
excel_file="Export/Lao People's Democratic Republic_2012_All_REP.xlsx"
database="Database/Prod.db"

x=questionnaire_test(excel_file,database)
#x.check_nadm1()

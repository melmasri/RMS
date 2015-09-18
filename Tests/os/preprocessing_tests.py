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

    def check_one_value(value):
        """Checks that value (the argument) is proper.
        
        This function can return three values:
        0 if there is an error.
        1 accept but write error (A or N).
        2 if the value is OK.
        """
        return_value=0
        if((type(value) == int or type(value) == float)  and value >=0  ):
            return_value=2
        elif(type(value) == str):
            match1=re.search('[Xx]\[[0-9]*:[0-9]+\]|^ +$|^[Zz]$|^[Mm]|^[Xx]',value) #Accept regexp
            match2=re.search('[Aa]$|^[Nn]$',value) # Accept with error regexp
            if ( not (match1==None) ):
                return_value=2 
            elif ( not (match2==None) ):
                return_value=1 
        return(return_value)




excel_file="Export/Lao People's Democratic Republic_2012_All_REP.xlsx"
database="Database/Prod.db"

x=questionnaire_test(excel_file,database)
#x.check_nadm1()

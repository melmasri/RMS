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

            
                
            


excel_file="../../Export/----"
database="Database/Prod.db"

x=questionnaire_test(excel_file,database)
x.check_nadm1()

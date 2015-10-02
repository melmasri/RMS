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
            #print("nadm1: {0}\n".format(nadm1))
        else:
            administrative_divisions_variables = pre_vars['fixed_sheets']['Administrative divisions']
            sheet = self.wb.sheet_by_name('Administrative divisions')
            nadm1 = sheet.cell( *indexes( administrative_divisions_variables['adm1_number'][0]  )   ).value
        if( (type(nadm1) == int or type(nadm1) == float) and int(nadm1)==nadm1 and nadm1 > 0 ):
            self.print_log("Number of administrative divisions: {0}\n".format(nadm1))
            return(True)
        else:
            self.print_log("Error: Wrong value for number of administrative divisions.\n")
            return(False)
        
    def check_adm1_names(self):
        """Checks that the region names are filled.
        """
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
            front_page_variables=pre_vars['fixed_sheets']['Front Page']
            cellname=front_page_variables['academic_year'][0]
            sheet=self.wb.sheet_by_name('Front Page')
            academic_year_value=sheet.cell(*indexes(cellname)).value
            test_value=academic_year_value >0 and academic_year_value <=2015
            if (test_value):
                self.print_log("Reference year: {0}\n".format(academic_year_value))
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
            if (test_value):
                self.print_log("Country name is filled: {0}\n".format(country_name))
            else:
                seld.print_log("Error: Country name is not filled or has a wrong format.")
            return(test_value)
        
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
            print("The questionnaire contains missing values. See data report for details.\n")
        if overall_undefined_references:
            print("The questionnaire contains undefined references. See data report for details.\n")
        return(overall_test)
    
    def print_log(self,text_string,log_type=False):
        """Puts the test in log and stdout.

        if log_type=True (the default), it writes to the validation log
        if log_type=False (the default), it writes to the error log
        """
        print(text_string,end='')
        if (not log_type):            
            self.validation_log_file.write(text_string)
            self.validation_log_file.flush()
            os.fsync(self.validation_log_file.fileno())
        else:
            self.error_log_file.write(text_string)
            self.error_log_file.flush()
            os.fsync(self.error_log_file.fileno())

                

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
        adm1_names_test=self.check_adm1_names()
        #reference_year_test=self.check_reference_year()
        reference_year_test=True
        country_name_test=self.check_country_name()
        number_of_sheets_test=self.check_number_of_sheets()
        edited_configuration_part_test=self.check_edited_configuration_part()
        values_test=self.check_values()        
        return ( nadm1_test and adm1_names_test and reference_year_test and country_name_test and number_of_sheets_test and edited_configuration_part_test and values_test )

    def check_region_totals(self):
        """Check that the regional numbers match the total."""                
        cursor=self.conn.cursor()
        edit_sheets_names=self.wb.sheet_names()
        pass_test=True
        self.print_log("Checking that region values add to the country value...")
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
                            self.print_log("\n")
                    self.add_data_issues(tab,table,'region_totals',col)
                    self.print_log("The regional figures do not add up to the country total in {0} column {1}\n".format(table,col))
                    pass_test=False
        cursor.close()
        if  pass_test :
            self.print_log("Test passed.\n")                        
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
        self.print_log("Checking that parts are less than the totals...")
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
                            self.print_log("\n")
                        self.print_log("{}: In row {} the value of column {} is bigger than the value in column {}.\n".format(sheet_name,i+1,pairs[0],pairs[1]))
                        pass_test=False
                if rows_with_problem:
                    self.add_data_issues(sheet_name, table,'check_less',[pairs[0],pairs[1],rows_with_problem ])
                    
        cursor.close()
        if  pass_test :
            self.print_log("Test passed.\n")                        
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
        self.print_log("Checking sums of columns...")
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
                    self.print_log("Columns {} in  {} do not add to column {} in {}. Problems in row(s) {}.\n".format(summands_columns,table_name,total_column,total_table_name,rows_problem))
                pass_test= (not rows_problem) and pass_test
        return(pass_test)

    def write_data_report(self):
        data_report_path=self.log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+"_data_report.csv"
        file=open(data_report_path,'a')
        if ( not (self.missing_data_dictionary or self.data_issues_dictionary ) ):
            file.write('No data issues were found.,')
        else:
            if self.missing_data_dictionary:
                file.write("1. Missing data:,\n\n")
                for sheet_name in self.missing_data_dictionary.keys():
                    file.write("Sheet: {},\n".format(sheet_name))
                    for table in self.missing_data_dictionary[sheet_name].keys():
                        file.write(",{0},\n".format(table))
                        file.write(",\"Missing data in column(s) {}\",\n".format( self.missing_data_dictionary[sheet_name][table] ))
            file.write("\n\n")
            if self.data_issues_dictionary:
                file.write("2. Data Issues:,\n\n")
                for sheet_name in self.data_issues_dictionary.keys():
                    file.write("Sheet: {},\n".format(sheet_name))
                    for table in self.data_issues_dictionary[sheet_name].keys():
                        file.write(",{0},\n".format(table))
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
                            self.print_log("The following items have No in the Checking sheet:\n")
                            printed_main_message=True
                        var[1]-=5
                        self.print_log("{0} : {1}\n".format( sheet_name, sheet.cell(*var).value ))

                    
    
    def init2(self,log_folder="/tmp/log"):
        self.log_folder=log_folder
        self.validation_log_file=open( log_folder + "/{}".format(self.country_name) + "_"+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+"_validation.log",'a')
        self.missing_data_dictionary={}
        ## Possible issues: 'undefined_reference','check_less','column_sums','region_totals'
        self.data_issues_dictionary={}
        # If needed, a similar thing can be done with incomplete
        # references (i.e. X alone with no further reference to other
        # column). A similar function to the one of missing data might
        # be added for this, or a parameter can be added to the
        # existing one.        

            
#excel_file="Export/Lao People's Democratic Republic_2012_All_REP.xlsx"

# Original questoinnaire
excel_file="Import/RM_Lao People's Democratic Republic_2012_15-08-20-21-29.xlsx"
database="Database/Prod.db"

x=questionnaire_test(excel_file,database)
x.init2()
x.validation()
x.check_region_totals()
x.check_less()
x.check_column_sums()
x.write_data_report()

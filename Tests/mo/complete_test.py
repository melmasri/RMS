import sys
sys.path.append('../../Librairies')
from rmquestionnaire import *

excel_file = "../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
database="../../Database/UISProd.db"
set_database_file(database)

x=questionnaire(excel_file,database)

x.preprocessing()
x.create_region_codes()
x.extract_data()
x.extract_comments()
x.extract_table_comments()


co_code = x.country_code
co_name = x.country_name
year = x.emco_year


filename = "{0}_{1}.xlsx".format(co_name, 2012)
wb = xlsxwriter.Workbook(filename)

#export_var('Administrative divisions', wb, co_code, year, var_type = "sheet")
export_var('Administrative divisions', wb, co_code, year, var_type = "sheet")
export_var('Pupils', wb, co_code, year, var_type = "sheet")
export_var('Teachers ISCED 1', wb, co_code, year, var_type = "sheet")
export_var('Teachers ISCED 2', wb, co_code, year, var_type = "sheet")
export_var('Teachers ISCED 3', wb, co_code, year, var_type = "sheet")
export_var('Teachers ISCED 23', wb, co_code, year, var_type = "sheet")
wb.close()

# y=questionnaire("{0}_{1}.xlsx".format(co_name, 2012),
#                     "../../Database/UISProd.db",
#                     True                )

# y.extract_data()
# y.extract_comments()
# y.extract_table_comments()

# filename = "{0}_{1} Second output.xlsx".format(co_name, 2012)
# wb = xlsxwriter.Workbook(filename)
# export_var('Teachers ISCED 2', wb, co_code, year, var_type = "sheet")


# useful sql visuaxflisation commands
#.mode column
#.header onqqq
#.width 6 4 4 4 4 4 4 4 4 10 4 4 
# For seeing contents for a specific emc_id
# select * from EDU_METER97_REP where emc_id=20102;
# To find something with the AC
# SELECT * FRO

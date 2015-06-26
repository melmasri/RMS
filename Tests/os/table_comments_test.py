import sys
sys.path.append('../../Librairies')
from rmquestionnaire import *


excel_file = "../../..//Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
database="../../Database/UISProd.db"
#set_database_file("../../Database/UISProd.db")

x=questionnaire(excel_file,database)

# x.preprocessing()
# x.create_region_codes()
# x.extract_data()
# x.extract_comments()
x.extract_table_comments()

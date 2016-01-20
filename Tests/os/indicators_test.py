import sys, os


os.chdir('/home/oscar/RMS')
sys.path.append('Libraries')

from rmquestionnaire import *



database="Database/Prod.db"
emco_year=2015
country_name="Lao People's Democratic Republic"


a=indicators("/home/oscar/RMS/Database/Prod.db",2015,"Lao People's Democratic Republic")

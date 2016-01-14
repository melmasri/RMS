import sys, getpass, os
import datetime
import sqlite3,re

os.chdir('/home/oscar/RMS')
sys.path.append('Libraries')


database="Database/Prod.db"
emco_year=2015
country_name="Lao People's Democratic Republic"

from rmquestionnaire import *

a=indicators("/home/oscar/RMS/Database/Prod.db",2015,"Lao People's Democratic Republic")

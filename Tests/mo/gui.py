import sys
sys.path.append('../../Librairies')
from rmquestionnaire import *

excel_file = "../../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
database="../../Database/UISProd.db"
set_database_file(database)


import  tkinter as tk
from tkinter.filedialog import  FileDialog
from tkinter import ttk, StringVar

##################################################
# Useful functions
FILEOPENOPTIONS = dict(filetypes=[('Excel sheets','*.xlsx*')])
def import_one():
    """Requests from the user to select an excel file for import"""
    dirname = tk.filedialog.askopenfilenames(**FILEOPENOPTIONS)
    if dirname:
        entry_one.insert(1, dirname)

def import_many():
    """ Requests from the user to select a folder of questionnaires to import"""
    dirname = tk.filedialog.askdirectory()
    if(dirname):
        entry_many.insert(1, dirname)

def choose_output_folder():
    """Requires the user to select a folder"""
    dirname = tk.filedialog.askdirectory()
    if dirname:
        output_folder.insert(0, dirname)
  
##################################################



root = tk.Tk()

root.title('Regional module Survey')
# width x height + x_offset + y_offset:
root.geometry("900x600+30+30") 

# Adding buttons and text boxes
h = 35
w = 200



readframe = ttk.LabelFrame(root, text="Importing Questionnaire to database")
readframe.pack(fill="both", expand="yes")
read_one = ttk.Button(readframe, text ='Import a single questionnaires', command = import_one)
read_one.place(x = 20, y = 30, width=w, height = h)
read_many = ttk.Button(readframe, text= 'Import all questionnaires in a folder', command = import_many)
read_many.place(x = 20, y = 90, width=w, height=h)
ofolder_button = ttk.Button(readframe, text= 'Select output folder', command = choose_output_folder)
ofolder_button.place(x = 20, y = 150, width=w, height=h)

# Text boxes
entry_one = ttk.Entry(readframe)
entry_one.place(x = 240, y = 30,width = w*3,  height=h)
entry_many = ttk.Entry(readframe)
entry_many.place(x = 240, y = 90,width = w*3,  height=h)
output_folder = ttk.Entry(readframe)
output_folder.place(x = 240, y = 150,width = w*3,  height=h)
output_folder.insert(1, "~/Desktop")



def updtCountry():
    """Queries the names of countries that submitted an rm questinnaire"""
    l = getAvailable_countries()
    country_cbox['values'] =  list(chain.from_iterable(l))

def updtYear():
    """ For a specific selectd country, returns the list of avialable data years."""
    l= str(country_cbox.get())
    if l:
        l = getAvailable_year(l)
        year_cbox['values'] = l   
        

    
writeframe = ttk.LabelFrame(root, text="Exporting data to Excel")
writeframe.pack(fill="both", expand="yes")

country_cbox = ttk.Combobox(writeframe, postcommand=updtCountry)
country_cbox.pack()

year_cbox = ttk.Combobox(writeframe, postcommand=updtYear)
year_cbox.pack()
root.mainloop()


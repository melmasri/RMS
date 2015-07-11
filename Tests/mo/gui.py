import sys
sys.path.append('../../Librairies')
from rmquestionnaire import *

excel_file = "../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
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
    cbox_co['values'] =  list(chain.from_iterable(l))

def updtYear():
    """ For a specific selectd country, returns the list of avialable data years."""
    l= str(cbox_co.get())
    if l:
        l = getAvailable_year(l)
        cbox_year['values'] = l   

def getSheetTableAC(m):
    if m =='sheet':
        l = "SELECT DISTINCT Tab FROM RM_Mapping order by Tab"
        cbox_sheet['values'] =  list(chain.from_iterable(sql_query(l)))
    elif m =='table':
        l = "SELECT DISTINCT RM_TABLE FROM RM_Mapping order by RM_TABLE"
        cbox_table['values'] =  list(chain.from_iterable(sql_query(l)))
    elif m=='AC':
        l = "SELECT DISTINCT AC FROM RM_Mapping order by AC"
        cbox_AC['values'] =  list(chain.from_iterable(sql_query(l)))

def export(x):
    co_name = str(cbox_co.get())
    year =str(cbox_year.get())
    filename = "{0}_{1}.xlsx".format(co_name, year)
    co_code = getCO_CODE(co_name)
    #wb = xlsxwriter.Workbook(filename)
    if x=='sheet':
        var = str(cbox_sheet.get())
        if var:
            print(co_name)
            print(year)
            print(co_code)
            print(var)
    #wb.close()
        
writeframe = ttk.LabelFrame(root, text="Exporting data to Excel")
writeframe.pack(fill="both", expand="yes")

ttk.Label(writeframe, text='Country').grid(row=0,column=0, sticky = 'W')
ttk.Label(writeframe, text='Year').grid(row=0,column=2, sticky='W')
cbox_co = ttk.Combobox(writeframe, postcommand=updtCountry, width=30)
cbox_year = ttk.Combobox(writeframe, postcommand=updtYear)
cbox_co.grid(row=0, column =1, sticky='W')
cbox_year.grid(row=0, column=3 ,sticky='W')

lf_exOptions = ttk.LabelFrame(writeframe , text="Export by:")
lf_exOptions.grid(row=3, columnspan=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)

ttk.Label(lf_exOptions, text='Sheet ').grid(row=0, column=0, sticky='W')
ttk.Label(lf_exOptions, text='Table ').grid(row=1, column=0, sticky='W')
ttk.Label(lf_exOptions, text='AC ').grid(row=2, column=0, sticky='W')

cbox_sheet = ttk.Combobox(lf_exOptions, postcommand= lambda m='sheet': getSheetTableAC(m), width=20)
cbox_sheet.grid(row=0, column=1, sticky='W')
cbox_table = ttk.Combobox(lf_exOptions, postcommand=lambda m='table': getSheetTableAC(m))
cbox_table.grid(row=1, column=1, sticky='W')
cbox_AC = ttk.Combobox(lf_exOptions,postcommand=lambda m='AC': getSheetTableAC(m))
cbox_AC.grid(row=2, column=1, sticky='W')

cc= ttk.Button(lf_exOptions, text ='Export', commad = lambda x='sheet': print(x))
cc.grid(row=0, column=3, sticky='W')
#ttk.Button(lf_exOptions, text ='Export').grid(row=1, column=3, sticky='W')
#ttk.Button(lf_exOptions, text ='Export').grid(row=2, column=3, sticky='W')


root.mainloop()


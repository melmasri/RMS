import sys, getpass

sys.path.append('../../Librairies')
from rmquestionnaire import *

excel_file = "../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
database="../../Database/UISProd.db"
set_database_file(database)


import tkinter as tk
from tkinter.filedialog import  FileDialog
from tkinter import ttk, StringVar

##################################################
# Useful functions
def select_file(x):
    """ Requests from the user to select a file/folder of questionnaires to import"""
    FILEOPENOPTIONS = dict(filetypes=[('Excel sheets','*.xlsx*')])
    if x=='file':
        dirname = tk.filedialog.askopenfilenames(**FILEOPENOPTIONS)
        if dirname:
            entry_one.insert(0, dirname)
    elif x=='folder':
        dirname = tk.filedialog.askdirectory()
        if(dirname):
            entry_many.insert(1, dirname)
    elif x=='out_folder':
        dirname = tk.filedialog.askdirectory()
        if dirname:
            output_folder.insert(0, dirname)

def imp_file(x):
    if x=='file':
        for i in entry_one.get():
            print(i)
        # x=questionnaire(entry_one.get(),database)
        # x.preprocessing()
        # x.create_region_codes()
        # x.extrct_data()
        # x.extract_comments()
        # x.extract_table_comments()
    
        
##################################################


root = tk.Tk()
root.title('Regional module Survey')
# width x height + x_offset + y_offset:
root.geometry("600x600+50+50") 
### Style 
ttk.Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')
 
###
style = ttk.Style()
style.configure("BW.TLabel", foreground="black", background="white")

settingframe = ttk.LabelFrame(root, text='General information')
settingframe.pack(fill="y", side= 'top')

username = getpass.getuser()
ttk.Label(settingframe, text ='User ').grid(row=0, column=0, sticky = 'W')
ttk.Label(settingframe, text = username, padding=2, style="BW.TLabel").grid(row=0, column=1, sticky = 'W')

# Adding buttons and text boxes
readframe = ttk.LabelFrame(root, text="Importing Questionnaire to database")
readframe.pack(fill="y", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')

ttk.Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')


ttk.Label(readframe, text='Select output folder ').grid(row=1, column=0, sticky='W')    

lf_impOptions = ttk.LabelFrame(readframe , text="Import a:")

lf_impOptions.columnconfigure(0, pad=3)
lf_impOptions.columnconfigure(1, pad=3)
lf_impOptions.columnconfigure(2, pad=3)
lf_impOptions.columnconfigure(3, pad=3)

lf_impOptions.rowconfigure(0, pad=3)
lf_impOptions.rowconfigure(1, pad=3)


lf_impOptions.grid(row=3, columnspan=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
ttk.Label(lf_impOptions, text='file ').grid(row=0, column=0, sticky='W')
ttk.Label(lf_impOptions, text='folder ').grid(row=1, column=0, sticky='W')

# Text boxes
entry_one = ttk.Entry(lf_impOptions)
entry_one.grid(row=0, column=1, sticky='W')
entry_many = ttk.Entry(lf_impOptions)
entry_many.grid(row=1, column=1, sticky='W')
output_folder = ttk.Entry(readframe)
output_folder.grid(row=1, column=1, sticky='W')
# Buttons
ttk.Button(lf_impOptions, text ='Browse..', command = lambda x='file': select_file(x)).grid(row=0, column=3, sticky='W') 
ttk.Button(lf_impOptions, text= 'Browse..', command = lambda x='folder': select_file(x)).grid(row=1, column=3, sticky='W')
ttk.Button(lf_impOptions, text= 'Browse..', command = lambda x='folder': select_file(x)).grid(row=1, column=3, sticky='W')
ttk.Button(readframe, text= 'Browse..', command = lambda x='out_folder': select_file(x)).grid(row=1, column=3, sticky='W')

ttk.Button(lf_impOptions, text ='Import', command = lambda x='file': imp_file(x)).grid(row=0, column=4, sticky='W')
ttk.Button(lf_impOptions, text ='Import', command = lambda x='folder': imp_file(x)).grid(row=1, column=4, sticky='W') 


#Another functions
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
        cbox_sheet['values'] =  ['All'] + list(chain.from_iterable(sql_query(l)))
    elif m =='table':
        l = "SELECT DISTINCT RM_TABLE FROM RM_Mapping order by RM_TABLE"
        cbox_table['values'] =  list(chain.from_iterable(sql_query(l)))
    elif m=='AC':
        l = "SELECT DISTINCT AC FROM RM_Mapping order by AC"
        cbox_AC['values'] =  list(chain.from_iterable(sql_query(l)))

def export(x):
    if x=='sheet':
        var = str(cbox_sheet.get())
    elif x=='table':
        var = str(cbox_table.get())
    elif x=='AC':
        var = str(cbox_AC.get())

    if var:
        co_name = str(cbox_co.get())
        year = cbox_year.get()

        if co_name and year:
            co_code = getCO_CODE(co_name)
            filename = "{2}{0}_{1}.xlsx".format(co_name, year,output_folder.get())
            wb = xlsxwriter.Workbook(filename)
            if x=='sheet' and var == 'All':
                [export_var(i, wb, co_code, int(year), var_type = x)for i in cbox_sheet['values'][1:]]
            else:
                export_var(var, wb, co_code, int(year), var_type = x)
            wb.close()
        
writeframe = ttk.LabelFrame(root, text="Exporting data to Excel")
writeframe.pack(fill="y", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')

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

ttk.Button(lf_exOptions, text ='Export', command = lambda x='sheet': export(x)).grid(row=0, column=3, sticky='W')
ttk.Button(lf_exOptions, text ='Export', command = lambda x='table': export(x)).grid(row=1, column=3, sticky='W')
ttk.Button(lf_exOptions, text ='Export', command = lambda x='AC': export(x)).grid(row=2, column=3, sticky='W')


root.mainloop()


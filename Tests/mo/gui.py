import sys, getpass

sys.path.append('../../Librairies')
from rmquestionnaire import *

excel_file = "../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
database="../../Database/UISProd.db"
set_database_file(database)


import tkinter as tk
from tkinter.filedialog import  FileDialog
from tkinter import ttk, StringVar
import re
#################################################
# Useful functions
def select_file(x):
    """ Requests from the user to select a file/folder of questionnaires to import"""
    FILEOPENOPTIONS = dict(filetypes=[('Excel sheets','*.xlsx*')])
    if x=='file':
        dirname = tk.filedialog.askopenfilenames(title="Select files",**FILEOPENOPTIONS )
        if dirname:
            entry_one.insert(0, dirname)
    elif x=='folder':
        dirname = tk.filedialog.askdirectory( title="Select a folder")
        if(dirname):
            entry_many.insert(1, dirname)
    elif x=='out_folder':
        dirname = tk.filedialog.askdirectory()
        if dirname:
            output_folder.insert(0, dirname)

def imp_file(x):
    if x=='file':
        file1 = root.splitlist(entry_one.get())
    elif x=='folder':
        file1 = os.listdir()
        
    for i in file1:
        if re.search(".xlsx", i):
            status.set('Importing {0}'.format(i))
            x=questionnaire(i,database, True)
            x.extract_data()
            x.extract_comments()
            x.extract_table_comments()
            x.extract_comments()
            x.extract_table_comments()
            status.set('Done.')
      
            

##################################################

### Root label
pad = 5
root = tk.Tk()
root.title('Regional module Survey')
# width x height + x_offset + y_offset:
root.geometry("700x500+50+50") 
### Style 
ttk.Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')
###
style = ttk.Style()
style.configure("BW.TLabel", foreground="black", background="white")

### Top setting frame
settingframe = ttk.LabelFrame(root, text='General information' ,padding= (pad, pad, pad, pad))
settingframe.pack(fill="y", side= 'top')

username = getpass.getuser()
ttk.Label(settingframe, text ='User ').grid(row=0, column=0, sticky = 'W')
ttk.Label(settingframe, text = username, padding=2, style="BW.TLabel").grid(row=0, column=1, sticky = 'W')
ttk.Label(settingframe, text = "Databse ").grid(row=1, column=0, sticky = 'W')
ttk.Label(settingframe, text = database, padding=2, style="BW.TLabel").grid(row=1, column=1, sticky = 'W')

# Reading frame
readframe = ttk.LabelFrame(root, text="Importing Questionnaire to database", padding = (pad, pad, pad, pad))
readframe.pack(fill="x", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')

ttk.Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')


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

# Buttons
ttk.Button(lf_impOptions, text ='Browse..', command = lambda x='file': select_file(x)).grid(row=0, column=3, sticky='W') 
ttk.Button(lf_impOptions, text= 'Browse..', command = lambda x='folder': select_file(x)).grid(row=1, column=3, sticky='W')
ttk.Button(lf_impOptions, text= 'Browse..', command = lambda x='folder': select_file(x)).grid(row=1, column=3, sticky='W')
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
            filename = "{2}/{0}_{1}_{3}.xlsx".format(co_name, year,output_folder.get(),var)
            wb = xlsxwriter.Workbook(filename)
            status.set('Exporting file {0}'.format(filename))
            if x=='sheet' and var == 'All':
                [export_var(i, wb, co_code, int(year), var_type = x)for i in cbox_sheet['values'][1:]]
            else:
                export_var(var, wb, co_code, int(year), var_type = x)
            wb.close()
            status.set('Sucessfully exported, see {0}.'.format(filename))
        else:
            status.set('Error: missing country name or year.')
    else:
        status.set("Error: no {0} is specified".format(x))


### Write frame
writeframe = ttk.LabelFrame(root, text="Exporting data to Excel", padding = (pad, pad, pad, pad))
writeframe.pack(fill="x", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')

ttk.Label(writeframe, text='Country').grid(row=0,column=0, sticky = 'W')
ttk.Label(writeframe, text='Year').grid(row=0,column=2, sticky='W')
cbox_co = ttk.Combobox(writeframe, postcommand=updtCountry, width=30)
cbox_year = ttk.Combobox(writeframe, postcommand=updtYear)
cbox_co.grid(row=0, column =1, sticky='W')
cbox_year.grid(row=0, column=3 ,sticky='W')

lf_exOptions = ttk.LabelFrame(writeframe , text="Export by:")
lf_exOptions.grid(row=3, columnspan=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)


lf_exOptions.columnconfigure(0, pad=3)
lf_exOptions.columnconfigure(1, pad=3)
lf_exOptions.columnconfigure(2, pad=3)

lf_exOptions.rowconfigure(0, pad=3)
lf_exOptions.rowconfigure(1, pad=3)
lf_exOptions.rowconfigure(2, pad=3)


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


##### Output folder
ttk.Label(writeframe, text='Select output folder ').grid(row=4, column=0, sticky='W')    
output_folder = ttk.Entry(writeframe)
output_folder.grid(row=4, column=1, sticky='W')
ttk.Button(writeframe, text= 'Browse..', command = lambda x='out_folder': select_file(x)).grid(row=4, column=3, sticky='W')


### Status frame
StatusLabelFrame = ttk.LabelFrame(root, text="Status:")
StatusLabelFrame.pack(fill="x", side = 'bottom', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 's')
status = StringVar()
status.set('Initializing..')
StatusLabel = ttk.Label(StatusLabelFrame, textvariable = status, justify= 'left').pack(fill ='x')

### Main loop
root.mainloop()


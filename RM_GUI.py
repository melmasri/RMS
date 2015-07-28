import sys, getpass

sys.path.append('Librairies')
from rmquestionnaire import *

# excel_file = "../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
# database="../../Database/UISProd.db"
# log_folder = "../../Log"
# set_database_file(database)

import tkinter as tk
from tkinter import ttk,StringVar, filedialog
import re
#################################################
# Useful functions

class StdoutRedirector(object):
    """ A class to write out the standard output to a tkinter Text widget."""
    def __init__(self,text_widget):
        self.text_space = text_widget

    def write(self,string):
        self.text_space.insert('end', string)
        self.text_space.see('end')
        
    def flush(self):
        pass


class RM():
    """ A class the generated the regional moduel gui."""
    series = {'Reported':'REP', 'Clean': 'OBS', 'Estimated':'EST'}
    def __init__(self, master, database, log_folder=''):
        """ Main initilization"""
        self.master = master
        self.database = database
        self.log_folder = log_folder
        self.master.title('Regional module Survey')
        # width x height + x_offset + y_offset:
        self.master.geometry("700x600+50+50")
        self.status = StringVar()
        self.createWidgets()
        self.setFormating()
        
    def createWidgets(self):
        """ Creating all widgets in the gui."""
        ## Static variables
        pad = 5                 # size padding for frames
        ## Styles
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")
        ###### Settings frame
        RM.username = getpass.getuser()
        settingframe = ttk.LabelFrame(self.master, text='General information' ,padding= (pad, pad, pad, pad))
        settingframe.pack(fill="y", side= 'top')
        ttk.Label(settingframe, text ='User ').grid(row=0, column=0, sticky = 'W')
        ttk.Label(settingframe, text = RM.username, padding=2, style="BW.TLabel").grid(row=0, column=1, sticky = 'W')
        ttk.Label(settingframe, text = "Databse ").grid(row=1, column=0, sticky = 'W')
        ttk.Label(settingframe, text = self.database, padding=2, style="BW.TLabel").grid(row=1, column=1, sticky = 'W')
        ttk.Label(settingframe, text = "Log folder ").grid(row=2, column=0, sticky = 'W')
        ttk.Label(settingframe, text = self.log_folder, padding=2, style="BW.TLabel").grid(row=2, column=1, sticky = 'W')
        
        # ####### Import frame
        readframe = ttk.LabelFrame(self.master, text="Importing Questionnaire to database", padding = (pad, pad, pad, pad))
        readframe.pack(fill="x", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')
        self.lf_impOptions = ttk.LabelFrame(readframe , text="Import a:")
        self.lf_impOptions.grid(row=3, columnspan=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)

        # ## Text boxes
        self.entry_one = ttk.Entry(self.lf_impOptions,width=50)
        self.entry_one.grid(row=0, column=1, sticky='W')
        self.entry_many = ttk.Entry(self.lf_impOptions,width=50)
        self.entry_many.grid(row=1, column=1, sticky='W')

        # # Buttons
        ttk.Button(self.lf_impOptions, text ='Browse..', command = lambda x='file': self.select_file(x)).grid(row=0, column=3, sticky='W') 
        ttk.Button(self.lf_impOptions, text= 'Browse..', command = lambda x='folder': self.select_file(x)).grid(row=1, column=3, sticky='W')
        ttk.Button(self.lf_impOptions, text= 'Browse..', command = lambda x='folder': self.select_file(x)).grid(row=1, column=3, sticky='W')
        ttk.Button(self.lf_impOptions, text ='Import', command = lambda x='file': self.imp_file(x)).grid(row=0, column=4, sticky='W')
        ttk.Button(self.lf_impOptions, text ='Import', command = lambda x='folder': self.imp_file(x)).grid(row=1, column=4, sticky='W')

        ttk.Label(self.lf_impOptions, text='file ').grid(row=0, column=0, sticky='W')
        ttk.Label(self.lf_impOptions, text='folder ').grid(row=1, column=0, sticky='W')

        # ####### Export frame
        # General Frame
        self.writeframe = ttk.LabelFrame(self.master, text="Exporting data to Excel", padding = (pad, pad, pad, pad))
        self.writeframe.pack(fill="x", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')
        
        ttk.Label(self.writeframe, text='Country').grid(row=0,column=0, sticky = 'W')
        ttk.Label(self.writeframe, text='Year').grid(row=1,column=0, sticky='W')
        ttk.Label(self.writeframe, text='Series').grid(row=2,column=0, sticky = 'W')
        

        self.cbox_co = ttk.Combobox(self.writeframe, postcommand=self.updtCountry, width=30)
        self.cbox_co.grid(row=0, column =1, sticky='W')
        self.cbox_year = ttk.Combobox(self.writeframe, postcommand=self.updtYear)
        self.cbox_year.grid(row=1, column=1 ,sticky='W')
        self.cbox_series = ttk.Combobox(self.writeframe)  # Make a postcommad
        self.cbox_series.grid(row=2, column =1, sticky='W')
        self.cbox_series['values']= ['Reported', 'Clean', 'Estimated']

        pane = ttk.Panedwindow(self.writeframe, orient='horizontal')
        # Exporting options
        self.lf_exOptions = ttk.LabelFrame(pane , text="Export by:")
        self.lf_exOptions.grid(row=3, columnspan=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)

        ttk.Label(self.lf_exOptions, text='Sheet ').grid(row=0, column=0, sticky='W')
        ttk.Label(self.lf_exOptions, text='Table ').grid(row=1, column=0, sticky='W')
        ttk.Label(self.lf_exOptions, text='AC ').grid(row=2, column=0, sticky='W')

        self.cbox_sheet = ttk.Combobox(self.lf_exOptions, postcommand= lambda m='sheet': self.getSheetTableAC(m), width=20)
        self.cbox_sheet.grid(row=0, column=1, sticky='W')
        self.cbox_table = ttk.Combobox(self.lf_exOptions, postcommand=lambda m='table': self.getSheetTableAC(m))
        self.cbox_table.grid(row=1, column=1, sticky='W')
        self.cbox_AC = ttk.Combobox(self.lf_exOptions,postcommand=lambda m='AC': self.getSheetTableAC(m))
        self.cbox_AC.grid(row=2, column=1, sticky='W')

        ttk.Button(self.lf_exOptions, text ='Export', command= lambda x='sheet': self.export(x)).grid(row=0, column=3, sticky='W')
        ttk.Button(self.lf_exOptions, text ='Export', command = lambda x='table': self.export(x)).grid(row=1, column=3, sticky='W')
        ttk.Button(self.lf_exOptions, text ='Export', command = lambda x='AC': self.export(x)).grid(row=2, column=3, sticky='W')

        # Migrating options
        self.lf_migrate = ttk.LabelFrame(pane , text="Move between databases")
        self.lf_migrate.grid(row=1, columnspan=2, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        ttk.Button(self.lf_migrate, text ='REP to OBS', command= lambda x = 'REP', y = 'OBS': self.migrate_serie(x,y)).grid(row=0, column=0, sticky='W',padx=5,pady=5)
        ttk.Button(self.lf_migrate, text ='OBS to EST', command = lambda x ='OBS', y = 'EST': self.migrate_serie(x,y)).grid(row=0, column=1, sticky='W')

        pane.add(self.lf_exOptions,weight=50)
        pane.add(self.lf_migrate,weight=50)
        pane.grid(row=3, columnspan=5,padx=5, pady=5, ipadx=5, ipady=5)
        # Output folder
        ttk.Label(self.writeframe, text='Select output folder ').grid(row=4, column=0, sticky='W')    
        self.output_folder = ttk.Entry(self.writeframe)
        self.output_folder.grid(row=4, column=1, sticky='W')
        ttk.Button(self.writeframe, text= 'Browse..', command = lambda x='out_folder': self.select_file(x)).grid(row=4, column=3, sticky='W')


        ### Status frame
        self.StatusLabelFrame = ttk.LabelFrame(self.master, text="Status:")
        self.StatusLabelFrame.pack(fill="x", side = 'bottom', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 's')
        self.text_box = tk.Text(self.StatusLabelFrame,wrap='word', height = 5)
        self.text_box.pack(fil='x')
        sys.stdout =  StdoutRedirector(self.text_box)


    ### Supporting functions
    def setFormating(self):
        """ Formats the sizes and padding of different widgets"""
        ### Import frame settings
        self.lf_impOptions.columnconfigure(0, pad=3)
        self.lf_impOptions.columnconfigure(1, pad=3)
        self.lf_impOptions.columnconfigure(2, pad=3)
        self.lf_impOptions.columnconfigure(3, pad=3)
        self.lf_impOptions.rowconfigure(0, pad=3)
        self.lf_impOptions.rowconfigure(1, pad=3)

        ### Export frame
        self.writeframe.columnconfigure(0,pad=3)
        self.writeframe.columnconfigure(1,pad=3)
        self.writeframe.columnconfigure(2,pad=3)
        self.writeframe.rowconfigure(0,pad=3)
        self.writeframe.rowconfigure(1,pad=3)
        self.writeframe.rowconfigure(2,pad=3)
        ### Export frame settings
        self.lf_exOptions.columnconfigure(0, pad=3)
        self.lf_exOptions.columnconfigure(1, pad=3)
        self.lf_exOptions.columnconfigure(2, pad=3)
        self.lf_exOptions.rowconfigure(0, pad=3)
        self.lf_exOptions.rowconfigure(1, pad=3)
        self.lf_exOptions.rowconfigure(2, pad=3)

        self.lf_migrate.columnconfigure(0, pad=3)
        self.lf_migrate.columnconfigure(1, pad=3)
        self.lf_migrate.rowconfigure(0, pad=3)
        
    def export(self,x):
        """ Exports a whole questionnare, sheet or AC"""
        if x=='sheet':
            var = str(self.cbox_sheet.get())
        elif x=='table':
            var = str(self.cbox_table.get())
        elif x=='AC':
            var = str(self.cbox_AC.get())

        if var:
            co_name = str(self.cbox_co.get())
            year = self.cbox_year.get()
            serie = str(self.cbox_series.get())
            if co_name and year and serie:
                co_code = getCO_CODE(co_name)
                serie = RM.series[serie]
                filename = "{0}_{1}_{2}_{3}.xlsx".format(co_name, year,var,serie)
                print('Exporting file {0}'.format(filename))
                filename = "{0}/{1}".format(self.output_folder.get(),filename)
                wb = xlsxwriter.Workbook(filename)
                if x=='sheet' and var == 'All':
                    [export_var(i, wb, co_code, int(year), var_type = x ,serie=serie) for i in self.cbox_sheet['values'][1:]]
                else:
                    export_var(var, wb, co_code, int(year), var_type = x,serie=serie)
                wb.close()
                print('Sucessfully exported, see {0}.'.format(filename))
            else:
                print('Error: missing country name, year or series.')
        else:
            print("Error: no {0} is specified".format(x))


    def select_file(self,x):
        """ Requests from the user to select a file/folder of questionnaires to import"""
        FILEOPENOPTIONS = dict(filetypes=[('Excel sheets','*.xlsx*'),('All files','*.*')])
        if x=='file':
            dirname = tk.filedialog.askopenfilenames(title="Select files",**FILEOPENOPTIONS )
            if dirname:
                self.entry_one.delete(0,'end')
                self.entry_one.insert(0, dirname)
        elif x=='folder':
            dirname = tk.filedialog.askdirectory( title="Select a folder")
            if(dirname):
                self.entry_many.delete(0, 'end')
                self.entry_many.insert(0, dirname)
        elif x=='out_folder':
            dirname = tk.filedialog.askdirectory()
            if dirname:
                self.output_folder.delete(0, 'end')
                self.output_folder.insert(0, dirname)

    def imp_file(self,x):
        """ Imports an excel questionnaire or sheets to the SQL database"""
        if x=='file':
            file1 = self.master.splitlist(self.entry_one.get())
            if not file1:
                print('No file is selected.')
                return
        elif x=='folder':
            file1 = self.entry_many.get()
            if not file1:
                print('No folder is selected.')
                return
        for i in file1:
                if re.search(".xlsx", i):
                    print('Importing {0}'.format(i))
                    x=questionnaire(i,self.database,self.log_folder)
                    if x.preprocessing():
                        x.extract_data()
                        x.extract_comments()
                        x.extract_table_comments()
                        x.extract_comments()
                        x.extract_table_comments()
                    print('Done.')
    
    def updtCountry(self):
        """Queries the names of countries that submitted an rm questinnaire"""
        l = getAvailable_countries()
        self.cbox_co['values'] =  list(chain.from_iterable(l))

    def updtYear(self):
        """ For a specific selectd country, returns the list of avialable data years."""
        l= str(self.cbox_co.get())
        if l:
            l = getAvailable_year(l)
            self.cbox_year['values'] = l   

    def getSheetTableAC(self,m):
        if m =='sheet':
            l = "SELECT DISTINCT Tab FROM RM_Mapping order by Tab"
            self.cbox_sheet['values'] =  ['All'] + list(chain.from_iterable(sql_query(l)))
        elif m =='table':
            l = "SELECT DISTINCT RM_TABLE FROM RM_Mapping order by RM_TABLE"
            self.cbox_table['values'] =  list(chain.from_iterable(sql_query(l)))
        elif m=='AC':
            l = "SELECT DISTINCT AC FROM RM_Mapping order by AC"
            self.cbox_AC['values'] =  list(chain.from_iterable(sql_query(l)))

    def migrate_serie(self, from_serie, to_serie):
        """ A funtion that migrates data between series Reported(REP), Clean(OBS), Estimated(EST)"""
        co_name = str(self.cbox_co.get())
        year = self.cbox_year.get()
        if co_name and year:
            moveSerie(getCO_CODE(co_name), int(year), from_serie, to_serie)
        else:
            print('Error: missing country name or year.')
        
   
def main():
    database="Database/UISProd.db"
    set_database_file(database)
    log_folder = "Log"
    root = tk.Tk()
    app = RM(root, database, log_folder)
    root.mainloop()

if __name__ == '__main__':
    main()

    

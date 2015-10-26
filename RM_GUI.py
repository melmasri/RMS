import sys, getpass, os
sys.path.append('Libraries')
from rmquestionnaire import *

# excel_file = "../../../../Dropbox/Regional module Survey/tests/Regional_Questionnaire_Asia_Final_v7_locked_LAOS.xlsx"
# database="../../Database/Prod.db"
# log_folder = "../../Log"
# set_database_file(database)
import tkinter as tk
from tkinter import ttk,StringVar, filedialog, scrolledtext, messagebox
import re
#################################################
# Useful functions
def open_file_local(f):
    """ Opens a file with the proper default program"""
    if sys.platform == 'linux':
        os.system("xdg-open \"{0}\" &".format(f))
    elif re.search("win", sys.platform):
        # http://www.quora.com/What-is-the-equivalent-of-xdg-open-on-Windows
        os.system("start \"\" \"{0}\"".format(f))

        
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
    """ A class the generated the regional module GUI."""
    series = {'Reported':'REP', 'Observed': 'OBS', 'Estimated':'EST'}
    def __init__(self, master, database, log_folder='Log', output_folder_var='Export'):
        """ Main initialization"""
        self.master = master
        self.database = database
        if not os.path.exists(log_folder): os.makedirs(log_folder)
        if not os.path.exists(output_folder_var): os.makedirs(output_folder_var)
        self.backup_folder = 'Import'
        self.log_folder = log_folder
        self.main_dir = os.getcwd()
        self.output_folder_var = output_folder_var
        self.master.title('Regional module Survey: main dir ' + self.main_dir)
        # width x height + x_offset + y_offset:
        self.master.geometry("730x730+50+50")
        self.status = StringVar()
        self.createWidgets()
        self.setFormating()
        self.messages()
        self.valid_quest = ''
        
    def createWidgets(self):
        """ Creating all widgets in the GUI."""
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
        ttk.Label(settingframe, text = "Main working directory ").grid(row=1, column=0, sticky = 'W')
        ttk.Label(settingframe, text = self.main_dir, padding=2, style="BW.TLabel").grid(row=1, column=1, sticky = 'W')
        ttk.Label(settingframe, text = "Database ").grid(row=2, column=0, sticky = 'W')
        ttk.Label(settingframe, text = self.database, padding=2, style="BW.TLabel").grid(row=2, column=1, sticky = 'W')
        ttk.Label(settingframe, text = "Log folder ").grid(row=0, column=2, sticky = 'W')
        ttk.Label(settingframe, text = self.log_folder, padding=2, style="BW.TLabel").grid(row=0, column=3, sticky = 'W')
        ttk.Label(settingframe, text = "Output folder ").grid(row=1, column=2, sticky = 'W')
        ttk.Label(settingframe, text = self.output_folder_var, padding=2, style="BW.TLabel").grid(row=1, column=3, sticky = 'W')
        ttk.Label(settingframe, text = "Import backup folder ").grid(row=2, column=2, sticky = 'W')
        ttk.Label(settingframe, text = self.backup_folder, padding=2, style="BW.TLabel").grid(row=2, column=3, sticky = 'W')
        # ####### Import frame
        readframe = ttk.LabelFrame(self.master, text="Importing questionnaire to database", padding = (pad, pad, pad, pad))
        readframe.pack(fill="x", side = 'top', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 'nw')
        self.lf_impOptions = ttk.LabelFrame(readframe , text="Insert a:")
        self.lf_impOptions.grid(row=3, columnspan=3, sticky='NSEW', padx=5, pady=5, ipadx=5, ipady=5)

        # ## Text boxes
        self.entry_one = ttk.Entry(self.lf_impOptions,width=50)
        self.entry_one.grid(row=0, column=1, sticky='W')

        # # Buttons
        self.rep_validate = tk.IntVar()
        ttk.Button(self.lf_impOptions, text ='Browse..', command = lambda x='file': self.select_file(x)).grid(row=0, column=3, sticky='W')
        ttk.Button(self.lf_impOptions, text ='Validate', command =  self.validate_file).grid(row=0, column=4, sticky='W')
        ttk.Button(self.lf_impOptions, text ='Check only', command =  self.check_file).grid(row=0, column=5, sticky='W')
        ttk.Button(self.lf_impOptions, text ='Insert', command =  self.imp_file).grid(row=1, column=5, sticky='W')

        ## Import into rep
        self.rep_import = tk.IntVar()
        self.checkbox =   ttk.Checkbutton(self.lf_impOptions, text="Import to REP", variable= self.rep_import)
        self.checkbox.grid(row=1, column = 3, sticky = 'W', columnspan=3)

        ## Auto open log file
        self.open_log = tk.IntVar()
        self.open_log.set(1)
        self.OpenLogCB =  ttk.Checkbutton(self.lf_impOptions, text="Open log file", variable= self.open_log)
        self.OpenLogCB.grid(row=2, column = 3, sticky = 'W', columnspan=3)
        ## Auto open data report
        self.open_data_report = tk.IntVar()
        self.open_data_report.set(1)
        self.OpenDRCB =  ttk.Checkbutton(self.lf_impOptions, text="Open data report", variable= self.open_data_report)
        self.OpenDRCB.grid(row=3, column = 3, sticky = 'W', columnspan=3)

        ## Force insert
        self.force_insert =  tk.IntVar()
        self.ForceCB =  ttk.Checkbutton(self.lf_impOptions, text="Force insert", variable= self.force_insert)
        self.ForceCB.grid(row=4, column = 3, sticky = 'W', columnspan=3)
     
        
        ttk.Label(self.lf_impOptions, text='file ').grid(row=0, column=0, sticky='W')

        # ####### Export frame
        # General Frame
        self.writeframe = ttk.LabelFrame(self.master, text="Extracting data to Excel", padding = (pad, pad, pad, pad))
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
        self.cbox_series['values']= ['Reported', 'Observed', 'Estimated']

        pane = ttk.Panedwindow(self.writeframe, orient='horizontal')
        # Exporting options
        self.lf_exOptions = ttk.LabelFrame(pane , text="Extract by:")
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

        ttk.Button(self.lf_exOptions, text ='Extract', command= lambda x='sheet': self.export(x)).grid(row=0, column=3, sticky='W')
        ttk.Button(self.lf_exOptions, text ='Extract', command = lambda x='table': self.export(x)).grid(row=1, column=3, sticky='W')
        ttk.Button(self.lf_exOptions, text ='Extract', command = lambda x='AC': self.export(x)).grid(row=2, column=3, sticky='W')

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
        self.output_folder = ttk.Entry(self.writeframe, textvariable= self.output_folder_var)
        self.output_folder.grid(row=4, column=1, columnspan =3, sticky='WE')
        ttk.Button(self.writeframe, text= 'Browse..', command = lambda x='out_folder': self.select_file(x)).grid(row=4, column=5, sticky='W')


        ### Status frame
        self.StatusLabelFrame = ttk.LabelFrame(self.master, text="Status:")
        self.StatusLabelFrame.pack(fill="both", side = 'bottom', padx = 3, pady=3,ipadx=3, ipady=3, anchor = 's')
        self.text_box = tk.scrolledtext.ScrolledText(self.StatusLabelFrame, wrap='word')
        self.text_box.pack()
        ## Error and information output.
        sys.stdout =  StdoutRedirector(self.text_box)
        sys.stderr = StdoutRedirector(self.text_box)


    ### Supporting functions
    def setFormating(self):
        """ Formats the sizes and padding of different widgets"""
        ### Import frame settings
        self.lf_impOptions.columnconfigure(0, pad=3)
        self.lf_impOptions.columnconfigure(1, pad=3)
        # self.lf_impOptions.columnconfigure(2, pad=0)
        # self.lf_impOptions.columnconfigure(3, pad=0)
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

    def messages(self):
        print('Main working directory is {0}.'.format(self.main_dir))
        print('Connection with database at {1} is established for User {0}.'.format(RM.username, self.database))
        print('All work logs by default are save to subfolder {0}.'.format(self.log_folder))
        print('Import backups are stored in subfolder {0}, default output subfolder is {1}.'.format(self.backup_folder, self.output_folder_var))
        print('-----------------------------------')
        
    def export(self,x):
        """ Exports a whole questionnaire, sheet or AC"""
        err1 = ''
        if x=='sheet':
            var = str(self.cbox_sheet.get())
            if var not in self.cbox_sheet['values']:     err1 = 'Selection should be from the given list.'
        elif x=='table':
            var = str(self.cbox_table.get())
            if var not in self.cbox_table['values']:     err1 = 'Selection should be from the given list.' 
        elif x=='AC':
            var = str(self.cbox_AC.get())
            if var not in self.cbox_AC['values']:     err1 = 'Selection should be from the given list.' 
        if err1:
            print(err1)
            return (None)
        if var:
            co_name = str(self.cbox_co.get())
            year = self.cbox_year.get()
            serie = str(self.cbox_series.get())
            if co_name and year and serie:
                co_code = getCO_CODE(co_name)
                serie = RM.series[serie]
                print('Extracting {0} from {1} series for {2}-{3}....'.format(var,serie, co_name, year))
                filename = "{0}_{1}_{2}_{3}.xlsx".format(co_name, year,var,serie)
                filename = "{0}/{1}".format(self.output_folder_var,filename)
                wb = xlsxwriter.Workbook(filename)
                print('File {0} is created..'.format(filename))
                if x=='sheet' and var == 'All':
                    [export_var(i, wb, co_code, int(year), var_type = x ,serie=serie) for i in self.cbox_sheet['values'][1:]]
                else:
                    export_var(var, wb, co_code, int(year), var_type = x,serie=serie)
                wb.close()
                open_file_local(self.main_dir + '/' +  filename)
                print('Done.')
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
                self.output_folder_var  =dirname
                self.output_folder.delete(0, 'end')
                self.output_folder.insert(0, dirname)


    def validate_file(self):
        """ Validating the file for processing"""
        i = self.master.splitlist(self.entry_one.get())
        if not i:
            print('No file is selected.')
            return
        i = i[0]
        if re.search(".xlsx", i):
            x=questionnaire(i,self.database,self.log_folder,RM.username)
            if x.validation():
                self.valid_quest = x
                print('Validation successful, see report in:')
            else:                
                print('Pre-processing validation failed. Some errors exist see log file in:')
                self.valid_quest = ''
            print(x.validation_log_file.name)
            if self.open_log.get():
                open_file_local(self.main_dir + '/' + x.validation_log_file.name)


    def check_file(self):
        file1 = self.master.splitlist(self.entry_one.get())
        if not file1:
            print('No file is selected.')
            return
        # if self.valid_file != file1[0]:
        #     print('Please validate the file first!')
        #     return
        i=file1[0]
        if re.search(".xlsx", i):
            print('Writing data report for \n {0}'.format(i))
            x=questionnaire(i,self.database,self.log_folder,RM.username)
            x.check_region_totals()
            x.check_less()
            x.check_column_sums()
            x.write_data_report()
            print("Data report written to: \n {0}".format(x.data_report_file))
            if self.open_data_report.get():
                open_file_local(self.main_dir + '/' + x.data_report_file)

        
    def imp_file(self):
        """ Imports an excel questionnaire or sheets to the SQL database"""
        if self.valid_quest == '':
            print('Please select a file and validate it.')
            return
        file1  = self.valid_quest.excel_file
        x = self.valid_quest
        msg = "Are you sure you want to import file: \n\n {0} \n\n to {1} series ?".format(file1, x.database_type)
        if not self.MsgBox("Import confirmation" , msg):
            print('You must confirm before proceeding!')
            return
        if re.search(".xlsx", file1):
            print('Inserting {0}'.format(file1))
            # x=questionnaire(i,self.database,self.log_folder,RM.username)
            if(x.database_type == 'REP' and x.edit_mode):
                if(not  self.rep_import.get()):
                    print("You're trying to import the data in REP series. If sure, please tick the checkbox 'Import to REP'! ")
                    return
            x.check_region_totals()
            x.check_less()
            x.check_column_sums()
            x.write_data_report()
            x.extract_data()
            x.extract_comments()
            x.extract_table_comments()
            self.valid_quest = ''
            print("Data report written to: \n {0}".format(x.data_report_file))
            if self.open_data_report.get():
                open_file_local(self.main_dir + '/' + x.data_report_file)
  
    def updtCountry(self):
        """Queries the names of countries that submitted an rm questionnaire"""
        l = getAvailable_countries()
        if l: 
            self.cbox_co['values'] =  list(chain.from_iterable(l))
        else:
            print('No questionnaires exist in the database.')

    def updtYear(self):
        """ For a specific selected country, returns the list of available data years."""
        l= str(self.cbox_co.get())
        if l:
            l = getAvailable_year(l)
            self.cbox_year['values'] = l
        else:
            print('No country is selected.')

    def getSheetTableAC(self,m):
        if m =='sheet':
            l = "SELECT DISTINCT Tab FROM RM_Mapping"
            self.cbox_sheet['values'] =  ['All'] + list(chain.from_iterable(sql_query(l)))
        elif m =='table':
            l = "SELECT DISTINCT RM_TABLE FROM RM_Mapping order by RM_TABLE"
            self.cbox_table['values'] =  list(chain.from_iterable(sql_query(l)))
        elif m=='AC':
            l = "SELECT DISTINCT AC FROM RM_Mapping order by AC"
            self.cbox_AC['values'] =  list(chain.from_iterable(sql_query(l)))

    def migrate_serie(self, from_serie, to_serie):
        """ A function that migrates data between series Reported(REP), Clean(OBS), Estimated(EST)"""
        co_name = str(self.cbox_co.get())
        year = self.cbox_year.get()
        if co_name and year:
            moveSerie(getCO_CODE(co_name), int(year), from_serie, to_serie)
            print('Done.')
        else:
            print('Error: missing country name or year.')

    def MsgBox(self, header = 'Default header' , msg='Generic.'):
        """ A pop-up message box to confirm an action"""
        result = tk.messagebox.askquestion(header, msg, icon='warning')
        if result == 'yes':
            return(True)
        else:
            return (False)
      
   
def main():
    database="Database/Prod.db"
    set_database_file(database)
    root = tk.Tk()
    app = RM(root, database)
    root.mainloop()

if __name__ == '__main__':
    main()

    

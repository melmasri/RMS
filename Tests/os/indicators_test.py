import sys, getpass, os
import datetime
import sqlite3,re

os.chdir('/home/oscar/RMS')
sys.path.append('Libraries')


database="Database/Prod.db"
emco_year=2015
country_name="Lao People's Democratic Republic"

from rmquestionnaire import *



class indicators_test(indicators):
    def teachers_percentage_female(self):
        cursor=self.conn.cursor()
        ## For women add .F
        ## Primary T.1 
        ## Secondary total: T.23.GPV
        ## Lower Secondary: T.2.GPV
        ## Upper Secondary: T.3.GPV
        ind_RT1F="FTP.1"
        ind_RT23GPVF="FTP.2t3"
        ind_RT2GPVF="FTP.2"
        ind_RT3GPVF="FTP.3"
        
        ## Get the values from the database
        RT1F_values = self.column_operation(["T.1.F",0],["T.1",0],lambda x,y:div(x,y)) ## Operation
        RT2GPVF_values = self.column_operation(["T.2.GPV.F",0],["T.2.GPV",0],lambda x,y:div(x,y)) ## Operation
        RT3GPVF_values = self.column_operation(["T.3.GPV.F",0],["T.3.GPV",0],lambda x,y:div(x,y)) ## Operation
        RT23GPVF_values = self.column_operation(["T.23.GPV.F",0],["T.23.GPV",0],lambda x,y:div(x,y)) ## Operation
        
        ## Prepare tupples for sql insertion
        RT1F_sql_tupple=()
        RT2GPVF_sql_tupple=()
        RT3GPVF_sql_tupple=()
        RT23GPVF_sql_tupple=()
        
        for i in range( len(RT1F_values)  ):
            ##The following lines should be erased once the right value is returned by the div function.
            RT1F_values[i][1]=0
            RT2GPVF_values[i][1]=0
            RT3GPVF_values[i][1]=0
            RT23GPVF_values[i][1]=0
            RT1F_sql_tupple = RT1F_sql_tupple + (  (ind_RT1F,self.country_code,i,self.emco_year ,1,RT1F_values[i][0],1, RT1F_values[i][1] ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
        for i in range( len(RT2GPVF_values)  ):
            RT2GPVF_sql_tupple = RT2GPVF_sql_tupple  + (  (ind_RT2GPVF,self.country_code,i,self.emco_year ,1,RT2GPVF_values[i][0],1,RT2GPVF_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
        for i in range( len(RT3GPVF_values)  ):
            RT3GPVF_sql_tupple = RT3GPVF_sql_tupple  + (  (ind_RT3GPVF,self.country_code,i,self.emco_year ,1,RT3GPVF_values[i][0],1,RT3GPVF_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
        for i in range( len(RT23GPVF_values)  ):
            RT23GPVF_sql_tupple = RT23GPVF_sql_tupple  + (  (ind_RT23GPVF,self.country_code,i,self.emco_year ,1,RT23GPVF_values[i][0],1,RT23GPVF_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
        
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)", RT1F_sql_tupple )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",  RT2GPVF_sql_tupple )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",  RT3GPVF_sql_tupple )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",  RT23GPVF_sql_tupple )        
        self.conn.commit()
        cursor.close()

a=indicators_test("/home/oscar/RMS/Database/Prod.db",2015,"Lao People's Democratic Republic")

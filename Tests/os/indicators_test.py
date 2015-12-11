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
    def pupils_teachers_ratio(self):
        """Computes PTRHC's, so head count.
        """
        ## Total number of pupils: E.1, E.2.GPV, E.3.GPV
        ## Total number of teachers: T.1, T.2.GPV, T.3.GPV
        ## We must sum 2 and 2 to get 23 because it does not exist for the pupils.
        cursor=self.conn.cursor()
        ind_PTRHC_1="PTRHC.1"
        ind_PTRHC_2="PTRHC.2"
        ind_PTRHC_3="PTRHC.3"
        ind_PTRHC_23="PTRHC.2t3"
        ind_highest_PTRHC_1="H.PTRHC.1"
        ind_lowest_PTRHC_1="L.PTRHC.1"
        ind_highest_PTRHC_2="H.PTRHC.2"
        ind_lowest_PTRHC_2="L.PTRHC.2"
        ind_highest_PTRHC_3="H.PTRHC.3"
        ind_lowest_PTRHC_3="L.PTRHC.3"
        ind_highest_PTRHC_23="H.PTRHC.2t3"
        ind_lowest_PTRHC_23="L.PTRHC.2t3"

        
        ind_PTRHC_1_values=self.column_operation(["E.1",0],["T.1",0],div)
        ind_PTRHC_2_values=self.column_operation(["E.2.GPV",0],["T.2.GPV",0],div)
        ind_PTRHC_3_values=self.column_operation(["E.3.GPV",0],["T.3.GPV",0],div)

        total_pupils_23=self.column_operation(["E.3.GPV",0],["E.2.GPV",0],sum)
        total_teachers_23=self.column_operation(["T.3.GPV",0],["T.2.GPV",0],sum)
        ind_PTRHC_23_values=list(map(div,total_pupils_23,total_teachers_23))

        H_PTRHC_1=max_sp(ind_PTRHC_1_values)
        L_PTRHC_1=min_sp(ind_PTRHC_1_values)
        H_PTRHC_2=max_sp(ind_PTRHC_2_values)
        L_PTRHC_2=min_sp(ind_PTRHC_2_values)
        H_PTRHC_3=max_sp(ind_PTRHC_3_values)
        L_PTRHC_3=min_sp(ind_PTRHC_3_values)
        H_PTRHC_23=max_sp(ind_PTRHC_23_values)
        L_PTRHC_23=min_sp(ind_PTRHC_23_values)

        H_PTRHC_1[1]=0
        L_PTRHC_1[1]=0
        H_PTRHC_2[1]=0
        L_PTRHC_2[1]=0
        H_PTRHC_3[1]=0
        L_PTRHC_3[1]=0
        H_PTRHC_23[1]=0
        L_PTRHC_23[1]=0

        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_1,self.country_code,0,self.emco_year,1,H_PTRHC_1[0],1,H_PTRHC_1[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_1,self.country_code,0,self.emco_year,1,L_PTRHC_1[0],1,L_PTRHC_1[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_2,self.country_code,0,self.emco_year,1,H_PTRHC_2[0],1,H_PTRHC_2[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_2,self.country_code,0,self.emco_year,1,L_PTRHC_2[0],1,L_PTRHC_2[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_3,self.country_code,0,self.emco_year,1,H_PTRHC_3[0],1,H_PTRHC_3[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_3,self.country_code,0,self.emco_year,1,L_PTRHC_3[0],1,L_PTRHC_3[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_23,self.country_code,0,self.emco_year,1,H_PTRHC_23[0],1,H_PTRHC_23[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_23,self.country_code,0,self.emco_year,1,L_PTRHC_23[0],1,L_PTRHC_23[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )




        ind_PTRHC_1_sql_tupple=()
        ind_PTRHC_2_sql_tupple=()
        ind_PTRHC_3_sql_tupple=()
        ind_PTRHC_23_sql_tupple=()

        for i in range( len(ind_PTRHC_1_values)  ):
            ##The following lines should be erased when their right value is known.
            ind_PTRHC_1_values[i][1]=0
            ind_PTRHC_2_values[i][1]=0
            ind_PTRHC_3_values[i][1]=0
            ind_PTRHC_23_values[i][1]=0

            ind_PTRHC_1_sql_tupple = ind_PTRHC_1_sql_tupple + \
                                     ((ind_PTRHC_1 ,self.country_code,i,self.emco_year,1,ind_PTRHC_1_values[i][0],1,ind_PTRHC_1_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
            ind_PTRHC_2_sql_tupple = ind_PTRHC_2_sql_tupple + \
                                     ((ind_PTRHC_2 ,self.country_code,i,self.emco_year,1,ind_PTRHC_2_values[i][0],1,ind_PTRHC_2_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
            ind_PTRHC_3_sql_tupple = ind_PTRHC_3_sql_tupple + \
                                     ((ind_PTRHC_3 ,self.country_code,i,self.emco_year,1,ind_PTRHC_3_values[i][0],1,ind_PTRHC_3_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
            ind_PTRHC_23_sql_tupple = ind_PTRHC_23_sql_tupple + \
                                     ((ind_PTRHC_23 ,self.country_code,i,self.emco_year,1,ind_PTRHC_23_values[i][0],1,ind_PTRHC_23_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)

        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_1_sql_tupple  )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_2_sql_tupple  )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_3_sql_tupple  )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_23_sql_tupple  )
        self.conn.commit()
        cursor.close()
    
    def newly_recruited_teachers(self):
        cursor=self.conn.cursor()
        ind_per_newly_recruited_primary="NTP.1" ## Perhaps it should be NTP.1.Pu, because there is difference between public and private
        ind_per_newly_recruited_isced2="NTP.2" ## Perhaps it should be NTP.2.Pu, because there is difference between public and private
        ind_per_newly_recruited_isced3="NTP.3" ## Perhaps it should be NTP.2.Pu, because there is difference between public and private
        ind_per_newly_recruited_isced23="NTP.2t3" ## Not in the list, invented.
        ## Newly recruited teachers: NT.1
        ## T.1 -1
        ind_per_newly_recruited_primary_values= self.column_operation(["NT.1",0],["T.1",-1],lambda x,y:div(x,y))
        ind_per_newly_recruited_isced2_values= self.column_operation(["NT.2.GPV",0],["T.2.GPV",-1],lambda x,y:div(x,y))
        ind_per_newly_recruited_isced3_values= self.column_operation(["NT.3.GPV",0],["T.3.GPV",-1],lambda x,y:div(x,y))
        
        newly_recruited_isced2t3 = self.column_operation(["NT.3.GPV",0],["NT.2.GPV",0],lambda x,y:sum(x,y))
        total_isced2t3=self.column_operation(["T.2.GPV",-1],["T.3.GPV",-1],lambda x,y:sum(x,y))
        
        ind_per_newly_recruited_isced23_values= list( map(div,newly_recruited_isced2t3,total_isced2t3))

        ind_per_newly_recruited_primary_sql_tupple=()
        ind_per_newly_recruited_isced2_sql_tupple=()
        ind_per_newly_recruited_isced3_sql_tupple=()
        ind_per_newly_recruited_isced23_sql_tupple=()
        
        for i in range( len(ind_per_newly_recruited_primary_values)  ):
            ##The following lines should be erased when their right value is known.
            ind_per_newly_recruited_primary_values[i][1]=0
            ind_per_newly_recruited_isced2_values[i][1]=0
            ind_per_newly_recruited_isced3_values[i][1]=0
            ind_per_newly_recruited_isced23_values[i][1]=0

            ind_per_newly_recruited_primary_sql_tupple = ind_per_newly_recruited_primary_sql_tupple + \
                                                         ((ind_per_newly_recruited_primary,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_primary_values[i][0],1,ind_per_newly_recruited_primary_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
            ind_per_newly_recruited_isced2_sql_tupple = ind_per_newly_recruited_isced2_sql_tupple + \
                                                                ((ind_per_newly_recruited_isced2,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_isced2_values[i][0],1,ind_per_newly_recruited_isced2_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), )
            ind_per_newly_recruited_isced3_sql_tupple = ind_per_newly_recruited_isced3_sql_tupple +\
                                                        ((ind_per_newly_recruited_isced3,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_isced3_values[i][0],1,ind_per_newly_recruited_isced3_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
            ind_per_newly_recruited_isced23_sql_tupple = ind_per_newly_recruited_isced23_sql_tupple +\
                                                        ((ind_per_newly_recruited_isced23,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_isced23_values[i][0],1,ind_per_newly_recruited_isced23_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)


        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)", ind_per_newly_recruited_primary_sql_tupple )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_per_newly_recruited_isced2_sql_tupple  )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_per_newly_recruited_isced3_sql_tupple  )
        cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_per_newly_recruited_isced23_sql_tupple  )


        self.conn.commit()
        cursor.close()
    
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
        ind_highest_RT1F="H.FTP.1" ## Highest female percentage isced 1
        ind_lowest_RT1F="L.FTP.1" ## Lowest female percentage isced 1
        ind_highest_RT23GPVF="H.FTP.2t3"
        ind_lowest_RT23GPVF="L.FTP.2t3"
        ind_highest_RT2GPVF="H.FTP.2"
        ind_lowest_RT2GPVF="L.FTP.2"
        ind_highest_RT3GPVF="H.FTP.3"
        ind_lowest_RT3GPVF="L.FTP.3"
        
        ## Get the values from the database
        RT1F_values = self.column_operation(["T.1.F",0],["T.1",0],lambda x,y:div(x,y)) ## Operation
        RT2GPVF_values = self.column_operation(["T.2.GPV.F",0],["T.2.GPV",0],lambda x,y:div(x,y)) ## Operation
        RT3GPVF_values = self.column_operation(["T.3.GPV.F",0],["T.3.GPV",0],lambda x,y:div(x,y)) ## Operation
        RT23GPVF_values = self.column_operation(["T.23.GPV.F",0],["T.23.GPV",0],lambda x,y:div(x,y)) ## Operation
        H_RT1F=max_sp(RT1F_values)
        L_RT1F=min_sp(RT1F_values)
        H_RT2GPVF=max_sp(RT2GPVF_values)
        L_RT2GPVF=min_sp(RT2GPVF_values)
        H_RT3GPVF=max_sp(RT3GPVF_values)
        L_RT3GPVF=min_sp(RT3GPVF_values)
        H_RT23GPVF=max_sp(RT23GPVF_values)
        L_RT23GPVF=min_sp(RT23GPVF_values)
        ##The following group of lines should be erased once the right value is returned by the div function.
        H_RT1F[1]=0
        L_RT1F[1]=0
        H_RT2GPVF[1]=0
        L_RT2GPVF[1]=0
        H_RT3GPVF[1]=0
        L_RT3GPVF[1]=0
        H_RT23GPVF[1]=0
        L_RT23GPVF[1]=0

        
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT1F,self.country_code,0,self.emco_year,1,H_RT1F[0],1,H_RT1F[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT1F,self.country_code,0,self.emco_year,1,L_RT1F[0],1,L_RT1F[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT23GPVF,self.country_code,0,self.emco_year,1,H_RT23GPVF[0],1,H_RT23GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT23GPVF,self.country_code,0,self.emco_year,1,L_RT23GPVF[0],1,L_RT23GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT2GPVF,self.country_code,0,self.emco_year,1,H_RT2GPVF[0],1,H_RT2GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT2GPVF,self.country_code,0,self.emco_year,1,L_RT2GPVF[0],1,L_RT2GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT3GPVF,self.country_code,0,self.emco_year,1,H_RT3GPVF[0],1,H_RT3GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
        cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT3GPVF,self.country_code,0,self.emco_year,1,L_RT3GPVF[0],1,L_RT3GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )

        
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

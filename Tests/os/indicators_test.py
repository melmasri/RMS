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
    def compute_percentages(self,indexes_dict ,highest_and_lowest=True):
        """Generic function for computing percentages of columns and computing
        the maximum and minimum if necessary

        the keys of indexes dict has to be the AC code of the
        indicator to compute, the value should be a list with two
        pairs that go in the column operation function.
        
        The functions that calculate the percentages for isced2 and
        isced3 (isced23) do not need to include a value, it can be
        just an empty string, they are calculated based on the other
        two.
        """
        cursor=self.conn.cursor()
        values_dict={}
        maximum_dict={}
        minimum_dict={}
        isced2_ind_name=''
        isced3_ind_name=''
        isced23_ind_name=''
        for indicator_AC in indexes_dict.keys():
            match2=re.search('2$',indicator_AC)
            match3=re.search('3$',indicator_AC)
            match23=re.search('2t3$',indicator_AC)
            if (match2!=None):
                isced2_ind_name=indicator_AC
            if (match3!=None):
                isced3_ind_name=indicator_AC
            if (match23 != None):
                isced23_ind_name=indicator_AC
            else:
                lista1=indexes_dict[indicator_AC][0]
                lista2=indexes_dict[indicator_AC][1]
                print(lista1)
                print(lista2)
                values_dict[indicator_AC]=self.column_operation(lista1,lista2,div)
                print(values_dict[indicator_AC])
                if highest_and_lowest:
                    maximum_dict[indicator_AC]=max_sp(values_dict[indicator_AC])
                    minimum_dict[indicator_AC]=min_sp(values_dict[indicator_AC])
                    ## The following lines can be erased when the mg_ids are figured out
                    maximum_dict[indicator_AC][1]=0
                    minimum_dict[indicator_AC][1]=0
                    
        if isced23_ind_name:
            numerator_23=self.column_operation(indexes_dict[isced2_ind_name][0],indexes_dict[isced3_ind_name][0],sum   )
            denominator_23=self.column_operation(indexes_dict[isced2_ind_name][1],indexes_dict[isced3_ind_name][1],sum   )
            # print(indexes_dict)
            # print(numerator_23)
            # print(denominator_23)
            # print(values_dict)
            values_dict[isced23_ind_name]=list(map(div,numerator_23,denominator_23))
            if highest_and_lowest:
                maximum_dict[isced23_ind_name]=max_sp(values_dict[isced23_ind_name])
                minimum_dict[isced23_ind_name]=min_sp(values_dict[isced23_ind_name])
                ## The following lines can be erased when the mg_ids are figured out
                maximum_dict[isced23_ind_name][1]=0
                minimum_dict[isced23_ind_name][1]=0

        ##We introduce everything in sql
        for indicator_AC in indexes_dict.keys():
            sql_tupple=()
            for i in range(len(values_dict[indicator_AC]  )):
                sql_tupple = sql_tupple + ((indicator_AC ,self.country_code,i,self.emco_year,1,values_dict[indicator_AC][i][0],1,values_dict[indicator_AC][i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
            cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)", sql_tupple  )
            # Now we insert the information for the biggest and smallest
            if highest_and_lowest:
                cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format("H." + indicator_AC  ,self.country_code,0,self.emco_year,1,maximum_dict[indicator_AC][0] ,1, maximum_dict[indicator_AC][1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
                cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format("L." + indicator_AC  ,self.country_code,0,self.emco_year,1,minimum_dict[indicator_AC][0] ,1, minimum_dict[indicator_AC][1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
            
        print(isced2_ind_name)
        print(isced3_ind_name)
        print(isced23_ind_name)
        print(values_dict)
        print(maximum_dict)
        print(minimum_dict)
        self.conn.commit()
        cursor.close()

    def pupils_teachers_ratio(self):
        variables_dict={ "PTRHC.1" : [["E.1",0],["T.1",0]]  , "PTRHC.2": [["E.2.GPV",0],["T.2.GPV",0]] , "PTRHC.3": [["E.3.GPV",0],["T.3.GPV",0]] , "PTRHC.2t3" : '' }
        self.compute_percentages(variables_dict)

    def newly_recruited_teachers(self):
        variables_dict={"NTP.1" : [["NT.1",0],["T.1",-1]]  , "NTP.2" : [["NT.2.GPV",0],["T.2.GPV",-1]] , "NTP.3" : [["NT.3.GPV",0],["T.3.GPV",-1]] , "NTP.2t3" : '' }
        self.compute_percentages(variables_dict)

    def teachers_percentage_female(self):
        variables_dict={ "FTP.1": [["T.1.F",0],["T.1",0]]  , "FTP.2": [["T.2.GPV.F",0],["T.2.GPV",0]]  , "FTP.3" : [["T.3.GPV.F",0],["T.3.GPV",0]]  , "FTP.2t3" : '' }
        self.compute_percentages(variables_dict)

    def percentage_trained_teachers(self):
        # number of trained teachers isced1: T.1.trained, T.2.GPV.trained, T.3.GPV.trained
        # number of teachers : T.1, T.2.GPV T.3.GPV
        # New recruited teachers: NT.1,NT.2.GPV,NT.3.GPV
        # New recruited and trained: NT.1.trained, NT.2.GPV.trained, NT.3.GPV.trained

        # Percentage of trained teachers: TRTP.1, TRTP.2, TRTP.3, TRTP.2t3
        # Percentage of newly recruited teachers: TrNTP.1,  TrNTP.2, TrNTP.3, TrNTP.2t3
        variables_dict1={"TRTP.1": [["T.1.trained",0 ],["T.1",0] ], "TRTP.2": [["T.2.GPV.trained",0 ],["T.2.GPV",0]], "TRTP.3" : [["T.3.GPV.trained",0],["T.3.GPV",0]],  "TRTP.2t3": ''  }
        variables_dict2={"TrNTP.1": [["NT.1.trained",0],["NT.1",0]],"TrNTP.2":[["NT.2.GPV.trained",0],["NT.2.GPV",0]],"TrNTP.3":[["NT.3.GPV.trained",0],["NT.3.GPV",0]],"TrNTP.2t3":''}
        self.compute_percentages(variables_dict1)
        self.compute_percentages(variables_dict2)

    def percentage_private_teachers(self):
        ## Percentage of private teachers: T.1.Pr, T.2.GPV.Pr, T.3.GPV.Pr, T.23.GPV.Pr
        ## number of teachers : T.1, T.2.GPV T.3.GPV
        ## indicators(invented, not foun in table):  TP.1.Pr, TP.2.Pr, TP.3.Pr, TP.2t3.Pr
        variables_dict={"TP.1.Pr":[["T.1.Pr",0],["T.2.GPV.Pr",0]],
                        "TP.2.Pr":[["T.2.GPV.Pr",0],["T.2.GPV",0]],
                        "TP.3.Pr":[["T.3.GPV.Pr",0],["T.3.GPV",0]],
                        "TP.2t3.Pr":''}
        self.compute_percentages(variables_dict)

    def percentage_non_permanent_teachers(self):
        ## Number of non-permanent teachers: T.1.Pr.Fix, T.2.GPV.Pr.Fix, T.3.GPV.Pr.Fix,T.23.GPV.Pr.Fix
        ## Number of permanent teachers: T.1.Pr.Perm, T.2.GPV.Pr.Perm, T.3.GPV.Pr.Perm,T.23.GPV.Pr.Fix
        ## indicators (invented):
        ## Percentage of non permanent teachers among public teachers isced 1: TP.1.Pr.Fix
        ## Percentage of non permanent teachers among public teachers isced 2: TP.2.GPV.Pr.Fix
        ## Percentage of non permanent teachers among public teachers isced 3: TP.3.GPV.Pr.Fix
        ## Percentage of non permanent teachers among public teachers isced 3: TP.2t3.GPV.Pr.Fix
        variables_dict_private={"TP.1.Pr.Fix":[["T.1.Pr.Fix",0],["T.1.Pr",0]],
                                "TP.2.GPV.Pr.Fix": [["T.2.GPV.Pr.Fix",0],["T.2.GPV.Pr",0]],
                                "TP.3.GPV.Pr.Fix": [["T.3.GPV.Pr.Fix",0],["T.3.GPV.Pr",0]],
                                "TP.2t3.GPV.Pr.Fix" : ''
                            }
        variables_dict_public={"TP.1.Pu.Fix":[["T.1.Pu.Fix",0],["T.1.Pu",0]],
                               "TP.2.GPV.Pu.Fix": [["T.2.GPV.Pu.Fix",0],["T.2.GPV.Pu",0]],
                               "TP.3.GPV.Pu.Fix": [["T.3.GPV.Pu.Fix",0],["T.3.GPV.Pu",0]],
                               "TP.2t3.GPV.Pu.Fix" : ''
                           }
        
        self.compute_percentages(variables_dict_public,False)
        self.compute_percentages(variables_dict_private,False)
    
    # def pupils_teachers_ratio(self):
    #     """Computes PTRHC's, so head count.
    #     """
    #     ## Total number of pupils: E.1, E.2.GPV, E.3.GPV
    #     ## Total number of teachers: T.1, T.2.GPV, T.3.GPV
    #     ## We must sum 2 and 2 to get 23 because it does not exist for the pupils.
    #     cursor=self.conn.cursor()
    #     ind_PTRHC_1="PTRHC.1"
    #     ind_PTRHC_2="PTRHC.2"
    #     ind_PTRHC_3="PTRHC.3"
    #     ind_PTRHC_23="PTRHC.2t3"
    #     ind_highest_PTRHC_1="H.PTRHC.1"
    #     ind_lowest_PTRHC_1="L.PTRHC.1"
    #     ind_highest_PTRHC_2="H.PTRHC.2"
    #     ind_lowest_PTRHC_2="L.PTRHC.2"
    #     ind_highest_PTRHC_3="H.PTRHC.3"
    #     ind_lowest_PTRHC_3="L.PTRHC.3"
    #     ind_highest_PTRHC_23="H.PTRHC.2t3"
    #     ind_lowest_PTRHC_23="L.PTRHC.2t3"

        
    #     ind_PTRHC_1_values=self.column_operation(["E.1",0],["T.1",0],div)
    #     ind_PTRHC_2_values=self.column_operation(["E.2.GPV",0],["T.2.GPV",0],div)
    #     ind_PTRHC_3_values=self.column_operation(["E.3.GPV",0],["T.3.GPV",0],div)

    #     total_pupils_23=self.column_operation(["E.3.GPV",0],["E.2.GPV",0],sum)
    #     total_teachers_23=self.column_operation(["T.3.GPV",0],["T.2.GPV",0],sum)
    #     ind_PTRHC_23_values=list(map(div,total_pupils_23,total_teachers_23))

    #     H_PTRHC_1=max_sp(ind_PTRHC_1_values)
    #     L_PTRHC_1=min_sp(ind_PTRHC_1_values)
    #     H_PTRHC_2=max_sp(ind_PTRHC_2_values)
    #     L_PTRHC_2=min_sp(ind_PTRHC_2_values)
    #     H_PTRHC_3=max_sp(ind_PTRHC_3_values)
    #     L_PTRHC_3=min_sp(ind_PTRHC_3_values)
    #     H_PTRHC_23=max_sp(ind_PTRHC_23_values)
    #     L_PTRHC_23=min_sp(ind_PTRHC_23_values)

    #     H_PTRHC_1[1]=0
    #     L_PTRHC_1[1]=0
    #     H_PTRHC_2[1]=0
    #     L_PTRHC_2[1]=0
    #     H_PTRHC_3[1]=0
    #     L_PTRHC_3[1]=0
    #     H_PTRHC_23[1]=0
    #     L_PTRHC_23[1]=0

    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_1,self.country_code,0,self.emco_year,1,H_PTRHC_1[0],1,H_PTRHC_1[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_1,self.country_code,0,self.emco_year,1,L_PTRHC_1[0],1,L_PTRHC_1[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_2,self.country_code,0,self.emco_year,1,H_PTRHC_2[0],1,H_PTRHC_2[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_2,self.country_code,0,self.emco_year,1,L_PTRHC_2[0],1,L_PTRHC_2[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_3,self.country_code,0,self.emco_year,1,H_PTRHC_3[0],1,H_PTRHC_3[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_3,self.country_code,0,self.emco_year,1,L_PTRHC_3[0],1,L_PTRHC_3[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_PTRHC_23,self.country_code,0,self.emco_year,1,H_PTRHC_23[0],1,H_PTRHC_23[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_PTRHC_23,self.country_code,0,self.emco_year,1,L_PTRHC_23[0],1,L_PTRHC_23[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )




    #     ind_PTRHC_1_sql_tupple=()
    #     ind_PTRHC_2_sql_tupple=()
    #     ind_PTRHC_3_sql_tupple=()
    #     ind_PTRHC_23_sql_tupple=()

    #     for i in range( len(ind_PTRHC_1_values)  ):
    #         ##The following lines should be erased when their right value is known.
    #         ind_PTRHC_1_values[i][1]=0
    #         ind_PTRHC_2_values[i][1]=0
    #         ind_PTRHC_3_values[i][1]=0
    #         ind_PTRHC_23_values[i][1]=0

    #         ind_PTRHC_1_sql_tupple = ind_PTRHC_1_sql_tupple + \
    #                                  ((ind_PTRHC_1 ,self.country_code,i,self.emco_year,1,ind_PTRHC_1_values[i][0],1,ind_PTRHC_1_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
    #         ind_PTRHC_2_sql_tupple = ind_PTRHC_2_sql_tupple + \
    #                                  ((ind_PTRHC_2 ,self.country_code,i,self.emco_year,1,ind_PTRHC_2_values[i][0],1,ind_PTRHC_2_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
    #         ind_PTRHC_3_sql_tupple = ind_PTRHC_3_sql_tupple + \
    #                                  ((ind_PTRHC_3 ,self.country_code,i,self.emco_year,1,ind_PTRHC_3_values[i][0],1,ind_PTRHC_3_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
    #         ind_PTRHC_23_sql_tupple = ind_PTRHC_23_sql_tupple + \
    #                                  ((ind_PTRHC_23 ,self.country_code,i,self.emco_year,1,ind_PTRHC_23_values[i][0],1,ind_PTRHC_23_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)

    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_1_sql_tupple  )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_2_sql_tupple  )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_3_sql_tupple  )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_PTRHC_23_sql_tupple  )
    #     self.conn.commit()
    #     cursor.close()
    
    # def newly_recruited_teachers(self):
    #     cursor=self.conn.cursor()
    #     ind_per_newly_recruited_primary="NTP.1" ## Perhaps it should be NTP.1.Pu, because there is difference between public and private
    #     ind_per_newly_recruited_isced2="NTP.2" ## Perhaps it should be NTP.2.Pu, because there is difference between public and private
    #     ind_per_newly_recruited_isced3="NTP.3" ## Perhaps it should be NTP.2.Pu, because there is difference between public and private
    #     ind_per_newly_recruited_isced23="NTP.2t3" ## Not in the list, invented.
    #     ## Newly recruited teachers: NT.1
    #     ## T.1 -1
    #     ind_per_newly_recruited_primary_values= self.column_operation(["NT.1",0],["T.1",-1],lambda x,y:div(x,y))
    #     ind_per_newly_recruited_isced2_values= self.column_operation(["NT.2.GPV",0],["T.2.GPV",-1],lambda x,y:div(x,y))
    #     ind_per_newly_recruited_isced3_values= self.column_operation(["NT.3.GPV",0],["T.3.GPV",-1],lambda x,y:div(x,y))
        
    #     newly_recruited_isced2t3 = self.column_operation(["NT.3.GPV",0],["NT.2.GPV",0],lambda x,y:sum(x,y))
    #     total_isced2t3=self.column_operation(["T.2.GPV",-1],["T.3.GPV",-1],lambda x,y:sum(x,y))
        
    #     ind_per_newly_recruited_isced23_values= list( map(div,newly_recruited_isced2t3,total_isced2t3))

    #     ind_per_newly_recruited_primary_sql_tupple=()
    #     ind_per_newly_recruited_isced2_sql_tupple=()
    #     ind_per_newly_recruited_isced3_sql_tupple=()
    #     ind_per_newly_recruited_isced23_sql_tupple=()
        
    #     for i in range( len(ind_per_newly_recruited_primary_values)  ):
    #         ##The following lines should be erased when their right value is known.
    #         ind_per_newly_recruited_primary_values[i][1]=0
    #         ind_per_newly_recruited_isced2_values[i][1]=0
    #         ind_per_newly_recruited_isced3_values[i][1]=0
    #         ind_per_newly_recruited_isced23_values[i][1]=0

    #         ind_per_newly_recruited_primary_sql_tupple = ind_per_newly_recruited_primary_sql_tupple + \
    #                                                      ((ind_per_newly_recruited_primary,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_primary_values[i][0],1,ind_per_newly_recruited_primary_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
    #         ind_per_newly_recruited_isced2_sql_tupple = ind_per_newly_recruited_isced2_sql_tupple + \
    #                                                             ((ind_per_newly_recruited_isced2,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_isced2_values[i][0],1,ind_per_newly_recruited_isced2_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), )
    #         ind_per_newly_recruited_isced3_sql_tupple = ind_per_newly_recruited_isced3_sql_tupple +\
    #                                                     ((ind_per_newly_recruited_isced3,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_isced3_values[i][0],1,ind_per_newly_recruited_isced3_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)
    #         ind_per_newly_recruited_isced23_sql_tupple = ind_per_newly_recruited_isced23_sql_tupple +\
    #                                                     ((ind_per_newly_recruited_isced23,self.country_code,i,self.emco_year,1,ind_per_newly_recruited_isced23_values[i][0],1,ind_per_newly_recruited_isced23_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),)


    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)", ind_per_newly_recruited_primary_sql_tupple )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_per_newly_recruited_isced2_sql_tupple  )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_per_newly_recruited_isced3_sql_tupple  )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",ind_per_newly_recruited_isced23_sql_tupple  )


    #     self.conn.commit()
    #     cursor.close()
    
    # def teachers_percentage_female(self):
    #     cursor=self.conn.cursor()
    #     ## For women add .F
    #     ## Primary T.1 
    #     ## Secondary total: T.23.GPV
    #     ## Lower Secondary: T.2.GPV
    #     ## Upper Secondary: T.3.GPV
    #     ind_RT1F="FTP.1"
    #     ind_RT23GPVF="FTP.2t3"
    #     ind_RT2GPVF="FTP.2"
    #     ind_RT3GPVF="FTP.3"
    #     ind_highest_RT1F="H.FTP.1" ## Highest female percentage isced 1
    #     ind_lowest_RT1F="L.FTP.1" ## Lowest female percentage isced 1
    #     ind_highest_RT23GPVF="H.FTP.2t3"
    #     ind_lowest_RT23GPVF="L.FTP.2t3"
    #     ind_highest_RT2GPVF="H.FTP.2"
    #     ind_lowest_RT2GPVF="L.FTP.2"
    #     ind_highest_RT3GPVF="H.FTP.3"
    #     ind_lowest_RT3GPVF="L.FTP.3"
        
    #     ## Get the values from the database
    #     RT1F_values = self.column_operation(["T.1.F",0],["T.1",0],lambda x,y:div(x,y)) ## Operation
    #     RT2GPVF_values = self.column_operation(["T.2.GPV.F",0],["T.2.GPV",0],lambda x,y:div(x,y)) ## Operation
    #     RT3GPVF_values = self.column_operation(["T.3.GPV.F",0],["T.3.GPV",0],lambda x,y:div(x,y)) ## Operation
    #     RT23GPVF_values = self.column_operation(["T.23.GPV.F",0],["T.23.GPV",0],lambda x,y:div(x,y)) ## Operation
    #     H_RT1F=max_sp(RT1F_values)
    #     L_RT1F=min_sp(RT1F_values)
    #     H_RT2GPVF=max_sp(RT2GPVF_values)
    #     L_RT2GPVF=min_sp(RT2GPVF_values)
    #     H_RT3GPVF=max_sp(RT3GPVF_values)
    #     L_RT3GPVF=min_sp(RT3GPVF_values)
    #     H_RT23GPVF=max_sp(RT23GPVF_values)
    #     L_RT23GPVF=min_sp(RT23GPVF_values)
    #     ##The following group of lines should be erased once the right value is returned by the div function.
    #     H_RT1F[1]=0
    #     L_RT1F[1]=0
    #     H_RT2GPVF[1]=0
    #     L_RT2GPVF[1]=0
    #     H_RT3GPVF[1]=0
    #     L_RT3GPVF[1]=0
    #     H_RT23GPVF[1]=0
    #     L_RT23GPVF[1]=0

        
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT1F,self.country_code,0,self.emco_year,1,H_RT1F[0],1,H_RT1F[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT1F,self.country_code,0,self.emco_year,1,L_RT1F[0],1,L_RT1F[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT23GPVF,self.country_code,0,self.emco_year,1,H_RT23GPVF[0],1,H_RT23GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT23GPVF,self.country_code,0,self.emco_year,1,L_RT23GPVF[0],1,L_RT23GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT2GPVF,self.country_code,0,self.emco_year,1,H_RT2GPVF[0],1,H_RT2GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT2GPVF,self.country_code,0,self.emco_year,1,L_RT2GPVF[0],1,L_RT2GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_highest_RT3GPVF,self.country_code,0,self.emco_year,1,H_RT3GPVF[0],1,H_RT3GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )
    #     cursor.execute( "INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (\"{}\",{},{},{},{},{},{},{},'{}')".format(ind_lowest_RT3GPVF,self.country_code,0,self.emco_year,1,L_RT3GPVF[0],1,L_RT3GPVF[1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) )

        
    #     ## Prepare tupples for sql insertion
    #     RT1F_sql_tupple=()
    #     RT2GPVF_sql_tupple=()
    #     RT3GPVF_sql_tupple=()
    #     RT23GPVF_sql_tupple=()
        
    #     for i in range( len(RT1F_values)  ):
    #         ##The following lines should be erased once the right value is returned by the div function.
    #         RT1F_values[i][1]=0
    #         RT2GPVF_values[i][1]=0
    #         RT3GPVF_values[i][1]=0
    #         RT23GPVF_values[i][1]=0
    #         RT1F_sql_tupple = RT1F_sql_tupple + (  (ind_RT1F,self.country_code,i,self.emco_year ,1,RT1F_values[i][0],1, RT1F_values[i][1] ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
    #     for i in range( len(RT2GPVF_values)  ):
    #         RT2GPVF_sql_tupple = RT2GPVF_sql_tupple  + (  (ind_RT2GPVF,self.country_code,i,self.emco_year ,1,RT2GPVF_values[i][0],1,RT2GPVF_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
    #     for i in range( len(RT3GPVF_values)  ):
    #         RT3GPVF_sql_tupple = RT3GPVF_sql_tupple  + (  (ind_RT3GPVF,self.country_code,i,self.emco_year ,1,RT3GPVF_values[i][0],1,RT3GPVF_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
    #     for i in range( len(RT23GPVF_values)  ):
    #         RT23GPVF_sql_tupple = RT23GPVF_sql_tupple  + (  (ind_RT23GPVF,self.country_code,i,self.emco_year ,1,RT23GPVF_values[i][0],1,RT23GPVF_values[i][1],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ) ,  )
        
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)", RT1F_sql_tupple )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",  RT2GPVF_sql_tupple )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",  RT3GPVF_sql_tupple )
    #     cursor.executemany("INSERT OR REPLACE INTO EDU_INDICATOR_EST (IND_ID,CO_CODE,ADM_CODE,IND_YEAR,FRM_ID,FIG,QUAL,MAGN,CALC_DATE) VALUES (?,?,?,?,?,?,?,?,?)",  RT23GPVF_sql_tupple )        
    #     self.conn.commit()
    #     cursor.close()


        

a=indicators_test("/home/oscar/RMS/Database/Prod.db",2015,"Lao People's Democratic Republic")
female_percentage={"FTP.1": [ ["T.1.F",0],["T.1",0] ]   , "FTP.2":[["T.2.GPV.F",0],["T.2.GPV",0] ] , "FTP.3":[["T.23.GPV.F",0],["T.23.GPV",0] ] , "FTP.2t3": [] }

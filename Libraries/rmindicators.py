import sqlite3,re
import sys, getpass, os, csv
import datetime
import csv

from functools import reduce


##################################################
#### table Algebra for sum/div/prod operations
##################################################
## Default algebra tables
algebra_sum = {'a': {'a': 'a', 'm': 'm', 'n': 'n','x':'x', 'value':'value'},
               'm': {'a': 'm', 'm': 'm', 'n': 'm','x':'m', 'value':'m'},
               'n': {'a': 'n', 'm': 'm', 'n': 'n','x':'x', 'value':'value'},
               'x': {'a': 'x', 'm': 'm', 'n': 'x','x':'x', 'value': 'x' }, 
               'value': {'a': 'value', 'm': 'm', 'n' :'value','x':'x', 'value':'value'}}
algebra_prod = algebra_sum
algebra_div  = algebra_sum

def read_algebra():
    """  Read an algebra table from a csv file and convert to a dictionary
    """
    # Reading sum algebra
    algfiles = ['algebra-sum.csv', 'algebra-prod.csv','algebra-div.csv']
    algop = ['Sum', 'Prod', 'Div']
    if os.path.isfile('Libraries/'+algfiles[0]):
        print('File {0} found, reading algebra..'.format(algfiles[0]))
        data = csv.DictReader(open('Libraries/'+ algfiles[0]))
        global algebra_sum
        algebra_sum  = arrange_algebra_dist(data,algop[0])
    if os.path.isfile('Libraries/'+algfiles[1]):
        print('File {0} found, reading algebra..'.format(algfiles[1]))
        data = csv.DictReader(open('Libraries/'+algfiles[1]))
        global algebra_prod
        algebra_prod  = arrange_algebra_dist(data,algop[1])
    if os.path.isfile('Libraries/'+ algfiles[2]):
        print('File {0} found, reading algebra..'.format(algfiles[2]))
        data = csv.DictReader(open('Libraries/'+algfiles[2]))
        global algebra_div
        algebra_div  = arrange_algebra_dist(data,algop[2])

def arrange_algebra_dist(data, op= 'Sum'):
    """ Arranging algebra from a csv file read in data based os an operation (op) in a dictionary as seen in the global variables.
        The left corner of the table in the csv file should be the op, case sensitive
    """
    result = {}
    for row in data:
        key = row.pop(op)
        if key in result:
            # implement your duplicate row handling here
            pass
        result[key] = row
    return(result)

## Reads new algebra tables
read_algebra()
##################################################

##################################################
##### Generic mathematical operators
##################################################           
def sum(x,y):
    """ 
    Sums two tuppels x = (fig, mg_symbol), y = (fig, mg_symbol). 
    Returns a tupple (fig, symbol), where symbol is the result of the multiplication tables, fig is '' is symbol is n, m ,a or x.

    Algebra Table 
    Sum,a, m,n,x, value
    a,a, m,n,x, value
    m,m, m,m,m,m
    n,n, m,n,x, value
    x,x, m, x,x, x
    value, value, m, value,x, value
    """
    global algebra_sum
    algeb = algebra_sum[x[1]][y[1]]
    if algeb =='value':
        return([(x[0] or 0 ) + (y[0] or 0),'value'])
    return(['',algeb])

def prod(x,y):
    """ 
    Product of two tuppels x = (fig, mg_symbol), y = (fig, mg_symbol). 
    Returns a tupple (fig, symbol), where symbol is the result of the multiplication tables, fig is '' is symbol is n, m ,a or x.

    Algebra Table 
    Prod,a, m,n,x, value
    a,a, m,n,x, value
    m,m, m,m,m,m
    n,n, m,n,x, value
    x,x, m, x,x, x
    value, value, m, value,x, value
    """
    global algebra_prod
    algeb = algebra_prod[x[1]][y[1]]
    if algeb =='value':
        return([(x[0] or 0)*(y[0] or 0),'value'])
    return(['',algeb])

def div(x,y):
    """ 
    Division of two tuppels x = (fig, mg_symbol), y = (fig, mg_symbol). 
    Returns a tupple (fig, symbol), where symbol is the result of the multiplication tables, fig is '' is symbol is n, m ,a or x.
    
    Algebra Table 
    Div,a, m,n,x, value
    a,a, m,n,x, value
    m,m, m,m,m,m
    n,n, m,n,x, value
    x,x, m, x,x, x
    value, value, m, value,x, value
    """
    global algebra_div
    algeb = algebra_div[x[1]][y[1]]
    if algeb == 'value':
        return([(x[0] or 0)/(y[0] or 0),'value'])
    return(['',algeb])

def op2col(col1, col2, op):
    """ Returns the op(sum/div/prod) of two columns"""
    return  list(map(lambda x,y: op(x, y), col1, col2))
##################################################

##################################################
#### Highest level of EdAttain
##################################################
def highestEA_list(level, indic, offset=0):
    """ Returns the ratio of the highest level of EdAttain given the level
        offset is the year, 0 for current year assigned by indic, -1 is N-1 year
        indic an instance of indicator class"""
    ac_pop = 'Pop.Ag0t99'
    if len(level) ==1:
        a = indic.column_operation([level[0], offset], [ac_pop,offset], lambda x,y: div(x,y)) 
    else:    
        b = list(map(lambda x: indic.column_operation([x, offset], [ac_pop,offset], lambda x,y: div(x,y)), level))
        a = reduce(lambda x,y: op2col(x, y, sum), b)
    return(a)

def highestEA(schoolLevel,  indic, offset=0):
    """ 
    Returns a dictionary of the indicator EA(x)PT.(y).(z), where
    x is 2m, 3, 4, or 5p as the attainment levels
    y is the parameter schoolLevel defined by ['1', '2.GPV', '3.GPV', '23.GPV']
    z is ['', '.Pu', '.Pr']
    
    The key of the dictionary is the indicator name EA(x)PT.(y).(z) and the value is
    a list of calculated figures for each region. 
    
    indic is an instance of indicator class,
    offset is the year offset, 0 as current year defined in indicator class indic, and -1, is the N-1 year.
    """
    if schoolLevel not in ['1', '2.GPV', '3.GPV', '23.GPV']:
        print("The only schoolLevel allowed is ['1', '2.GPV', '3.GPV', '23.GPV'] ")
        return
    
    dic_level = {'2m':['T.x.EA.2m'] , '3':['T.x.EA.3'], '4': ['T.x.EA.4'], '5p':['T.x.EA.5', 'T.x.EA.6','T.x.EA.7','T.x.EA.8'], 'uk':['T.x.EA.uk'] }
    typeSchool  = ['', '.Pu', '.Pr']
    EA_dic = {}
    for key, value in dic_level.items():
        for t in typeSchool:
            name = 'EA' + key + 'PT.' + s + t
            level_list = list(map(lambda x: x.replace('x', s+t), dic_level[key]))
            EA_dic.update({name:highestEA_list(level_list, indic, offset)})
    return EA_dic


def EA_all(indic, offset=0):
    """
    Calculates the highest EdAttain for for levels  ['1', '2.GPV', '3.GPV', '23.GPV']
    returns a dictionary of dictionaries. The first level is of size 4, as for each level
    and the second levels is a dictionary creates by highestEA_list  as:
    
    A dictionary of the indicator EA(x)PT.(y).(z), where
    x is 2m, 3, 4, or 5p as the attainment levels
    y is the parameter schoolLevel defined by ['1', '2.GPV', '3.GPV', '23.GPV']
    z is ['', '.Pu', '.Pr']
    
    The key of the dictionary is the indicator name EA(x)PT.(y).(z) and the value is
    a list of calculated figures for each region. 
    """
    ea = {} 
    isced = ['1', '2.GPV', '3.GPV', '23.GPV']
    for s in isced:
        ea.update({s : highestEA(s,  indic, offset) })
    return(ea)    


##################################################
### Mean functions
##################################################
def mean_category(indic, codes, midpoints, ac_pop = 'Pop.Ag0t99'):
    """ Calculates a generic mean by category given the category and a list of indicators
    returns the mean category by ADM
    """
    if len(midpoints)!=len(codes):
        print("Length of midpoints doesn't equal length of codes!")
        return
    temp = list(map(lambda z,v: indic.column_operation([z,0], [ac_pop, 0], lambda x,y:   prod(div(x,y), v)),codes, midpoints))
    temp = list(map(lambda l: reduce(lambda x,y: sum(x,y), l), temp))
    return(temp)

def mean_age_level(indic,level):
    """ 
    Given a level of the format ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV'] 
    and an instance of class indicator (indic), 
    the function returns the average mean age of the given level for total, public and private in a dictionary format, with indicator names as key of the dictionary.
    
    The average is calculated by using the midpoint ages defined in the midpoint variable below in a ascending order. 

"""
    if level not in ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV']:
        print("The only levels allowed are ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV']")
        return
    midpoint = [[20,''], [24,''], [34,''], [44,''],[54,''], [65,'']]
    levelsExt = ['x.Ag20m','x.Ag20t29','x.Ag30t39','x.Ag40t49','x.Ag50t59','x.Ag60p']
    typeSchool  = ['', '.Pu', '.Pr']
    MAge = {}
    for t in typeSchool:
        name = 'MAge' + level + t
        codes = list(map(lambda x: x.replace('x', level+t), levelsExt))
        MAge.update({name:mean_category(indic,codes,midpoint)})
    return MAge
    
def mean_exp_level(indic, level):
    if level not in ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV']:
        print("The only levels allowed are ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV']")
        return
    midpoint = [[1.5,''], [4,''], [8,''], [13,''],[15,'']] ## midpoint years of experience for each level.
    levelsExt = ['z.Exp1t2', 'z.Exp3t5','z.Exp6t10', 'z.Exp11t15', 'z.Exp15p']
    typeSchool  = ['', '.Pu', '.Pr']
    MExp = {}
    for t in typeSchool:
        name = 'MExp' + level + t
        codes = list(map(lambda x: x.replace('z', level+t), levelsExt))
        print(codes)
        MExp.update({name:mean_category(indic,codes,midpoint)})
    return MExp

def mean_level(indic, levelFun):
    """
    Calculates the mean of age/exp/... for the following levels ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV']. 
    It requires a levelFun(indic, level) as in mean_age_level or mean_exp_level. 

    Returns a dictionary for each level in ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV'], with the key as the level and the result is the return of levelFun.
    """
    M = {}
    for s in ['T.1', 'T.2.GPV', 'T.3.GPV', 'T.23.GPV']:
        M.update({s: levelFun(indic, s)})
    return M


##################################################
##################################################

def min_sp(lala):
    """Used to find the minimum value for the lowest female percentage
    calculation.

    """
    def auxf(x,y):
        if ( (type(x[0]) in [int,float]) and (type(y[0]) in [int,float]) ):
            return ( [min(x[0],y[0]),''] )
        elif (type(x) in [int,float]):
            return (y)
        else:
            return(x)
    return(reduce(auxf,lala[1:])) # lala[1:] because the first element
                                  # corresponds to the country value
                                  # and we only want it for the
                                  # regions.

def max_sp(lala):
    """Used to find the maximum value for the highest female percentage
    calculation.

    """
    def auxf(x,y):
        if ( (type(x[0]) in [int,float]) and (type(y[0]) in [int,float]) ):
            return ( [max(x[0],y[0]),''] )
        elif (type(x) in [int,float]):
            return (y)
        else:
            return(x)

    return(reduce(auxf,lala[1:]))


def inverse_mg_id(x):
    if type(x) in [int,float]:
        return('')
    elif x==3:
        return('X')
    elif x==6:
        return('A')
    elif x=="D":
        return("m")

def none_emptytr(x):
    if x==None:
       return('value')
    else:
        return(x)
    
class indicators():
    def get_nadm1(self):
        """Gets the number of regions"""
        cursor=self.conn.cursor()
        cursor.execute("select count(ADM_CODE) from regions where co_code={} and ADM_CODE>0".format(self.country_code))
        nadm1=cursor.fetchone()
        
    def set_database_connection(self,database_file):
        """Sets the connection to the database"""
        self.conn=sqlite3.connect(database_file)
        
    def get_country_code(self):
        """Sets the country code by looking in the COUNTRY table.

        This function searches the country code in the COUNTRY table
        using the self.country_name variable of the class. It assumes
        that there will be an exact match up to case. If this is not
        the case it returns None.
        """
        name=self.country_name.upper()
        # The following is necessary for compatibility with sql syntax
        name="'"+re.sub("'","''",name)+"'"
        cursor=self.conn.cursor()
        #The following is not working so I am using .format, but this is not secure
#        cursor.execute(u'SELECT CO_CODE FROM COUNTRY  WHERE UPPER(CO_LONG_NAME) IS ?', (name,) )
        cursor.execute("SELECT CO_CODE FROM COUNTRY  WHERE UPPER(CO_LONG_NAME) IS {0};".format(name) )
        country_code=cursor.fetchone()
        if(country_code==None):
            self.country_code=0
        else:
            self.country_code=country_code[0]
        cursor.close()

        
    def column_operation(self,info1,info2,operation):
        """Perform column operations given ACs and year.
        
        This function returns a vector with an operation applied to
        two columns. infoi is a vector [ACi,yeari], where ACi is an
        alphanumeric code and year is the year for which that
        alphanumeric code is going to be computed. operation is a
        function that receives two arguments. This is the operation
        that is going to be applied element by element to both colums.
        The years should be zero or -1.
        """
        AC1=info1[0]
        year1=info1[1]
        AC2=info2[0]
        year2=info2[1]
        cursor=self.conn.cursor()
        cursor.execute("SELECT EMC_ID FROM RM_Mapping WHERE AC='{0}' AND CUR_YEAR={1} LIMIT 1".format(AC1,year1))
        emc_id1=cursor.fetchone()[0]
        cursor.execute("SELECT EMC_ID FROM RM_Mapping WHERE AC='{0}' AND CUR_YEAR={1} LIMIT 1".format(AC2,year2))
        emc_id2=cursor.fetchone()[0]
        #cursor.execute("select EM_FIG,MG_ID from EDU_METER97_REP where CO_CODE={} and emc_id={} and emco_year={}".format(self.country_code,emc_id1,self.emco_year+year1))
        cursor.execute("select a.EM_FIG,b.SYMBOL from EDU_METER97_REP AS a LEFT JOIN MAGNITUDE AS b ON ( a.mg_id = b.mg_id) WHERE a.CO_CODE={} and a.emc_id={} AND a.emco_year={} ORDER BY ADM_CODE ASC".format(self.country_code,emc_id1,self.emco_year+year1));
        values1=cursor.fetchall()  #list(map(lambda x: x[0],cursor.fetchall() ))
        values1= list(map( lambda x: [x[0],none_emptytr(x[1])],values1 ))
        #values1=list(map(lambda x: aux(x[0]),values1 ))
        #cursor.execute("select EM_FIG,MG_ID from EDU_METER97_REP where CO_CODE={} and emc_id={} and emco_year={}".format(self.country_code,emc_id2,self.emco_year+year2))
        cursor.execute("select a.EM_FIG,b.SYMBOL from EDU_METER97_REP AS a LEFT JOIN MAGNITUDE AS b ON ( a.mg_id = b.mg_id) WHERE a.CO_CODE={} and a.emc_id={} AND a.emco_year={} ORDER BY ADM_CODE ASC".format(self.country_code,emc_id2,self.emco_year+year2));
        values2=cursor.fetchall() #list(map(lambda x: x[0],cursor.fetchall() ))
        values2= list(map( lambda x: [x[0],none_emptytr(x[1])],values2 ))
        #values2=list(map(lambda x: aux(x[0]),values2 ))
        column_operation_result=list(map(operation,values1,values2))
        cursor.close()
        return column_operation_result

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
            match2=re.search('2[^t]|2$',indicator_AC)
            match3=re.search('[^t]3',indicator_AC)
            match23=re.search('2t3',indicator_AC)
            if (match2!=None):
                isced2_ind_name=indicator_AC
            if (match3!=None):
                isced3_ind_name=indicator_AC
            if (match23 != None):
                isced23_ind_name=indicator_AC
            else:
                lista1=indexes_dict[indicator_AC][0]
                lista2=indexes_dict[indicator_AC][1]
                values_dict[indicator_AC]=self.column_operation(lista1,lista2,div)
                if highest_and_lowest:
                    maximum_dict[indicator_AC]=max_sp(values_dict[indicator_AC])
                    minimum_dict[indicator_AC]=min_sp(values_dict[indicator_AC])
                    ## The following lines can be erased when the mg_ids are figured out
                    maximum_dict[indicator_AC][1]=0
                    minimum_dict[indicator_AC][1]=0
                    
        if isced23_ind_name:
            numerator_23=self.column_operation(indexes_dict[isced2_ind_name][0],indexes_dict[isced3_ind_name][0],sum   )
            denominator_23=self.column_operation(indexes_dict[isced2_ind_name][1],indexes_dict[isced3_ind_name][1],sum   )
            
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
            
        # print(isced2_ind_name)
        # print(isced3_ind_name)
        # print(isced23_ind_name)
        # print(values_dict)
        # print(maximum_dict)
        # print(minimum_dict)
        self.conn.commit()
        cursor.close()

    def pupils_teachers_ratio(self):
        ## Total number of pupils: E.1, E.2.GPV, E.3.GPV
        ## Total number of teachers: T.1, T.2.GPV, T.3.GPV
        ## We must sum 2 and 3 to get 23 because it does not exist for the pupils.
        variables_dict={ "PTRHC.1" : [["E.1",0],["T.1",0]]  , "PTRHC.2": [["E.2.GPV",0],["T.2.GPV",0]] , "PTRHC.3": [["E.3.GPV",0],["T.3.GPV",0]] , "PTRHC.2t3" : '' }
        self.compute_percentages(variables_dict)

    def newly_recruited_teachers(self):
        ## NTP.2t3 was not in the list, so we invented it.
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
        variables_dict={"TP.1.Pr":[["T.1.Pr",0],["T.1",0]],
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

    def compute_all_indicators(self):
        self.pupils_teachers_ratio()
        self.newly_recruited_teachers()
        self.teachers_percentage_female()
        self.percentage_trained_teachers()
        self.percentage_private_teachers()
        self.percentage_non_permanent_teachers()
    
        
    def __init__ (self,database_file,emco_year,country_name):
        self.set_database_connection(database_file)
        self.emco_year=emco_year
        self.country_name=country_name
        self.get_country_code()

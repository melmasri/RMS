import sqlite3 #sql connection



def set_database_file(database_file):
    """Sets the databse file.

    This function will set the country_cursor global variable to  a
    cursor connected to the dabase in databse_file
    """
    global con
    con=sqlite3.connect(database_file)
    if con:
        print('Connectoin established')
    else :
        print('Connectioned failed.')


def sql_query(sql_str):
    """ Write sql queries"""
    global con
    database_cursor = con.cursor()
    if database_cursor.execute(sql_str):
        aux = database_cursor.fetchall()
        database_cursor.close()
        return aux
    else:
        database_cursor.close()
        None    

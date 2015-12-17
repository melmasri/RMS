import sqlite3 #sql connection



def set_database_file(database_file):
    """Sets the database file.

    This function will set the country_cursor global variable to  a
    cursor connected to the debase in database_file
    """
    global con
    con=sqlite3.connect(database_file)
    if con:
        print('Connection established.')
    else :
        print('Connection failed.')


def sql_query(sql_str, readonly = True):
    """ Write sql queries"""
    global con
    database_cursor = con.cursor()
    try:
        aux = database_cursor.execute(sql_str)    
        if aux :
            if readonly:
                aux = database_cursor.fetchall()
                database_cursor.close()
                return aux
            else:
                con.commit()
                database_cursor.close()
    except sqlite3.Error as e:
        print ("An error occurred:", e.args[0])
        
    



# co_code = 4180
# year = 2012
# var_type='sheet'
# var = 'Teachers ISCED 1'


# filename = "{0}_{1}.xlsx".format(co_name, 2012)
# wb = xlsxwriter.Workbook(filename)


import  tkinter as tk
from tkinter import ttk, StringVar

values = ['car', 'house', 'computer']
root = tk.Tk()
labels = dict((value, tk.Label(root, text=value)) for value in values)

def handler(event):
    current = combobox.current()
    if current != -1:
        for label in labels.values():
            label.config(relief='flat')
        value = values[current]
        label = labels[value]
        label.config(relief='raised')

combobox = ttk.Combobox(root, values=values)
combobox.bind('<<ComboboxSelected>>', handler)
combobox.pack()
for value in labels:
    labels[value].pack()

root.mainloop()

"DELETE FROM METER_AUDIT_TEMP;"
# Inserting from METER to AUDIT_TEMP
("INSERT INTO METER_AUDIT_TEMP (MC_ID, CO_CODE, ADM_CODE, MC_YEAR, "
 "EM_FIG_OLD, MQ_ID_OLD, MG_ID_OLD, USER_NAME, SERIES, SURVEY_ID) "
 "SELECT c.EMC_ID,c.CO_CODE, c.ADM_CODE, c.EMCO_YEAR,"
 "c.EM_FIG, c.MQ_ID, c.MG_ID, '{5}', '{4}', 'RM' from RM_MAPPING as a "
 "LEFT JOIN EDU_METER_AID AS b ON b.AC = a.AC "
 "JOIN EDU_METER97_REP as c  ON b.EMC_ID = c.EMC_ID "
 "WHERE a.Tab='{0}' AND  c.CO_CODE = {1} AND "
 "(( c.EMCO_YEAR={2} AND a.CUR_YEAR=0) OR (c.EMCO_YEAR={3} AND a.CUR_YEAR=-1))".format(Table, co_code, year,username, series))


("SELECT a.MC_ID, a.CO_CODE, a.ADM_CODE, a.MC_YEAR,"
 "a.EM_FIG_OLD, a.MQ_ID_OLD, a.MG_ID_OLD, b.EM_FIG, "
 "b.MQ_ID, b.MG_ID from  METER_AUDIT_TEMP as a "
 "join EDU_METER97_REP as b on a.MC_ID = b.EMC_ID and "
 "a.CO_CODE = b.CO_CODE and a.ADM_CODE = b.ADM_CODE "  
 "and a.MC_YEAR = b.EMCO_YEAR AND "
 "(a.EM_FIG_OLD !=b.EM_FIG OR a.MQ_ID_OLD != b.MQ_ID OR a.MG_ID_OLD != b.MG_ID)"



("INSERT INTO METER_AUDIT_TRAIL " 
 "(MC_ID, CO_CODE, ADM_CODE, MC_YEAR, EM_FIG_OLD, MQ_ID_OLD, "
 "MG_ID_OLD, USER_NAME, SERIES, SURVEY_ID, EM_FIG_NEW, MQ_ID_NEW, MG_ID_NEW) " 
 "SELECT a.MC_ID, a.CO_CODE, a.ADM_CODE, a.MC_YEAR," 
 "a.EM_FIG_OLD, a.MQ_ID_OLD, a.MG_ID_OLD," 
 "a.USER_NAME, a.SERIES, a.SURVEY_ID," 
 "b.EM_FIG, b.MQ_ID, b.MG_ID from  METER_AUDIT_TEMP as a "
 "join EDU_METER97_{0} as b on a.MC_ID = b.EMC_ID "
 "and a.CO_CODE = b.CO_CODE and a.ADM_CODE = b.ADM_CODE "
 "and a.MC_YEAR = b.EMCO_YEAR AND "
 "(a.EM_FIG_OLD !=b.EM_FIG OR a.MQ_ID_OLD != b.MQ_ID OR a.MG_ID_OLD != b.MG_ID)".format(series))

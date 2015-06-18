import  tkinter as tk
from tkinter.filedialog import  FileDialog
    

def import_one():
    dirname = tk.filedialog.askopenfilenames()
    if dirname:
        entry_one.insert(1, dirname)

def import_one():
    dirname = tk.filedialog.askdirectory()
    if dirname:
        entry_many.insert(1, dirname)

        
root = tk.Tk()

root.title('Regional module Survey')
# width x height + x_offset + y_offset:
root.geometry("900x450+30+30") 

# Adding buttons and text boxes
h = 35
w = 200
readframe = tk.LabelFrame(root, text="Importing Questionnaire to database")
readframe.pack(fill="both", expand="yes")
read_one = tk.Button(readframe, text ='Import a single questionnaires', command = import_one, justify = tk.LEFT)
read_one.place(x = 20, y = 30, width=w, height = h)
read_many = tk.Button(readframe, text= 'Import all questionnaires in a folder', command = import_one, justify =tk.LEFT)
read_many.place(x = 20, y = 90, width=w, height=h)

# Text boxes
entry_one = tk.Entry(readframe)
entry_one.place(x = 240, y = 30,width = w*3,  height=h)
entry_many = tk.Entry(readframe)
entry_many.place(x = 240, y = 90,width = w*3,  height=h)

writeframe = tk.LabelFrame(root, text="Exporting data to Excel")
writeframe.pack(fill="both", expand="yes")



root.mainloop()


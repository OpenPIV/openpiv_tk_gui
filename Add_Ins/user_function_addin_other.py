from openpivgui.Add_Ins.AddIn import AddIn
import tkinter.messagebox as messagebox
import tkinter as tk
import tkinter.ttk as ttk


class user_function_addin_other(AddIn):

    example_user_function = '''
filelistbox = GUI.get_filelistbox()
properties  = GUI.p
import pandas as pd

def textbox(title='Title', text='Hello!'):
    from tkinter.scrolledtext import ScrolledText
    from tkinter.constants import END
    frame = tk.Tk()
    frame.title(title)
    textarea = ScrolledText(frame, height=10, width=80)
    textarea.insert(END, text)
    textarea.pack(fill='x', side='left', expand=True)
    textarea.focus()
    frame.mainloop()

try:
    index = filelistbox.curselection()[0]
except IndexError:
    messagebox.showerror(
        title="No vector file selected.",
        message="Please select a vector file " +
                "in the file list and run again."
    )
else:
    f = properties['fnames'][index]
    names=('x','y','v_x','v_y','var')
    df = pd.read_csv(f, sep='\t', header=None, names=names)
    print(df.describe())
    textbox(title='Statistics of {}'.format(f),
            text=df.describe()
    )
'''

    variables = {'addin_user_func': [10000, None, None, None, 'User-Function', None],
                 'addin_user_func_def': [10010, 'text', example_user_function,
                 None, None, None]}

    add_in_name = "user_function_addin"

    def create_user_function_buttons(self, GUI, menu):
        menu.add_command(label='Show User Function',
                                      command=lambda: GUI.selection(10))
        menu.add_command(label='Execute User Function',
                                      command=lambda: self.user_function(GUI))

    def user_function(self, GUI):
        """
            Executes user function.
        """
        GUI.get_settings()
        print(GUI.p['addin_user_func_def'])
        exec(GUI.p['addin_user_func_def'])

    def __init__(self, GUI):
        super().__init__()
        GUI.buttons.update({"user_function_addin_other":
                            self.create_user_function_buttons})

import tkinter as tk
from tkinter import ttk
import os
from functools import partial
import importlib

add_ins = {}
imported_add_ins = {}


def init_add_ins(gui):
    """
        In this method, the parameters that are already part of the GUI
        (loaded from OpenPIVParams) are extended by the parameters of
        the selected AddIns.
    :param gui: active instance of the OpenPivGui class
    :type gui: obj(OpenPivGui)
    :return:
    """
    # get the parameters which are already part of the gui
    parameters = gui.get_parameters()
    # get the add_ins loaded in the last session
    add_ins_to_be_included = parameters['used_addins']
    # Iterate through the selected add-ins, creating an instance of the
    # add-ins and reading out the variables of the class. These are then
    # appended to the parameter object.
    for add_in in add_ins_to_be_included:
        add_in_file = importlib.import_module("openpivgui.AddIns." + add_in)
        add_in_instance = getattr(add_in_file, add_in)(gui)
        imported_add_ins.update({add_in: add_in_instance.get_variables()})
        parameters.add_parameters(add_in_instance.get_variables())


def load_add_ins(gui) -> None:
    """
        Method that determines which add_ins are loaded on forced
        restart, and which parameters and methods must be removed based
         on the selection made.
        :param gui: active object of the OpenPivGui class
        :type gui: obj(OpenPivGui)
        :return: None
    """
    # get the add_ins loaded
    for add_in in add_ins:
        # if the add_in is chosen in the add_in menu
        if add_ins[add_in][0].get():
            imported_add_ins.update({add_in[:-3]: None})
            # if the add_in was not loaded yet
            if add_in[:-3] not in gui.get_parameters()['used_addins']:
                gui.get_parameters()['used_addins'].append(add_in[:-3])
        else:
            if add_in[:-3] in imported_add_ins.keys():
                imported_add_ins.pop(add_in[:-3])
                index = 0
                for i in gui.get_parameters()['used_addins']:
                    if i == add_in[:-3]:
                        gui.get_parameters()['used_addins'].pop(index)
                    index += 1
            if add_in[:-3] in gui.buttons:
                gui.buttons.pop(add_in[:-3])
            if add_in[:-3] in gui.preprocessing_methods:
                gui.preprocessing_methods.pop(add_in[:-3])
    # forced restart
    gui.destroy_for_new_addins()


def linebreak(text):
    """
        used to make the text fit in the textarea in the add_in menu
        :param text: add_in_tip which has to be cutted
        :return: add_in_tip within the linebreak needed
    """
    if len(text) > 60:
        char = 60
        while char > 0:
            if text[char] == " ":
                returntext = text[0:char] + "\n" + linebreak(text[char + 1:])
                break
            else:
                char = char - 1
        return returntext
    else:
        return text


def description(add_in: list) -> None:
    """
        method, which is used to load the add_in_tip from the specified
        add_in and then output it in the textarea
        :param add_in: list containing add_in name and an obj(OpenPivGui)
        :type add_in: list
        :return: None
    """
    # get add_in_py_file within the use of importlib
    add_in_py_file = importlib.import_module("AddIns." + add_in[0])
    # get the init method of the given add_in
    add_in_init = getattr(add_in_py_file, add_in[0])
    add_in_obj = add_in_init(add_in[1])
    # get the add_in_tip
    add_in_description = add_in_obj.get_description()
    add_in_description = linebreak(add_in_description)
    # print the add_in_tip in the textarea
    textarea.config(state="normal")
    textarea.delete("3.0", tk.END)
    textarea.insert("3.0", "\n" + add_in_description)
    textarea.config(state="disabled")


def select_add_ins(gui) -> None:
    """
        Creates a popup menu in which the user is able to decide which
        Add Ins he/she wants to be included and which he/she wants to remove
        By pressing the Save button the load_addins function which is used
        to store the selected addins is called.
        :param gui: active object of the OpenPivGui class
        :type gui: obj(OpenPivGui)
        :return: None
    """
    global add_in_tk_frame
    add_in_tk_frame = tk.Toplevel()
    add_in_tk_frame.geometry("850x690")
    selection_menu = ttk.Frame(add_in_tk_frame)
    selection_menu.pack(side='left',
                        fill='both',
                        expand='True')
    available_add_ins = os.listdir(os.path.dirname(__file__) + "/AddIns")
    possible_add_ins = ["general", "preprocessing",
                        "postprocessing", "other", "plotting"]
    buttons = []
    add_ins_chosen = gui.get_parameters()['used_addins']
    j = 1
    for i in possible_add_ins:
        tk.Label(selection_menu, text=i.capitalize(),
                 font='Helvetica 10 bold').pack(padx=5, side="top",
                                                fill="both")
        j += 1
        for add_in in available_add_ins:
            add_in_string_parts = add_in.split("_")
            if add_in_string_parts[-1][:-3] == i:
                add_ins.update({add_in: [tk.BooleanVar(),
                                         add_in_string_parts[-1][:-3],
                                         "information(add_in[:-3])"]})
                if add_in[:-3] in add_ins_chosen:
                    add_ins[add_in][0].set(True)
                else:
                    add_ins[add_in][0].set(False)
                tk.Checkbutton(selection_menu,
                               var=add_ins[add_in][0],
                               onvalue=True, offvalue=False)\
                    .pack(padx=5)
                buttons.append(tk.Button(selection_menu, text=add_in[:-3],
                                         command=partial(description, [add_in[:-3],
                                                                       gui])))
                buttons[-1].pack(padx=5)
                j += 1
        ttk.Separator(selection_menu).pack(side="top", expand=2)
    global textarea
    textarea = tk.Text(add_in_tk_frame)
    textarea.pack(side="left", fill="both")
    textarea.insert("1.0", "ADD_IN DESCRIPTION \n")
    textarea.insert(tk.END, 60 * "-" + "\n")
    textarea.insert(tk.END, "variable")
    textarea.config(state="disabled")

    tk.Button(selection_menu, text="Save", bg="white", command=lambda:
              load_add_ins(gui)) \
        .pack(side="bottom", fill="both", expand="True")

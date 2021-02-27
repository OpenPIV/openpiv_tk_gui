#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''A simple GUI for OpenPIV.'''

import openpivgui.vec_plot as vec_plot
from openpivgui.open_piv_gui_tools import str2list, str2dict, get_dim, _round
from openpivgui.ErrorChecker import check_PIVprocessing, check_processing, check_postprocessing
from openpivgui.PostProcessing import PostProcessing
from openpivgui.PreProcessing import gen_background, process_images
from openpivgui.MultiProcessing import MultiProcessing
from openpivgui.CreateToolTip import CreateToolTip
from openpivgui.OpenPivParams import OpenPivParams
from scipy.ndimage.filters import gaussian_filter, gaussian_laplace
from matplotlib.figure import Figure as Fig
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import openpiv.tools as piv_tls
import pandas as pd
import numpy as np
from tkinter import colorchooser
from datetime import datetime
import threading
import shutil
import webbrowser
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter as tk
import inspect
import json
import sys
import re
import os

__version__ = '0.4.2'

__licence__ = '''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__email__ = 'vennemann@fh-muenster.de'


class OpenPivGui(tk.Tk):
    '''Simple OpenPIV GUI

    Usage:

    1. Press »File« and then »Import files« or »Import directory«. 
       Either select some image pairs (Ctrl + Shift) or a directory
       that contains image files.

    2. Click on the links in the file-list on the right to inspect
       the images.

    3. Walk through the drop-down-menues »General«, »Preprocessing«,
       and »Analysis« and edit the parameters. 

    4. Press the »start processing« butten (bottom left), to 
       start the processing chain.

    5. Inspect the results by clicking on the links in the file-list.
       Use the »Plot« drop-down menu for changing the plot parameters.

    6. Use the »back« and »forward« buttons to go back to the images,
       in case you want to repeat the evaluation.

    7. For post-processing, use the »back« and »forward« buttons« 
       to list the vector files. Modify the Post-Processing
       parameters and hit the »start post-processing« button.

    See also:

    https://github.com/OpenPIV/openpiv_tk_gui
   '''

    def __init__(self):
        '''Standard initialization method.'''
        print('Initializing GUI')
        self.VERSION = __version__
        self.TITLE = 'Simple OpenPIV GUI'
        tk.Tk.__init__(self)
        self.path = os.path.dirname(
            os.path.abspath(__file__))  # path of gui folder
        self.icon_path = os.path.join(
            self.path, 'res/icon.png')  # path for image or icon
        # convert .png into a usable icon photo
        self.iconphoto(False, tk.PhotoImage(file=self.icon_path))
        self.title(self.TITLE + ' ' + self.VERSION)
        # handle for user closing GUI through window manager
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        # the parameter object
        self.p = OpenPivParams()
        self.p.load_settings(self.p.params_fname)
        # background variable for widget data:
        self.tkvars = {}
        # handle for settings frames on riders
        self.set_frame = []
        # handle for text-area objects
        self.ta = []
        # handle for list-box
        self.lb = None
        print('Initializing widgets')
        self.__init_widgets()
        self.set_settings()
        self.log(timestamp=True, text='--------------------------------' +
                                      '\nTkinter OpenPIV session started.')
        self.log(text='OpenPivGui version: ' + self.VERSION)
        print('Initialized GUI, ready for processing')

    def start_processing(self):
        '''Wrapper function to start processing in a separate thread.'''
        try:
            self.get_settings()
            check_processing(self)  # simple error checking.
            check_PIVprocessing(self.p)
            self.processing_thread = threading.Thread(target=self.processing)
            self.processing_thread.start()
        except Exception as e:
            print('PIV evaluation thread stopped. ' + str(e))
            

    def processing(self):
        try:
            self.log(timestamp=True,
                     text='-----------------------------' +
                     '\nPre processing finished.',
                     group=self.p.PREPROC)
            '''Start the processing chain.

            This is the place to implement additional function calls.
            '''


            # parallel PIV evaluation:
            print('Starting evaluation.')
            self.progressbar.start()

            self.get_settings()
            mp = MultiProcessing(self.p)

            number_of_frames = mp.get_num_frames()
            self.process_type.config(text = 'Processing {} PIV image pair(s)'.format(number_of_frames))

            return_fnames = mp.get_save_fnames()

            # keep number of cores in check
            if os.cpu_count() == 0:  # if there are no cored available, then raise exception
                raise Exception('Warning: no available threads to process in.')

            if self.p['manual_select_cores']:  # allow for automatic or manual core selection
                cpu_count = self.p['cores']

            else:
                cpu_count = os.cpu_count()

            if "idlelib" in sys.modules:
                self.log('Running as a child of IDLE: ' +
                         'Deactivated multiprocessing.')
                cpu_count = 1

            if cpu_count >= os.cpu_count():
                raise Exception('Please lower the amount of cores ' +
                                'or deselect >manually select cores<.')

            print('Cores left: {} of {}.'.format(
                (os.cpu_count() - cpu_count), os.cpu_count()))

            mp.run(func=mp.process, n_cpus=cpu_count)

            # update file list with result vector files:
            self.tkvars['fnames'].set(return_fnames)
            self.log(timestamp=True,
                     text='\nPIV evaluation finished.',
                     group=self.p.PIVPROC)

            self.progressbar.stop()
            self.process_type.config(text = 'Processed {} PIV image pair(s)'.format(number_of_frames))

            # update file count
            self.get_settings()
            self.num_label.config(text=len(self.p['fnames']))
        except Exception as e:
            print('PIV evaluation thread stopped. ' + str(e))
            self.progressbar.stop()
            self.process_type.config(text = 'Failed to process image pair(s)')
                

    def start_postprocessing(self):
        '''Wrapper function to start processing in a separate thread.'''
        try:
            #if os.cpu_count() == 0:  # if there are no cored available, then raise exception
            #    raise Exception('Warning: no available threads to process in.')
            check_processing(self)
            check_postprocessing(self.p)  # simple error checking
            self.postprocessing_thread = threading.Thread(
                target=self.postprocessing)
            self.postprocessing_thread.start()
        except Exception as e:
            print('Post-processing thread stopped. ' + str(e))

    def postprocessing(self):
        try:
            self.progressbar.start()
            self.process_type.config(text = 'Processing {} PIV result(s)'.format(len(self.p['fnames'])))

            print('Starting validation. Please wait for validation to finish')
            # sig2 noise validation
            self.get_settings()
            if self.p['vld_sig2noise']:
                self.tkvars['fnames'].set(
                    PostProcessing(self.p).sig2noise())

            # standard deviation validation
            self.get_settings()
            if self.p['vld_global_std']:
                self.tkvars['fnames'].set(
                    PostProcessing(self.p).global_std())

            # global threshold validation
            self.get_settings()
            if self.p['vld_global_thr']:
                self.tkvars['fnames'].set(
                    PostProcessing(self.p).global_val())

            # local median validation
            self.get_settings()
            if self.p['vld_local_med']:
                self.tkvars['fnames'].set(
                    PostProcessing(self.p).local_median())

            # log validation parameters
            if (self.p['vld_sig2noise'] or
                self.p['vld_global_std'] or
                self.p['vld_global_thr'] or
                    self.p['vld_local_med']):
                self.log(timestamp=True,
                         text='\nValidation finished.',
                         group=self.p.VALIDATION)
            print('Finished validation. Please wait for postprocessing to finish.')

            # post processing
            self.get_settings()
            if self.p['repl']:
                self.tkvars['fnames'].set(
                    PostProcessing(self.p).repl_outliers())

            # smooth post processing
            self.get_settings()
            if self.p['smoothn']:
                self.tkvars['fnames'].set(
                    PostProcessing(self.p).smoothn_r())

            # average all ressults
            #self.get_settings()
            #if self.p['average_results']:
            #    self.tkvars['fnames'].set(
            #        PostProcessing(self.p).average())

            # log parameters
            if (self.p['repl'] or
                self.p['smoothn'] or
                    self.p['average_results']):
                self.log(timestamp=True,
                         text='\nPost processing finished.',
                         group=self.p.POSTPROC)
            print('Finished postprocessing.')

            self.progressbar.stop()
            self.process_type.config(text = 'Processed {} PIV result(s)'.format(len(self.p['fnames'])))

            # update file count
            self.get_settings()
            self.num_label.config(text = len(self.p['fnames']))
        except Exception as e:
            print('Postprocessing thread stopped. ' + str(e))
            self.progressbar.stop()
            self.process_type.config(text = 'Failed to postprocess results(s)')

    def __init_widgets(self):
        '''Creates a widget for each variable in a parameter object.'''
        self.__init_buttons()
        f = ttk.Frame(self)
        f.pack(side='left',
               fill='both',
               expand='True')
        # holds riders for parameters
        self.__init_notebook(f)
        # plotting area
        self.__init_fig_canvas(f)
        # variable widgets:
        for key in sorted(self.p.index, key=self.p.index.get):
            if self.p.type[key] == 'dummy':
                pass
            elif self.p.type[key] == 'bool':
                self.__init_checkbutton(key)
            elif self.p.type[key] == 'str[]':
                self.__init_listbox(key)
            elif self.p.type[key] == 'text':
                self.__init_text_area(key)
            elif self.p.type[key] == 'labelframe':
                self.__init_labelframe(key)
            elif self.p.type[key] == 'label':
                self.__init_label(key)
            elif self.p.type[key] == 'post_button':
                self.__init_post_button(key)
            elif self.p.type[key] == 'h-spacer':
                self.__init_horizontal_spacer(key)
            elif self.p.type[key] == 'sub_bool':
                self.__init_sub_checkbutton(key)
            elif self.p.type[key] == 'sub_labelframe':
                self.__init_sub_labelframe(key)
            elif self.p.type[key] == 'sub_h-spacer':
                self.__init_sub_horizontal_spacer(key)
            elif self.p.type[key] is None:
                self.__add_tab(key)
            else:
                self.__init_entry(key)

            # create widgets that are not in OpenPivParams
            if self.p.index[key] == 3500:
                self.__init_analysisframe(key)
            if self.p.index[key] == 8120:
                self.__init_vec_colorpicker(key)

    def __init_fig_canvas(self, mother_frame):
        '''Creates a plotting area for matplotlib.

        Parameters
        ----------
        mother_frame : ttk.Frame
            A frame to place the canvas in.
        '''
        self.fig = Fig()  # Enlargended canvas to my preference
        self.fig_frame = ttk.Frame(mother_frame)
        self.fig_frame.pack(side='left',
                            fill='both',
                            expand='True')

        self.fig_canvas = FigureCanvasTkAgg(
            self.fig, master=self.fig_frame)
        self.fig_canvas.draw()

        self.fig_canvas.get_tk_widget().pack(
            side='left',
            fill='x',
            expand='True')
        fig_toolbar = NavigationToolbar2Tk(self.fig_canvas,
                                           self.fig_frame)
        fig_toolbar.update()

        ttk.Button(self.fig_frame,
                   text='start processing',
                   command=self.start_processing).pack(side='left')
        ttk.Button(self.fig_frame,
                   text='start postprocessing',
                   command=self.start_postprocessing).pack(side='left')
        ttk.Button(self.fig_frame, 
                   text = '% invalid vectors', 
                   command = self.calculate_invalid_vectors).pack(side = 'left')

        self.progressbar = ttk.Progressbar(self.fig_frame, orient = 'horizontal', length = 200, mode = 'indeterminate')
        self.progressbar.pack(side = 'right')
        
        self.process_type = ttk.Label(self.fig_frame, text = ' ')
        self.process_type.pack(side = 'right')    
        
        self.fig_canvas._tkcanvas.pack(side='top',
                                       fill='both',
                                       expand='True')
        self.fig_canvas.mpl_connect("key_press_event",
                                    lambda: key_press_handler(event,
                                                              self.fig_canvas,
                                                              fig_toolbar))

    def __fig_toolbar_key_pressed(self, event):
        '''Handles matplotlib toolbar events.'''
        key_press_handler(event,
                          self.fig_canvas,
                          self.fig_toolbar)

    def __init_notebook(self, mother_frame):
        '''The notebook is the root widget for tabs or riders.'''
        style = ttk.Style()
        style.layout('TNotebook.Tab', [])
        self.nb = ttk.Notebook(mother_frame, width=260)
        self.nb.pack(side='right',
                     fill='both',
                     expand='False')

    def __add_tab(self, key):
        '''Add an additional rider to the notebook.'''
        self.set_frame.append(ttk.Frame(self.nb))
        self.nb.add(self.set_frame[-1], text=self.p.label[key])

    def __init_buttons(self):
        '''Add buttons and bind them to methods.'''
        f = ttk.Frame(self)

        files = ttk.Menubutton(f, text='File')
        options = tk.Menu(files, tearoff=0)
        files.config(menu=options)
        options.add_command(label='Import files',
                            command=self.select_image_files)
        options.add_command(label='Import directory',
                            command=self.open_directory)
        options.add_separator()
        options.add_command(label='Save session', command=lambda: self.p.dump_settings(
            filedialog.asksaveasfilename()))
        options.add_command(label='Load session', command=self.load_settings)
        options.add_command(label='Reset session', command=self.reset_params)
        options.add_separator()
        options.add_command(label='Move files', command=self.move_files)
        options.add_command(label='Delete files', command=self.delete_files)
        options.add_separator()
        options.add_command(label='Exit', command=self.destroy)
        files.pack(side='left', fill='x')

        general = ttk.Menubutton(f, text='General')
        options1 = tk.Menu(general, tearoff=0)
        general.config(menu=options1)
        options1.add_command(label='General settings',
                             command=lambda: self.selection(0))
        general.pack(side='left', fill='x')

        preproc = ttk.Menubutton(f, text='Preprocessing')
        options2 = tk.Menu(preproc, tearoff=0)
        preproc.config(menu=options2)
        options2.add_command(label='Preprocessing',
                             command=lambda: self.selection(1))
        preproc.pack(side='left', fill='x')

        piv = ttk.Menubutton(f, text='Analysis')
        options2 = tk.Menu(piv, tearoff=0)
        piv.config(menu=options2)
        options2.add_command(label='Algorithms\Calibration',
                             command=lambda: self.selection(2))
        options2.add_command(label='Windowing',
                             command=lambda: self.selection(3))
        options2.add_command(label='Validation',
                             command=lambda: self.selection(4))
        options2.add_command(label='Pass Postprocessing',
                             command=lambda: self.selection(5))
        options2.add_command(label='Start Analysis',
                             command=self.start_processing)
        piv.pack(side='left', fill='x')

        postproc = ttk.Menubutton(f, text='Postprocess')
        options3 = tk.Menu(postproc, tearoff=0)
        postproc.config(menu=options3)
        options3.add_command(label='Postprocess',
                             command=lambda: self.selection(6))
        options3.add_command(label='Start Postprocessing',
                             command=self.start_postprocessing)
        postproc.pack(side='left', fill='x')

        plot = ttk.Menubutton(f, text='Plotting')
        options4 = tk.Menu(plot, tearoff=0)
        plot.config(menu=options4)
        options4.add_command(
            label='Plotting', command=lambda: self.selection(7))
        options4.add_command(
            label='Modify Appearance', command=lambda: self.selection(8))
        plot.pack(side='left', fill='x')

        u_func = ttk.Menubutton(f, text='User Function')
        options5 = tk.Menu(u_func, tearoff=0)
        u_func.config(menu=options5)
        options5.add_command(label='Show User Function',
                             command=lambda: self.selection(10))
        options5.add_command(label='Execute User Function',
                             command=self.user_function)
        u_func.pack(side='left', fill='x')

        lab_func = ttk.Menubutton(f, text='Lab Book')
        options6 = tk.Menu(lab_func, tearoff=0)
        lab_func.config(menu=options6)
        options6.add_command(label='Show Lab Book',
                             command=lambda: self.selection(9))
        lab_func.pack(side='left', fill='x')

        usage_func = ttk.Menubutton(f, text='Usage')
        options7 = tk.Menu(usage_func, tearoff=0)
        usage_func.config(menu=options7)
        options7.add_command(label='Usage',
                             command=lambda: messagebox.showinfo(
                                 title='Help',
                                 message=inspect.cleandoc(
                                     OpenPivGui.__doc__)))
        usage_func.pack(side='left', fill='x')

        web_func = ttk.Menubutton(f, text='Web')
        options8 = tk.Menu(web_func, tearoff=0)
        web_func.config(menu=options8)
        options8.add_command(label='Web', command=self.readme)
        web_func.pack(side='left', fill='x')

        f.pack(side='top', fill='x')

    def selection(self, num):
        self.nb.select(num)

    def calculate_invalid_vectors(self):
        try:
            self.get_settings()
            
            data = self.load_pandas(self.p['fnames'][self.index])
            data = data.to_numpy().astype(np.float)

            try:
                invalid = data[:, 4].astype('bool')

            except:
                invalid = np.asarray([True for i in range(len(data))])
                print('No typevectors found')
                
            invalid = np.count_nonzero(invalid)
            percent = _round(((invalid / len(data[:, 0])) * 100), 4)
            message = ('Percent invalid vectors for result index {}: {}%'.format(self.index, percent))
            
            if self.p['pop_up_info']:
                messagebox.showinfo(title = 'Statistics',
                                    message = message)
            print(message)

        except Exception as e:
            print('Could not read file for calculating percent of invalid vectors.')
            print('Reason: '+str(e))
            
    def user_function(self):
        '''Executes user function.'''
        self.get_settings()
        exec(self.p['user_func_def'])

    def reset_params(self):
        '''Reset parameters to default values.'''
        answer = messagebox.askyesno(
            title='Reset session',
            message='Reset all parameters to default values?')
        if answer == True:
            self.p = OpenPivParams()
            self.set_settings()

    def readme(self):
        '''Opens https://github.com/OpenPIV/openpiv_tk_gui.'''
        webbrowser.open('https://github.com/OpenPIV/openpiv_tk_gui')

    def delete_files(self):
        '''Delete files currently listed in the file list.'''
        answer = messagebox.askyesno(
            title='Delete files',
            message='Are you sure you want to delete selected files?')
        if answer == True:
            files = self.p['fnames'][:]
            for f in files:
                os.remove(f)
            self.navigate('back')

    def move_files(self):
        '''Move files to a new place.'''
        files = self.p['fnames'][:]
        dir = filedialog.askdirectory(mustexist=False)
        if len(dir) > 0:
            if not os.path.exists(dir):
                os.mkdir(dir)
            for src in files:
                dst = dir + os.path.sep + os.path.basename(src)
                shutil.move(src, dst)
            self.navigate('back')

    def load_settings(self):
        '''Load settings from a JSON file.'''
        settings = filedialog.askopenfilename()
        if len(settings) > 0:
            self.p.load_settings(settings)
            self.set_settings()

    def load_pandas(self, fname):
        '''Load files in a pandas data frame.

        On the rider named General, the parameters for loading
        the data frames can be specified.
        No parameters have to be set for image processing. 

        Parameters
        ----------
        fname : 
            A filename.

        Returns
        -------
        pandas.DataFrame :
            In case of an error, the errormessage is returned (str).
        '''
        sep = self.p['sep']
        if sep == 'tab':
            sep = '\t'
        if sep == 'space':
            sep = ' '

        ext = fname.split('.')[-1]
        if ext in ['txt', 'dat', 'jvc', 'vec', 'csv']:
            if self.p['load_settings'] == True:
                if self.p['header'] == True:
                    data = pd.read_csv(fname,
                                       decimal=self.p['decimal'],
                                       skiprows=int(self.p['skiprows']),
                                       sep=sep)
                elif self.p['header'] == False:
                    data = pd.read_csv(fname,
                                       decimal=self.p['decimal'],
                                       skiprows=int(self.p['skiprows']),
                                       sep=sep,
                                       header=0,
                                       names=self.p['header_names'].split(','))
            else:
                data = pd.read_csv(fname,
                                   decimal=',',
                                   skiprows=0,
                                   sep='\t',
                                   names=['x', 'y', 'vx', 'vy', 'sig2noise'])
        else:
            data = 'File could not be read. Possibly it is an image file.'
        return(data)

    def __init_listbox(self, key):
        '''Creates an interactive list of filenames.

        Parameters
        ----------
        key : str
            Key of a settings object.
        '''
        # root widget
        f = ttk.Frame(self)
        f.pack(side='bottom',
               fill='both',
               expand='True')
        # filter hint
        hint_frame = ttk.Frame(f)
        hint_title = ttk.Label(hint_frame, text=' filter: ')
        self.filter_hint = ttk.Label(hint_frame,
                                     text='None')
        hint_title.pack(anchor='nw', side='left')
        self.filter_hint.pack(anchor='nw')
        hint_frame.pack(side='top', fill='x', expand='False')

        # number of files
        num_frame = ttk.Frame(f)
        num_label = ttk.Label(num_frame, text=' number of files: ')
        self.num_label = ttk.Label(num_frame,
                                   text=len(self.p['fnames']))
        num_label.pack(anchor='nw', side='left')
        self.num_label.pack(anchor='nw')
        num_frame.pack(side='top', fill='x', expand='False')

        # scrolling
        sbx = ttk.Scrollbar(f, orient="horizontal")
        sbx.pack(side='top', fill='x')
        sby = ttk.Scrollbar(f, orient="vertical")
        sby.pack(side='right', fill='y')
        self.lb = tk.Listbox(f, yscrollcommand=sbx.set)
        self.lb = tk.Listbox(f, yscrollcommand=sby.set)
        sbx.config(command=self.lb.xview)
        sby.config(command=self.lb.yview)
        self.lb['width'] = 25

        # background variable
        self.tkvars.update({key: tk.StringVar()})
        self.tkvars[key].set(self.p['fnames'])
        self.lb['listvariable'] = self.tkvars[key]

        # interaction
        self.lb.bind('<<ListboxSelect>>', self.__listbox_selection_changed)
        self.lb.pack(side='top', fill='y', expand='True')

        # navigation buttons
        f = ttk.Frame(f)
        ttk.Button(f,
                   text='< back',
                   command=lambda: self.navigate('back')).pack(
            side='left', fill='x')
        ttk.Button(f,
                   text='forward >',
                   command=lambda: self.navigate('forward')).pack(
            side='right', fill='x')
        f.pack()

    def get_filelistbox(self):
        '''Return a handle to the file list widget.

        Returns
        -------
        tkinter.Listbox
            A handle to the listbox widget holding the filenames
        '''
        return(self.lb)

    def navigate(self, direction):
        '''Navigate through processing steps.

        Display a filtered list of files of the current
        directory. This function cycles through the filters
        specified by the key 'navi_pattern' in the settings object.

        Parameters
        ----------
        direction : str
            'back' or 'forward'.
        '''
        pattern_lst = str2list(self.p['navi_pattern'])
        dirname = os.path.dirname(self.p['fnames'][0])
        files = os.listdir(dirname)
        if direction == 'back':
            self.p.navi_position -= 1
            if self.p.navi_position == -1:
                self.p.navi_position = len(pattern_lst)-1
        elif direction == 'forward':
            self.p.navi_position += 1
            if self.p.navi_position == len(pattern_lst):
                self.p.navi_position = 0
        filtered = (self.file_filter(
                    files,
                    pattern_lst[self.p.navi_position]))
        if filtered != []:
            filtered = [dirname + os.sep + f for f in filtered]
            filtered.sort()
            self.tkvars['fnames'].set(filtered)
            self.get_settings()

        # try next filter, if result is empty
        else:
            self.navigate(direction)

        # update file count
        self.num_label.config(text=len(self.p['fnames']))

    def file_filter(self, files, pattern):
        '''Filter a list of files to  match a pattern.

        Parameters
        ----------
        files : str[]
            A list of pathnames.
        pattern : str
            A regular expression for filtering the list.

        Returns
        -------
        str[]
            List items that match the pattern.
        '''
        filtered = []
        self.filter_hint.config(text=pattern)
        print('file filter: ' + pattern)
        p = re.compile(pattern)
        for f in files:
            if p.search(f):
                filtered.append(f)
        return(filtered)

    def __init_text_area(self, key):
        '''Init a text area, here used as a lab-book, for example.

        The content is saved automatically to the parameter object,
        when the mouse leaves the text area.'''
        self.ta.append(tk.Text(self.set_frame[-1], undo=True))
        ta = self.ta[-1]
        ta.pack()
        ta.bind('<Leave>',
                (lambda _: self.__get_text(key, ta)))
        ttk.Button(self.set_frame[-1],
                   text='clear',
                   command=lambda: ta.delete(
            '1.0', tk.END)
        ).pack(fill='x')
        ttk.Button(self.set_frame[-1],
                   text='undo',
                   command=lambda: ta.edit_undo()
                   ).pack(fill='x')
        ttk.Button(self.set_frame[-1],
                   text='redo',
                   command=lambda: ta.edit_redo()
                   ).pack(fill='x')

    def __get_text(self, key, text_area):
        '''Get text from text_area and copy it to parameter object.'''
        self.p[key] = text_area.get('1.0', tk.END)

    def __listbox_selection_changed(self, event):
        '''Handles selection change events of the file listbox.'''
        try:
            self.index = event.widget.curselection()[0]
        except IndexError:
            pass  # nothing selected
        else:
            self.get_settings()
            self.show(self.p['fnames'][self.index])
            if self.p['data_information'] == True:
                self.show_informations(self.p['fnames'][self.index])

    def __init_labelframe(self, key):
        '''Add a label frame for widgets.'''
        f = ttk.Frame(self.set_frame[-1])
        self.pane = ttk.Panedwindow(f, orient='vertical', width=400)
        self.lf = tk.LabelFrame(self.pane, text=self.p.label[key])
        self.lf.config(borderwidth=2, width=400, relief='groove')
        self.pane.add(self.lf)
        self.pane.pack(side='left', fill='both')
        f.pack(fill='both')

    def __init_sub_labelframe(self, key):
        '''Add a label frame for widgets.'''
        self.sub_lf = tk.LabelFrame(self.lf, text=self.p.label[key])
        self.sub_lf.config(borderwidth=2, width=400, relief='groove')
        self.sub_lf.pack(fill='both', pady=4, padx=4)

    def __init_post_button(self, event):
        f = ttk.Frame(self.lf)
        f.pack(fill='both')
        ttk.Button(f,
                  text='start postprocessing',
                  command=self.start_postprocessing).pack(side='top')

    def __init_horizontal_spacer(self, key):
        '''Add a horizontal spacer line for widgets.'''
        f = ttk.Frame(self.lf)
        hs = ttk.Separator(f)
        hs.pack(fill='x')
        f.pack(fill='both')

    def __init_sub_horizontal_spacer(self, key):
        '''Add a horizontal spacer line for widgets'''
        f = ttk.Frame(self.sub_lf)
        hs = ttk.Separator(f)
        hs.pack(fill='x')
        f.pack(fill='both')

    def __init_label(self, key):
        f = ttk.Frame(self.lf)
        label1 = ttk.Label(f,
                           text=self.p.label[key])
        label1.pack(side='left')
        f.pack()

    def __init_entry(self, key):
        '''Creates a label and an entry in a frame.

        A corresponding tk background textvariable is also crated. An 
        option menu is created instead of en entry, if a hint is given
        in the parameter object. The help string in the parameter object
        is used for creating a tooltip.

        Parameter
        ---------
        key : str
            Key of a parameter obj.
        '''
        padding = 2
        # sub label frames
        if(self.p.type[key] == 'sub_int' or
                self.p.type[key] == 'sub_float' or
                self.p.type[key] == 'sub'):
            f = ttk.Frame(self.sub_lf)
            f.pack(fill='x')
            l = ttk.Label(f, text=self.p.label[key])
            CreateToolTip(l, self.p.help[key])
            l.pack(side='left', padx=padding, pady=padding)
            if self.p.type[key] == 'sub_int':
                self.tkvars.update({key: tk.IntVar()})
            elif self.p.type[key] == 'sub_float':
                self.tkvars.update({key: tk.DoubleVar()})
            elif self.p.type[key] == 'sub':
                self.tkvars.update({key: tk.StringVar()})
            if self.p.hint[key] is not None:
                e = ttk.OptionMenu(f,
                                   self.tkvars[key],
                                   'spacer', *self.p.hint[key])
            else:
                e = ttk.Entry(f, width=17)
                e['textvariable'] = self.tkvars[key]
            CreateToolTip(e, self.p.help[key])
            e.pack(side='right', padx=padding, pady=padding)

        else:
            f = ttk.Frame(self.lf)
            f.pack(fill='x')
            l = ttk.Label(f, text=self.p.label[key])
            CreateToolTip(l, self.p.help[key])
            l.pack(side='left', padx=padding, pady=padding)
            if self.p.type[key] == 'int':
                self.tkvars.update({key: tk.IntVar()})
            elif self.p.type[key] == 'float':
                self.tkvars.update({key: tk.DoubleVar()})
            else:
                self.tkvars.update({key: tk.StringVar()})
            if self.p.hint[key] is not None:
                e = ttk.OptionMenu(f,
                                   self.tkvars[key],
                                   'spacer', *self.p.hint[key])
            else:
                e = ttk.Entry(f, width=17)
                e['textvariable'] = self.tkvars[key]
            CreateToolTip(e, self.p.help[key])
            e.pack(side='right', padx=padding, pady=padding)

    def __init_checkbutton(self, key):
        '''Create a checkbutton with label and tooltip.'''
        f = ttk.Frame(self.lf)
        f.pack(fill='x')
        self.tkvars.update({key: tk.BooleanVar()})
        self.tkvars[key].set(bool(self.p[key]))
        cb = ttk.Checkbutton(f)
        cb['variable'] = self.tkvars[key]
        cb['onvalue'] = True
        cb['offvalue'] = False
        cb['text'] = self.p.label[key]
        CreateToolTip(cb, self.p.help[key])
        cb.pack(side='left')

    def __init_sub_checkbutton(self, key):
        '''Create a checkbutton with label and tooltip.'''
        f = ttk.Frame(self.sub_lf)
        f.pack(fill='x')
        self.tkvars.update({key: tk.BooleanVar()})
        self.tkvars[key].set(bool(self.p[key]))
        cb = ttk.Checkbutton(f)
        cb['variable'] = self.tkvars[key]
        cb['onvalue'] = True
        cb['offvalue'] = False
        cb['text'] = self.p.label[key]
        CreateToolTip(cb, self.p.help[key])
        cb.pack(side='left')

    def __init_vec_colorpicker(self, key):
        whitespace = '                                 '
        f = ttk.Frame(self.lf)
        l = ttk.Label(f, text='invalid vector color')
        CreateToolTip(l, self.p.help[key])
        l.pack(side='left')
        self.invalid_color = tk.Button(f,
                                       text=whitespace,
                                       bg=self.p['invalid_color'],
                                       relief='groove',
                                       command=self.invalid_colorpicker)
        self.invalid_color.pack(side='right')
        f.pack(fill='x')

        f = ttk.Frame(self.lf)
        l = ttk.Label(f, text='valid vector color')
        CreateToolTip(l, self.p.help[key])
        l.pack(side='left')
        self.valid_color = tk.Button(f,
                                     text=whitespace,
                                     bg=self.p['valid_color'],
                                     relief='groove',
                                     command=self.valid_colorpicker)
        self.valid_color.pack(side='right')
        f.pack(fill='x')

    def invalid_colorpicker(self):
        self.p['invalid_color'] = colorchooser.askcolor()[1]
        self.invalid_color.config(bg=self.p['invalid_color'])

    def valid_colorpicker(self):
        self.p['valid_color'] = colorchooser.askcolor()[1]
        self.valid_color.config(bg=self.p['valid_color'])

    def log(self, columninformation=None, timestamp=False, text=None,
            group=None):
        ''' Add an entry to the lab-book.

        The first initialized text-area is assumed to be the lab-book.
        It is internally accessible by self.ta[0].

        Parameters
        ----------
        timestamp : bool
            Print current time.
            Pattern: yyyy-mm-dd hh:mm:ss.
            (default: False)
        text : str
            Print a text, a linebreak is appended. 
            (default None)
        group : int
            Print group of parameters.
            (e.g. OpenPivParams.PIVPROC)
        columninformation : list
            Print column information of the selected file.

        Example
        -------
        log(text='processing parameters:', 
            group=OpenPivParams.POSTPROC)
        '''
        if text is not None:
            self.ta[0].insert(tk.END, text + '\n')
        if timestamp:
            td = datetime.today()
            s = '-'.join((str(td.year), str(td.month), str(td.day))) + \
                ' ' + \
                ':'.join((str(td.hour), str(td.minute), str(td.second)))
            self.log(text=s)
        if group is not None:
            self.log(text='Parameters:')
            for key in self.p.param:
                key_type = self.p.type[key]
                if key_type not in ['labelframe', 'sub_labelframe', 'h-spacer',
                                    'sub_h-spacer', 'post_button']:
                    if group < self.p.index[key] < group+1000:
                        s = key + ': ' + str(self.p[key])
                        self.log(text=s)
        if columninformation is not None:
            self.ta[0].insert(tk.END, str(columninformation) + '\n')

    def show_informations(self, fname):
        ''' Shows the column names of the chosen file in the labbook.

        Parameters
        ----------
        fname : str
            A filename.
        '''
        data = self.load_pandas(fname)
        if isinstance(data, str) == True:
            self.log(text=data)
        else:
            self.log(columninformation=list(data.columns.values))

    def get_settings(self):
        '''Copy widget variables to the parameter object.'''
        for key in self.tkvars:
            if self.p.type[key] == 'str[]':
                self.p[key] = str2list(self.tkvars[key].get())
            else:
                self.p[key] = self.tkvars[key].get()
        self.__get_text('lab_book_content', self.ta[0])
        self.__get_text('user_func_def', self.ta[1])

    def set_settings(self):
        '''Copy values of the parameter object to widget variables.'''
        for key in self.tkvars:
            self.tkvars[key].set(self.p[key])
        self.ta[0].delete('1.0', tk.END)
        self.ta[0].insert('1.0', self.p['lab_book_content'])
        self.ta[1].delete('1.0', tk.END)
        self.ta[1].insert('1.0', self.p['user_func_def'])

    def select_image_files(self):
        '''Show a file dialog to select one or more filenames.'''
        print('Use Ctrl + Shift to select multiple files.')
        files = filedialog.askopenfilenames(multiple=True)
        if len(files) > 0:
            self.p['fnames'] = list(files)
            self.tkvars['fnames'].set(self.p['fnames'])

        # update file count
        self.num_label.config(text=len(self.p['fnames']))

    def open_directory(self):
        '''Show a dialog for opening a directory.'''
        dir = filedialog.askdirectory()
        if len(dir) > 0:
            files = [dir + os.sep + file for file in os.listdir(dir)]
            self.p['fnames'] = list(files)
            self.tkvars['fnames'].set(self.p['fnames'])
        self.navigate('back')

        # update file count
        self.num_label.config(text=len(self.p['fnames']))

    def show(self, fname):
        '''Display a file.

        This method distinguishes vector data (file extensions
        txt, dat, jvc,vec and csv) and images (all other file extensions).

        Parameters
        ----------
        fname : str
            A filename.
        '''
        ext = fname.split('.')[-1]
        self.fig.clear()
        data = self.load_pandas(fname)
        if ext in ['txt', 'dat', 'jvc', 'vec', 'csv']:
            if self.p['plot_type'] == 'vectors':
                vec_plot.vector(
                    data,
                    self.p,
                    self.fig,
                    invert_yaxis=self.p['invert_yaxis'],
                    scale=self.p['vec_scale'],
                    width=self.p['vec_width'],
                    valid_color=self.p['valid_color'],
                    invalid_color=self.p['invalid_color']
                )
            elif self.p['plot_type'] == 'profiles':
                vec_plot.profiles(data, self.p,
                                  fname,
                                  self.fig,
                                  orientation=self.p['profiles_orientation']
                                  )
            elif self.p['plot_type'] == 'scatter':
                vec_plot.scatter(data,
                                 self.fig
                                 )
            elif self.p['plot_type'] == 'contour':
                vec_plot.contour(data, self.p,
                                 self.fig)
            elif self.p['plot_type'] == 'contour + vectors':
                vec_plot.contour_and_vector(data, self.p,
                                            self.fig,
                                            scale=self.p['vec_scale'],
                                            width=self.p['vec_width'])
            elif self.p['plot_type'] == 'streamlines':
                vec_plot.streamlines(data,
                                     self.p,
                                     self.fig)
            else:
                vec_plot.pandas_plot(data,
                                     self.p,
                                     self.fig)
        else:
            self.show_img(fname)
        self.fig.canvas.draw()

    def show_img(self, fname):
        '''Display an image.

        Parameters
        ----------
        fname : str
            Pathname of an image file.
        '''
        img = piv_tls.imread(fname)
        print('\nimage data type: {}'.format(img.dtype))
        print('max count: {}'.format(img.max()))
        print('min count {}:'.format(img.min()))
        if 'int' not in str(img.dtype):
            print('Warning: For PIV processing, ' +
                  'image will be normalized and converted to uint8. ' +
                  'This may cause a loss of precision.')
        print('Processing image.')
        img = (img).astype(np.int32)
        # generate background if needed
        if self.p['background_subtract'] == True and self.p['background_type'] != 'minA - minB':
            background = gen_background(self.p)

        elif self.p['background_subtract'] == True and self.p['background_type'] == 'minA - minB':
            if fname == self.p['fnames'][-1]:
                img2 = self.p['fnames'][-2]
                img2 = piv_tls.imread(img2)
                background = gen_background(self.p, img2, img)
            else:
                img2 = self.p['fnames'][self.index + 1]
                img2 = piv_tls.imread(img2)
                background = gen_background(self.p, img, img2)
        else:
            background = None

        print('Processing image.')
        img = (img).astype(np.int32)
        # generate background if needed
        if self.p['background_subtract'] == True and self.p['background_type'] != 'minA - minB':
            background = gen_background(self.p)

        elif self.p['background_subtract'] == True and self.p['background_type'] == 'minA - minB':
            if fname == self.p['fnames'][-1]:
                img2 = self.p['fnames'][-2]
                img2 = piv_tls.imread(img2)
                background = gen_background(self.p, img2, img)
            else:
                img2 = self.p['fnames'][self.index + 1]
                img2 = piv_tls.imread(img2)
                background = gen_background(self.p, img, img2)
        else:
            background = None

        img = process_images(self.p, img, background=background)
        img = (img).astype(np.int32)

        print('Processed image.')
        print('max count: {}'.format(img.max()))
        print('min count {}:'.format(img.min()))

        self.fig.add_subplot(111).matshow(img, cmap=plt.cm.Greys_r,
                                          vmax=self.p['matplot_intensity'])
        self.fig.canvas.draw()

    def destroy(self):
        '''Destroy the OpenPIV GUI.

        Settings are automatically saved.
        '''
        if messagebox.askyesno('Exit Manager', 'Are you sure you want to exit?'):
            print('Saving settings')
            self.get_settings()
            self.p.dump_settings(self.p.params_fname)
            print('Destroying GUI')
            tk.Tk.destroy(self)
            # sometimes the GUI closes, but the main thread still runs
            print('Destorying main thread')
            sys.exit()
            print('Destoryed main thread.') # This should not execute if the thread is destroyed. 
                                            # Could cause possible issue in the future.

if __name__ == '__main__':
    openPivGui = OpenPivGui()
    openPivGui.geometry("1150x690") # a good starting size for the GUI
    openPivGui.mainloop()

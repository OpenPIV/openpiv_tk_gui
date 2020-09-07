#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''A simple GUI for OpenPIV.'''

__version__ = '0.2.4'

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

__email__= 'vennemann@fh-muenster.de'

import os
import re
import sys
import json
import inspect
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import webbrowser

from datetime import datetime

import numpy as np
import openpiv.tools as piv_tls
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure as Fig

from openpivgui.OpenPivParams import OpenPivParams
from openpivgui.CreateToolTip import CreateToolTip
from openpivgui.MultiProcessing import MultiProcessing
from openpivgui.PostProcessing import PostProcessing

from openpivgui.open_piv_gui_tools import str2list, str2dict, get_dim
from openpivgui.vec_plot import vector, histogram, scatter, profiles

class OpenPivGui(tk.Tk):
    '''Simple OpenPIV GUI

    Usage:

    1. Press »select files« and choose some images. 
    Use Ctrl + Shift for selecting mutliple files.

    2. Click on the links in the file-list to inspect the images.

    3. Walk through the riders, select the desired functions,
    and edit the corresponding parameters.

    4. Press »start processing« to start the processing.

    5. Inspect the results by clicking on the links in the file-list.

    6. Use the »back« and »forward« buttons to inspect
    intermediate results.

    4. Use »dump settings« to document your project. You can recall them
    anytime by pressing »load settings«. The lab-book entries
    are also restored from the settings file.

    See also:

    https://github.com/OpenPIV/openpiv_tk_gui
    '''

    def __init__(self):
        '''Standard initialization method.'''
        self.VERSION = __version__
        self.TITLE = 'Simple OpenPIV GUI'
        tk.Tk.__init__(self)
        self.title(self.TITLE + ' ' + self.VERSION)
        # the parameter object
        self.p = OpenPivParams()
        self.p.load_settings(self.p.params_fname)
        # background variable for widget data:
        self.tkvars = {}
        # handle for settings frames on riders
        self.set_frame = []
        # handle for text-area objects
        self.ta = []
        self.__init_widgets()
        self.set_settings()
        self.log(timestamp=True, text='OpenPIV session started.')
        self.log(text = 'OpenPivGui version: ' + self.VERSION)

    def start_processing(self):
        '''Start the processing chain.
        
        This is the place to implement additional function calls.
        '''
        # preprocessing
        
        # parallel PIV evaluation:
        self.get_settings()
        if self.p['do_piv_evaluation']:
            mp = MultiProcessing(self.p)
            return_fnames = mp.get_save_fnames()
            if "idlelib" in sys.modules:
                self.log('Running as a child of IDLE: ' +
                         'Deactivate multiprocessing.')
                cpu_count = 1
            else:
                cpu_count = os.cpu_count()
            mp.run(func=mp.process, n_cpus=cpu_count)
            # update file list with result vector files:
            self.tkvars['fnames'].set(return_fnames)
            self.log(timestamp=True,
                     text='\nPIV evaluation finished.',
                     group=self.p.PIVPROC)
        # sig2 noise validation
        self.get_settings()
        if self.p['vld_sig2noise']:
            self.tkvars['fnames'].set(
                PostProcessing(self.p).sig2noise())
            self.log(timestamp=True,
                text='\nValidation finished.',
                group=self.p.VALIDATION)
        # standard deviation validation
        self.get_settings()
        if self.p['vld_global_std']:
            self.tkvars['fnames'].set(
                PostProcessing(self.p).global_std())
            self.log(timestamp=True,
                text='\nValidation finished.',
                group=self.p.VALIDATION)
        # local median validation
        self.get_settings()
        if self.p['vld_local_med']:
            self.tkvars['fnames'].set(
                PostProcessing(self.p).local_median())
            self.log(timestamp=True,
                text='\nValidation finished.',
                group=self.p.VALIDATION)
        # post processing            
        self.get_settings()
        if self.p['repl']:
            self.tkvars['fnames'].set(
                PostProcessing(self.p).repl_outliers())
            self.log(timestamp=True,
                     text='\nPost processing finished.',
                     group=self.p.POSTPROC)

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
            if self.p.type[key] == 'bool':
                self.__init_checkbutton(key)
            elif self.p.type[key] == 'str[]':
                self.__init_listbox(key)
            elif self.p.type[key] == 'text':
                self.__init_text_area(key)
            elif self.p.type[key] is None:
                self.__add_tab(key)
            else:
                self.__init_entry(key)

    def __init_fig_canvas(self, mother_frame):
        '''Creates a plotting area for matplotlib.

        Args:
            mother_frame (ttk.Frame): A frame to place the canvas in.
        '''
        self.fig = Fig()
        self.fig_frame = ttk.Frame(mother_frame)
        side_='left'
        if self.p['compact_layout']:
            side_='bottom'
        self.fig_frame.pack(side=side_,
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
        self.fig_canvas._tkcanvas.pack(side='top',
                                       fill='both',
                                       expand='True')
        self.fig_canvas.mpl_connect(
            "key_press_event",
            lambda: key_press_handler(event,
                                      self.fig_canvas,
                                      fig_toolbar))
        
    def __fig_toolbar_key_pressed(self, event):
        '''Handles matplotlib toolbar events.'''
        key_press_handler(event,
                          self.fig_canvas,
                          self.fig_toolbar)

    def __init_notebook(self, mother_frame):
        '''The notebook is the root widget for tabs or riders.

        Args:
            mother_frame (ttk.Frame): A frame to place the notebook in.
        '''
        self.nb = ttk.Notebook(mother_frame)
        side_='right'
        if self.p['compact_layout']:
            side_='top'
        self.nb.pack(side=side_,
                     fill='both',
                     expand='True')

    def __add_tab(self, key):
        '''Add an additional rider to the notebook.'''
        self.set_frame.append(ttk.Frame(self.nb))
        self.nb.add(self.set_frame[-1], text=self.p.label[key])

    def __init_buttons(self):
        '''Add buttons and bind them to methods.'''
        f = ttk.Frame(self)
        ttk.Button(f,
                   text='exit',
                   command=self.destroy).pack(
                       side='left', fill='x')
        ttk.Button(f,
                   text='select files',
                   command=self.select_image_files).pack(
                       side='left', fill='x')
        ttk.Button(f,
                   text='start processing',
                   command=self.start_processing).pack(
                       side='left', fill='x')
        ttk.Button(f,
                   text='dump settings',
                   command=lambda: self.p.dump_settings(
                       filedialog.asksaveasfilename())).pack(
                           side='left', fill='x')
        ttk.Button(f,
                   text='load settings',
                   command=self.load_settings).pack(
                       side='left', fill='x')
        ttk.Button(f,
                   text='delete files',
                   command=self.delete_files).pack(
                       side='left', fill='x')
        ttk.Button(f,
                   text='user function',
                   command=self.user_function).pack(
                       side='left', fill='x')
        ttk.Button(f,
                   text='usage',
                   command=lambda: messagebox.showinfo(
                       title='Help',
                       message=inspect.cleandoc(
                           OpenPivGui.__doc__))).pack(
                               side='left', fill='x')
        ttk.Button(f,
                   text='web',
                   command=self.readme).pack(
                       side='left', fill='x')
        f.pack(side='top', fill='x')
    
    def user_function(self):
        '''User function.'''
        self.get_settings()
        exec(self.p['user_func_def'])

    def readme(self):
        '''Opens https://github.com/OpenPIV/openpiv_tk_gui.'''
        webbrowser.open('https://github.com/OpenPIV/openpiv_tk_gui')

    def delete_files(self):
        '''Delete files currently listed in the file list.'''
        files = self.p['fnames'][:]
        for f in files:
            os.remove(f)
        self.navigate('back')

    def load_settings(self):
        '''Load settings from a JSON file.'''
        settings = filedialog.askopenfilename()
        if len(settings) > 0:
            self.p.load_settings(settings)
            self.set_settings()

    def __init_listbox(self, key):
        '''Creates an interactive list of filenames.

        Args:
            key (str): Key of a settings object of type str[].
        '''
        # root widget
        f = ttk.Frame(self)
        f.pack(side='right',
               fill='both',
               expand='True')
        # scrolling
        sb = ttk.Scrollbar(f, orient="vertical")
        sb.pack(side='right', fill='y')
        lb = tk.Listbox(f, yscrollcommand=sb.set)
        lb['height'] = 25
        sb.config(command=lb.yview)
        # background variable
        self.tkvars.update({key: tk.StringVar()})
        self.tkvars[key].set(self.p['fnames'])
        lb['listvariable'] = self.tkvars[key]
        # interaction
        lb.bind('<<ListboxSelect>>', self.__listbox_selection_changed)
        lb.pack(side='top', fill='both', expand='True')
        # navigation buttons
        f = ttk.Frame(f)
        ttk.Button(f,
                   text='< back',
                   command=lambda : self.navigate('back')).pack(
                   side='left', fill='x')
        ttk.Button(f,
                   text='forward >',
                   command=lambda : self.navigate('forward')).pack(
                   side='right', fill='x')
        f.pack()

    def navigate(self, direction):
        '''Navigate through processing steps.

        Args:
            direction (str): »back« or »forward«.

        Display a filtered list of files of the current
        directory. This function cycles through the filters
        specified by the key 'navi_pattern' in the settings object.
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
        else: self.navigate(direction)

    def file_filter(self, files, pattern):
        '''Filter a list of files to  match a pattern.

        Args:
            files (str[]): A list of pathnames.
            pattern (str): A regular expression for filtering the list.

        Returns:
            str[]: List items that match pattern.
        '''
        filtered = []
        print('file filter: ' + pattern)
        p = re.compile(pattern)
        for f in files:
            if p.search(f):
                filtered.append(f);
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
                   command=lambda : ta.delete(
                           '1.0', tk.END)
        ).pack(fill='x')
        ttk.Button(self.set_frame[-1],
                   text='undo',
                   command=lambda : ta.edit_undo()
        ).pack(fill='x')
        ttk.Button(self.set_frame[-1],
                   text='redo',
                   command=lambda : ta.edit_redo()
        ).pack(fill='x')

    def __get_text(self, key, text_area):
        '''Get text from text_area and copy it to parameter object.'''
        self.p[key] = text_area.get('1.0', tk.END)

    def __listbox_selection_changed(self, event):
        '''Handles selection change events of the file listbox.'''
        try:
            index = event.widget.curselection()[0]
        except IndexError:
            pass  # nothing selected
        else:
            self.get_settings()
            self.show(self.p['fnames'][index])

    def __init_entry(self, key):
        '''Creates a label and an entry in a frame.

        A corresponding tk background textvariable is also crated. An 
        option menu is created instead of en entry, if a hint is given
        in the parameter object. The help string in the parameter object
        is used for creating a tooltip.

        Args:
            key (str): Key of a parameter obj.
        '''
        f = ttk.Frame(self.set_frame[-1])
        f.pack(fill='x')
        l = ttk.Label(f, text=self.p.label[key])
        CreateToolTip(l, self.p.help[key])
        l.pack(side='left')
        if self.p.type[key] == 'int':
            self.tkvars.update({key: tk.IntVar()})
        elif self.p.type[key] == 'float':
            self.tkvars.update({key: tk.DoubleVar()})
        else:
            self.tkvars.update({key: tk.StringVar()})
        if self.p.hint[key] is not None:
            e = tk.OptionMenu(f,
                              self.tkvars[key],
                              *self.p.hint[key])
        else:
            e = ttk.Entry(f)
            e['textvariable'] = self.tkvars[key]
        CreateToolTip(e, self.p.help[key])
        e.pack(side='right')

    def __init_checkbutton(self, key):
        '''Create a checkbutton with label and tooltip.'''
        f = ttk.Frame(self.set_frame[-1])
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

    def log(self, timestamp=False, text=None, group=None):
        ''' Add an entry to the lab-book.

        The first initialized text-area is assumed to be the lab-book.
        It is internally accessible by self.ta[0].

        Kwargs:
            timestamp (bool): Print current time.
                              Pattern: yyyy-mm-dd hh:mm:ss.
                              (default False)
            text (str): Print a text, a linebreak is appended. 
                        (default None)
            group (int): Print group of parameters.
                         (e.g. OpenPivParams.PIVPROC)

        Example:
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
                if group < self.p.index[key] < group+1000:
                    s = key + ': ' + str(self.p[key])
                    self.log(text=s)

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


    def show(self, fname):
        '''Display a file.

        This method distinguishes vector data (file extensions
        txt, dat, jvc and vec) and images (all other file extensions).

        Args:
            fname (str): A filename.
        '''
        ext = fname.split('.')[-1]
        self.fig.clear()
        if ext in ['txt', 'dat', 'jvc', 'vec']:
            if self.p['plot_type'] == 'histogram':
                histogram(
                    fname,
                    self.fig,
                    quantity=self.p['histogram_quantity'],
                    bins=self.p['histogram_bins'],
                    log_y=self.p['histrogram_log_scale']
                )
            elif self.p['plot_type'] == 'profiles':
                profiles(fname,
                         self.fig,
                         orientation=self.p['profiles_orientation']
                )
            elif self.p['plot_type'] == 'scatter':
                scatter(fname,
                        self.fig
                )
            else:
                vector(
                    fname,
                    self.fig,
                    invert_yaxis=self.p['invert_yaxis'],
                    scale=self.p['vec_scale'],
                    width=self.p['vec_width'])
        else:
            self.show_img(fname)
        self.fig.canvas.draw()


    def show_img(self, fname):
        '''Display an image.

        Args:
            fname (str): Pathname of an image file.
        '''
        img = piv_tls.imread(fname)
        print('image data type: {}'.format(img.dtype))
        print('max count: {}'.format(img.max()))
        print('min count {}:'.format(img.min()))
        if 'int' not in str(img.dtype):
            print('Warning: For PIV processing, ' +
                  'image will be converted to np.dtype int32. ' +
                  'This may cause a loss of precision.')
        self.fig.add_subplot(111).matshow(img, cmap=plt.cm.Greys_r)
        self.fig.canvas.draw()

    def destroy(self):
        '''Destroy the OpenPIV GUI.

        Settings are automatically saved.
        '''
        self.get_settings()
        self.p.dump_settings(self.p.params_fname)
        tk.Tk.destroy(self)


if __name__ == '__main__':
    openPivGui = OpenPivGui()
    openPivGui.mainloop()

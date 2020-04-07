#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''A class for simple parameter handling.

This class is also used as a basis for automated widget creation
by OpenPivGui.
'''

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

import json
import os


class OpenPivParams():
    '''A class for convenient parameter handling.

    Widgets are automatically created based on the content of the
    variables in the dictionary OpenPivParams.default.

    The entries in OpenPivParams.default are assumed to follow this
    pattern:

    (str) key:
        [(int) index, 
         (str) type, 
         value,
         (tuple) hints,
         (str) label,
         (str) help]

    The index is used for sorting and grouping, because Python 
    dictionaries below version 3.7 do not preserve their order. A 
    corresponding input widged ist chosen based on the type string:
    
        None:                    no widget, no variable, but a rider
        boolean:                 checkbox
        str[]:                   listbox
        text:                    text area
        other (float, int, str): entry (if hints not None: option menu)
    
    A label is placed next to each input widget. The help string is
    displayed as a tooltip.

    The parameter value is directly accessible via indexing the base
    variable name. For example, if your OpenPivParams object variable
    name is »my_settings«, you can access a value by typing:

    my_settings[key] 
    
    This is a shortcut for my_settings.param[key]. To access other 
    fields, use my_settings.label[key], my_settings.help[key] and so on.
    '''

    def __init__(self):
        # hard coded location of the parameter file in the home dir:
        self.params_fname = os.environ['HOME'] + \
                            os.sep + \
                            ".open_piv_gui.json"
        # grouping and sorting based on an index:
        self.GENERAL = 1000
        self.PREPROC = 2000
        self.PIVPROC = 3000
        self.VALIDATION = 6000
        self.POSTPROC = 7000
        self.PLOTTING = 8000
        self.LOGGING = 9000
        # remember the current file filter
        # (one of the comma separated values in ['navi_pattern']):
        self.navi_position = 0
        # these are the default parameters, basis for widget creation:
        self.default = {
            #########################################################
            # Place additional variables in the following sections. #
            # Widgets are created automatically. Don't care about   #
            # saving and restoring - new variables are included     #
            # automatically.                                        #
            #########################################################
            # general
            'general':
                [1000,
                 None,        # type None: This will create a rider.
                 None,
                 None,
                 'General',
                 None],
            'fnames':
                [1010,        # index, here: group GENERAL
                 'str[]',     # type
                 [],          # value
                 None,        # hint (used for option menu, if not None)
                 'filenames', # label
                 None],       # help (tooltip)
            'vec_fname':
                [1020, 'str', 'vec', None,
                 'base output filename',
                 'Filename for vector output. A number and an acronym ' +
                 'that indicates the process history are added ' +
                 'automatically.'],
            'navi_pattern':
                [1030, 'str',
                 'sig2noise, repl, piv_[0-9]+\.vec$, ' +
                 'sig2noise_repl\.vec$, sig2noise\.vec$, repl\.vec$, ' +
                 'vec$, png$, tif$, bmp$, pgm$',
                 None,
                 'navigation pattern',
                 'Regular expression patterns for filtering the files ' +
                 'in the current directory. Use the back and forward ' +
                 'buttons to apply ' +
                 'a different filter.'],
            # preprocessing
            'preproc':
                [2000, None, None, None,
                 'Preprocess',
                 None],
            # processing
            'piv':
                [3000, None, None, None,
                 'PIV',
                 None],
            'extd_search_area':
                [3010, 'bool', True, None,
                 'direct correlation',
                 'Direct correlation with extended size of the ' +
                 'search area.'],
            'corr_window':
                [3020, 'int', 32, (8, 16, 32, 64, 128),
                 'interrogation window size',
                 'Size of square interrogation windows in pixel.'],
            'search_area':
                [3030, 'int', 64, (16, 32, 64, 128, 256),
                 'search area size',
                 'Size of square search area in pixel.'],
            'overlap':
                [3040, 'int', 16, (4, 8, 16, 32, 64, 128),
                 'overlap',
                 'Overlap of correlation windows or vector spacing ' +
                 'in pixel.'],
            'dt':
                [3050, 'float', 0.01, None,
                 'dt',
                 'Interframing time in seconds.'],
            'subpixel_method':
                [3060, 'str', 'gaussian',
                 ('centroid', 'gaussian', 'parabolic'),
                 'subpixel method',
                 'Fit function for determining the subpixel position ' +
                 'of the correlation peak.'],
            'sig2noise_method':
                [3070, 'string', 'peak2peak',
                 ('peak2peak', 'peak2mean'),
                 'signal2noise calculation method',
                 'Calculation method for the signal to noise ratio.'],
            # validation
            'vld':
                [6000, None, None, None,
                 'Validation',
                 None],
            'sig2noise':
                [6010, 'bool', True, None,
                 'validate based on signal to noise ratio',
                 'Do validation based on signal to noise ratio.'],
            'sig2noise_threshold':
                [6020, 'float', 1.3, None,
                 'signal to noise threshold',
                 'Threshold for filtering based on signal to noise ' +
                 'ratio.'],
            # postprocessing
            'post':
                [7000, None, None, None,
                 'Postprocess',
                 None],
            'repl':
                [7010, 'bool', True, None,
                 'replace outliers',
                 'Replace outliers.'],
            'repl_method':
                [7020, 'str', 'localmean',
                 ('localmean', 'disk', 'distance'),
                 'replacement method',
                 'Each NaN element is replaced by a weighed average' +
                 'of neighbours. Localmean uses a square kernel, ' +
                 'disk a uniform circular kernel, and distance a ' +
                 'kernel with a weight that is proportional to the ' +
                 'distance.'],
            'repl_iter':
                [7030, 'int', 10, None,
                 'number of iterations',
                 'If there are adjacent NaN elements, iterative ' +
                 'replacement is needed.'],
            'repl_kernel':
                [7040, 'int', 2, None,
                 'kernel size',
                 'Diameter of the weighting kernel.'],
            # plotting
            'plt':
                [8000, None, None, None,
                 'Plot',
                 None],
            'vec_scale':
                [8010, 'int', 10000, None,
                 'vector scaling',
                 'Velocity as a fraction of the plot width, e.g.: ' +
                 'm/s per plot width. Large values result in shorter ' +
                 'vectors.'],
            'vec_width':
                [8020, 'float', 0.0025, None,
                 'vector line width',
                 'Line width as a fraction of the plot width.'],
            'invert_yaxis':
                [8030, 'bool', True, None,
                 'invert y-axis',
                 'Define the top left corner as the origin ' +
                 'of the vector plot coordinate sytem, ' +
                 'as it is common practice in image processing.'],
            # lab-book
            'lab_book':
                [9000, None, None, None,
                 'Lab-Book',
                 None],
            'lab_book_content':
                [9010, 'text',
                 '',
                 None,
                 None,
                 None]
        }
        # splitting the dictionary for more convenient access
        self.index = dict(zip(
            self.default.keys(),
            [val[0] for val in self.default.values()]))
        self.type = dict(zip(
            self.default.keys(),
            [val[1] for val in self.default.values()]))
        self.param = dict(zip(
            self.default.keys(),
            [val[2] for val in self.default.values()]))
        self.hint = dict(zip(
            self.default.keys(),
            [val[3] for val in self.default.values()]))
        self.label = dict(zip(
            self.default.keys(),
            [val[4] for val in self.default.values()]))
        self.help = dict(zip(
            self.default.keys(),
            [val[5] for val in self.default.values()]))

    def __getitem__(self, key):
        return(self.param[key])

    def __setitem__(self, key, value):
        self.param[key] = value

    def load_settings(self, fname):
        '''Read parameters from a JSON file.
        
        Args: 
            fname (str): Path of the settings file in JSON format.

        Reads only parameter values. Content of the fields index, 
        type, hint, label and help are always read from the default
        dictionary. The default dictionary may contain more entries
        than the JSON file (ensuring backwards compatibility).
        '''
        try:
            f = open(fname, 'r')
            p = json.load(f)
            f.close()
        except:
            print('File not found: ' + fname)
        else:
            for key in self.param:
                if key in p:
                    self.param[key] = p[key]

    def dump_settings(self, fname):
        '''Dump parameter values to a JSON file.

        Args:
            fname (str): A filename.
        
        Only the parameter values are saved. Other data like
        index, hint, label and help should only be defined in the
        default dictionary in this source code.'''
        try:
            f = open(fname, 'w')
            json.dump(self.param, f)
            f.close()
        except:
            print('Unable to save settings: ' + fname)

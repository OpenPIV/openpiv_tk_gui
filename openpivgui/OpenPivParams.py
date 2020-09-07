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
        self.params_fname = os.path.expanduser('~' + os.sep + \
                                               'open_piv_gui.json')
        # grouping and sorting based on an index:
        self.GENERAL = 1000
        self.PREPROC = 2000
        self.PIVPROC = 3000
        self.VALIDATION = 6000
        self.POSTPROC = 7000
        self.PLOTTING = 8000
        self.LOGGING = 9000
        self.USER = 10000
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
            'compact_layout':
                [1020, 'bool', False, None,
                 'compact layout',
                 'If selected, the layout is optimized for full ' +
                 'screen usage and small screens. Otherwise, the ' +
                 'layout leaves some horizontal space for other ' +
                 'apps like a terminal window or source code editor. ' +
                 'This setting takes effect after restart.'],
            'vec_fname':
                [1030, 'str', 'vec', None,
                 'base output filename',
                 'Filename for vector output. A number and an acronym ' +
                 'that indicates the process history are added ' +
                 'automatically.'],
            'navi_pattern':
                [1040, 'str',
                 'png$, tif$, bmp$, pgm$, vec$, ' +
                 'extd_[0-9]+\.vec$, ' +
                 'widim_[0-9]+\.vec$, ' +
                 'windef_[0-9]+\.vec$, ' +
                 'sig2noise\.vec$, std_thrhld\.vec, ' +
                 'repl\.vec$, ' +
                 'sig2noise_repl\.vec$, std_thrhld_repl\.vec$ ',
                 None,
                 'navigation pattern',
                 'Regular expression patterns for filtering the files ' +
                 'in the current directory. Use the back and forward ' +
                 'buttons to apply a different filter.'],
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
            'do_piv_evaluation':
                [3005, 'bool', 'True', None,
                 'do PIV evaluation',
                 'Do PIV evaluation, select method and parameters below. ' +
                 'Deselect, if you just want to do some post-processing.'],
            'overlap':
                [3010, 'int', 16, (4, 8, 16, 32, 64, 128),
                 'overlap',
                 'Overlap of correlation windows or vector spacing ' +
                 '(final pass, in pixel).'],
            'corr_window':
                [3020, 'int', 32, (8, 16, 32, 64, 128),
                 'interrogation window size',
                 'Size of square interrogation windows in pixel ' +
                 '(final pass, in pixel).'],
            'dt':
                [3030, 'float', 1.0, None,
                 'dt',
                 'Interframing time in seconds.'],
            'subpixel_method':
                [3040, 'str', 'gaussian',
                 ('centroid', 'gaussian', 'parabolic'),
                 'subpixel method',
                 'Fit function for determining the subpixel position ' +
                 'of the correlation peak.'],
            'sig2noise_method':
                [3050, 'string', 'peak2peak',
                 ('peak2peak', 'peak2mean'),
                 'signal2noise calculation method',
                 'Calculation method for the signal to noise ratio.'],
            'evaluation_method':
                [3100, 'string', 'extd',
                 ('extd', 'widim', 'windef'),
                 'evaluation method',
                 'extd: ' +
                 'Direct correlation with extended size of the ' +
                 'search area. \n' +
                 'widim: ' +
                 'Window displacement iterative method. (Iterative ' +
                 'grid refinement or multi pass PIV). \n' +
                 'windef: ' +
                 'Iterative grid refinement with window deformation ' +
                 '(recommended).'],
            'search_area':
                [3110, 'int', 64, (16, 32, 64, 128, 256),
                 'search area size',
                 'Size of square search area in pixel for ' +
                 'extd method.'],      
            'coarse_factor':
                [3210, 'int', 2, (1, 2, 3, 4, 5),
                 'number of refinement steps',
                 'Example: A window size of 16 and a number of refinement steps ' +
                 'of 2 gives an window size of 64×64 in the fist pass, 32×32 in ' +
                 'the second pass and 16×16 pixel in the final pass. (Applies ' +
                 'to widim and windef methods only.)'],
            # validation
            'vld':
                [6000, None, None, None,
                 'Validation',
                 None],
            'vld_sig2noise':
                [6010, 'bool', False, None,
                 'signal to noise ratio validation',
                 'Validate the data based on the signal to nose ratio '+
                 'of the cross correlation.'],
            'sig2noise_threshold':
                [6030, 'float', 1.5, None,
                 'signal to noise threshold',
                 'Threshold for filtering based on signal to noise ' +
                 'ratio.'],
            'vld_global_std':
                [6040, 'bool', False, None,
                 'standard deviation validation',
                 'Validate the data based on a multiple of the '+
                 'standard deviation.'],
            'global_std_threshold':
                [6050, 'float', 2.0, None,
                 'standard deviation threshold',
                 'Remove vectors, if the the sum of the squared ' +
                 'vector components is larger than the threshold ' +
                 'times the standard deviation of the flow field.'],
            'vld_local_med':
                [6060, 'bool', True, None,
                 'local median validation',
                 'Validate the data based on a local median ' +
                 'threshold.'],
            'local_median_threshold':
                [6070, 'float', 1.2, None,
                 'local median threshold',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold. '], 
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
            'plot_type':
                [8010, 'str', 'vectors',
                 ('vectors', 'histogram', 'profiles', 'scatter'),
                 'plot type',
                 'Select, how to plot velocity data.'],
            'vec_scale':
                [8030, 'int', 100, None,
                 'vector scaling',
                 'Velocity as a fraction of the plot width, e.g.: ' +
                 'm/s per plot width. Large values result in shorter ' +
                 'vectors.'],
            'vec_width':
                [8040, 'float', 0.0025, None,
                 'vector line width',
                 'Line width as a fraction of the plot width.'],
            'invert_yaxis':
                [8050, 'bool', True, None,
                 'vector plot invert y-axis',
                 'Define the top left corner as the origin ' +
                 'of the vector plot coordinate sytem, ' +
                 'as it is common practice in image processing.'],
            'histogram_quantity':
                [8110, 'str', 'v_x', ('v', 'v_x', 'v_y'),
                 'histogram quantity',
                 'The absolute value of the velocity (v) or its x- ' +
                 'or y-component (v_x or v_y).'], 
            'histogram_bins':
                [8120, 'int', 20, None,
                 'histogram number of bins',
                 'Number of bins (bars) in the histogram.'],
            'histrogram_log_scale':
                [8130, 'bool', True, None,
                 'histogram log scale',
                 'Use a logarithmic y-axis.'],
            'profiles_orientation':
                [8210, 'str', 'vertical', ('vertical', 'horizontal'),
                 'profiles orientation',
                 'Plot v_y over x (horizontal) or v_x over y (vertical).'],
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
                 None],
            # user-function
            'user_func':
                [10000, None, None, None,
                 'User-Function',
                 None],
            'user_func_def':
                [10010, 'text',
                 'messagebox.showinfo(\n' +
                 '    title="User Function",\n' +
                 '    message="Replace this by something useful.")',
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

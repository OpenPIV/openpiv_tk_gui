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

example_user_function='''
filelistbox = self.get_filelistbox()
properties  = self.p
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
            
            'cores':
                [1015, 'int', 2, 
                 (1,2,3,4,5,6,7,8),
                 'number of cores',
                 'Select amount of cores to be used for PIV evaluations.'],

            'step':
                [1020, 'int', 2, 
                 (1,2),
                 'sequence order step',
                 'Select sequence order step for evaluation.' +
                 '\nAssuming >>skip<< = 1; ' +
                 '\n>>1<< yields (1+2),(2+3)' +
                 '\n>>2<< yields (1+2),(3+4)'],
            
            'skip':
                [1021, 'int', 1, 
                 (1,2,3,4,5,6,7,8),
                 'sequence order skip',
                 'Select sequence order jump for evaluation.' +
                 '\nAssuming >>step<< = 1; ' +
                 '\n>>1<< yields (1+2),(2+3)' +
                 '\n>>2<< yields (1+3),(2+4)' +
                 '\n>>3<< yields (1+4),(2+5)' +
                 '\nand so on...'],

            'compact_layout':
                [1030, 'bool', False, None,
                 'compact layout',
                 'If selected, the layout is optimized for full ' +
                 'screen usage and small screens. Otherwise, the ' +
                 'layout leaves some horizontal space for other ' +
                 'apps like a terminal window or source code editor. ' +
                 'This setting takes effect after restart.'],
            
            'vec_fname':
                [1040, 'str', 'vec', None,
                 'base output filename',
                 'Filename for vector output. A number and an acronym ' +
                 'that indicates the process history are added ' +
                 'automatically.'],
            
            'navi_pattern':
                [1050, 'str',
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
            
            'load_settings':
                [1060, 'bool', False, None,
                 'use individual settings for loading data',
                 'Individual settings ' +
                 'for loading files using pandas.'],
            
            'skiprows':
                [1061, 'str', '0', None,
                 'skip rows', 
                 'Number of rows skipped at the beginning of the file.'],
            
            'decimal':
                [1062, 'str', '.', None,
                 'decimal separator', 
                 'Decimal separator for floating point numbers.'],
            
            'sep':
                [1063, 'str', 'tab', (',', ';', 'space', 'tab'),
                 'column separator',
                 'Column separator.'],
            
            'header':
                [1064, 'bool', False, None,
                 'read header', 
                 'Read header. ' + 
                 'If chosen, first line will be interpreted as the header.' + 
                 'Otherwise first line will be replaced with header names' +
                 'specified in the text field below.'],
            
            'header_names':
                [1065, 'str', 'x,y,vx,vy,sig2noise', None,
                 'specify own header names',
                 'Specify comma separated list of column names.' +
                 'Example: x,y,vx,vy,sig2noise'],
            
            # preprocessing
            'preproc':
                [2000, None, None, None,
                 'Preprocess',
                 None],
            
            'ROI':
                [2010, 'bool', 'False', None,
                 'region of interest',
                 'Define region of interest.'],
            
            'roi-xmin':
                [2011, 'int', 200, None,
                 'x min',
                 'Defining region of interest.'],
            
            'roi-xmax':
                [2012, 'int', 800, None,
                 'x max',
                 'Defining region of interest.'],
            
            'roi-ymin':
                [2013, 'int', 200, None,
                 'y min',
                 'Defining region of interest.'],
            
            'roi-ymax':
                [2014, 'int', 800, None,
                 'y max',
                 'Defining region of interest.'],
            
            'invert':
                [2020, 'bool', 'False', None,
                 'invert image',
                 'Invert image (see skimage invert()).'],
            
            'gaussian_filter':
                [2030, 'bool', 'False', None,
                 'Gaussian filter',
                 'Standard Gaussian blurring filter (see scipy gaussian_filter()).'],
            
            'gf_sigma':
                [2035, 'int', 10, None,
                 'sigma/kernel size',
                 'Defining the size of the sigma/kernel for gaussian blur filter.'],
            
            'CLAHE':
                [2040, 'bool', 'False', None,
                 'CLAHE filter',
                 'Contrast Limited Adaptive Histogram Equalization filter (see skimage adapthist()).'],
            
            'CLAHE_kernel':
                [2041, 'int', 20, None,
                 'kernel size',
                 'Defining the size of the kernel for CLAHE.'],
            
            'CLAHE_clip':
                [2042, 'float', 0.01, None,
                 'clip limit',
                 'Defining the contrast with 0-1 (1 gives highest contrast).'],
            
            'un_sharp':
                [2050, 'bool', 'False', None,
                 'UnSharp high pass mask/filter',
                 'A simple image high pass filter (see skimage un_sharp()).'],
            
            'un_sharp_first':
                [2051, 'bool', 'False', None,
                 'perform before CLAHE',
                 'Perform UnSharp high pass mask/filter before CLAHE.'],
            
            'us_radius':
                [2052, 'int', 1, None,
                 'filter radius',
                 'Defining the radius value of the subtracted gaussian filter in the ' + 
                 'UnSharp high pass mask/filter (positive ints only).'],
            
            'us_amount':
                [2053, 'float', 15.0, None,
                 'clip limit',
                 'Defining the clip of the UnSharp filter (higher values remove more background noise).'],

            'dynamic_mask':
                [2060, 'bool', 'False', None,
                 'dynamic masking',
                 'Dynamic masking for masking of images. \n' +
                 'Warning: This is still in testing and is not recommended for use.'],
            
            'dynamic_mask_type':
                [2061, 'str', 'edge', 
                 ('edge', 'intensity'),
                 'mask type',
                 'Defining dynamic mask type.'],
            
            'dynamic_mask_threshold':
                [2062, 'float', 0.01, None,
                 'mask threshold',
                 'Defining threshold of dynamic mask.'],
            
            'dynamic_mask_size':
                [2063, 'int', 7, None,
                 'mask filter size',
                 'Defining size of the masks.'],

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
            
            'evaluation_method':
                [3010, 'string', 'windef',
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
                [3020, 'int', 64, (16, 32, 64, 128, 256),
                 'search area size',
                 'Size of square search area in pixel for ' +
                 'extd method.'], 
            
            
            'corr_window':
                [3030, 'int', 32, (8, 16, 32, 64, 128),
                 'interrogation window size',
                 'Size of square interrogation windows in pixel ' +
                 '(final pass, in pixel).'],
            
            'overlap':
                [3040, 'int', 16, (4, 8, 16, 32, 64, 128),
                 'overlap',
                 'Overlap of correlation windows or vector spacing ' +
                 '(final pass, in pixel).'],
            
            'coarse_factor':
                [3050, 'int', 2, (1, 2, 3, 4, 5),
                 'number of refinement steps',
                 'Example: A window size of 16 and a number of refinement steps ' +
                 'of 2 gives an window size of 64×64 in the fist pass, 32×32 in ' +
                 'the second pass and 16×16 pixel in the final pass. (Applies ' +
                 'to widim and windef methods only.)'],
            
            'corr_method':
                [3060, 'str', 'circular',
                 ('circular', 'linear'),
                 'correlation method',
                 'Correlation method. Circular is no padding and' + 
                 'linear is zero padding (applies to Windef).'],
            
            'subpixel_method':
                [3070, 'str', 'gaussian',
                 ('centroid', 'gaussian', 'parabolic'),
                 'subpixel method',
                 'Fit function for determining the subpixel position ' +
                 'of the correlation peak.'],
            
            'sig2noise_method':
                [3080, 'string', 'peak2peak',
                 ('peak2peak', 'peak2mean'),
                 'signal2noise calculation method',
                 'Calculation method for the signal to noise ratio.'],
            'dt':
                [3090, 'float', 1.0, None,
                 'dt',
                 'Interframing time in seconds.'],
            
            'scale':
                [3100, 'float', 1.0, None,
                 'scale',
                 'Interframing scaling in pix/m'],
            
            'flip_u':
                [3110, 'bool', 'False', None,
                 'invert u-component',
                 'Invert (negative) u-component when saving RAW results.'],
            
            'flip_v':
                [3120, 'bool', 'False', None,
                 'invert v-component',
                 'Invert (negative) v-component when saving RAW results.'],
            
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
            
            'vld_global_thr':
                [6080, 'bool', False, None,
                 'global threshold validation',
                 'Validate the data based on a set global ' +
                 'thresholds.'],
            
            'MinU':
                [6090, 'float', -30.0, None,
                 'min u',
                 'Minimum U allowable component.'], 
            
            'MaxU':
                [6090, 'float', 30.0, None,
                 'max u',
                 'Maximum U allowable component.'],
            
            'MinV':
                [6090, 'float', -30.0, None,
                 'min v',
                 'Minimum V allowable component.'],
            
            'MaxV':
                [6090, 'float', 30.0, None,
                 'max v',
                 'Maximum V allowable component.'],
            
            
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
            
            'smoothn':
                [7050, 'bool', True, None,
                 'smoothn data',
                 'Smoothn data using openpiv.smoothn.'],
            
            'smoothn_type':
                [7060, 'str', 'last pass', 
                 ('last pass','each pass'),
                 'smoothn vectors',
                 'Smoothn data with openpiv.smoothn. <each pass> only applies to windef'],
            
            'smoothn_each_pass':
                [7050, 'bool', False, None,
                 'smoothn each pass',
                 'Smoothn each pass using openpiv.smoothn.'],
            
            'robust':
                [7070, 'bool', False, None,
                 'smoothn robust',
                 'Activate robust in smoothn (minimizes influence of outlying data).'],
            
            'smoothn_val':
                [7080, 'float', 0.5, None,
                 'smoothning strength',
                 'Strength of smoothn script. Higher scalar number produces ' +
                  'more smoothned data.'],
            
            
            # plotting
            'plt':
                [8000, None, None, None,
                 'Plot',
                 None],
            
            'plot_type':
                [8010, 'str', 'vectors',
                 ('vectors', 'histogram', 'profiles', 'scatter', 'line',
                  'bar', 'density', 'contour', 'streamlines'),
                 'plot type',
                 'Select, how to plot velocity data.'],
                
            'u_data':
                [8020, 'str', 'vx', None, 
                 'column name for u-velocity component',
                 'column name for the u-velocity component.' +
                 ' If unknown watch labbook entry.'],
            
            'v_data':
                [8030, 'str', 'vy', None, 
                 'column name for v-veloctiy component',
                 'column name for v-velocity component.' +
                 ' If unknown watch labbook entry.' +
                 ' For histogram only the v-velocity component is needed.'],
                
            'plot_title':
                [8040, 'str', 'Title', None, 
                 'diagram title', 'diagram title.'],
                
            'plot_grid':
                [8050, 'bool', True, None, 'grid', 
                 'adds a grid to the diagram.'],
                
            'plot_legend':
                [8060, 'bool', True, None, 'legend', 
                 'adds a legend to the diagram.'],
                
            'plot_scaling': 
                [8070, 'str', 'None', ('None', 'logx', 'logy', 'loglog'),
                 'axis scaling', 'scales the axes. logarithm scaling x-axis' +
                 ' --> logx; logarithm scaling y-axis --> logy; ' +
                 'logarithm scaling both axes --> loglog.'],
                
            'plot_xlim':
                [8080, 'str', '', None, 'limits for the x-axis', 
                 'For implementation use (lower_limit, upper_limit).'],
            
            'plot_ylim':
                [8085, 'str', '', None, 'limits for the y-axis',
                 'For implementation use (lower_limit, upper_limit).'],
                
            'color_map':
                [8090, 'str', 'jet', ('jet','None','autumn','binary'),
                 'Color map for streamline- and contour-plot', 'Color map '
                 'for streamline- and contour-plot.'],
            
            'streamline_density':
                [8095, 'str', '0.5, 1', None, 'streamline density',
                 'streamline density. Can be one value (e.g. 1) or a couple' +
                 ' of values for a range (e.g. 0.5, 1).'],
                
            'streamlines_color':
                [8096, 'str', 'vy', ('vx', 'vy', 'v'), 'set colorbar to: ',
                 'set colorbar to velocity components.'],
                
            'integrate_dir':
                [8097, 'str', 'both', ('both', 'forward', 'backward'),
                 'direction for integrating the streamlines',
                 'Integrate the streamline in forward, backward or both ' +
                 'directions. default is both.'],
                
            'vec_scale':
                [8100, 'int', 100, None,
                 'vector scaling',
                 'Velocity as a fraction of the plot width, e.g.: ' +
                 'm/s per plot width. Large values result in shorter ' +
                 'vectors.'],
            
            'vec_width':
                [8110, 'float', 0.0025, None,
                 'vector line width',
                 'Line width as a fraction of the plot width.'],
            
            'invalid_color':
                [8120, 'str', 'blue', ('red', 'blue', 'black'),
                 'invalid vector color',
                 'The color of the invalid vectors'],
            
            'valid_color':
                [8130, 'str', 'red', ('red', 'blue', 'black'),
                 'valid vector color',
                 'The color of the valid vectors'],
            
            'invert_yaxis':
                [8140, 'bool', True, None,
                 'vector plot invert y-axis',
                 'Define the top left corner as the origin ' +
                 'of the vector plot coordinate sytem, ' +
                 'as it is common practice in image processing.'],
                
            'histogram_type':
                [8200, 'str', 'bar', ('bar', 
                                      'barstacked', 
                                      'step',
                                      'stepfilled'), 'histogram type', 
                 'Choose histogram type. Only available for histogram' + 
                 'plot.'],
            
            'histogram_quantity':
                [8210, 'str', 'v_x', ('v', 'v_x', 'v_y'),
                 'histogram quantity',
                 'The absolute value of the velocity (v) or its x- ' +
                 'or y-component (v_x or v_y).'], 
            
            'histogram_bins':
                [8220, 'int', 20, None,
                 'histogram number of bins',
                 'Number of bins (bars) in the histogram.'],
            
            'profiles_orientation':
                [8300, 'str', 'vertical', ('vertical', 'horizontal'),
                 'profiles orientation',
                 'Plot v_y over x (horizontal) or v_x over y (vertical).'],
            
            'color_levels':
                [8400, 'str', '10', None, 'number of color levels',
                 'Select the number of color levels for contour plot!'],
            'vmin':
                [8410, 'str', '', None, 'minimum velocity for colormap',
                 'minimum velocity for colormap (contour plot).'],
            'vmax':
                [8410, 'str', '', None, 'maximum velocity for colormap',
                 'maximum velocity for colormap (contour plot).'],

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
            'data_information':
                [9020, 'bool', False, None, 'log column information', 
                 'shows column names, if you choose a file at the ' + 
                 'right side.'],
            # user-function
            'user_func':
                [10000, None, None, None,
                 'User-Function',
                 None],
            
            'user_func_def':
                [10010, 'text',
                 example_user_function,
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



    def generate_parameter_documentation(self, group=None):
        '''Return parameter labels and help as reStructuredText def list.

        Parameters
        ----------
        group : int
            Parameter group.
            (e.g. OpenPivParams.PIVPROC)

        Returns
        -------
        str : A reStructuredText definition list for documentation.
        '''
        s = ''
        for key in self.default:
            if group < self.index[key] < group+1000:
                s = s + str(self.label[key]) + '\n' + \
                '    ' + str.replace(str(self.help[key]), '\n', '\n    ') + '\n\n'
        return(s)

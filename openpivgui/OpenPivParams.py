#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''A class for simple parameter handling.

This class is also used as a basis for automated widget creation
by OpenPivGui.
'''

import os
import json
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

example_user_function = '''
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
        self.params_fname = os.path.expanduser('~' + os.sep +
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
                 'filenames',  # label
                 None],       # help (tooltip)

            'general_frame':
                [1015, 'labelframe', None,
                 None,
                 'General settings',
                 None],

            'warnings':
                [1020, 'bool', 'True', None,
                 'Enable popup warnings',
                 'Enable popup warning messages (recommended).'],
            
            'pop_up_info':
                [1025, 'bool', 'True', None,
                 'Enable popup info',
                 'Enable popup information messages (recommended).'],

            'multicore_frame':
                [1030, 'sub_labelframe', None,
                 None,
                 'multicore settings',
                 None],

            'manual_select_cores':
                [1035, 'sub_bool', 'True', None,
                 'manually select cores',
                 'Mannualy select cores. ' +
                 'If not seected, all available cores will be used.'],

            'cores':
                [1040, 'sub_int', 1,
                 (1, 2, 3, 4, 5, 6, 7, 8),
                 'number of cores',
                 'Select amount of cores to be used for PIV evaluations.'],

            'frequencing_sub_frame':
                [1045, 'sub_labelframe', None,
                 None,
                 'image frequencing',
                 None],

            'sequence':
                [1050, 'sub', '(1+2),(3+4)',
                 ('(1+2),(2+3)', '(1+2),(3+4)'),
                 'sequence order',
                 'Select sequence order for evaluation.'],

            'skip':
                [1051, 'sub_int', 1,
                 None,
                 'jump',
                 'Select sequence order jump for evaluation.' +
                 '\nEx: (1+(1+x)),(2+(2+x))'],

            'filters_sub_frame':
                [1100, 'sub_labelframe', None,
                 None,
                 'listbox filters',
                 None],

            'navi_pattern':
                [1110, 'sub',
                 'png$, tif$, bmp$, pgm$, vec$, ' +
                 'DCC_[0-9]+\.vec$, ' +
                 'FFT_[0-9]+\.vec$, ' +
                 'sig2noise\.vec$, ' +
                 'std_thrhld\.vec, ' +
                 'med_thrhld\.vec, ' +
                 'glob_thrhld\.vec, ' +
                 'repl\.vec$, ' +
                 'smthn\.vec$ ',
                 None,
                 'navigation pattern',
                 'Regular expression patterns for filtering the files ' +
                 'in the current directory. Use the back and forward ' +
                 'buttons to apply a different filter.'],

            'pandas_sub_frame':
                [1200, 'sub_labelframe', None,
                 None,
                 'Pandas',
                 None],

            'load_settings':
                [1210, 'sub_bool', True, None,
                 'settings for using pandas',
                 'Individual settings ' +
                 'for loading files using pandas.'],

            'skiprows':
                [1211, 'sub', '0', None,
                 'skip rows',
                 'Number of rows skipped at the beginning of the file.'],

            'decimal':
                [1212, 'sub', '.', None,
                 'decimal separator',
                 'Decimal separator for floating point numbers.'],

            'sep':
                [1213, 'sub', 'tab', (',', ';', 'space', 'tab'),
                 'column separator',
                 'Column separator.'],

            'header':
                [1214, 'sub_bool', False, None,
                 'read header',
                 'Read header. ' +
                 'If chosen, first line will be interpreted as the header.' +
                 'Otherwise first line will be replaced with header names' +
                 'specified in the text field below.'],

            'header_names':
                [1215, 'sub', 'x,y,vx,vy,val,sig2noise', None,
                 'specify header names',
                 'Specify comma separated list of column names.' +
                 'Example: x,y,vx,vy,sig2noise'],

            'save_sub_frame':
                [1300, 'sub_labelframe', None,
                 None,
                 'PIV save settings',
                 None],

            'vec_fname':
                [1310, 'sub', 'vec', None,
                 'base output filename',
                 'Filename for vector output. A number and an acronym ' +
                 'that indicates the process history are added ' +
                 'automatically.'],

            'separator':
                [1320, 'sub', 'tab', (',', ';', 'space', 'tab'),
                 'delimiter',
                 'Delimiter.'],

            'image_plotting_sub_frame':
                [1500, 'sub_labelframe', None,
                 None,
                 'image plotting',
                 None],

            'matplot_intensity':
                [2032, 'sub_int', 255, None,
                 'reference intensity',
                 'Define a reference intensity for the plotting of images.'],

            'image_plotting_sub_frame':
                [1500, 'sub_labelframe', None,
                 None,
                 'image plotting',
                 None],

            'matplot_intensity':
                [2032, 'sub_int', 255, None,
                 'reference intensity',
                 'Define a reference intensity for the plotting of images.'],

            # preprocessing
            'preproc':
                [2000, None, None, None,
                 'Preprocessing',
                 None],

            'preprocess_frame':
                [2005, 'labelframe', None,
                 None,
                 'Preprocessing',
                 None],

            'preprocess-info':
                [2010, 'label', None, None,

                 'All images are normalized to [0,1] float, \npreprocessed, ' +
                 'and resized to user defined value.',
                 None],

            'Invert_spacer':
                [2015, 'h-spacer', None,
                 None,
                 None,
                 None],

            'invert':
                [2020, 'bool', 'False', None,
                 'invert image',
                 'Invert image (see skimage invert()).'],

            'background_spacer':
                [2025, 'h-spacer', None,
                 None,
                 None,
                 None],

            'background_subtract':
                [2030, 'bool', 'False', None,
                 'subtract background',
                 'Subtract background via local sliding windows.'],

            'background_type':
                [2031, 'str', 'global mean', ('global mean', 'minA - minB'),
                 'background algorithm',
                 'The algorithm used to generate the background which is subtracted ' +
                 'from the piv images. ' +
                 'Warning: »minA - minB« is still in development, so it may not perform '+
                 'to standard.'],

            'starting_frame':
                [2032, 'int', 0, None,
                 'starting image',
                 'Defining the starting image of the background subtraction.'],

            'ending_frame':
                [2033, 'int', 3, None,
                 'ending image',
                 'Defining the ending image of the background subtraction.'],

            'crop_ROI_spacer':
                [2035, 'h-spacer', None,
                 None,
                 None,
                 None],

            'crop_ROI':
                [2040, 'bool', 'False', None,
                 'crop region of interest',
                 'Crop region of interest. Allows images with different sizes to ' +
                 'have a uniform size after cropping.'],

            'crop_roi-xminmax':
                [2041, 'str', '200,800', None,
                 'x min/max',
                 "Define left/right side of region of interest by 'min,max'."],

            'crop_roi-yminmax':
                [2042, 'str', '200,800', None,
                 'y min/max',
                 "Define top/bottom of region of interest by 'min,max.'"],

            #'dynamic_mask_spacer': # failed testing, needs fixing/testing
            #    [2045, 'h-spacer', None,
            #     None,
            #     None,
            #     None],

            #'dynamic_mask':
            #    [2050, 'bool', 'False', None,
            #     'dynamic masking',
            #     'Dynamic masking for masking of images. \n' +
            #     'Warning: This is still in testing and is not recommended for use.'],

            #'dynamic_mask_type':
            #    [2051, 'str', 'edge',
            #     ('edge', 'intensity'),
            #     'mask type',
            #     'Defining dynamic mask type.'],

            #'dynamic_mask_threshold':
            #    [2052, 'float', 0.01, None,
            #     'mask threshold',
            #     'Defining threshold of dynamic mask.'],

            #'dynamic_mask_size':
            #    [2053, 'int', 7, None,
            #     'mask filter size',
            #     'Defining size of the masks.'],

            'CLAHE_spacer':
                [2055, 'h-spacer', None,
                 None,
                 None,
                 None],

            'CLAHE':
                [2060, 'bool', 'True', None,
                 'CLAHE filter',
                 'Contrast Limited Adaptive Histogram Equalization filter ' +
                 '(see skimage adapthist()).'],

            'CLAHE_first':
                [2061, 'bool', 'False', None,
                 'perform CLAHE before high pass',
                 'Perform CLAHE filter before Gaussian high pass filters.'],

            'CLAHE_auto_kernel':
                [2062, 'bool', True, None,
                 'automatic kernel sizing',
                 'Have the kernel automatically sized to 1/8 width and height of the image.'],

            'CLAHE_kernel':
                [2063, 'int', 20, None,
                 'kernel size',
                 'Defining the size of the kernel for CLAHE.'],

            'high_pass_filter_spacer':
                [2065, 'h-spacer', None, 
                 None,
                 None,
                 None],
            
            'high_pass_filter':
                [2070, 'bool', 'False', None,
                 'Gaussian high pass filter',
                 'A simple subtracted Gaussian high pass filter.'],
            
            'hp_sigma':
                [2071, 'int', 5, None,
                 'sigma',
                 'Defining the sigma size of the subtracted gaussian filter in the ' + 
                 'high pass filter (positive ints only).'],
            
            'hp_clip':
                [2072, 'bool', 'True', None,
                 'clip at zero',
                 'Set all values less than zero to zero.'],

            'intensity_threshold_spacer':
                [2075, 'h-spacer', None,
                 None,
                 None,
                 None],

            'intensity_cap_filter':
                [2080, 'bool', 'False', None,
                 'intensity capping',
                 'Simple global intesity cap filter. ' +
                 'Masked pixels are set to the mean pixel intensity.'],

            'ic_mult':
                [2081, 'float', 2, None,
                 'std multiplication',
                 'Multiply the standard deviation of the pixel intensities ' +
                 'to get a higher cap value.'],

            'Gaussian_lp_spacer':
                [2085, 'h-spacer', None,
                 None,
                 None,
                 None],

            'gaussian_filter':
                [2090, 'bool', 'False', None,
                 'Gaussian filter',
                 'Standard Gaussian blurring filter (see scipy gaussian_filter()).'],

            'gf_sigma':
                [2095, 'int', 1, None,
                 'sigma',
                 'Defining the sigma size for gaussian blur filter.'],

            'intensity_clip_spacer':
                [2100, 'h-spacer', None,
                 None,
                 None,
                 None],

            'intensity_clip':
                [2105, 'bool', 'False', None,
                 'intensity clip',
                 'Any intensity less than the threshold is set to zero.'],

            'intensity_clip_min':
                [2110, 'int', 20, None,
                 'min intensity',
                 'Any intensity less than the threshold is set to zero with respect to ' +
                 'the resized image inntensities.'],

            'img_int_resize_spacer':
                [2115, 'h-spacer', None,
                 None,
                 None,
                 None],

            'img_int_resize':
                [2120, 'int', 255, None,
                 'resize intensity',
                 'Resize the image intensity to \n[0,x], where x is a user defined value.'],

            # processing
            'piv':
                [3000, None, None, None,
                 'PIV',
                 None],

            'piv_frame':
                [3005, 'labelframe', None,
                 None,
                 'Algorithms/Calibration',
                 None],

            #'evaluation_method':
            #    [3010, 'string', 'FFT WinDef',
            #     ('Direct Correlation', 'FFT WinDef'),
            #     'evaluation method',
            #     'Direct Correlation: ' +
            #     'Direct correlation with extended size of the ' +
            #     'search area. \n' +
            #     'FFT WinDef: ' +
            #     'Fast Fourier Transforms with window deformation ' +
            #     '(recommended).'],

            'corr_method':
                [3020, 'str', 'circular',
                 ('circular', 'linear'),
                 'correlation method',
                 'Correlation method. Circular is no padding and' +
                 'linear is zero padding.'],

            'subpixel_method':
                [3030, 'str', 'gaussian',
                 ('centroid', 'gaussian', 'parabolic'),
                 'subpixel method',
                 'Fit function for determining the subpixel position ' +
                 'of the correlation peak.'],

            'sig2noise_method':
                [3040, 'string', 'peak2peak',
                 ('peak2peak', 'peak2mean'),
                 'signal2noise calc. method',
                 'Calculation method for the signal to noise ratio.'],

            's2n_mask':
                [3045, 'int', 2, None,
                 'signal to noise mask',
                 'the half size of the region around the first correlation peak to ignore for ' +
                 'finding the second peak. Only used if sig2noise method = \'peak2peak\' '],
            
            'deformation_method':
                [3047, 'str', 'symmetric', ('symmetric', 'second image'),
                 'deformation method',
                 'Window deformation method. '+
                 '»symmetric« deforms both first and second images. '+
                 '\n»second image« deforms the second image only.'],
            
            'interpolation_order':
                [3048, 'int', 3, (0, 1, 2, 3, 4, 5),
                 'interpolation order',
                 'Interpolation oder of the spline window deformation. \n' +
                 '»0« yields zero order nearest interpolation \n' +
                 '»1« yields first order linear interpolation \n'
                 '»2« yields second order quadratic interpolation \n'
                 'and so on...'],
            
            'normalize_correlation':
                [3050, 'bool', False, None,
                 'normalize correlation',
                 'Normalize correlation.'],
            
            'calibration_spacer':
                [3055, 'h-spacer', None,
                 None,
                 None,
                 None],

            'dt':
                [3060, 'float', 1.0, None,
                 'dt',
                 'Interframing time in seconds.'],

            'scale':
                [3070, 'float', 1.0, None,
                 'scale',
                 'Interframing scaling in pix/m'],

            'flip_spacer':
                [3075, 'h-spacer', None,
                 None,
                 None,
                 None],

            'flip_u':
                [3080, 'bool', 'False', None,
                 'flip u-component',
                 'flip u-component array when saving RAW results.'],

            'flip_v':
                [3085, 'bool', 'False', None,
                 'flip v-component',
                 'flip v-component array when saving RAW results.'],

            'invert_spacer':
                [3090, 'h-spacer', None,
                 None,
                 None,
                 None],

            'invert_u':
                [3095, 'bool', 'False', None,
                 'invert u-component',
                 'Invert (negative) u-component when saving RAW results.'],

            'invert_v':
                [3096, 'bool', 'False', None,
                 'invert v-component',
                 'Invert (negative) v-component when saving RAW results.'],

            'swap_files_spacer':
                [3097, 'h-spacer', None,
                 None,
                 None,
                 None],

            'swap_files':
                [3098, 'bool', 'False', None,
                 'swap A/B files',
                 'Swap A/B files when analyzing.'],

            'windowing':
                [3100, None, None, None,
                 'Windowing',
                 None],

            'window_frame':
                [3105, 'labelframe', None,
                 None,
                 'Windowing',
                 None],

            #'search_area':
            #    [3110, 'int', 64, (16, 32, 64, 128, 256),
            #     'search area',
            #     'Size of square search area in pixel for ' +
            #     'Single-pass DCC method.'],

            'corr_window':
                [3120, 'int', 32, (8, 16, 32, 64, 128),
                 'interrogation window',
                 'Size of the final interrogation windows in pixels.'],

            'overlap':
                [3130, 'int', 16, (4, 8, 16, 32, 64),
                 'overlap',
                 'Size of the final overlap in pixels.'],

            'coarse_factor':
                [3140, 'int', 3, (1, 2, 3, 4, 5),
                 'number of passes',
                 'Example: A window size of 16 and a number of refinement steps ' +
                 'of 3 gives an window size of 64×64 in the fist pass, 32×32 in ' +
                 'the second pass and 16×16 pixel in the final pass.'],

            'grid_refinement':
                [3150, 'str', 'all passes', ('all passes', '2nd pass on', 'none'),
                 'grid refinement',
                 'Refine the interregationg grid every PIV pass when performing multipass FFT. \n' +
                 '»all passes« refines all passes. \n'
                 '»2nd pass on« refines second pass on.'],

            'sub_window_frame':
                [3200, 'sub_labelframe', None,
                 None,
                 'custom windowing',
                 None],

            'custom_windowing':
                [3205, 'sub_bool', False, None,
                 'custom windowing',
                 'Enable custom windowing for more advanced techniques.'],

            'pass_1_spacer':
                [3210, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'corr_window_1':
                [3220, 'sub_int', 256, None,
                 'interrogation window',
                 'Interrogation window for the first pass.'],

            'overlap_1':
                [3230, 'sub_int', 128, None,
                 'overlap',
                 'Size of the overlap of the first pass in pixels. The overlap will then be ' +
                 'calculated for the following passes.'],

            'pass_2_spacer':
                [3235, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'pass_2':
                [3237, 'sub_bool', False, None,
                 'second pass',
                 'Enable a second pass in the FFT window deformation evaluation.'],

            'corr_window_2':
                [3240, 'sub_int', 128, None,
                 'interrogation window',
                 'Interrogation window for the second pass.'],

            'pass_3_spacer':
                [3245, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'pass_3':
                [3247, 'sub_bool', False, None,
                 'third pass',
                 'Enable a third pass in the FFT window deformation evaluation.'],

            'corr_window_3':
                [3250, 'sub_int', 64, None,
                 'interrogation window',
                 'Interrogation window for the third pass.'],

            'pass_4_spacer':
                [3255, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'pass_4':
                [3257, 'sub_bool', False, None,
                 'fourth pass',
                 'Enable a fourth pass in the FFT window deformation evaluation.'],

            'corr_window_4':
                [3260, 'sub_int', 32, None,
                 'interrogation window',
                 'Interrogation window for the fourth pass.'],

            'pass_5_spacer':
                [3265, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'pass_5':
                [3267, 'sub_bool', False, None,
                 'fifth pass',
                 'Enable a fifth pass in the FFT window deformation evaluation.'],

            'corr_window_5':
                [3270, 'sub_int', 16, None,
                 'interrogation window',
                 'Interrogation window for the fifth pass.'],

            'pass_6_spacer':
                [3275, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'pass_6':
                [3277, 'sub_bool', False, None,
                 'sixth pass',
                 'Enable a sixth pass in the FFT window deformation evaluation.'],

            'corr_window_6':
                [3280, 'sub_int', 16, None,
                 'interrogation window',
                 'Interrogation window for the sixth pass.'],

            'pass_7_spacer':
                [3285, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'pass_7':
                [3287, 'sub_bool', False, None,
                 'seventh pass',
                 'Enable a seventh pass in the FFT window deformation evaluation.'],

            'corr_window_7':
                [3290, 'sub_int', 16, None,
                 'interrogation window',
                 'Interrogation window for the seventh pass.'],

            # individual pass validations
            'validation':
                [3300, None, None, None,
                 'Validation',
                 None],

            'validation_frame':
                [3305, 'labelframe', None,
                 None,
                 'Validation',
                 None],

            'piv_sub_frame1':
                [3306, 'sub_labelframe', None,
                 None,
                 'first pass validation',
                 None],

            'fp_local_med_threshold':
                [3310, 'sub_bool', True, None,
                 'local median validation',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold. '],
            
            'fp_local_med':
                [3311, 'sub_float', 1.2, None,
                 'local median threshold',
                 'Local median absolute difference threshold.'],

            'fp_local_med_size':
                [3312, 'sub_int', 1, None,
                 'local median kernel',
                 'Local median filter kernel size.'],

            'globa_thr_spacer':
                [3325, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'fp_vld_global_threshold':
                [3330, 'sub_bool', False, None,
                 'global threshold validation',
                 'Validate first pass based on set global ' +
                 'thresholds.'],

            'fp_MinU':
                [3331, 'sub_float', -100.0, None,
                 'min u',
                 'Minimum U allowable component.'],

            'fp_MaxU':
                [3332, 'sub_float', 100.0, None,
                 'max u',
                 'Maximum U allowable component.'],

            'fp_MinV':
                [3333, 'sub_float', -100.0, None,
                 'min v',
                 'Minimum V allowable component.'],

            'fp_MaxV':
                [3334, 'sub_float', 100.0, None,
                 'max v',
                 'Maximum V allowable component.'],

            'piv_sub_frame2':
                [3340, 'sub_labelframe', None,
                 None,
                 'other pass validations',
                 None],
            
            'sp_local_med_validation':
                [3350, 'sub_bool', True, None,
                 'local median validation',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold.'],
            
            'sp_local_med':
                [3351, 'sub_float', 1.2, None,
                 'local median threshold',
                 'Local median absolute difference threshold.'],

            'sp_local_med_size':
                [3352, 'sub_int', 1, None,
                 'local median kernel',
                 'Local median filter kernel size.'],

            'glob_std_spacer':
                [3355, 'sub_h-spacer', None,
                 None,
                 None,
                 None],

            'sp_vld_std_threshold':
                [3360, 'sub_bool', False, None,
                 'standard deviation validation',
                 'Remove vectors, if the the sum of the squared ' +
                 'vector components is larger than the threshold ' +
                 'times the standard deviation of the flow field.'],
            
            'sp_std_threshold':
                [3361, 'sub_float', 8.0, None,
                 'std threshold',
                 'Standard deviation threshold.'],

            'glob_thr_spacer':
                [3365, 'sub_h-spacer', None,
                 None,
                 None,
                 None],
            
            'sp_vld_global_threshold':
                [3370, 'sub_bool', False, None,
                 'global threshold validation',
                 'Validate first pass based on set global ' +
                 'thresholds.'],
            
            'sp_vld_global_set_first': # this needs some rewording
                [3371, 'sub_bool', True, None,
                 'set to first pass',
                 'Set the settings of the other pass validations ' +
                 'to the same as first pass.'],
            
            'sp_MinU':
                [3372, 'sub_float', -100.0, None,
                 'min u',
                 'Minimum U allowable component.'],

            'sp_MaxU':
                [3373, 'sub_float', 100.0, None,
                 'max u',
                 'Maximum U allowable component.'],

            'sp_MinV':
                [3374, 'sub_float', -100.0, None,
                 'min v',
                 'Minimum V allowable component.'],

            'sp_MaxV':
                [3375, 'sub_float', 100.0, None,
                 'max v',
                 'Maximum V allowable component.'],

            'individual_pass_postprocessing':
                [3380, None, None, None,
                 'PostProcessing',
                 None],
            
            'piv_pass_postprocessing_frame':
                [3383, 'labelframe', None,
                 None,
                 'Pass Postprocessing',
                 None],
            
            'piv_sub_frame3':
                [3385, 'sub_labelframe', None,
                 None,
                 'interpolation',
                 None],
            
            'adv_repl':
                [3390, 'sub_bool', True, None,
                 'replace vectors',
                 'Replace vectors between each pass.'],
            
            'adv_repl_method':
                [3391, 'sub', 'localmean',
                 ('localmean', 'disk', 'distance'),
                 'replacement method',
                 'Each NaN element is replaced by a weighed average' +
                 'of neighbours. Localmean uses a square kernel, ' +
                 'disk a uniform circular kernel, and distance a ' +
                 'kernel with a weight that is proportional to the ' +
                 'distance.'],

            'adv_repl_iter':
                [3392, 'sub_int', 10, None,
                 'number of iterations',
                 'If there are adjacent NaN elements, iterative ' +
                 'replacement is needed.'],

            'adv_repl_kernel':
                [3393, 'sub_int', 2, None,
                 'kernel size',
                 'Diameter of the NaN interpolation kernel.'],

            'piv_sub_frame4':
                [3395, 'sub_labelframe', None,
                 None,
                 'Smoothing',
                 None],

            'smoothn_each_pass':
                [3400, 'sub_bool', True, None,
                 'smoothen each pass',
                 'Smoothen each pass using openpiv.smoothn.'],

            'smoothn_first_more':
                [3401, 'sub_bool', False, None,
                 'double first pass strength',
                 'Double the smoothing strength on the first pass.'],

            'robust1':
                [3402, 'sub_bool', False, None,
                 'smoothen robust',
                 'Activate robust in smoothen (minimizes influence of outlying data).'],

            'smoothn_val1':
                [3403, 'sub_float', 1.0, None,
                 'smoothing strength',
                 'Strength of smoothen script. Higher scalar number produces ' +
                 'more smoothed data.'],

            # validation/postprocessing
            'vld':
                [6000, None, None, None,
                 'PostProcessing',
                 None],

            'vld_frame':
                [6001, 'labelframe', None,
                 None,
                 'Postprocess',
                 None],

            'vld_sig2noise':
                [6010, 'bool', False, None,
                 'signal to noise ratio validation',
                 'Validate the data based on the signal to nose ratio ' +
                 'of the cross correlation.'],

            'sig2noise_threshold':
                [6030, 'float', 1.05, None,
                 's2n threshold',
                 'Threshold for filtering based on signal to noise ' +
                 'ratio. Recommended value: between 1.05 and 1.1.'],

            'horizontal_spacer11':
                [6035, 'h-spacer', None,
                 None,
                 None,
                 None],

            'vld_global_std':
                [6040, 'bool', False, None,
                 'standard deviation validation',
                 'Validate the data based on a multiple of the ' +
                 'standard deviation.'],

            'global_std_threshold':
                [6050, 'float', 5.0, None,
                 'std threshold',
                 'Remove vectors, if the the sum of the squared ' +
                 'vector components is larger than the threshold ' +
                 'times the standard deviation of the flow field.'],

            'horizontal_spacer12':
                [6055, 'h-spacer', None,
                 None,
                 None,
                 None],

            'vld_local_med':
                [6060, 'bool', True, None,
                 'local median validation',
                 'Validate the data based on a local median ' +
                 'threshold.'],

            'local_median_threshold':
                [6065, 'float', 1.2, None,
                 'local median threshold',
                 'Discard vector, if the absolute difference with ' +
                 'the local median is greater than the threshold. '],
            
            'local_median_size':
                [6070, 'int', 1, None,
                 'local median kernel',
                 'Local median filter kernel size.'],
            
            'horizontal_spacer13':
                [6075, 'h-spacer', None,
                 None,
                 None,
                 None],

            'vld_global_thr':
                [6080, 'bool', False, None,
                 'global threshold validation',
                 'Validate the data based on set global ' +
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

            'horizontal_spacer14':
                [6095, 'h-spacer', None,
                 None,
                 None,
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

            'horizontal_spacer15':
                [7045, 'h-spacer', None,
                 None,
                 None,
                 None],

            'smoothn':
                [7050, 'bool', False, None,
                 'smoothn data',
                 'Smoothn data using openpiv.smoothn.'],

            'smoothn_type':
                [7060, 'str', 'last pass',
                 ('last pass', 'each pass'),
                 'smoothn vectors',
                 'Smoothn data with openpiv.smoothn. <each pass> only applies to windef'],

            'robust':
                [7070, 'bool', False, None,
                 'smoothn robust',
                 'Activate robust in smoothn (minimizes influence of outlying data).'],

            'smoothn_val':
                [7080, 'float', 1.0, None,
                 'smoothning strength',
                 'Strength of smoothn script. Higher scalar number produces ' +
                 'more smoothned data.'],

            'average_spacer':
                [7085, 'h-spacer', None,
                 None,
                 None,
                 None],

            'average_results':
                [7090, 'bool', False, None,
                 'average results (not implemented yet)',
                 'Average all results in selected directory. ' +
                 'Results in a single file with averaged results.'],

            'delimiter_spacer':
                [7095, 'h-spacer', None,
                 None,
                 None,
                 None],

            'delimiter':
                [7100, 'str', 'tab', (',', ';', 'space', 'tab'),
                 'delimiter',
                 'Delimiter.'],

            'postproc_spacer':
                [7105, 'h-spacer', None,
                 None,
                 None,
                 None],

            'post_button':
                [7110, 'post_button', None,
                 None,
                 None,
                 None],
            
            # plotting
            'plt':
                [8000, None, None, None,
                 'Plot',
                 None],
            'plt_frame':
                [8005, 'labelframe', None, 
                 None,
                 'Plotting',
                 None],
            'plot_type':
                [8010, 'str', 'contour + vectors', ('vectors', 'contour', 'contour + vectors', 
                                          'streamlines','histogram','profiles','scatter', 
                                          'line',
                                          #'bar', Failed testing (for Windows 10), simply locks GUI.
                                          'density'),
                 'plot type',
                 'Select how to plot velocity data.'],
            'plot_title':
                [8020, 'str', 'Title', None, 
                 'diagram title', 
                 'diagram title.'],
            #plot_derivatives':
            #   [8075, 'str', 'None', ('None', 'Vorticity'),
            #   'plot derivatives',
            #   'Plot derivatives of the vector map (for vectors, countours, and streamlines only).'],
            'streamline_density':
                [8095, 'str', '0.5, 1', None, 
                 'streamline density',
                 'streamline density. Can be one value (e.g. 1) or a couple' +
                 ' of values for a range (e.g. 0.5, 1).'],
            'integrate_dir':
                [8097, 'str', 'both', ('both', 'forward','backward'),
                 'streamline direction',
                 'Integrate the streamline in forward, backward or both ' +
                 'directions. default is both.'],
            'statistics_frame':
                [8105, 'labelframe', None, 
                 None,
                 'Statistics',
                 None],
            'u_data':
                [8110, 'str', 'vx', None, 
                 'column name for u-velocity component',
                 'column name for the u-velocity component.' +
                 ' If unknown watch labbook entry.'],
            'v_data':
                [8120, 'str', 'vy', None, 
                 'column name for v-veloctiy component',
                 'column name for v-velocity component.' +
                 ' If unknown watch labbook entry.' +
                 ' For histogram only the v-velocity component is needed.'],
            'plot_scaling': 
                [8130, 'str', 'None', ('None','logx','logy','loglog'),
                 'axis scaling', 'scales the axes. logarithm scaling x-axis' +
                 ' --> logx; logarithm scaling y-axis --> logy; ' +
                 'logarithm scaling both axes --> loglog.'],
            'histogram_type':
                [8140, 'str', 'bar', ('bar','barstacked','step','stepfilled'), 
                 'histogram type', 
                 'Choose histogram type. Only available for histogram' + 
                 'plot.'],
            'histogram_quantity':
                [8150, 'str', 'v_x', ('v','v_x','v_y'),
                 'histogram quantity',
                 'The absolute value of the velocity (v) or its x- ' +
                 'or y-component (v_x or v_y).'], 
            'histogram_bins':
                [8160, 'int', 20, None,
                 'histogram number of bins',
                 'Number of bins (bars) in the histogram.'],
            'profiles_orientation':
                [8170, 'str', 'vertical', ('vertical','horizontal'),
                 'profiles orientation',
                 'Plot v_y over x (horizontal) or v_x over y (vertical).'],
            'profiles_jump':
                [8180, 'int', 5, None, 
                 'profile density', 
                 'The amount of profile lines (minimum of 1).'],
            'plot_xlim':
                [8190, 'str', '', None, 
                 'limits for the x-axis', 
                 'For implementation use (lower_limit, upper_limit).'],
            'plot_ylim':
                [8200, 'str', '', None, 
                 'limits for the y-axis',
                 'For implementation use (lower_limit, upper_limit).'],
            'modify_plot_appearance':
                [8500, None, None, None,
                 'Plot',
                 None],
            'modify_plot_frame':
                [8505, 'labelframe', None, 
                 None,
                 'Modify Plot Appearance',
                 None],
            'vector_subframe':
                [8505, 'sub_labelframe', None, 
                 None,
                 'Vectors',
                 None],
            'vec_scale':
                [8510, 'sub_int', 100, None,
                 'vector scaling',
                 'Velocity as a fraction of the plot width, e.g.: ' +
                 'm/s per plot width. Large values result in shorter ' +
                 'vectors.'],
            'vec_width':
                [8520, 'sub_float', 0.0025, None,
                 'vector line width',
                 'Line width as a fraction of the plot width.'],
            'invalid_color':
                [8530, 'dummy', 'red', None,
                 None,
                 'Choose the color of the vectors'],
            'valid_color':
                [8540, 'dummy', 'black', None,
                 None,
                 'Choose the color of the vectors'],
            'invert_yaxis': # now applies to contours, so it is placed in the main labelframe
                [8550, 'bool', True, None,
                 'invert y-axis',
                 'Define the top left corner as the origin ' +
                 'of the vector plot coordinate sytem, ' +
                 'as it is common practice in image processing.'],
            'derived_subframe':
                [8555, 'sub_labelframe', None, 
                 None,
                 'Derived Parameters',
                 None],
            'color_map':
                [8560, 'sub', 'viridis', ('viridis','jet','short rainbow',
                                          'long rainbow','seismic','autumn','binary'),
                 'Color map', 'Color map for streamline- and contour-plot.'],
            'extend_cbar':
                [8570, 'sub_bool', True, None,
                'extend colorbar',
                'Extend the top and bottom of the colorbar to accept out of range values.'],
            'velocity_color':
                [8575, 'sub', 'v', ('vx','vy','v'),
                 'set colorbar to: ',
                 'Set colorbar to velocity components.'],
            'color_levels':
                [8580, 'sub', '30', None, 'number of color levels',
                 'Select the number of color levels for contour plot.'],
            'vmin':
                [8590, 'sub', '', None, 
                 'min velocity for colormap',
                 'minimum velocity for colormap (contour plot).'],
            'vmax':
                [8595, 'sub', '', None, 
                 'max velocity for colormap',
                 'maximum velocity for colormap (contour plot).'],
            'statistics_subframe':
                [8600, 'sub_labelframe', None, 
                 None,
                 'Statistics',
                 None],
            'plot_grid':
                [8610, 'sub_bool', True, None, 
                 'grid', 
                 'adds a grid to the diagram.'],
            'plot_legend':
                [8620, 'sub_bool', True, None,
                 'legend', 
                 'adds a legend to the diagram.'],
            
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
            if (group < self.index[key] < group+1000
                and self.type[key] not in [
                    'labelframe', 
                    'sub_labelframe', 
                    'h-spacer', 
                    'sub_h-spacer',
                    'dummy'
                    ]):
                s = s + str(self.label[key]) + '\n' + \
                '    ' + str.replace(str(self.help[key]), '\n', '\n    ') + '\n\n'
        return(s)

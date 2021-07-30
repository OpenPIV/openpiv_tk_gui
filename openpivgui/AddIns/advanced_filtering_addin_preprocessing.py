from openpivgui.AddIns.AddIn import AddIn
from scipy.ndimage.filters import gaussian_filter
from skimage import exposure
import numpy as np


class advanced_filtering_addin_preprocessing(AddIn):
    """
        Blueprint for developing own methods and inserting own variables
        into the already existing PIV GUI via the AddIn system
    """

    # description for the Add_In_Handler textarea
    addin_tip = "This is the description of the advanced filter addin which " \
                "is still missing now"

    # has to be the add_in_name and its abbreviation
    add_in_name = "advanced_filtering_addin (afa)"

    # variables
    #########################################################
    # Place additional variables in the following sections. #
    # Widgets are created automatically. Don't care about   #
    # saving and restoring - new variables are included     #
    # automatically.                                        #
    #                                                       #
    # e.g.                                                  #
    #   **abbreviation**_**variable_name** =                #
    #       [**id over super group**, **variable_type**,    #
    #        **standard_value**,**hint**, **label**         #
    #        **tool tip**                                   #
    #########################################################
    variables = {
        'afa_frame': [2060, 'sub_labelframe', None, None, 'advanced filtering',
                      None],

        'afa_CLAHE': [2065, 'sub_bool', 'True', None, 'CLAHE filter',
                      'Contrast Limited Adaptive Histogram Equalization '
                      'filter (see skimage adapthist()).'],

        'afa_CLAHE_first': [2066, 'sub_bool', 'False', None,
                            'perform CLAHE before high pass',
                            'Perform CLAHE filter before Gaussian high pass '
                            'filters.'],

        'afa_CLAHE_auto_kernel': [2067, 'sub_bool', True, None,
                                  'automatic kernel sizing',
                                  'Have the kernel automatically sized to 1/8 '
                                  'width and height of the image.'],

        'afa_CLAHE_kernel': [2068, 'sub_int', 20, None, 'kernel size',
                             'Defining the size of the kernel for CLAHE.'],

        'afa_high_pass_filter_spacer': [2069, 'sub_h-spacer', None, None, None,
                                        None],

        'afa_high_pass_filter': [2074, 'sub_bool', 'False', None,
                                 'Gaussian high pass filter',
                                 'A simple subtracted Gaussian high pass '
                                 'filter.'],

        'afa_hp_sigma': [2075, 'sub_int', 5, None, 'sigma',
                         'Defining the sigma size of the subtracted gaussian '
                         'filter in the high pass filter '
                         '(positive ints only).'],

        'afa_hp_clip': [2076, 'sub_bool', 'True', None, 'clip at zero',
                        'Set all values less than zero to zero.'],

        'afa_intensity_threshold_spacer': [2080, 'sub_h-spacer', None, None,
                                           None, None],
        'afa_intensity_cap_filter': [2085, 'sub_bool', 'False', None,
                                     'intensity capping',
                                     'Simple global intesity cap filter. '
                                     'Masked pixels are set to the mean pixel '
                                     'intensity.'],

        'afa_ic_mult': [2086, 'sub_float', 2, None, 'std multiplication',
                        'Multiply the standard deviation of the pixel '
                        'intensities to get a higher cap value.'],

        'afa_Gaussian_lp_spacer': [2090, 'sub_h-spacer', None, None, None,
                                   None],

        'afa_gaussian_filter': [2095, 'sub_bool', 'False', None,
                                'Gaussian filter',
                                'Standard Gaussian blurring filter'
                                ' (see scipy gaussian_filter()).'],

        'afa_gf_sigma': [2100, 'sub_int', 1, None, 'sigma',
                         'Defining the sigma size for gaussian blur filter.'],

        'afa_intensity_clip_spacer': [2105, 'sub_h-spacer', None, None, None,
                                      None],

        'afa_intensity_clip': [2110, 'sub_bool', 'False', None,
                               'intensity clip',
                               'Any intensity less than the threshold is set '
                               'to zero.'],

        'afa_intensity_clip_min': [2115, 'sub_int', 20, None, 'min intensity',
                                   'Any intensity less than the threshold is '
                                   'set to zero with respect to the resized '
                                   'image inntensities.']
    }

    def advanced_filtering_method(self, img, GUI):
        resize = GUI.p['img_int_resize']
        if GUI.p['afa_CLAHE'] or GUI.p['afa_high_pass_filter']:
            if GUI.p['afa_CLAHE_first']:
                if GUI.p['afa_CLAHE']:
                    if GUI.p['afa_CLAHE_auto_kernel']:
                        kernel = None
                    else:
                        kernel = GUI.p['afa_CLAHE_kernel']

                    img = exposure.equalize_adapthist(img,
                                                      kernel_size=kernel,
                                                      clip_limit=0.01,
                                                      nbins=256)

                if GUI.p['afa_high_pass_filter']:
                    low_pass = gaussian_filter(img,
                                               sigma=GUI.p['afa_hp_sigma'])
                    img -= low_pass

                    if GUI.p['afa_hp_clip']:
                        img[img < 0] = 0

            else:
                if GUI.p['afa_high_pass_filter']:
                    low_pass = gaussian_filter(img,
                                               sigma=GUI.p['afa_hp_sigma'])
                    img -= low_pass

                    if GUI.p['afa_hp_clip']:
                        img[img < 0] = 0

                if GUI.p['afa_CLAHE']:
                    if GUI.p['afa_CLAHE_auto_kernel']:
                        kernel = None
                    else:
                        kernel = GUI.p['afa_CLAHE_kernel']

                    img = exposure.equalize_adapthist(img,
                                                      kernel_size=kernel,
                                                      clip_limit=0.01,
                                                      nbins=256)

        # simple intensity capping
        if GUI.p['afa_intensity_cap_filter']:
            upper_limit = np.mean(img) + GUI.p['afa_ic_mult'] * img.std()
            img[img > upper_limit] = upper_limit

        # simple intensity clipping
        if GUI.p['afa_intensity_clip']:
            img *= resize
            lower_limit = GUI.p['afa_intensity_clip_min']
            img[img < lower_limit] = 0
            img /= resize

        if GUI.p['afa_gaussian_filter']:
            img = gaussian_filter(img, sigma=GUI.p['afa_gf_sigma'])

        return img

    def __init__(self, gui):
        super().__init__()
        # has to be the method which is implemented above
        gui.preprocessing_methods.update(
            {"advanced_filtering_addin_preprocessing":
             self.advanced_filtering_method})

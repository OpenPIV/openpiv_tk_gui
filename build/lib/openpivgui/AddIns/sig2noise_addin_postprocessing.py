from openpivgui.AddIns.AddIn import AddIn
import numpy as np
import openpiv.validation as piv_vld
from openpivgui.open_piv_gui_tools import create_save_vec_fname, save


class sig2noise_addin_postprocessing(AddIn):
    """
        Blueprint for developing own methods and inserting own variables
        into the already existing PIV GUI via the AddIn system
    """

    # description for the Add_In_Handler textarea
    addin_tip = "This is the description of the advanced filter addin which " \
                "is still missing now"

    # has to be the add_in_name and its abbreviation
    add_in_name = "sig2noise_addin (s2n)"

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
        's2n_vld_sig2noise':
        [6010, 'bool', False, None,
         'signal to noise ratio validation',
         'Validate the data based on the signal to nose ratio ' +
         'of the cross correlation.'],

            's2n_sig2noise_threshold':
                [6030, 'float', 1.05, None,
                 's2n threshold',
                 'Threshold for filtering based on signal to noise ' +
                 'ratio. Recommended value: between 1.05 and 1.1.'],

            's2n_horizontal_spacer11': [6035, 'h-spacer', None, None, None,
                                        None]
    }

    def sig2noise(self, gui, delimiter):
        """Filter vectors based on the signal to noise threshold.

        See:
            openpiv.validation.sig2noise_val()
        """
        result_fnames = []
        for i, f in enumerate(gui.p['fnames']):
            data = np.loadtxt(f)
            u, v, mask = piv_vld.sig2noise_val(
                data[:, 2], data[:, 3], data[:, 5],
                threshold=gui.p['s2n_sig2noise_threshold'])

            save_fname = create_save_vec_fname(
                path=f,
                postfix='_sig2noise')

            save(data[:, 0],
                 data[:, 1],
                 u, v,
                 data[:, 4] + mask,
                 sig2noise=data[:, 5],
                 filename=save_fname,
                 delimiter=delimiter)
            result_fnames.append(save_fname)
        return result_fnames

    def __init__(self, gui):
        super().__init__()
        # has to be the method which is implemented above
        gui.postprocessing_methods.update(
            {"sig2noise_addin_postprocessing":
             ['validation', 's2n_vld_sig2noise', self.sig2noise]})

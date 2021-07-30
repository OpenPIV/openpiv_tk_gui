from openpivgui.AddIns.AddIn import AddIn
import numpy as np
from openpivgui.open_piv_gui_tools import create_save_vec_fname, save
import openpiv.filters as piv_flt


class repl_outliers_addin_postprocessing(AddIn):
    """
        Blueprint for developing own methods and inserting own variables
        into the already existing PIV GUI via the AddIn system
    """

    # description for the Add_In_Handler textarea
    addin_tip = "This is the description of the advanced filter addin which " \
                "is still missing now"

    # has to be the add_in_name and its abbreviation
    add_in_name = "repl_outliers_addin (roa)"

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
        'roa_repl':
        [7010, 'bool', True, None,
         'replace outliers',
         'Replace outliers.'],

            'roa_repl_method':
                [7020, 'str', 'localmean',
                 ('localmean', 'disk', 'distance'),
                 'replacement method',
                 'Each NaN element is replaced by a weighed average' +
                 'of neighbours. Localmean uses a square kernel, ' +
                 'disk a uniform circular kernel, and distance a ' +
                 'kernel with a weight that is proportional to the ' +
                 'distance.'],

            'roa_repl_iter':
                [7030, 'int', 10, None,
                 'number of iterations',
                 'If there are adjacent NaN elements, iterative ' +
                 'replacement is needed.'],

            'roa_repl_kernel':
                [7040, 'int', 2, None,
                 'kernel size',
                 'Diameter of the weighting kernel.'],

            'roa_horizontal_spacer15':
                [7045, 'h-spacer', None, None, None, None]
    }

    def repl_outliers(self, gui, delimiter):
        """Replace outliers."""
        result_fnames = []
        for i, f in enumerate(gui.p['fnames']):
            data = np.loadtxt(f)
            u, v = piv_flt.replace_outliers(
                np.array([data[:, 2]]), np.array([data[:, 3]]),
                method=gui.p['roa_repl_method'],
                max_iter=gui.p['roa_repl_iter'],
                kernel_size=gui.p['roa_repl_kernel'])
            save_fname = create_save_vec_fname(
                path=f,
                postfix='_repl')
            save(data[:, 0],
                 data[:, 1],
                 u, v,
                 data[:, 4],
                 data[:, 5],
                 save_fname,
                 delimiter=delimiter)
            result_fnames.append(save_fname)
        return result_fnames

    def __init__(self, gui):
        super().__init__()
        # has to be the method which is implemented above
        gui.postprocessing_methods.update(
            {"repl_outliers_addin_postprocessing":
             ['postprocessing', 'roa_repl', self.repl_outliers]})

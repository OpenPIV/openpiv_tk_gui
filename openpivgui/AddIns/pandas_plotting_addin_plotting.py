from openpivgui.AddIns.AddIn import AddIn


class pandas_plotting_addin_plotting(AddIn):
    """
        Blueprint for developing own methods and inserting own variables
        into the already existing PIV GUI via the AddIn system
    """

    # description for the Add_In_Handler textarea
    addin_tip = "This is the description of the advanced filter addin which " \
                "is still missing now"

    # has to be the add_in_name and its abbreviation
    add_in_name = "pandas_plotting_addin (ppa)"

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
        'ppa_pandas_frame':
        [8505, 'labelframe', None, None,
         'pandas', None],
            'ppa_plot_scaling':
                [8515, 'str', 'None', ('None', 'logx', 'logy', 'loglog'),
                 'axis scaling', 'scales the axes. logarithm scaling x-axis' +
                 ' --> logx; logarithm scaling y-axis --> logy; ' +
                 'logarithm scaling both axes --> loglog.'],
            'ppa_plot_xlim':
                [8525, 'str', '', None,
                 'limits for the x-axis',
                 'For implementation use (lower_limit, upper_limit).'],
            'ppa_plot_ylim':
                [8535, 'str', '', None,
                 'limits for the y-axis',
                 'For implementation use (lower_limit, upper_limit).'],
            'ppa_u_data':
                [8545, 'str', 'vx', None,
                 'x-data',
                 'Column name for the u-velocity component.' +
                 ' If unknown watch labbook entry.'],
            'ppa_v_data':
                [8555, 'str', 'vy', None,
                 'y-data',
                 'Column name for v-velocity component.' +
                 ' If unknown watch labbook entry.' +
                 ' For histogram only the v-velocity component is needed.'],
            'ppa_plot_grid':
                [8565, 'bool', True, None,
                 'grid',
                 'adds a grid to the diagram.'],
            'ppa_plot_legend':
                [8575, 'bool', True, None,
                 'legend',
                 'adds a legend to the diagram.'],

            'ppa_histogram_sub_frame':
                [8605, 'sub_labelframe', None, None, 'histogram', None],
            'ppa_histogram_quantity':
                [8615, 'sub', 'v_x', ('v', 'v_x', 'v_y'),
                 'histogram quantity',
                 'The absolute value of the velocity (v) or its x- ' +
                 'or y-component (v_x or v_y).'],
            'ppa_histogram_bins':
                [8625, 'sub_int', 20, None,
                 'histogram number of bins',
                 'Number of bins (bars) in the histogram.'],
            'ppa_histogram_normalize':
                [8635, 'sub_bool', False, None,
                 'normalize histogram',
                 'Normalize histogram (divide by the number of counts, '
                 'density).'],
            'ppa_histogram_type':
                [8645, 'sub', 'bar',
                 ('bar', 'barstacked', 'step', 'stepfilled'),
                 'histogram type',
                 'Choose histogram type. Only available for histogram' +
                 'plot.'],
    }

    def pandas_plot(self, data, parameter, figure):
        """
            Display a plot with the pandas plot utility.

            Parameters
            ----------
            data : pandas.DataFrame
                Data to plot.
            parameter : openpivgui.OpenPivParams.py
                Parameter-object.
            figure : matplotlib.figure.Figure
                An (empty) figure.

            Returns
            -------
            None.

        """
        # set boolean for chosen axis scaling
        if parameter['ppa_plot_scaling'] == 'None':
            logx, logy, loglog = False, False, False
        elif parameter['ppa_plot_scaling'] == 'logx':
            logx, logy, loglog = True, False, False
        elif parameter['ppa_plot_scaling'] == 'logy':
            logx, logy, loglog = False, True, False
        elif parameter['ppa_plot_scaling'] == 'loglog':
            logx, logy, loglog = False, False, True
        else:
            raise ValueError("non supported plot scaling chosen")
        # add subplot
        ax = figure.add_subplot(111)
        # set limits initially to None
        xlim = None
        ylim = None
        # try to set limits, if not possible (no entry) --> None
        try:
            xlim = (float(list(parameter['ppa_plot_xlim'].split(','))[0]),
                    float(list(parameter['ppa_plot_xlim'].split(','))[1]))
        except BaseException:
            pass
            # print('No Values or wrong syntax for x-axis limitation.')
        try:
            ylim = (float(list(parameter['ppa_plot_ylim'].split(','))[0]),
                    float(list(parameter['ppa_plot_ylim'].split(','))[1]))
        except BaseException:
            pass
            # print('No Values or wrong syntax for y-axis limitation.')
        # iteration to set value types to float
        for i in list(data.columns.values):
            data[i] = data[i].astype(float)

        if parameter['plot_type'] == 'histogram':
            # get column names as a list for comparing with chosen histogram
            # quantity
            col_names = list(data.columns.values)
            # if loop for histogram quantity
            if parameter['ppa_histogram_quantity'] == 'v_x':
                data_hist = data[col_names[2]]
            elif parameter['ppa_histogram_quantity'] == 'v_y':
                data_hist = data[col_names[3]]
            elif parameter['ppa_histogram_quantity'] == 'v':
                data_hist = (data[col_names[2]] ** 2 + data[
                    col_names[3]] ** 2) ** 0.5
            # histogram plot
            ax.hist(data_hist,
                    bins=int(parameter['ppa_histogram_bins']),
                    label=parameter['ppa_histogram_quantity'],
                    log=logy,
                    range=xlim,
                    density=parameter['ppa_histogram_normalize'],
                    histtype=parameter['ppa_histogram_type'],
                    )
            ax.grid(parameter['ppa_plot_grid'])
            ax.legend()
            ax.set_xlabel('velocity [m/s]')
            ax.set_ylabel('number of vectors')
            ax.set_title(parameter['plot_title'])
        else:
            data.plot(x=parameter['ppa_u_data'],
                      y=parameter['ppa_v_data'],
                      kind=parameter['plot_type'],
                      title=parameter['plot_title'],
                      grid=parameter['ppa_plot_grid'],
                      legend=parameter['ppa_plot_legend'],
                      logx=logx,
                      logy=logy,
                      loglog=loglog,
                      xlim=xlim,
                      ylim=ylim,
                      ax=ax)

    def __init__(self, gui):
        super().__init__()
        hint = gui.p.hint["plot_type"]
        hint = hint + ('histogram', 'line', 'density')
        gui.p.hint["plot_type"] = hint
        # has to be the method which is implemented above
        gui.plotting_methods.update(
            {"pandas_plotting_addin_plotting":
             ['plotting', 'pandas_plotting', ['histogram', 'line', 'density'],
              self.pandas_plot]})

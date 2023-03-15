from openpivgui.AddIns.AddIn import AddIn
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from copy import copy
from matplotlib import pyplot as plt


class streamlines_plotting_addin_plotting(AddIn):
    """
        Blueprint for developing own methods and inserting own variables
        into the already existing PIV GUI via the AddIn system
    """

    # description for the Add_In_Handler textarea
    addin_tip = "This is the description of the advanced filter addin which " \
                "is still missing now"

    # has to be the add_in_name and its abbreviation
    add_in_name = "streamlines_plotting_addin (spa)"

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
            'spa_streamline_frame': [8405, 'labelframe', None, None,
                                     'streamlines', None],
            'spa_density': [8415, 'str', '0.5, 1', None, 'streamline density',
                            'streamline density. Can be one value (e.g. 1) or '
                            'a couple of values for a range (e.g. 0.5, 1).'],
            'spa_color_map': [8425, 'str', 'viridis', ('viridis', 'jet',
                                                       'short rainbow',
                                                       'long rainbow',
                                                       'seismic',
                                                       'autumn',
                                                       'binary'),
                              'Color map', 'Color map for streamline- '
                                           'and contour-plot.'],
            'spa_velocity_color': [8435, 'str', 'v', ('vx', 'vy', 'v'),
                                   'set colorbar to: ',
                                   'Set colorbar to velocity components.'],
            'spa_integrate_dir': [8445, 'str', 'both', ('both', 'forward',
                                                        'backward'),
                                  'streamline direction',
                                  'Integrate the streamline in forward, '
                                  'backward or both directions. default is '
                                  'both.'],
            'spa_vec_width': [8455, 'float', 0.0025, None, 'vector line width',
                              'Line width as a fraction of the plot width.'],
    }

    # creating a custom rainbow colormap
    short_rainbow = {'red': ((0.0, 0.0, 0.0),
                             (0.2, 0.2, 0.2),
                             (0.5, 0.0, 0.0),
                             (0.8, 1.0, 1.0),
                             (1.0, 1.0, 1.0)),
                     'green': ((0.0, 0.0, 0.0),
                               (0.2, 1.0, 1.0),
                               (0.5, 1.0, 1.0),
                               (0.8, 1.0, 1.0),
                               (1.0, 0.0, 0.0)),
                     'blue': ((0.0, 1.0, 1.0),
                              (0.2, 1.0, 1.0),
                              (0.5, 0.0, 0.0),
                              (0.8, 0.0, 0.0),
                              (1.0, 0.0, 0.0))}

    long_rainbow = {'red': ((0.0, 0.0, 0.0),
                            (0.1, 0.5, 0.5),
                            (0.2, 0.0, 0.0),
                            (0.3, 0.2, 0.2),
                            (0.5, 0.0, 0.0),
                            (0.7, 1.0, 1.0),
                            (0.8, 1.0, 1.0),
                            (1.0, 1.0, 1.0)),
                    'green': ((0.0, 0.0, 0.0),
                              (0.1, 0.0, 0.0),
                              (0.2, 0.0, 0.0),
                              (0.3, 1.0, 1.0),
                              (0.5, 1.0, 1.0),
                              (0.7, 1.0, 1.0),
                              (0.8, 0.0, 0.0),
                              (1.0, 0.3, 0.3)),
                    'blue': ((0.0, 0.0, 0.0),
                             (0.1, 0.5, 0.5),
                             (0.2, 1.0, 1.0),
                             (0.3, 1.0, 1.0),
                             (0.5, 0.0, 0.0),
                             (0.7, 0.0, 0.0),
                             (0.8, 0.0, 0.0),
                             (1.0, 1.0, 1.0))}

    short_rainbow = LinearSegmentedColormap('my_colormap', short_rainbow, 256)
    long_rainbow = LinearSegmentedColormap('my_colormap', long_rainbow, 256)

    def streamlines(self, data, parameter, figure):
        """
            Display a streamline plot.

            Parameters
            ----------
            data : pandas.DataFrame
                Data to plot.
            parameter : openpivgui.OpenPivParams.py
                Parameter object.
            figure : matplotlib.figure.Figure
                An (empty) Figure object.
        """
        ax = figure.add_subplot(111)

        # make sure all values are from type float
        for i in list(data.columns.values):
            data[i] = data[i].astype(float)

        # get density for streamline plot.
        try:
            density = (float(list(parameter['spa_density'].split(','))[0]),
                       float(list(parameter['spa_density'].split(','))[1]))
        except:
            density = float(parameter['spa_density'])

        # Choosing the correct colormap
        if parameter['spa_color_map'] == 'short rainbow':
            colormap = self.short_rainbow
        elif parameter['spa_color_map'] == 'long rainbow':
            colormap = self.long_rainbow
        else:
            colormap = parameter['spa_color_map']

        # pivot table for streamline plot
        data_vx = data.pivot(index='y',
                             columns='x',
                             values='vx')
        data_vy = data.pivot(index='y',
                             columns='x',
                             values='vy')

        # choosing data for the colormap
        if parameter['spa_velocity_color'] == 'vx':
            color_values = data_vx.values
        elif parameter['spa_velocity_color'] == 'vy':
            color_values = data_vy.values
        else:
            color_values = (data_vx.values ** 2 + data_vy.values ** 2) ** 0.5

        # try to create streamline plot. If values are not equally spaced the
        # exception will space the values equally (mean difference is
        # calculated.)

        try:
            fig = ax.streamplot(data_vx.columns,
                                data_vx.index,
                                data_vx.values,
                                data_vy.values,
                                density=density,
                                color=color_values,
                                cmap=colormap,
                                integration_direction=parameter[
                                    'spa_integrate_dir'],
                                linewidth=parameter['spa_vec_width'])
        except:
            # get dimension of the DataFrame
            dim = [len(set(data.x)), len(set(data.y))]

            # calculate mean difference for x and y values
            diff = [round(np.mean([data.x[i + 1] - data.x[i]
                                   for i in range(dim[0] - 1)]), 6),
                    round(
                        np.mean([data.y[dim[0] * (i + 1)] - data.y[dim[0] * i]
                                 for i in range(dim[1] - 1)]), 6)]

            # this list is initialized with starting values and will be
            # added by
            # equally spaced values.
            cache = [round(copy(data.x[0]), 6), round(copy(data.y[0]), 6)]

            # nested lists with equally spaced coordinates
            coordinates = [[], []]

            # loop for calculating the new x data
            j = 1
            for i in range(1, len(data)):
                if i == dim[0] * j:
                    coordinates[0].append(round(cache[0], 6))
                    cache[0] = coordinates[0][0]
                    j += 1
                else:
                    coordinates[0].append(round(cache[0], 6))
                    cache[0] += diff[0]
            coordinates[0].append(round(cache[0], 6))

            # loop for calculating the new y data
            j = 1
            for i in range(len(data)):
                if i == dim[0] * j:
                    cache[1] += diff[1]
                    coordinates[1].append(round(cache[1], 6))
                    j += 1
                else:
                    coordinates[1].append(round(cache[1], 6))

            # overwrite the old x and y values with the new ones
            data.x = coordinates[0]
            data.y = coordinates[1]

            # create new pivot tables for streamline plot
            data_vx = data.pivot(index='y', columns='x', values='vx')
            data_vy = data.pivot(index='y', columns='x', values='vy')

            # choosing data for the colormap
            if parameter['spa_velocity_color'] == 'vx':
                color_values = data_vx.values
            elif parameter['spa_velocity_color'] == 'vy':
                color_values = data_vy.values
            else:
                color_values = (data_vx.values ** 2
                                + data_vy.values ** 2) ** 0.5

            # new streamline plot with equally spaced coordinates
            fig = ax.streamplot(data_vx.columns,
                                data_vx.index,
                                data_vx.values,
                                data_vy.values,
                                density=density,
                                color=color_values,
                                cmap=colormap,
                                integration_direction=parameter[
                                    'spa_integrate_dir'],
                                linewidth=parameter['spa_vec_width'])
        # add colorbar
        cb = plt.colorbar(fig.lines, ax=ax)
        cb.ax.set_ylabel('Velocity [m/s]')

        # set origin to top left or bottom left
        if parameter['invert_yaxis']:
            ax.set_ylim(ax.get_ylim()[::-1])

        # add diagram options
        ax.set_xlabel('x-position')
        ax.set_ylabel('y-position')
        ax.set_title(parameter['plot_title'])

    def __init__(self, gui):
        super().__init__()
        hint = gui.p.hint["plot_type"]
        hint = hint + ('streamlines',)
        gui.p.hint["plot_type"] = hint
        # has to be the method which is implemented above
        gui.plotting_methods.update(
                {"streamlines_plotting_addin_plotting":
                    ['plotting', 'streamlines_plotting', ['streamlines'],
                     self.streamlines]})

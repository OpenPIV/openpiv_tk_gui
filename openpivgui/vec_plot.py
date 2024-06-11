#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plotting vector data.

This module can be used in two different ways:

1. As a library. Just import the module and call the functions.
   This is the way, how this module is used in openpivgui, for
   example.

2. As a terminal-application. Execute
   python3 -m openpivgui.vec_plot --help
   for more information.
   This is the way, how this module ist used in JPIV, for example.
   For now, not all functions are callable in this way.
"""

import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
import argparse
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


# creating a custom rainbow colormap

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


def histogram(data, parameter, figure, quantity, bins, log_y):
    """
        Plot an histogram.

        Plots an histogram of the specified quantity.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to plot.
        figure : matplotlib.figure.Figure
            An (empty) Figure object.
        quantity : str
            Either v (abs v), v_x (x-component) or v_y (y-component).
        bins : int
             Number of bins (bars) in the histogram.
        log_scale : boolean
            Use logaritmic vertical axis.
    """

    if quantity == 'v':
        xlabel = 'absolute displacement'
        h_data = np.array([(l[2]**2 + l[3]**2)**0.5 for l in data])
    elif quantity == 'v_x':
        xlabel = 'x displacement'
        h_data = np.array([l[2] for l in data])
    elif quantity == 'v_y':
        xlabel = 'y displacement'
        h_data = np.array([l[3] for l in data])
    ax = figure.add_subplot(111)
    if log_y:
        ax.set_yscale("log")
    ax.hist(h_data, bins, label=quantity)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('number of vectors')
    ax.set_title(parameter['plot_title'])


def profiles(data, parameter, fname, figure, orientation):
    """
        Plot velocity profiles.

        Line plots of the velocity component specified.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to plot.
        fname : str
            A filename containing vector data.
            (will be deprecated in later updates)
        figure : matplotlib.figure.Figure
            An (empty) Figure object.
        orientation : str
            horizontal: Plot v_y over x.
            vertical: Plot v_x over y.
    """
    #data = data.to_numpy().astype(float)
    data = np.loadtxt(fname)

    dim_x, dim_y = get_dim(data)

    p_data = []

    ax = figure.add_subplot(111)

    if orientation == 'horizontal':
        xlabel = 'x position'
        ylabel = 'y displacement'

        for i in range(0, dim_y, parameter['profiles_jump']):
            p_data.append(data[dim_x * i:dim_x * (i + 1), 3])
        # print(p_data[-1])
        for p in p_data:
            # print(len(p))
            ax.plot(range(dim_x), p, '.-')

    elif orientation == 'vertical':
        xlabel = 'y position'
        ylabel = 'x displacement'

        for i in range(0, dim_x, parameter['profiles_jump']):
            p_data.append(data[i::dim_x, 2])

        for p in p_data:
            ax.plot(range(dim_y), p, '.-')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(parameter['plot_title'])


def scatter(data, figure):
    """
        Scatter plot.

        Plots v_y over v_x.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to plot.
        figure : matplotlib.figure.Figure
            An (empty) Figure object.
    """
    data = data.to_numpy()

    v_x = data[:, 2]
    v_y = data[:, 3]

    ax = figure.add_subplot(111)

    ax.scatter(v_x, v_y, label='scatter')

    ax.set_xlabel('x displacement')
    ax.set_ylabel('y displacement')


def vector(data, parameter, figure, invert_yaxis=True, valid_color='blue',
           invalid_color='red', **kw):
    """
        Display a vector plot.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to plot.
        figure : matplotlib.figure.Figure
            An (empty) Figure object.
    """
    data = data.to_numpy().astype(float)

    try:
        invalid = data[:, 4].astype('bool')
    except BaseException:
        invalid = np.asarray([True for i in range(len(data))])

    # tilde means invert:
    valid = ~invalid

    ax = figure.add_subplot(111)

    ax.quiver(data[invalid, 0],
              data[invalid, 1],
              data[invalid, 2],
              data[invalid, 3],
              color=invalid_color,
              label='invalid', **kw)

    ax.quiver(data[valid, 0],
              data[valid, 1],
              data[valid, 2],
              data[valid, 3],
              color=valid_color,
              label='valid', **kw)

    if invert_yaxis:
        for ax in figure.get_axes():
            ax.invert_yaxis()

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.set_title(parameter['plot_title'])


def contour(data, parameter, figure):
    """
        Display a contour plot

        Parameters
        ----------
        data : pandas.DataFrame
            Data to plot.
        parameter : openpivgui.OpenPivParams.py
            Parameter-object.
        figure : matplotlib.figure.Figure
           An (empty) Figure object.
    """
    # figure for subplot
    ax = figure.add_subplot(111)
    # iteration to set value types to float
    for i in list(data.columns.values):
        data[i] = data[i].astype(float)
    # choosing velocity for the colormap and add it to an new column in data
    if parameter['velocity_color'] == 'vx':
        data['abs'] = data.vx
    elif parameter['velocity_color'] == 'vy':
        data['abs'] = data.vy
    else:
        data['abs'] = (data.vx**2 + data.vy**2)**0.5
    # pivot table for contour function
    data_pivot = data.pivot(index='y',
                            columns='x',
                            values='abs')
    # try to get limits, if not possible set to None
    try:
        vmin = float(parameter['vmin'])
    except BaseException:
        vmin = None
    try:
        vmax = float(parameter['vmax'])
    except BaseException:
        vmax = None
    # settings for color scheme of the contour plot
    if vmax is not None and vmin is not None:
        levels = np.linspace(vmin, vmax, int(parameter['color_levels']))
    elif vmax is not None:
        levels = np.linspace(0, vmax, int(parameter['color_levels']))
    elif vmin is not None:
        vmax = data_pivot.max().max()
        levels = np.linspace(vmin, vmax, int(parameter['color_levels']))
    else:
        levels = int(parameter['color_levels'])
    # Choosing the correct colormap
    if parameter['color_map'] == 'short rainbow':
        colormap = short_rainbow
    elif parameter['color_map'] == 'long rainbow':
        colormap = long_rainbow
    else:
        colormap = parameter['color_map']
    # set contour plot to the variable fig to add a colorbar
    if parameter['extend_cbar']:
        extend = 'both'
    else:
        extend = None
    fig = ax.contourf(data_pivot.columns,
                      data_pivot.index,
                      data_pivot.values,
                      levels=levels,
                      cmap=colormap,
                      vmin=vmin,
                      vmax=vmax,
                      extend=extend)

    # set the colorbar to the variable cb to add a description
    cb = plt.colorbar(fig, ax=ax)

    # set origin to top left or bottom left
    if parameter['invert_yaxis']:
        ax.set_ylim(ax.get_ylim()[::-1])

    # description to the contour lines
    cb.ax.set_ylabel('Velocity [m/s]')

    # labels for the axes
    ax.set_xlabel('x-position')
    ax.set_ylabel('y-position')

    # plot title from the GUI
    ax.set_title(parameter['plot_title'])


def contour_and_vector(data, parameter, figure, **kw):
    """
        Display a contour plot

        Parameters
        ----------
        data : pandas.DataFrame
            Data to plot.
        parameter : openpivgui.OpenPivParams.py
            Parameter-object.
        figure : matplotlib.figure.Figure
           An (empty) Figure object.
    """
    # figure for subplot
    ax = figure.add_subplot(111)
    # iteration to set value types to float
    for i in list(data.columns.values):
        data[i] = data[i].astype(float)
    # choosing velocity for the colormap and add it to an new colummn in data
    if parameter['velocity_color'] == 'vx':
        data['abs'] = data.vx
    elif parameter['velocity_color'] == 'vy':
        data['abs'] = data.vy
    else:
        data['abs'] = (data.vx**2 + data.vy**2)**0.5
    # pivot table for contour function
    data_pivot = data.pivot(index='y',
                            columns='x',
                            values='abs')
    # try to get limits, if not possible set to None
    try:
        vmin = float(parameter['vmin'])
    except BaseException:
        vmin = None
    try:
        vmax = float(parameter['vmax'])
    except BaseException:
        vmax = None
    # settings for color scheme of the contour plot
    if vmax is not None and vmin is not None:
        levels = np.linspace(vmin, vmax, int(parameter['color_levels']))
    elif vmax is not None:
        levels = np.linspace(0, vmax, int(parameter['color_levels']))
    elif vmin is not None:
        vmax = data_pivot.max().max()
        levels = np.linspace(vmin, vmax, int(parameter['color_levels']))
    else:
        levels = int(parameter['color_levels'])
    # Choosing the correct colormap
    if parameter['color_map'] == 'short rainbow':
        colormap = short_rainbow
    elif parameter['color_map'] == 'long rainbow':
        colormap = long_rainbow
    else:
        colormap = parameter['color_map']

    # set contour plot to the variable fig to add a colorbar
    if parameter['extend_cbar']:
        extend = 'both'
    else:
        extend = None
    fig = ax.contourf(data_pivot.columns,
                      data_pivot.index,
                      data_pivot.values,
                      levels=levels,
                      cmap=colormap,
                      vmin=vmin,
                      vmax=vmax,
                      extend=extend)

    # quiver plot
    data = data.to_numpy().astype(float)

    try:
        invalid = data[:, 4].astype('bool')
    except BaseException:
        invalid = np.asarray([True for i in range(len(data))])

    # tilde means invert:
    valid = ~invalid

    ax.quiver(data[invalid, 0],
              data[invalid, 1],
              data[invalid, 2],
              data[invalid, 3],
              color=parameter['invalid_color'],
              label='invalid', **kw)

    ax.quiver(data[valid, 0],
              data[valid, 1],
              data[valid, 2],
              data[valid, 3],
              color=parameter['valid_color'],
              label='valid', **kw)

    # set the colorbar to the variable cb to add a description
    cb = plt.colorbar(fig, ax=ax)

    # set origin to top left or bottom left
    if parameter['invert_yaxis']:
        ax.set_ylim(ax.get_ylim()[::-1])

    # description to the contour lines
    cb.ax.set_ylabel('Velocity [m/s]')

    # labels for the axes
    ax.set_xlabel('x-position')
    ax.set_ylabel('y-position')

    # plot title from the GUI
    ax.set_title(parameter['plot_title'])


def get_dim(array):
    """
        Computes dimension of vector data.

        Assumes data to be organised as follows (example):
        x  y  v_x v_y ..
        16 16 4.5 3.2 ..
        32 16 4.3 3.1 ..
        16 32 4.2 3.5 ..
        32 32 4.5 3.2 ..
        .. .. ..  ..

        Parameters
        ----------
        array : np.array
            Flat numpy array.

        Returns
        -------
        tuple
            Dimension of the vector field (x, y).
    """
    return(len(set(array[:, 0])),
           len(set(array[:, 1])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot vector data.')
    parser.add_argument('--plot_type',
                        type=str,
                        required=False,
                        choices=['histogram',
                                 'profiles',
                                 'vector',
                                 'scatter',
                                 'contour'
                                 'contour_and_vector',
                                 'streamlines'],
                        default='vector',
                        help='type of plot')
    parser.add_argument('--fname',
                        required=True,
                        type=str,
                        help='name of vector data file')
    parser.add_argument('--quantity',
                        type=str,
                        required=False,
                        choices=['v', 'v_x', 'v_y'],
                        default='v',
                        help='quantity to plot')
    parser.add_argument('--bins',
                        type=int,
                        required=False,
                        default=20,
                        help='number of histogram bins')
    parser.add_argument('--log_y',
                        type=bool,
                        required=False,
                        default=False,
                        help='logarithmic y-axis')
    parser.add_argument('--orientation',
                        type=str,
                        required=False,
                        choices=['horizontal', 'vertical'],
                        default='vertical',
                        help='plot profiles, either horizontal ' +
                             '(v_y over x) or vertical (v_x over y)')
    parser.add_argument('--invert_yaxis',
                        type=str,
                        required=False,
                        default=True,
                        help='Invert y-axis of vector plot')
    args = parser.parse_args()
    data = np.loadtxt(args.fname)
    fig = Figure()
    if args.plot_type == 'histogram':
        histogram(data,
                  fig,
                  quantity=args.quantity,
                  bins=args.bins,
                  log_y=args.log_y)
    elif args.plot_type == 'profiles':
        profiles(data,
                 fig,
                 orientation=args.orientation)
    elif args.plot_type == 'vector':
        vector(data,
               fig,
               invert_yaxis=args.invert_yaxis)
    elif args.plot_type == 'scatter':
        scatter(data,
                fig)
    elif args.plot_type == 'contour':
        print('Not yet implemented')
    elif args.plot_type == 'contour_and_vector':
        print('Not yet implemented')
    elif args.plot_type == 'streamlines':
        print('Not yet implemented')
    plt.show()

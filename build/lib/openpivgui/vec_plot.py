#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Plotting vector data.'''

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


import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def histogram(fname, figure, quantity, bins, log_y):
    '''Plot an histogram.

    Plots an histogram of the specified quantity.

    Args:
        fname (str): A filename containing vector data.
        figure (matplotlib.figure.Figure): 
            An (empty) Figure object.
        quantity (str): Either v (abs v), 
                               v_x (x-component) or 
                               v_y (y-component).
        bins (int): Number of bins (bars) in the histogram.
        log_scale (boolean): Use logaritmic vertical axis.
    '''
    data = np.loadtxt(fname)
    if quantity == 'v':
        xlabel = 'absolute displacement'
        h_data = np.array([(l[2]**2+l[3]**2)**0.5 for l in data])
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


def profiles(fname, figure, orientation):
    '''Plot velocity profiles.

    Line plots of the velocity component specified.

    Args:
        fname (str): A filename containing vector data.
        figure (matplotlib.figure.Figure): 
            An (empty) Figure object.
        orientation (str): 
            horizontal: Plot v_y over x.
            vertical: Plot v_x over y.
    '''
    data = np.loadtxt(fname)
    dim_x, dim_y = get_dim(data)
    p_data = []
    ax = figure.add_subplot(111)
    if orientation == 'horizontal':
        xlabel = 'x position'
        ylabel = 'y displacement'
        for i in range(dim_y):
            p_data.append(data[dim_x*i:dim_x*(i+1),3])
        for p in p_data:
            ax.plot(range(dim_x), p, '.-')
    elif orientation == 'vertical':
        xlabel = 'y position'
        ylabel = 'x displacement'
        for i in range(dim_x):
            p_data.append(data[i::dim_x,2])
        for p in p_data:
            ax.plot(range(dim_y), p, '.-')            
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def scatter(fname, figure):
    '''Scatter plot.

    Plots v_y over v_x.

    Args:
        fname (str): Name of a file containing vector data.
        figure (matplotlib.figure.Figure): 
            An (empty) Figure object.
    '''
    data = np.loadtxt(fname)
    v_x = data[:,2]
    v_y = data[:,3]
    ax = figure.add_subplot(111)
    ax.scatter(v_x, v_y, label='scatter')
    ax.set_xlabel('x displacement')
    ax.set_ylabel('y displacement')

    
def vector(fname, figure, invert_yaxis=True, **kw):
    '''Display a vector plot.

    Args:
        fname (str): Pathname of a text file containing vector data.
        figure (matplotlib.figure.Figure): 
            An (empty) Figure object.
    '''
    data = np.loadtxt(fname)
    invalid = data[:, 4].astype('bool')
    # tilde means invert:
    valid = ~invalid
    ax = figure.add_subplot(111)
    ax.quiver(data[invalid, 0],
              data[invalid, 1],
              data[invalid, 2],
              data[invalid, 3],
              color='r',
              label='invalid', **kw)
    ax.quiver(data[valid, 0],
              data[valid, 1],
              data[valid, 2],
              data[valid, 3],
              color='b',
              label='valid', **kw)
    if invert_yaxis:
        for ax in figure.get_axes():
            ax.invert_yaxis()
    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    
def pandas_plot(data, parameter, figure):
    '''Display a plot with the pandas plot utility.
    Choose your parameters under plot-tab.
    Plot will be created if you choose the data you want to plot.
    
    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame for plotting.
    parameter : parameter-object
        parameter-object from the plot tab.
    figure : matplotlib.figure.Figure
        An (empty) Figure object.

    Returns
    -------
    None.

    '''
    if parameter['plot_scaling'] == 'None':
        logx, logy, loglog = False, False, False
    elif parameter['plot_scaling'] == 'logx':
        logx, logy, loglog = True, False, False
    elif parameter['plot_scaling'] == 'logy':
        logx, logy, loglog = False, True, False
    elif parameter['plot_scaling'] == 'loglog':
        logx, logy, loglog = False, False, True
        
    ax = figure.add_subplot(111)
    
    xlim = None
    ylim = None
    
    try:
        xlim = (int(list(parameter['plot_xlim'].split(','))[0]),
            int(list(parameter['plot_xlim'].split(','))[1]))
    except:       
        print('No Values or wrong syntax for x-axis limitation.')
    try:
        ylim = (int(list(parameter['plot_ylim'].split(','))[0]),
            int(list(parameter['plot_ylim'].split(','))[1]))
    except:
        print('No Values or wrong syntax for y-axis limitation.')
    
    for i in list(data.columns.values):
        data[i] = data[i].astype(float)
        
    if parameter['plot_type'] == 'hist':
        data_hist = data[parameter['y_data']]
        data_hist.plot.hist(by = parameter['y_data'],
                       bins = int(parameter['plot_bins']), 
                       title = parameter['plot_title'],
                       grid = parameter['plot_grid'],
                       legend = parameter['plot_legend'],
                       logx = logx,
                       logy = logy,
                       loglog = loglog,
                       xlim = xlim,
                       ylim = ylim,
                       ax = ax)
    else:
        data.plot(x = parameter['x_data'], 
              y = parameter['y_data'], 
              kind = parameter['plot_type'], 
              title = parameter['plot_title'], 
              grid = parameter['plot_grid'], 
              legend = parameter['plot_legend'],
              logx = logx, 
              logy = logy , 
              loglog = loglog, 
              xlim = xlim,
              ylim = ylim,
              ax = ax)
    
def get_dim(array):
    '''Computes dimension of vector data.

    Assumes data to be organised as follows (example):
    x  y  v_x v_y
    16 16 4.5 3.2
    32 16 4.3 3.1
    16 32 4.2 3.5
    32 32 4.5 3.2

    Args:
        array (np.array): Flat numpy array.

    Returns:
        (tuple): Dimension of the vector field (x, y).
    '''
    return(len(set(array[:, 0])),
           len(set(array[:, 1])))

                      
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Plot vector data.')
    parser.add_argument('--plot_type',
                        type=str,
                        required=False,
                        choices=['histogram',
                                 'profiles',
                                 'vector',
                                 'scatter'],
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
    fig = Figure()
    if args.plot_type=='histogram':
        histogram(args.fname,
                  fig,
                  quantity=args.quantity,
                  bins=args.bins,
                  log_y=args.log_y)
    elif args.plot_type=='profiles':
        profiles(args.fname,
                 fig,
                 orientation=args.orientation)
    elif args.plot_type=='vector':
        vector(args.fname,
               fig,
               invert_yaxis=args.invert_yaxis)
    elif args.plot_type=='scatter':
        scatter(args.fname, fig)
    plt.show()

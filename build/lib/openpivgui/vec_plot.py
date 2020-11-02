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
from copy import copy
from matplotlib.figure import Figure


def histogram(fname, figure, quantity, bins, log_y):
    '''Plot an histogram.

    Plots an histogram of the specified quantity.

    Parameters
    ----------
    fname : str
        A filename containing vector data.
    figure : matplotlib.figure.Figure
        An (empty) Figure object.
    quantity : str
        Either v (abs v), v_x (x-component) or v_y (y-component).
    bins : int
         Number of bins (bars) in the histogram.
    log_scale : boolean
        Use logaritmic vertical axis.
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
    ax.set_title(parameter['plot_title'])


def profiles(data, figure, orientation):
    '''Plot velocity profiles.

    Line plots of the velocity component specified.

    Parameters
    ----------
    fname : str
        A filename containing vector data.
    figure : matplotlib.figure.Figure 
        An (empty) Figure object.
    orientation : str 
        horizontal: Plot v_y over x.
        vertical: Plot v_x over y.
    '''
    data = data.to_numpy().astype(np.float)
    
    dim_x, dim_y = get_dim(data)
    
    p_data = []
    
    ax = figure.add_subplot(111)
    
    if orientation == 'horizontal':
        xlabel = 'x position'
        ylabel = 'y displacement'
        
        for i in range(dim_y):
            p_data.append(data[dim_x*i:dim_x*(i+1),3])
        #print(p_data[-1])
        for p in p_data:
            #print(len(p))
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
    ax.set_title(parameter['plot_title'])


def scatter(data, figure):
    '''Scatter plot.

    Plots v_y over v_x.

    Parameters
    ----------
    fname : str
        Name of a file containing vector data.
    figure : matplotlib.figure.Figure 
        An (empty) Figure object.
    '''
    data = data.to_numpy()
    
    v_x = data[:,2]
    v_y = data[:,3]
    
    ax = figure.add_subplot(111)
    
    ax.scatter(v_x, v_y, label='scatter')
    
    ax.set_xlabel('x displacement')
    ax.set_ylabel('y displacement')

    
def vector(data, parameter, figure, invert_yaxis=True, valid_color='blue', 
           invalid_color='red', **kw):
    '''Display a vector plot.

    Parameters
    ----------
    fname : str
        Pathname of a text file containing vector data.
    figure : matplotlib.figure.Figure 
        An (empty) Figure object.
    '''
    data = data.to_numpy().astype(np.float)

    try:
        invalid = data[:, 4].astype('bool')
    except:
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
    '''Display a contour plot    

    Parameters
    ----------
    data : pandas.DataFrame
        Data to plot.
    parameter : openpivgui.OpenPivParams
        Parameter-object.
    figure : matplotlib.figure.Figure
       An (empty) Figure object.
    '''
    # figure for subplot
    ax = figure.add_subplot(111)
    # iteration to set value types to float
    for i in list(data.columns.values):
        data[i] = data[i].astype(float)
    # calculate absolute velocity and add it in a new column in data    
    data['abs'] = (data.vx**2 + data.vy**2)**0.5
    
    # pivot table for contour function    
    data_pivot = data.pivot(index = 'y',
                            columns = 'x',
                            values = 'abs')
    # try to get limits, if not possible set to None
    try:
        vmin = float(parameter['vmin'])
    except:
        vmin = None
    try:
        vmax = float(parameter['vmax'])
    except:
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
    if parameter['color_map'] == 'None':
        colormap = None
    else:
        colormap = parameter['color_map']
    # set contour plot to the variable fig to add a colorbar 
    fig = ax.contourf(data_pivot.columns, 
                data_pivot.index, 
                data_pivot.values, 
                levels = levels, 
                cmap = colormap,
                vmin = vmin,
                vmax = vmax)
    # set the colorbar to the variable cb to add a description
    cb = plt.colorbar(fig, ax=ax)
    # description to the contour lines
    cb.ax.set_ylabel('Velocity [m/s]')
    # labels for the axes
    ax.set_xlabel('x-position')
    ax.set_ylabel('y-position')
    # plot title from the GUI
    ax.set_title(parameter['plot_title'])
    
def streamlines(data, parameter, figure):
    '''Display a streamline plot.    

    Parameters
    ----------
    data : pandas.DataFrame
        Data to plot.
    parameter : openpivgui.OpenPivParams
        Parameter object.
    figure : matplotlib.figure.Figure
        An (empty) Figure object.
    '''
    ax = figure.add_subplot(111)
    
    # make sure all values are from type float
    for i in list(data.columns.values):
        data[i] = data[i].astype(float)
        
    # get density for streamline plot.
    try:    
        density = (float(list(parameter['streamline_density'].split(','))[0]),
            float(list(parameter['streamline_density'].split(','))[1]))
    except:
        density = float(parameter['streamline_density'])
        
    # Choosing the correct colormap
    if parameter['color_map'] == 'None':
        colormap = None
    else:
        colormap = parameter['color_map']
        
    # pivot table for streamline plot
    data_vx = data.pivot(index = 'y',
                         columns = 'x',
                         values = 'vx')
    data_vy = data.pivot(index = 'y',
                         columns = 'x',
                         values = 'vy')

    # choosing data for the colormap
    if parameter['streamlines_color'] == 'vx':
        color_values = data_vx.values
    elif parameter['streamlines_color'] == 'vy':
        color_values = data_vy.values
    else:
        color_values = (data_vx.values**2+data_vy.values**2)**0.5
    
    # try to create streamline plot. If values are not equally spaced the 
    # exception will space the values equally (mean difference is 
    # calculated.)          

    try:
        fig = ax.streamplot(data_vx.columns,
                  data_vx.index,
                  data_vx.values,
                  data_vy.values,
                  density = density,   
                  color = color_values,
                  cmap = colormap, 
                  integration_direction = parameter['integrate_dir'],
                  linewidth = parameter['vec_width'])
    except:
        # get dimension of the DataFrame
        dim = [len(set(data.x)), len(set(data.y))]
        
        # calculate mean difference for x and y values
        diff = [round(np.mean(
            [data.x[i+1]-data.x[i] for i in range(dim[0]-1)]),6), 
            round(np.mean([data.y[dim[0]*(i+1)]-data.y[dim[0]*i] 
                            for i in range(dim[1]-1)]),6)]
        
        # this list is initialized with starting values and will be added by 
        # equally spaced values.
        cache = [round(copy(data.x[0]),6), round(copy(data.y[0]),6)]
        
        # nested lists with equally spaced coordinates
        coordinates = [[],[]]
        
        # loop for calculating the new x data
        j=1
        for i in range(1,len(data)):
            if i == dim[0]*j:
                coordinates[0].append(round(cache[0],6))
                cache[0] = coordinates[0][0]
                j+=1
            else:
                coordinates[0].append(round(cache[0],6))
                cache[0]+=diff[0]
        coordinates[0].append(round(cache[0],6))
            
        # loop for calculating the new y data
        j=1
        for i in range(len(data)):
            if i == dim[0]*j:
                cache[1]+=diff[1]
                coordinates[1].append(round(cache[1],6))
                j+=1
            else:
                coordinates[1].append(round(cache[1],6))
                
        # overwrite the old x and y values with the new ones
        data.x = coordinates[0]
        data.y = coordinates[1]
        
        # create new pivot tables for streamline plot
        data_vx = data.pivot(index='y', columns='x', values='vx')
        data_vy = data.pivot(index='y', columns='x', values='vy')
        
        # choosing data for the colormap
        if parameter['streamlines_color'] == 'vx':
            color_values = data_vx.values
        elif parameter['streamlines_color'] == 'vy':
            color_values = data_vy.values
        else:
            color_values = (data_vx.values**2+data_vy.values**2)**0.5
            
        # new streamline plot with equally spaced coordinates
        fig = ax.streamplot(data_vx.columns,
                            data_vx.index,
                            data_vx.values,
                            data_vy.values,
                            density = density,
                            color = color_values,
                            cmap = colormap,
                            integration_direction = parameter['integrate_dir'],
                            linewidth = parameter['vec_width'])
    # add colorbar   
    cb = plt.colorbar(fig.lines, ax=ax)
    cb.ax.set_ylabel('Velocity [m/s]')
    
    # add diagram options    
    ax.set_xlabel('x-position')
    ax.set_ylabel('y-position')
    ax.set_title(parameter['plot_title'])
        
    
def pandas_plot(data, parameter, figure):
    '''Display a plot with the pandas plot utility.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Data to plot.
    parameter : openpivgui.OpenPivParams
        Parameter-object.
    figure : matplotlib.figure.Figure
        An (empty) figure.

    Returns
    -------
    None.

    '''
    # set boolean for chosen axis scaling
    if parameter['plot_scaling'] == 'None':
        logx, logy, loglog = False, False, False
    elif parameter['plot_scaling'] == 'logx':
        logx, logy, loglog = True, False, False
    elif parameter['plot_scaling'] == 'logy':
        logx, logy, loglog = False, True, False
    elif parameter['plot_scaling'] == 'loglog':
        logx, logy, loglog = False, False, True
    # add subplot    
    ax = figure.add_subplot(111)
    # set limits initially to None
    xlim = None
    ylim = None
    # try to set limits, if not possible (no entry) --> None
    try:
        xlim = (float(list(parameter['plot_xlim'].split(','))[0]),
            float(list(parameter['plot_xlim'].split(','))[1]))
    except:  
        pass
        #print('No Values or wrong syntax for x-axis limitation.')
    try:
        ylim = (float(list(parameter['plot_ylim'].split(','))[0]),
            float(list(parameter['plot_ylim'].split(','))[1]))
    except:
        pass
        #print('No Values or wrong syntax for y-axis limitation.')
    # iteration to set value types to float
    for i in list(data.columns.values):
        data[i] = data[i].astype(float)
        
    if parameter['plot_type'] == 'histogram':
        # get column names as a list for comparing with chosen histogram
        # quantity
        col_names = list(data.columns.values)
        # if loop for histogram quantity
        if parameter['histogram_quantity'] == 'v_x':
            data_hist = data[col_names[2]]
        elif parameter['histogram_quantity'] == 'v_y':
            data_hist = data[col_names[3]]
        elif parameter['histogram_quantity'] == 'v':
            data_hist = (data[col_names[2]]**2 + data[col_names[3]]**2)**0.5
        # histogram plot
        ax.hist(data_hist,
                bins = int(parameter['histogram_bins']),
                label = parameter['histogram_quantity'],
                log = logy,
                range = xlim,
                histtype = parameter['histogram_type'],
                )
        ax.grid(parameter['plot_grid'])
        ax.legend()
        ax.set_xlabel('velocity [m/s]')
        ax.set_ylabel('number of vectors')
        ax.set_title(parameter['plot_title'])
    else:
        data.plot(x = parameter['u_data'], 
              y = parameter['v_data'], 
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

    Parameters
    ----------
    array : np.array
        Flat numpy array.

    Returns
    -------
    tuple
        Dimension of the vector field (x, y).
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

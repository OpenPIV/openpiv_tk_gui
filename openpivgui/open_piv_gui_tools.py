#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Methods for reuse within the OpenPivGui project.'''

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

import os
import math
import numpy as np

def str2list(s):
    '''Parses a string representation of a list.

    Args:
        s (str): String containing comma separated values.
                 Example:
                 ('img01.png', 'img02.png')

    Returns:
        []
    '''
    return([t.strip("' ") for t in s.strip('(),').split(',')])


def str2dict(s):
    '''Parses a string representation of a dictionary.

    Args:
        s (str): Comma separated list of colon separated key value pairs.
                 Example:
                 ('key1: value1', 'key2: value2')
    '''
    d = {}
    l = str2list(s)
    for elem in l:
        key, value = elem.split(':')
        key.strip(' ')
        value.strip(' ')
        d.update({key: value})
    return(d)


def create_save_vec_fname(path=os.getcwd(),
                          basename=None,
                          postfix='',
                          count=-1,
                          max_count=9):
    '''Assembles a valid absolute path for saving vector data.

    Kwargs:
        path (str): Directory pass. Default: Working directory.
        basename (str): Prefix. Default: None.
        postfix (str): Postfix. Dfault: None.
        count (int): Counter for numbering filenames. 
                     Default: -1 (no number)
        max_count (int): Highest number to expect. Used for generating 
                         leading zeros. Default: 9 (no leading zeros).
    '''
    if count == -1:
        num = ''
    else:
        num = str(count).zfill(math.ceil(math.log10(max_count)))
    if basename is None:
        basename = os.path.basename(path)
    elif basename == '':
        basename = 'out'
    return(os.path.dirname(path) +
           os.sep +
           basename.split('.')[0] +
           postfix +
           num +
           '.vec')

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

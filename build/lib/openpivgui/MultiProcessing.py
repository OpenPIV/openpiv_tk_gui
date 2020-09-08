#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Parallel Processing of PIV images.'''

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

import openpiv.tools as piv_tls
import openpiv.process as piv_prc
import openpiv.windef as piv_wdf
import openpiv.validation as piv_vld
import openpiv.filters as piv_flt
import openpiv.smoothn as piv_smt
import numpy as np

from openpivgui.open_piv_gui_tools import create_save_vec_fname


class MultiProcessing(piv_tls.Multiprocesser):
    '''Parallel processing, based on the corrresponding OpenPIV class.

    Do not run from the interactive shell or within IDLE! Details at:
    https://docs.python.org/3.6/library/multiprocessing.html#using-a-pool-of-workers

    Args:
        params (OpenPivParams): A parameter object.
    '''

    def __init__(self, params):
        '''Standard initialization method.

        For separating GUI and PIV code, the output filenames are
        generated here and not in OpenPivGui. In this way, this object
        might also be useful independently from OpenPivGui.
        '''
        self.p = params
        self.files_a = self.p['fnames'][::2]
        self.files_b = self.p['fnames'][1::2]
        self.n_files = len(self.files_a)
        self.save_fnames = []
        postfix = '_piv_' + self.p['evaluation_method'] + '_'
        for n in range(self.n_files):
            self.save_fnames.append(
                create_save_vec_fname(path=self.files_a[n],
                                      basename=self.p['vec_fname'],
                                      postfix=postfix,
                                      count=n,
                                      max_count=self.n_files))
        if self.n_files == 0:
            raise ValueError(
                'Please provide image filenames.')
        if self.n_files != len(self.files_b):
            raise ValueError(
                'Please provide an equal number of A and B images.')

    def get_save_fnames(self):
        '''Return a list of result filenames.

        Returns:
            str[]: List of filenames with resulting PIV data.
        '''
        return(self.save_fnames)

    def process(self, args):
        '''Process chain as configured in the GUI.

        Args:
            args (tuple): Tuple as expected by the inherited run method.
                          file_a (str) -- image file a
                          file_b (str) -- image file b
                          counter (int) -- index pointing to an element 
                                           of the filename list
        '''
        file_a, file_b, counter = args
        frame_a = piv_tls.imread(file_a)
        frame_b = piv_tls.imread(file_b)
        if self.p['evaluation_method'] == 'extd':
            u, v, sig2noise = piv_prc.extended_search_area_piv(
                frame_a.astype(np.int32), frame_b.astype(np.int32),
                window_size      = self.p['corr_window'],
                search_area_size = self.p['search_area'],
                subpixel_method  = self.p['subpixel_method'],
                overlap          = self.p['overlap'],
                dt               = self.p['dt'],
                sig2noise_method = self.p['sig2noise_method'])
            x, y = piv_prc.get_coordinates(
                image_size       = frame_a.shape,
                window_size      = self.p['corr_window'],
                overlap          = self.p['overlap'])
            piv_tls.save(x, y, u, v, sig2noise, self.save_fnames[counter])
            print('Processed {} and {}.'.format(file_a, file_b))
        elif self.p['evaluation_method'] == 'widim':
            mark = np.ones(frame_a.shape, dtype=np.int32)
            overlap_ratio = self.p['overlap'] / self.p['corr_window']
            x, y, u, v, mask = piv_prc.WiDIM(
                frame_a.astype(np.int32), frame_b.astype(np.int32),
                mark,
                min_window_size  = self.p['corr_window'],
                overlap_ratio    = overlap_ratio,
                coarse_factor    = self.p['coarse_factor'],
                dt               = self.p['dt'],
                subpixel_method  = self.p['subpixel_method'],
                sig2noise_method = self.p['sig2noise_method'])
            piv_tls.save(x, y, u, v, mask, self.save_fnames[counter])
            print('Processed {} and {}.'.format(file_a, file_b))
        elif self.p['evaluation_method'] == 'windef':
            # evaluation first pass
            corr_window_0 = self.p['corr_window'] * 2**self.p['coarse_factor']
            overlap_0     = self.p['overlap']     * 2**self.p['coarse_factor']
            x, y, u, v, sig2noise = piv_wdf.first_pass(
                frame_a.astype(np.int32), frame_b.astype(np.int32),
                corr_window_0,
                overlap_0,
                self.p['coarse_factor'] + 1, # number of iterations
                correlation_method = 'circular', # 'circular' or 'linear'
                subpixel_method    = self.p['subpixel_method'])
            print('Finished first pass for {} and {}.'.format(file_a, file_b))
            # validation first pass
            u, v, mask = piv_vld.local_median_val(
                u, v,
                u_threshold = self.p['local_median_threshold'],
                v_threshold = self.p['local_median_threshold'])
            # filtering first pass
            u, v = piv_flt.replace_outliers(
                u, v,
                method = 'localmean')
            print('Median filtering first pass result of {} and {}.'.format(file_a, file_b))
            # evaluation of all other passes
            for i in range(self.p['coarse_factor']):
                corr_window = self.p['corr_window'] * 2**(self.p['coarse_factor']-i-1)
                overlap     = self.p['overlap']     * 2**(self.p['coarse_factor']-i-1)
                x, y, u, v, sig2noise, mask = piv_wdf.multipass_img_deform(
                    frame_a.astype(np.int32), frame_b.astype(np.int32),
                    corr_window,
                    overlap,
                    self.p['coarse_factor'] + 1, # number of iterations
                    i+1,                         # current iteration
                    x, y, u, v,
                    correlation_method = 'circular',
                    subpixel_method    = self.p['subpixel_method'],
                    do_sig2noise       = True)
                print('Finished {} pass for {} and {}.'.format(i+2, file_a, file_b))
            # scaling
            u = u/self.p['dt']
            v = v/self.p['dt']
            # saving
            piv_tls.save(x, y, u, v, sig2noise, self.save_fnames[counter])

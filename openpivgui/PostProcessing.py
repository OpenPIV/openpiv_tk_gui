#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Post Processing for OpenPIVGui.'''

from openpivgui.open_piv_gui_tools import create_save_vec_fname, save
import openpiv.smoothn as piv_smt
import openpiv.filters as piv_flt
import openpiv.validation as piv_vld
import openpiv.tools as piv_tls
import numpy as np
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


class PostProcessing():
    '''Post Processing routines for vector data.

    Parameters
    ----------
    params : openpivgui.OpenPivParams
        Parameter object.
    '''

    def __init__(self, params):
        '''Initialization method.'''
        self.p = params

        global delimiter
        delimiter = self.p['delimiter']
        if delimiter == 'tab':
            delimiter = '\t'
        if delimiter == 'space':
            delimiter = ' '

    def sig2noise(self):
        '''Filter vectors based on the signal to noise threshold.

        See:
            openpiv.validation.sig2noise_val()
        '''
        result_fnames = []
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u, v, mask = piv_vld.sig2noise_val(
                data[:, 2], data[:, 3], data[:, 5],
                threshold=self.p['sig2noise_threshold'])

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
        return(result_fnames)

    def global_std(self):
        '''Filters vectors by a multiple of the standard deviation.

        See Also
        --------
        openpiv.validation.global_std()
        '''
        result_fnames = []
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u, v, mask = piv_vld.global_std(
                data[:, 2], data[:, 3],
                std_threshold=self.p['global_std_threshold'])
            save_fname = create_save_vec_fname(
                path=f,
                postfix='_std_thrhld')
            save(data[:, 0],
                 data[:, 1],
                 u, v,
                 data[:, 4] + mask,
                 data[:, 5],
                 save_fname,
                 delimiter=delimiter)
            result_fnames.append(save_fname)
        return(result_fnames)

    def global_val(self):
        '''Filter vectors based on a global min-max threshold.

        See:
            openpiv.validation.global_val()
        '''
        result_fnames = []
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u, v, mask = piv_vld.global_val(
                data[:, 2], data[:, 3],
                u_thresholds=(self.p['MinU'], self.p['MaxU']),
                v_thresholds=(self.p['MinV'], self.p['MaxV']))
            save_fname = create_save_vec_fname(
                path=f,
                postfix='_glob_thrhld')
            save(data[:, 0],
                 data[:, 1],
                 u, v,
                 data[:, 4] + mask,
                 data[:, 5],
                 save_fname,
                 delimiter=delimiter)
            result_fnames.append(save_fname)
        return(result_fnames)

    def local_median(self):
        '''Filter vectors based on a local median threshold.

        See Also
        --------
        openpiv.validation.local_median_val()
        '''
        result_fnames = []
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u, v, mask = piv_vld.local_median_val(
                data[:, 2], data[:, 3],
                u_threshold=self.p['local_median_threshold'],
                v_threshold=self.p['local_median_threshold'],
                size=self.p['local_median_size'])
            save_fname = create_save_vec_fname(
                path=f,
                postfix='_med_thrhld')
            save(data[:, 0],
                 data[:, 1],
                 u, v,
                 data[:, 4] + mask,
                 data[:, 5],
                 save_fname,
                 delimiter=delimiter)
            result_fnames.append(save_fname)
        return(result_fnames)

    def repl_outliers(self):
        '''Replace outliers.'''
        result_fnames = []
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u, v = piv_flt.replace_outliers(
                np.array([data[:, 2]]), np.array([data[:, 3]]),
                method=self.p['repl_method'],
                max_iter=self.p['repl_iter'],
                kernel_size=self.p['repl_kernel'])
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
        return(result_fnames)

    def smoothn_r(self):
        '''Smoothn postprocessing results.'''
        result_fnames = []
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u, _, _, _ = piv_smt.smoothn(
                data[:, 2], s=self.p['smoothn_val'], isrobust=self.p['robust'])
            v, _, _, _ = piv_smt.smoothn(
                data[:, 3], s=self.p['smoothn_val'], isrobust=self.p['robust'])
            save_fname = create_save_vec_fname(
                path=f,
                postfix='_smthn')
            save(data[:, 0],
                 data[:, 1],
                 u, v,
                 data[:, 4],
                 data[:, 5],
                 save_fname,
                 delimiter=delimiter)
            result_fnames.append(save_fname)
        return(result_fnames)

    def average(self):
        '''Average all results.'''
        '''data = np.loadtxt(self.p['fnames'][0])
        u = data[:, 2]
        v = data[:, 3]
        for i, f in enumerate(self.p['fnames']):
            data = np.loadtxt(f)
            u += data[:,2]; u /= 2
            v += data[:,3]; v /= 2
        save_fname = create_save_vec_fname(
            path=self.p['fnames'][0],
            postfix='_average')
        piv_tls.save(data[:, 0],
                     data[:, 1],
                     u, v,
                     data[:, 4],
                     save_fname,
                     delimiter = delimiter)
        print(f)
        return(save_fname)'''
        return('Averaging of vectors fileds is not implemented.')

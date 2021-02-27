#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Parallel Processing of PIV images.'''

from openpivgui.PreProcessing import gen_background, process_images
from openpivgui.open_piv_gui_tools import create_save_vec_fname, _round
import numpy as np
import time
import openpiv.smoothn as piv_smt
import openpiv.scaling as piv_scl
import openpiv.filters as piv_flt
import openpiv.validation as piv_vld
import openpiv.windef as piv_wdf
import openpiv.pyprocess as piv_prc
import openpiv.preprocess as piv_pre
import openpiv.tools as piv_tls
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


class MultiProcessing(piv_tls.Multiprocesser):
    '''Parallel processing, based on the corrresponding OpenPIV class.

    Do not run from the interactive shell or within IDLE! Details at:
    https://docs.python.org/3.6/library/multiprocessing.html#using-a-pool-of-workers

    Parameters
    ----------
    params : OpenPivParams
        A parameter object.
    '''

    def __init__(self, params):
        '''Standard initialization method.

        For separating GUI and PIV code, the output filenames are
        generated here and not in OpenPivGui. In this way, this object
        might also be useful independently from OpenPivGui.
        '''
        self.p = params

        # generate background if needed
        if self.p['background_subtract'] == True and self.p['background_type'] != 'minA - minB':
            self.background = gen_background(self.p)
        else:
            self.background = None

        # custom image sequence with (1+[1+x]), (2+[2+x]) and ((1+[1+x]), (3+[3+x]))
        if self.p['sequence'] == '(1+2),(2+3)':
            step = 1
        else:
            step = 2
        self.files_a = self.p['fnames'][0::step]
        self.files_b = self.p['fnames'][self.p['skip']::step]

        # making sure files_a is the same length as files_b
        diff = len(self.files_a)-len(self.files_b)
        if diff != 0:
            for i in range(diff):
                self.files_a.pop(len(self.files_b))
        print('Number of a files: ' + str(len(self.files_a)))
        print('Number of b files: ' + str(len(self.files_b)))

        if self.p['swap_files']:
            self.files_a, self.files_b = self.files_b, self.files_a

        self.n_files = len(self.files_a)
        self.save_fnames = []
        
        evaluation_method = 'FFT'
        
        postfix = '_piv_' + evaluation_method + '_'
        for n in range(self.n_files):
            self.save_fnames.append(
                create_save_vec_fname(path=self.files_a[n],
                                      basename=self.p['vec_fname'],
                                      postfix=postfix,
                                      count=n,
                                      max_count=self.n_files))
        
        # setup widgets so the user could still use the GUI when processing
        self.parameter = {}
        for key in self.p.param:
            key_type = self.p.type[key]
            if key_type not in ['labelframe', 
                                'sub_labelframe',
                                'h-spacer', 
                                'sub_h-spacer',
                                'dummy'
                               ]:
                if 1030 < self.p.index[key] < 4000:
                    self.parameter[key] = self.p[key]

    def get_save_fnames(self):
        '''Return a list of result filenames.

        Returns:
            str[]: List of filenames with resulting PIV data.
        '''
        return(self.save_fnames)

    def get_num_frames(self):
        '''Return the amount of image pairs that will be processed.
        
        Returns:
            int: The number of image pairs to be processed'''
        return(len(self.files_a))
    
    def process(self, args):
        '''Process chain as configured in the GUI.

        Parameters
        ----------
        args : tuple
            Tuple as expected by the inherited run method:
            file_a (str) -- image file a
            file_b (str) -- image file b
            counter (int) -- index pointing to an element of the filename list
        '''
        file_a, file_b, counter = args
        frame_a = piv_tls.imread(file_a)
        frame_b = piv_tls.imread(file_b)

        # Smoothning script borrowed from openpiv.windef
        s = self.p['smoothn_val']

        def smoothn(u, s):
            s = s
            u, _, _, _ = piv_smt.smoothn(
                u, s=s, isrobust=self.p['robust'])
            return(u)

        # delimiters placed here for safety
        delimiter = self.p['separator']
        if delimiter == 'tab':
            delimiter = '\t'
        if delimiter == 'space':
            delimiter = ' '

        # preprocessing
        print('\nPre-pocessing image pair: {}'.format(counter+1))
        if self.p['background_subtract'] == True and self.p['background_type'] == 'minA - minB':
            self.background = gen_background(self.p, frame_a, frame_b)

        frame_a = frame_a.astype(np.int32)
        frame_a = process_images(self.p, frame_a,
                                 background=self.background)
        frame_b = frame_b.astype(np.int32)
        frame_b = process_images(self.p, frame_b,
                                 background=self.background)
        
        print('Evaluating image pair: {}'.format(counter + 1))
        
        # evaluation first pass
        start = time.time()
        passes = 1
        if self.parameter['custom_windowing']: # setup custom windowing if selected
            corr_window_0   = self.parameter['corr_window_1']
            overlap_0       = self.parameter['overlap_1']
            for i in range(2, 8):
                if self.parameter['pass_%1d' % i]:
                    passes += 1
                else:
                    break;
                        
        else:
            passes = self.parameter['coarse_factor']
            if self.parameter['grid_refinement'] == 'all passes' and self.parameter['coarse_factor'] != 1: 
                corr_window_0 = self.parameter['corr_window'] * \
                    2**(self.parameter['coarse_factor'] - 1)
                overlap_0     = self.parameter['overlap'] * \
                    2**(self.parameter['coarse_factor'] - 1)

            # Refine all passes after first when there are more than 1 pass.    
            elif self.parameter['grid_refinement'] == '2nd pass on' and self.parameter['coarse_factor'] != 1: 
                corr_window_0 = self.parameter['corr_window'] * \
                    2**(self.parameter['coarse_factor'] - 2)
                overlap_0     = self.parameter['overlap'] * \
                    2**(self.parameter['coarse_factor'] - 2)

            # If >>none<< is selected or something goes wrong, the window size would remain the same.    
            else:
                corr_window_0 = self.parameter['corr_window']
                overlap_0     = self.parameter['overlap']
        overlap_percent = overlap_0 / corr_window_0 
        sizeX = corr_window_0
        
        u, v, sig2noise = piv_wdf.extended_search_area_piv(
            frame_a.astype(np.int32),
            frame_b.astype(np.int32),
            window_size = corr_window_0,
            overlap = overlap_0,
            search_area_size = corr_window_0,
            width = self.parameter['s2n_mask'],
            subpixel_method        = self.parameter['subpixel_method'],
            sig2noise_method       = self.parameter['sig2noise_method'],
            correlation_method     = self.parameter['corr_method'],
            normalized_correlation = self.parameter['normalize_correlation'])

        x, y = piv_wdf.get_coordinates(frame_a.shape,
                                       corr_window_0,
                                       overlap_0)
        
        # validating first pass
        mask = np.full_like(x, 0)
        if self.parameter['fp_vld_global_threshold']:
            u, v, Mask = piv_vld.global_val(
                u, v,
                u_thresholds=(self.parameter['fp_MinU'], self.parameter['fp_MaxU']),
                v_thresholds=(self.parameter['fp_MinV'], self.parameter['fp_MaxV']))
            mask += Mask # consolidate effects of mask
            
        if self.parameter['fp_local_med']:
            u, v, Mask = piv_vld.local_median_val(
                u, v,
                u_threshold = self.parameter['fp_local_med'],
                v_threshold = self.parameter['fp_local_med'],
                size        = self.parameter['fp_local_med_size'])
            mask += Mask
            
        if self.parameter['adv_repl']:
            u, v = piv_flt.replace_outliers(
                    u, v,
                    method      = self.parameter['adv_repl_method'],
                    max_iter    = self.parameter['adv_repl_iter'],
                    kernel_size = self.parameter['adv_repl_kernel'])
        print('Validated first pass result of image pair: {}.'.format(counter+1)) 

        # smoothning  before deformation if 'each pass' is selected
        if self.parameter['smoothn_each_pass']:
            if self.parameter['smoothn_first_more']:
                s *=2
            u = smoothn(u, s); v = smoothn(v, s) 
            print('Smoothned pass 1 for image pair: {}.'.format(counter+1))
            s = self.parameter['smoothn_val1']

        print('Finished pass 1 for image pair: {}.'.format(counter+1))
        print("window size: "   + str(corr_window_0))
        print('overlap: '       + str(overlap_0), '\n')  

        # evaluation of all other passes
        if passes != 1:
            iterations = passes - 1
            for i in range(2, passes + 1):
                # setting up the windowing of each pass
                if self.parameter['custom_windowing']:
                    corr_window = self.parameter['corr_window_%1d' % i]
                    overlap = int(corr_window * overlap_percent)
                       
                else:
                    if self.parameter['grid_refinement'] == 'all passes' or \
                        self.parameter['grid_refinement'] == '2nd pass on':
                        corr_window = self.parameter['corr_window'] * 2**(iterations - 1)
                        overlap     = self.parameter['overlap'] * 2**(iterations - 1) 

                    else:
                        corr_window = self.parameter['corr_window']
                        overlap     = self.parameter['overlap']
                sizeX = corr_window

                # translate settings to windef settings object
                piv_wdf_settings = piv_wdf.Settings()
                piv_wdf_settings.correlation_method  = self.parameter['corr_method']
                piv_wdf_settings.normalized_correlation = self.parameter['normalize_correlation']
                piv_wdf_settings.windowsizes = (corr_window,) * (passes+1)
                piv_wdf_settings.overlap = (overlap,) * (passes+1)
                piv_wdf_settings.num_iterations = passes
                piv_wdf_settings.subpixel_method = self.parameter['subpixel_method']
                piv_wdf_settings.deformation_method  = self.parameter['deformation_method']
                piv_wdf_settings.interpolation_order = self.parameter['interpolation_order']
                piv_wdf_settings.sig2noise_validate  = True,
                piv_wdf_settings.sig2noise_method  = self.parameter['sig2noise_method']
                piv_wdf_settings.sig2noise_mask  = self.parameter['s2n_mask']

                # do the correlation
                x, y, u, v, sig2noise, mask = piv_wdf.multipass_img_deform(
                    frame_a.astype(np.int32),
                    frame_b.astype(np.int32),
                    i, # current iteration
                    x, y, u, v,
                    piv_wdf_settings)
                
                # validate other passes
                if self.parameter['sp_vld_global_threshold']:
                    u, v, Mask = piv_vld.global_val(
                        u, v,
                        u_thresholds=(self.parameter['sp_MinU'], self.parameter['sp_MaxU']),
                        v_thresholds=(self.parameter['sp_MinV'], self.parameter['sp_MaxV']))
                    mask += Mask # consolidate effects of mask
                
                if self.parameter['sp_vld_global_threshold']:
                    u, v, Mask = piv_vld.global_std(
                        u, v, 
                        std_threshold=self.parameter['sp_std_threshold'])
                    mask += Mask
                    
                if self.parameter['sp_local_med_validation']:
                    u, v, Mask = piv_vld.local_median_val(
                        u, v,
                        u_threshold = self.parameter['sp_local_med'],
                        v_threshold = self.parameter['sp_local_med'],
                        size        = self.parameter['sp_local_med_size'])  
                    mask += Mask
                
                if self.parameter['adv_repl']:
                    u, v = piv_flt.replace_outliers(
                        u, v,
                        method      = self.parameter['adv_repl_method'],
                        max_iter    = self.parameter['adv_repl_iter'],
                        kernel_size = self.parameter['adv_repl_kernel'])
                print('Validated pass {} of image pair: {}.'.format(i,counter+1))             
                           
                # smoothning each individual pass if 'each pass' is selected
                if self.parameter['smoothn_each_pass']:
                    u = smoothn(u, s); v = smoothn(v, s) 
                    print('Smoothned pass {} for image pair: {}.'.format(i,counter+1))

                print('Finished pass {} for image pair: {}.'.format(i,counter+1))
                print("window size: "   + str(corr_window))
                print('overlap: '       + str(overlap), '\n')
                iterations -= 1

        if self.p['flip_u']:
            u = np.flipud(u)

        if self.p['flip_v']:
            v = np.flipud(v)

        if self.p['invert_u']:
            u *= -1

        if self.p['invert_v']:
            v *= -1

                
        # scaling
        u = u/self.parameter['dt']
        v = v/self.parameter['dt']
        x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.parameter['scale']) 
        end = time.time() 
        
        # save data to file.
        out = np.vstack([m.ravel() for m in [x, y, u, v, mask, sig2noise]])
        np.savetxt(self.save_fnames[counter], out.T, fmt='%8.4f', delimiter=delimiter)
        print('Processed image pair: {}'.format(counter+1))
        
        sizeY = sizeX
        sizeX = ((int(frame_a.shape[0] - sizeX) // (sizeX - (sizeX * overlap_percent))) + 1)
        sizeY = ((int(frame_a.shape[1] - sizeY) // (sizeY - (sizeY * overlap_percent))) + 1)
        
        time_per_vec = _round((((end - start) * 1000) / ((sizeX * sizeY) - 1)), 3)
        
        print('Process time: {} second(s)'.format((_round((end - start), 3))))
        print('Number of vectors: {}'.format(int((sizeX * sizeY) - 1)))
        print('Time per vector: {} millisecond(s)'.format(time_per_vec))
        
        
        
        
        
        
        
       

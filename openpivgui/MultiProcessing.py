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
import openpiv.preprocess as piv_pre
import openpiv.process as piv_prc
import openpiv.windef as piv_wdf
import openpiv.validation as piv_vld
import openpiv.filters as piv_flt
import openpiv.scaling as piv_scl
import openpiv.smoothn as piv_smt

import numpy as np

from scipy.ndimage.filters import gaussian_filter, gaussian_laplace
from openpivgui.open_piv_gui_tools import create_save_vec_fname
from openpivgui.PreProcessing import process_images


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
        # custom image sequence. Step effects first set and jump effects second set.
        # Ex: step=2, jump=2 yields (1+2),(3+4)    
        self.files_a = self.p['fnames'][0::self.p['step']]
        self.files_b = self.p['fnames'][self.p['skip']::self.p['step']]
        
        test = self.files_a[0] # testing if images are loaded. The previous one did not work for some reason
        ext = test.split('.')[-1]
        if ext not in ['bmp', 'tiff', 'tif', 'jpeg', 'png', 'pgm']:
            raise ValueError(
                'Please provide image pairs.')
        
        diff = len(self.files_a)-len(self.files_b) # making sure files_a is the same length as files_b
        if diff != 0:
            for i in range (diff):
                self.files_a.pop(len(self.files_b))
        
        print('Number of a files: ' + str(len(self.files_a)))
        print('Number of b files: ' + str(len(self.files_b)))

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

    def get_save_fnames(self):
        '''Return a list of result filenames.

        Returns:
            str[]: List of filenames with resulting PIV data.
        '''
        return(self.save_fnames)
        
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
        
        '''preprocessing'''
        if self.p['ROI'] == True:
            frame_a =  frame_a[self.p['roi-ymin']:self.p['roi-ymax'],self.p['roi-xmin']:self.p['roi-xmax']]
            frame_b =  frame_b[self.p['roi-ymin']:self.p['roi-ymax'],self.p['roi-xmin']:self.p['roi-xmax']]
            
        if self.p['dynamic_mask']==True:    
            frame_a = piv_pre.dynamic_masking(frame_a,method=self.p['dynamic_mask_type'],
                                                 filter_size=self.p['dynamic_mask_size'],
                                                 threshold=self.p['dynamic_mask_threshold'])   
            frame_b = piv_pre.dynamic_masking(frame_b,method=self.p['dynamic_mask_type'],
                                                 filter_size=self.p['dynamic_mask_size'],
                                                 threshold=self.p['dynamic_mask_threshold'])
            print('Warning: Dynamic masking is still in testing and is not recommended for use.')
        
        if self.p['gaussian_filter'] == True:
            frame_a = gaussian_filter(frame_a, sigma=self.p['gf_sigma'])
            frame_b = gaussian_filter(frame_b, sigma=self.p['gf_sigma'])

        # Not yet implemented and tested.    
        #if self.p['gaussian_laplace'] == True:
        #    frame_a = gaussian_laplace(frame_a, sigma=self.p['gl_sigma'])
        #    frame_b = gaussian_laplace(frame_b, sigma=self.p['gl_sigma'])
        frame_a = (frame_a).astype(np.int32)  # this conversion is needed to avoid major conflicts from float64 data types
        frame_b = (frame_b).astype(np.int32)
        
        frame_a = process_images(self.p, frame_a)
        frame_b = process_images(self.p, frame_b)
        
        frame_a = (frame_a).astype(np.int32) 
        frame_b = (frame_b).astype(np.int32)
        
        def smoothn(u): #Smoothning script borrowed from openpiv.windef
            u,dummy_u1,dummy_u2,dummy_u3=piv_smt.smoothn(u,s=self.p['smoothn_val'], isrobust=self.p['robust'])
            return(u) 
        
        if self.p['smoothn'] == True: # This is to allow controllable smoothning in windef evaluation
            smoothn_type=self.p['smoothn_type']
        else:
            smoothn_type='none'
        
        '''evaluation'''
        if self.p['evaluation_method'] == 'extd':
            print('Processing image pair: {}.'.format(counter+1))
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
            
            if self.p['smoothn'] == True:
                u = smoothn(u)
                v = smoothn(v) 
                print('Finished smoothning data for image pair: {}.'.format(counter+1))
            
            x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.p['scale'])
            if self.p['smoothn_each_pass'] == True:
                u = smoothn(u)
                v = smoothn(v) 
                print('Finished smoothning results for image pair: {}.'.format(counter+1))
            
            x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.p['scale'])
            
            if self.p['flip_u'] == True:
                u = -u
                
            if self.p['flip_v'] == True:
                v = -v
            piv_tls.save(x, y, u, v, sig2noise, self.save_fnames[counter])
            print('Processed image pair: {}.'.format(counter+1))
            
        elif self.p['evaluation_method'] == 'widim':
            print('Processing image pair: {}'.format(counter+1))
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
            
            if self.p['smoothn'] == True:
                u = smoothn(u); v = smoothn(v) 
                print('Finished smoothning data for image pair: {}.'.format(counter+1))
            
            x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.p['scale'])
            if self.p['smoothn_each_pass'] == True:
                u = smoothn(u); v = smoothn(v) 
                print('Finished smoothning results for image pair: {}.'.format(counter+1))
            
            x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.p['scale'])
            
            if self.p['flip_u'] == True:
                u = -u
                
            if self.p['flip_v'] == True:
                v = -v
            piv_tls.save(x, y, u, v, mask, self.save_fnames[counter])
            print('Processed image pair: {}.'.format(counter+1))
            
        elif self.p['evaluation_method'] == 'windef':
            # evaluation first pass
            print('Processing image pair: {}'.format(counter+1))
            corr_window_0 = self.p['corr_window'] * 2**self.p['coarse_factor']
            overlap_0     = self.p['overlap']     * 2**self.p['coarse_factor']
            x, y, u, v, sig2noise = piv_wdf.first_pass(
                frame_a.astype(np.int32), frame_b.astype(np.int32),
                corr_window_0,
                overlap_0,
                self.p['coarse_factor'] + 1, # number of iterations
                correlation_method = self.p['corr_method'], # 'circular' or 'linear'
                subpixel_method    = self.p['subpixel_method'])
            print('Finished first pass for image pair: {}.'.format(counter+1))
            
            # validation first pass
            u, v, mask = piv_vld.local_median_val(
                u, v,
                u_threshold = self.p['local_median_threshold'],
                v_threshold = self.p['local_median_threshold'])
            # filtering first pass
            u, v = piv_flt.replace_outliers(
                u, v,
                method = 'localmean')
            print('Median filtering first pass result of image pair: {}.'.format(counter+1))
            
            # smoothning  before deformation if 'each pass' is selected

            if self.p['smoothn_each_pass'] == True:
                u = smoothn(u); v = smoothn(v) 
                print('Finished smoothning first pass result for image pair: {}.'.format(counter+1))
                
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
                    correlation_method = self.p['corr_method'],
                    subpixel_method    = self.p['subpixel_method'],
                    do_sig2noise       = True)
                
                # smoothning each individual pass if 'each pass' is selected

                if self.p['smoothn_each_pass'] == True:
                    u = smoothn(u); v = smoothn(v) 
                    print('Finished smoothning pass {} for image pair: {}.'.format(i+2,counter+1))
                print('Finished pass {} for image pair: {}.'.format(i+2,counter+1))
            
            # smoothning last pass only if 'last pass' is chosen. This could be removed by doing some extra work.
            if self.p['smoothn'] == True and smoothn_type == 'last pass':
                u = smoothn(u); v = smoothn(v) 
                print('Finished smoothning pass {} for image pair: {}.'.format(i+2,counter+1))
            
            # scaling
            u = u/self.p['dt']
            v = v/self.p['dt']
            x,y,u,v=piv_scl.uniform(x,y,u,v, scaling_factor=self.p['scale'])
            

            # saving

            if self.p['flip_u'] == True:
                u = -u
                
            if self.p['flip_v'] == True:
                v = -v

            piv_tls.save(x, y, u, v, sig2noise, self.save_fnames[counter])
            print('Processed image pair: {}.'.format(counter+1))

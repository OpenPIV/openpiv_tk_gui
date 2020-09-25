#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Post Processing for OpenPIVGui.'''

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
import numpy as np
import openpiv.preprocess as piv_pre
from scipy.ndimage.filters import gaussian_filter
from skimage import exposure, filters, img_as_uint, util
'''Pre Processing chain for image arrays.

Parameters
----------
params : openpivgui.OpenPivParams
    Parameter object.
'''
    
def process_images(self, img):
    self.p = self
    '''Starting the preprocess chain'''
    img = img_as_uint(img)  # this conversion is needed to avoid major conflicts from float64 data types.
    
    if self.p['ROI'] == True:
        img =  img[self.p['roi-ymin']:self.p['roi-ymax'],self.p['roi-xmin']:self.p['roi-xmax']]
    
    if self.p['invert'] == True:
        img = img_as_uint(img)
        img = img_as_uint(util.invert(img))
        
    if self.p['dynamic_mask'] == True:    
        img = piv_pre.dynamic_masking(img,method=self.p['dynamic_mask_type'],
                                             filter_size=self.p['dynamic_mask_size'],
                                             threshold=self.p['dynamic_mask_threshold'])
    
    if self.p['gaussian_filter'] == True:
        img = gaussian_filter(img, sigma=self.p['gf_sigma'])
        
    if self.p['CLAHE'] == True or self.p['un_sharp'] == True:
        if self.p['un_sharp_first'] == False:    
            if self.p['CLAHE'] == True:
                img = img_as_uint(img)
                img = img_as_uint(exposure.equalize_adapthist(img, 
                                                              kernel_size=self.p['CLAHE_kernel'], 
                                                              clip_limit = self.p['CLAHE_clip']))

            if self.p['un_sharp'] == True:
                img = img_as_uint(img)
                img = img_as_uint(filters.unsharp_mask(img, 
                                                       radius = self.p['us_radius'], 
                                                       amount = self.p['us_amount']))
        
        else:
            if self.p['un_sharp'] == True:
                img = img_as_uint(img)
                img = img_as_uint(filters.unsharp_mask(img, 
                                                       radius = self.p['us_radius'], 
                                                       amount = self.p['us_amount']))
                
            if self.p['CLAHE'] == True:
                img = img_as_uint(img)
                img = img_as_uint(exposure.equalize_adapthist(img, 
                                                              kernel_size=self.p['CLAHE_kernel'], 
                                                              clip_limit = self.p['CLAHE_clip']))
    return(img)
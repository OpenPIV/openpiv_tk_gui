#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Post Processing for OpenPIVGui.'''

from skimage import exposure, filters, util
from scipy.ndimage.filters import gaussian_filter
import openpiv.preprocess as piv_pre
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

'''Pre Processing chain for image arrays.

Parameters
----------
params : openpivgui.OpenPivParams
    Parameter object.
'''


def gen_background(self, image1=None, image2=None):
    self.p = self
    images = self.p['fnames'][self.p['starting_frame']: self.p['ending_frame']]
    # This needs more testing. It creates artifacts in the correlation for images not selected in the background.
    if self.p['background_type'] == 'global min':
        background = piv_tls.imread(self.p['fnames'][self.p['starting_frame']])
        maximum = background.max()
        background = background / maximum
        background *= 255
        for im in images:
            # the original image is already included, so skip it in the for loop
            if im == self.p['fnames'][self.p['starting_frame']]:
                pass
            else:
                image = piv_tls.imread(im)
                maximum = image.max()
                image = image / maximum
                image *= 255
                background = np.min(np.array([background, image]), axis=0)
        return(background)

    elif self.p['background_type'] == 'global mean':
        images = self.p['fnames'][self.p['starting_frame']
            : self.p['ending_frame']]
        background = piv_tls.imread(self.p['fnames'][self.p['starting_frame']])
        maximum = background.max()
        background = background / maximum
        background *= 255
        for im in images:
            # the original image is already included, so skip it in the for loop
            if im == self.p['fnames'][self.p['starting_frame']]:
                pass
            else:
                image = piv_tls.imread(im)
                maximum = image.max()
                image = image / maximum
                image *= 255
                background += image
        background /= (self.p['ending_frame'] - self.p['starting_frame'])
        return(background)

    elif self.p['background_type'] == 'minA - minB':
        # normalize image1 and image2 intensities to [0,255]
        maximum1 = image1.max()
        maximum2 = image2.max()
        image1 = image1 / maximum1
        image2 = image2 / maximum2
        image1 *= 255
        image2 *= 255
        background = np.min(np.array([image2, image1]), axis=0)
        return(background)

    else:
        print('Background algorithm not implemented.')


def process_images(self, img, background=None):
    self.p = self
    '''Starting the pre-processing chain'''

    # normalize image to [0, 1] float
    maximum = img.max()
    img = img / maximum
    resize = self.p['img_int_resize']

    if self.p['invert']:
        img = util.invert(img)

    if self.p['background_subtract']:
        try:
            img *= 255
            img -= background
            img[img < 0] = 0  # values less than zero are set to zero
            img = img / 255
        except:
            print('Could not subtract background. Ignoring background subtraction.')

    if self.p['crop_ROI']:  # ROI crop done after background subtraction to avoid image shape issues
        crop_x = (int(list(self.p['crop_roi-xminmax'].split(','))[0]),
                  int(list(self.p['crop_roi-xminmax'].split(','))[1]))
        crop_y = (int(list(self.p['crop_roi-yminmax'].split(','))[0]),
                  int(list(self.p['crop_roi-yminmax'].split(','))[1]))
        img = img[crop_y[0]:crop_y[1], crop_x[0]:crop_x[1]]

    #if self.p['dynamic_mask']: # needs more testing
    #    img = piv_pre.dynamic_masking(img,
    #                                  method=self.p['dynamic_mask_type'],
    #                                  filter_size=self.p['dynamic_mask_size'],
    #                                  threshold=self.p['dynamic_mask_threshold'])

    if self.p['CLAHE'] == True or self.p['high_pass_filter'] == True:
        if self.p['CLAHE_first']:
            if self.p['CLAHE']:
                if self.p['CLAHE_auto_kernel']:
                    kernel = None
                else:
                    kernel = self.p['CLAHE_kernel']

                img = exposure.equalize_adapthist(img,
                                                  kernel_size=kernel,
                                                  clip_limit=0.01,
                                                  nbins=256)

            if self.p['high_pass_filter']:
                low_pass = gaussian_filter(img, sigma = self.p['hp_sigma'])
                img -= low_pass
                
                if self.p['hp_clip']:
                    img[img < 0] = 0

        else:
            if self.p['high_pass_filter']:
                low_pass = gaussian_filter(img, sigma = self.p['hp_sigma'])
                img -= low_pass
                
                if self.p['hp_clip']:
                    img[img < 0] = 0

            if self.p['CLAHE']:
                if self.p['CLAHE_auto_kernel']:
                    kernel = None
                else:
                    kernel = self.p['CLAHE_kernel']

                img = exposure.equalize_adapthist(img,
                                                  kernel_size=kernel,
                                                  clip_limit=0.01,
                                                  nbins=256)

    # simple intensity capping
    if self.p['intensity_cap_filter']:
        upper_limit = np.mean(img) + self.p['ic_mult'] * img.std()
        img[img > upper_limit] = upper_limit

    # simple intensity clipping
    if self.p['intensity_clip']:
        img *= resize
        lower_limit = self.p['intensity_clip_min']
        img[img < lower_limit] = 0
        img /= resize

    if self.p['gaussian_filter']:
        img = gaussian_filter(img, sigma=self.p['gf_sigma'])

    return(img * resize)

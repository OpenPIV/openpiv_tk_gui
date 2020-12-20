import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import openpiv.tools as piv_tls

# A lot of optimization could be done in this file.


# check number of images, image types, and window sizing
def check_PIVprocessing(self):
    self.p = self
    '''Error checking'''
    # making sure there are 2 or more files loaded
    message = 'Please import two or more image files'
    if len(self.p['fnames']) < 2:
        if self.p['warnings']:
            messagebox.showwarning(title='Error Message',
                                   message=message)
        raise Exception(message)

    # checking for images
    message = "Please supply image files in 'bmp', 'tiff', 'tif', 'TIF', 'jpg', 'jpeg', 'png', 'pgm'."
    test = self.p['fnames'][0]
    ext = test.split('.')[-1]
    if ext not in ['bmp', 'tiff', 'tif', 'TIF', 'jpg', 'jpeg', 'png', 'pgm']:
        if self.p['warnings']:
            messagebox.showwarning(title='Error Message',
                                   message=message)
        raise Exception(message)

    # checking interrogation window sizes in an inefficent manner (for now)
    test = piv_tls.imread(test)
    if 8 != 1: # too lazy to fix spacing
        message = ('Please lower your starting interrogation window size.')
        if self.p['custom_windowing']:
            # making sure that the initial window is not too large
            if ((test.shape[0] / self.p['corr_window_1']) < 3 or
                    (test.shape[1] / self.p['corr_window_1']) < 3):
                if self.p['warnings']:
                    messagebox.showwarning(title='Error Message',
                                           message=message)
                raise ValueError(message)
            # making sure each pass has a decreasing interrogation window
            Message = 'Plase make sure that the custom windowing is decresing with each pass.'
            window = self.p['corr_window_1']
            for i in range(2, 8):
                if self.p['pass_%1d' % i]:
                    if window >= self.p['corr_window_%1d' % i]:
                        window = self.p['corr_window_%1d' % i]

                    else:
                        if self.p['warnings']:
                            messagebox.showwarning(title='Error Message',
                                                   message=Message)
                        raise ValueError(Message)
                else:
                    break
        else:
            # checking the windowing for different multi pass setups
            message = ('Please lower your starting interrogation window size or ' +
                       'change multipass/grid refinement settings.')
            if self.p['grid_refinement'] == 'all passes' and self.p['coarse_factor'] != 1:
                if ((test.shape[0] / (self.p['corr_window'] * 2**(self.p['coarse_factor'] - 1))) < 2.5 or
                        (test.shape[1] / (self.p['corr_window'] * 2**(self.p['coarse_factor'] - 1))) < 2.5):
                    if self.p['warnings']:
                        messagebox.showwarning(title='Error Message',
                                               message=message)
                    raise ValueError(message)

            elif self.p['grid_refinement'] == '2nd pass on' and self.p['coarse_factor'] != 1:
                if ((test.shape[0] / (self.p['corr_window'] * 2**(self.p['coarse_factor'] - 2))) < 2.5 or
                        (test.shape[1] / (self.p['corr_window'] * 2**(self.p['coarse_factor'] - 2))) < 2.5):
                    if self.p['warnings']:
                        messagebox.showwarning(title='Error Message',
                                               message=message)
                    raise ValueError(message)

            else:
                if ((test.shape[0] / self.p['corr_window']) < 3 or
                        (test.shape[1] / self.p['corr_window']) < 3):
                    if self.p['warnings']:
                        messagebox.showwarning(title='Error Message',
                                               message=message)
                    raise ValueError(message)


def check_processing(self):  # check for threads
    self = self
    message = 'Please stop all threads/processes to start processing.'
    checker = 0
    # check if any threads are alive
    try:
        if self.processing_thread.is_alive():
            if self.p['warnings']:
                messagebox.showwarning(title='Error Message',
                                       message=message)
            checker += 1
    except:
        pass

    try:
        if self.postprocessing_thread.is_alive():
            if self.p['warnings']:
                messagebox.showwarning(title='Error Message',
                                       message=message)
            checker += 1
    except:
        pass
    # if a thread is alive, an error shall be raised
    if checker != 0:
        # raising errors did not work in try statement for some reason
        raise Exception(message)


def check_postprocessing(self):  # check for file types
    self.p = self
    test = self.p['fnames'][0]  # testing if .vec or .txt files are loaded.
    ext = test.split('.')[-1]
    if ext not in ('txt', 'vec'):
        message = 'Please provide ASCI-II .vec or .txt files.'
        if self.p['warnings']:
            messagebox.showwarning(title='Error Message',
                                   message=message)
        raise Exception(message)

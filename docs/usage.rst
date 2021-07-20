Usage
=====

Video Tutorial
--------------

Learn how to use and extend OpenPivGui in less than eight minutes in a `video tutorial <https://video.fh-muenster.de/Panopto/Pages/Viewer.aspx?id=309dccc2-af58-44e0-8cd3-ab9500c5b7f4>`_.

Workflow
--------

1. Press the button »open directory« and choose a directory that contains some PIV images.
2. To inspect the images, click on the links in the file-list on the right side of the OpenPivGui window.
3. Walk through the riders, select the desired functions, and edit the corresponding parameters.
4. Press »start processing« to start the evaluation.
5. Inspect the results by clicking on the links in the file-list.
6. Use the »back« and »forward« buttons to inspect intermediate results. Use the »back« and »forward« buttons also to list the image files again, and to repeat the evaluation.
7. Use »dump settings« to document your project. You can recall the settings anytime by pressing »load settings«. The lab-book entries are also restored from the settings file.

Adaption
--------

First, get the source code. There are two possibilities:

1. Clone the git repository::

    git clone https://github.com/OpenPIV/openpiv_tk_gui.git

2. Find out, where pip3 placed the source scripts and edit them in place::

    pip3 show openpivgui

In both cases, cd into the subdirectory ``openpivgui`` and find the main scripts to edit:

- ``OpenPivParams.py``
- ``OpenPivGui.py``
		
Usually, there are two things to do:

1. Adding new variables and a corresponding widgets to enable users to modify its values.
2. Adding a new method (function).

Adding new variables
^^^^^^^^^^^^^^^^^^^^

Open the script ``OpenPivParams.py``. Find the method ``__init__()``. There, you find a variable, called ``default`` of type dict. All widgets like checkboxes, text entries, and option menus are created based on the content of this dictionary. 

By adding a dictionary element, you add a variable. A corresponding widget is automatically created. Example::
  
    'corr_window':             # key
         [3020,                # index
         'int',                # type
         32,                   # value
         (8, 16, 32, 64, 128), # hints
         'window size',        # label
         'Size in pixel.'],    # help

In ``OpenPivGui.py``, you access the value of this variable via ``p['corr_window']``. Here, ``p`` is the instance name of an ``OpenPivParams`` object. Typing::

    print(self.p['corr_window'])

will thus result in::

    32

The other fields are used for widget creation:

- index: An index of 3xxx will place the widget on the third rider (»PIV«).
- type:
    + ``None``: Creates a new notebook rider.
	+ ``bool``: A checkbox will be created.
	+ ``str[]``: Creates a listbox.
	+ ``text``: Provides a text area.
	+ ``float``, ``int``, ``str``: An entry widget will be created.
- hints: If hints is not ``None``, an option menu is provided with ``hints`` (tuple) as options.
- label: The label next to the manipulation widget.
- help: The content of this field will pop up as a tooltip, when the mouse is moved over the widget.

Adding a new method
^^^^^^^^^^^^^^^^^^^

Open the script ``OpenPivGui``. There are two main possibilities, of doing something with the newly created variables:

1. Extend the existing processing chain.

2. Create a new method.
   
Extend existing processing chain
""""""""""""""""""""""""""""""""

Find the function definition ``start_processing()``. Add another ``if`` statement and some useful code.

Create a new method
"""""""""""""""""""

Find the function definition ``__init_buttons()``. Add something like::

    ttk.Button(f,
               text='button label',
               command=self.new_func).pack(
    		       side='left', fill='x')

Add the new function::

    def new_func(self):
        # do something useful here
        pass

Add_In_Handler
--------------
Alternatively, an Add_In can be programmed that requires less detailed knowledge about the rest of the code. Within these Add_Ins new variables and or methods can be implemented within one file and without manipulating the main code. The structure of the individual Add_In types will be explained below. (Examplary Addins are stored in the Addin folder)

1. Create a new python file (e.g. user_function_addin_other.py)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: The last part of the file name is used to load the Addin in the right position in source code. (possible scopes are: general, preprocessing, postprocessing, plotting and other) Addins for the main process are not possible yet. Take care of splitting the file name by underscores.

2. Structure of an example addin file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	In this section the main structure of an AddIn will become clear as well as the difference between the different scopes. First of all, the components to be completed for each Add_In will be explained.
	
	**2.1 Main structure**
	
		- import the AddIn super class in the first line of your Add_In::
		
			from openpivgui.Add_Ins.AddIn import AddIn
		
		- (perform the imports for your Add_In if necessary)
		- declare a class that has the same name as your Python file and inherits from the class AddIn, e.g.::
			
			class user_function_addin_other(AddIn):
			
		- Give your plugin a name as well as a three-letter abbreviation, this can be done by::
		
			add_in_name = "user_function_addin (ufa)"
		
		- Write a description of your plugin, this will be visible in the Add_In_Handler GUI, and increase the understanding of your plugin.::
		
			addin_tip = "This is the description of the user function addin which is still missing now"
		
		- Declare your variables as described above, make sure your variables start with the three letter abbreviation to avoid confusion::
		
			# variables
		        #########################################################
		        # Place additional variables in the following sections. #
		        # Widgets are created automatically. Don't care about   #
		        # saving and restoring - new variables are included     #
		        # automatically.                                        #
		        #                                                       #
		        # e.g.                                                  #
		        #   **abbreviation**_**variable_name** =                #
		        #       [**id over super group**, **variable_type**,    #
		        #        **standard_value**,**hint**, **label**         #
		        #        **tool tip**                                   #
		        #########################################################
			
			variables = {'ufa_addin_user_func':
                     			[10000, None, None, None, 'User-Function', None],
                 		     'ufa_addin_user_func_def':
                     			[10010, 'text', example_user_function, None, None, None]}
		
		- The last thing to do is to write the Init method, this initializes the Super class, and will make the difference between the different plugins.::
		
			    def __init__(self, gui):
        			super().__init__()
		
	**2.2 Extras of the various AddIns**
		In the main structure it was already explained how variables are added, these are loaded into the OpenPivParam object as already before the implementation of the Add_In_Handler and will appear in the GUI for example as checkbox or text field. However, this does not affect the process yet. 
		
		First, we will take a look at the effect on **preprocessing**.
		Now you need to write a method that has the image as a parameter, manipulates it, and returns it to postprocessing at the end of the method.::
			
			    def advanced_filtering_method(self, img, GUI):
				resize = GUI.p['img_int_resize']
				if GUI.p['afa_CLAHE'] == True or GUI.p['afa_high_pass_filter'] == True:
				    if GUI.p['afa_CLAHE_first']:
					if GUI.p['afa_CLAHE']:
					    if GUI.p['afa_CLAHE_auto_kernel']:
						kernel = None
					    else:
						kernel = GUI.p['afa_CLAHE_kernel']

					    img = exposure.equalize_adapthist(img,
									      kernel_size=kernel,
									      clip_limit=0.01,
									      nbins=256)

					if GUI.p['afa_high_pass_filter']:
					    low_pass = gaussian_filter(img,
								       sigma=GUI.p['afa_hp_sigma'])
					    img -= low_pass

					    if GUI.p['afa_hp_clip']:
						img[img < 0] = 0

				    else:
					if GUI.p['afa_high_pass_filter']:
					    low_pass = gaussian_filter(img,
								       sigma=GUI.p['afa_hp_sigma'])
					    img -= low_pass

					    if GUI.p['afa_hp_clip']:
						img[img < 0] = 0

					if GUI.p['afa_CLAHE']:
					    if GUI.p['afa_CLAHE_auto_kernel']:
						kernel = None
					    else:
						kernel = GUI.p['afa_CLAHE_kernel']

					    img = exposure.equalize_adapthist(img,
									      kernel_size=kernel,
									      clip_limit=0.01,
									      nbins=256)

				# simple intensity capping
				if GUI.p['afa_intensity_cap_filter']:
				    upper_limit = np.mean(img) + GUI.p['afa_ic_mult'] * img.std()
				    img[img > upper_limit] = upper_limit

				# simple intensity clipping
				if GUI.p['afa_intensity_clip']:
				    img *= resize
				    lower_limit = GUI.p['afa_intensity_clip_min']
				    img[img < lower_limit] = 0
				    img /= resize

				if GUI.p['afa_gaussian_filter']:
				    img = gaussian_filter(img, sigma=GUI.p['afa_gf_sigma'])

				return img
				
		The second thing to do is to tell the GUI that this method exists. This is done in the Init method as follows. (Make sure you use the preprocessing_methods dictionary.)::
		    
		    	def __init__(self, gui):
			    super().__init__()
			    # has to be the method which is implemented above
			    gui.preprocessing_methods.update(
		      		{"advanced_filtering_addin_preprocessing":
				 self.advanced_filtering_method})
		
		Another maipulable scope is the **postprocessing**, this will be considered in the following.
		For this purpose, a new method must be written, which can look like the following::
		
			    def sig2noise(self, gui, delimiter):
				"""Filter vectors based on the signal to noise threshold.

				See:
				    openpiv.validation.sig2noise_val()
				"""
				result_fnames = []
				for i, f in enumerate(gui.p['fnames']):
				    data = np.loadtxt(f)
				    u, v, mask = piv_vld.sig2noise_val(
					data[:, 2], data[:, 3], data[:, 5],
					threshold=gui.p['s2n_sig2noise_threshold'])

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
				return result_fnames
				
		Also the inclusion in the GUI is similar to the one above.
		In the list passed here, the first entry describes whether the plugin targets validation or post-processing. The second contains the name of the boolean value of the checkbox and the third the method to be executed once the boolean value is true.::
		
			    def __init__(self, gui):
				super().__init__()
				# has to be the method which is implemented above
				gui.postprocessing_methods.update(
				    {"sig2noise_addin_postprocessing":
				     ['validation', 's2n_vld_sig2noise', self.sig2noise]})
		
Testing
^^^^^^^

Overwrite the original scripts in the installation directory (locate the installation directory by ``pip3 show openpivgui``) with your altered version and test it. There are test images in the `OpenPivGui Github repository <https://github.com/OpenPIV/openpiv_tk_gui/tree/master/tst_img>`_, if needed.

	
Reusing code
------------

The openpivgui modules and classes can be used independently from the GUI. The can be used in other scipts or jupyter notebooks and some can be called from the command line directly.
	
Troubleshooting
---------------

I can not install OpenPivGui.
    Try ``pip`` instead of ``pip3`` or try the ``--user`` option::

        pip install --user openpivgui

    Did you read the error messages? If there are complaints about missing packages, install them prior to OpenPivGui::

        pip3 install missing-package

Something is not working properly.
    Ensure, you are running the latest version::

        pip3 install --upgrade openpivgui

Something is still not working properly.
    Start OpenPivGui from the command line::

        python3 -m openpivgui.OpenPivGui

    Check the command line for error messages. Do they provide some useful information?

I can not see a file list.
    The GUI may hide some widgets. Toggle to full-screen mode or try to check the »compact layout« option on the »General« rider.

I do not understand, how the »back« and »forward« buttons work.
    All output files are stored in the same directory as the input files. To display a clean list of a single processing step, the content of the working directory can be filtered. The »back« and »forward« buttons change the filter. The filters are defined as a list of comma separated regular expressions in the variable »navigation pattern« on the »General« tab.

    Examples:

    ``png$`` Show only files that end on the letters »png«.

    ``piv_[0-9]+\.vec$`` Show only files that end on ``piv_``, followed by a number and ``.vec``. These are usually the raw results.

    ``sig2noise_repl\.vec$`` Final result after applying a validation based on the signal to noise ratio and filling the gaps.

    You can learn more about regular expressions by reading the `Python3 Regular Expression HOWTO <https://docs.python.org/3/howto/regex.html#regex-howto>`_.

I get »UnidentifiedImageError: cannot identify image file«
    This happens, when a PIV evaluation is started and the file list contains vector files instead of image files. Press the »back« button until the file list contains image files.

I get »UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 85: invalid start byte«
    This happens, when PIV evaluation is NOT selected and the file list contains image files. Either press the »back button« until the file list contains vector files or select »direct correlation« on the PIV rider.

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

Alternatively one might write an Addin. Therefore the following steps have to be done:
(Examplary Addins are stored in the Addin folder)

1. Create a new python file (e.g. user_function_addin_other.py)

.. note:: The last part of the file name is used to load the Addin in the right position in source code. (possible scopes are: general, preprocessing, postprocessing, plotting and other) Addins for the main process are not possible yet. Take care of splitting the file name by underscores.

2. Structure of an example addin file::

	# first of all one have to import the AddIn class which is the super class of each new Addin
	from openpivgui.Add_Ins.AddIn import AddIn
	# than one can import packages needed in the Addin e.g.
	import numpy as np
	
	# here one might implement functions that do not need attributes from class e.g.
	def user_function(gui):
	    """
		Executes user function.
	    """
	    gui.get_settings()
	    print(gui.p['ufa_addin_user_func_def'])
	    exec(gui.p['ufa_addin_user_func_def'])


	def create_user_function_buttons(gui, menu):
	    menu.add_command(label='Show User Function',
			     command=lambda: gui.selection(10))
	    menu.add_command(label='Execute User Function',
			     command=lambda: user_function(gui))

	# Take care class has the same name as the python file 
	class user_function_addin_other(AddIn):
	    """
		Blueprint for developing own methods and inserting own variables
		into the already existing PIV GUI via the AddIn system
	    """

	    # description for the Add_In_Handler textarea
	    addin_tip = "This is the description of the example addin"

	    # has to be the add_in_name and its abbreviation
	    add_in_name = "user_function_addin_other (ufa)"
	    
	    # new method which is stored in the parameter dictionary 
	    example_user_function = '''
		filelistbox = gui.get_filelistbox()
		properties  = gui.p
		import pandas as pd

		def textbox(title='Title', text='Hello!'):
		    from tkinter.scrolledtext import ScrolledText
		    from tkinter.constants import END
		    frame = tk.Tk()
		    frame.title(title)
		    textarea = ScrolledText(frame, height=10, width=80)
		    textarea.insert(END, text)
		    textarea.pack(fill='x', side='left', expand=True)
		    textarea.focus()
		    frame.mainloop()

		try:
		    index = filelistbox.curselection()[0]
		except IndexError:
		    messagebox.showerror(
			title="No vector file selected.",
			message="Please select a vector file " +
				"in the file list and run again."
		    )
		else:
		    f = properties['fnames'][index]
		    names=('x','y','v_x','v_y','var')
		    df = pd.read_csv(f, sep='\t', header=None, names=names)
		    print(df.describe())
		    textbox(title='Statistics of {}'.format(f),
			    text=df.describe()
		    )
		'''
	    # variables
	    #########################################################
	    # Place additional variables in the following sections. #
	    # Widgets are created automatically. Don't care about   #
	    # saving and restoring - new variables are included     #
	    # automatically. The structure of the variable dict is  #
	    # the same  as the one described above. 		    #	
	    #                                                       #
	    # e.g.                                                  #
	    #   **abbreviation**_**variable_name** =                #
	    #       [**id over super group**, **variable_type**,    #
	    #        **standard_value**,**hint**, **label**         #
	    #        **tool tip**                                   #
	    #########################################################
	    variables = {
	    	# example variable 
		'ufa_addin_user_func':
                     [10000, None, None, None, 'User-Function', None],
		'ufa_addin_user_func_def':
			[10010, 'text', example_user_function,
                 	 None, None, None]
		}

	    def __init__(self, gui):
	    	# init the super class 
		super().__init__()
		# add buttons and / or methods 
		gui.buttons.update({"user_function_addin_other":
                            create_user_function_buttons})
		# gui.preprocessing_methods.update(
            	# 	{"addinname":
             	# 	self.method name})
		
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

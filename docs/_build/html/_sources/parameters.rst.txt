Parameters
==========

General
-------

.. computron-injection::

   from openpivgui.OpenPivParams import OpenPivParams
   p = OpenPivParams()
   print(p.generate_parameter_documentation(group=p.GENERAL))

Pre-Processing
--------------
   
.. computron-injection::

   from openpivgui.OpenPivParams import OpenPivParams
   p = OpenPivParams()
   print(p.generate_parameter_documentation(group=p.PREPROC))

PIV Evaluation
--------------
   
.. computron-injection::

   from openpivgui.OpenPivParams import OpenPivParams
   p = OpenPivParams()
   print(p.generate_parameter_documentation(group=p.PIVPROC))

Validation
----------
   
.. computron-injection::

   from openpivgui.OpenPivParams import OpenPivParams
   p = OpenPivParams()
   print(p.generate_parameter_documentation(group=p.VALIDATION))

Post-Processing
---------------
   
.. computron-injection::

   from openpivgui.OpenPivParams import OpenPivParams
   p = OpenPivParams()
   print(p.generate_parameter_documentation(group=p.POSTPROC))

Plotting
--------
   
.. computron-injection::

   from openpivgui.OpenPivParams import OpenPivParams
   p = OpenPivParams()
   print(p.generate_parameter_documentation(group=p.PLOTTING))

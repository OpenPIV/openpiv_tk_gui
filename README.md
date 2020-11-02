![Upload Python Package](https://github.com/OpenPIV/openpiv_tk_gui/workflows/Upload%20Python%20Package/badge.svg?event=release)

# A GUI for Open PIV

This graphical user interface provides an efficient workflow for evaluating and postprocessing particle image velocimetry (PIV) images. OpenPivGui relies on the Python libraries provided by the [OpenPIV project](http://www.openpiv.net/).

![Screen shot of the GUI showing a vector plot.](https://raw.githubusercontent.com/OpenPIV/openpiv_tk_gui/master/fig/open_piv_gui_vector_plot.png)

[Installation](#installation)

[Launching](#launching)

[Usage](#usage)

[Video Tutorial](#video_tuturial)

[Documentation](#documentation)

[Contribution](#contribution)


## Installation <a id=installation></a>

You may use Pip to install `OpenPivGui`:

```
pip3 install openpivgui
```

## Launching <a id=launching></a>

Launch `OpenPivGui` by executing:

```
python3 -m openpivgui.OpenPivGui
```

## Usage <a id=usage></a>

1. Press the button »open directory«. Choose a direktory that contains PIV images. Use the »back« or »forward« button to filter the directory content, until there is a list of images in the file list on the right side of the OpenPivGui.
2. To inspect the images, click on  the links in the file-list.
3. Walk through the riders, select the desired functions, and edit the corresponding parameters.
4. Press »start processing« to start the evaluation.
5. Inspect the results by clicking on the links in the file-list.
6. Use the »back« and »forward« buttons to inspect intermediate results.
7. Use »dump settings« to document your project. You can recall the settings anytime by pressing »load settings«.


## Video tutorial <a id=video_tutorial></a>

Learn how to use and extend OpenPivGui [watching a less than eight minute video tutorial](https://video.fh-muenster.de/Panopto/Pages/Viewer.aspx?id=309dccc2-af58-44e0-8cd3-ab9500c5b7f4).


## Documentation <a id=documentation></a>

Find the [detailed documentation on readthedocs.io](https://openpiv-tk-gui.readthedocs.io/en/latest/index.html).


## Contribution <a id=contribution></a>

Contributions are very welcome! Please follow the [step by step guide in the documentation](https://openpiv-tk-gui.readthedocs.io/en/latest/contribution.html).

## Related

Also check out [JPIV](https://eguvep.github.io/jpiv/index.html).

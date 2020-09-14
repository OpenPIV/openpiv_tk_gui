Contribution
============

Contributions are very welcome! Please have the design considerations in mind and follow the step by step guides below.

Design Considerations
---------------------

- The order of parameters and parameter riders in the GUI should represent the flow of data processing (figure).

.. figure:: ./fig/data_flow.svg
    :alt: Data processing flow diagram.
    :figwidth: 100%

    OpenPivGui data processing flow diagram.

- OpenPivGui ist designed for providing a very fast workflow. Don't interrupt this workflow by asking for individual user input, as far as possible. Rather use parameters or algorithms.

- Separate the user interface code from the working code. An OpenPivParams object can be created and used independently from the GUI. Also the vec_plot module or the MultiProcessing class can be called from the command line from another program or Jupyter notebook, independently from the GUI.
  
- The code is designed for developing it together with PIV-experimentalists rather than programmers. Therefore, keep the code as clear and concise as possible, also by resigning from too many user-friendly gimmicks.

- Write your docstrigs in the `Numpy/Scipy style <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

Without Write Access
--------------------

This is the standard procedure of contributing to OpenPivGui.

1. If not done, install Git (platform dependend) and configure it on the command line::

    git config --global user.name "first name surname"
    git config --global user.email "e-mail address"

2. Create a Github account, navigate to the `OpenPivGui Github page <https://github.com/OpenPIV/openpiv_tk_gui>`_ and press the fork button (top right of the page). Github will create a personal online fork of the repository for you.

3. Clone your fork, to get a local copy::

    git clone https://github.com/your_user_name/openpiv_tk_gui.git

4. Your fork is independent from the original (upstream) repository. To be able to sync changes in the upstream repository with your fork later, specify the upstream repository::

    cd openpiv_tk_gui
    git remote add upstream https://github.com/OpenPIV/openpiv_tk_gui.git
    git remote -v

5. Change the code locally, commit the changes::

    git add . 
    git commit -m 'A meaningful comment on the changes.'

6. See, if there are updates in the upstream repository and save them in your local branch upstream/master:::

    git fetch upstream

7. Merge possible upstream changes into your local master branch::

    git merge upstream/master

8. If there are merge conflicts, use ``git status`` and ``git diff`` for displaying them. Git marks conflicts in your files, `as described in the Github documentation on solving merge conflicts <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/resolving-a-merge-conflict-using-the-command-line>`_. After resolving merge conflicts, upload everything::

    git add .
    git commit -m 'A meaningful comment.'
    git push

9. Propose your changes to the upstream developer by creating a pull-request, as described `in the Github documentation for creating a pull-request from a fork <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork>`_. (Basically just pressing the »New pull request« button.)

Good luck!

With Write Access
-----------------

1. If not done, install Git and configure it::

    git config --global user.name "first name surname"
    git config --global user.email "e-mail address"

2. Clone the git repository::

    git clone https://github.com/OpenPIV/openpiv_tk_gui.git

3. Create a new branch and switch over to it::

    cd openpiv_tk_gui
    git branch meaningful-branch-name
    git checkout meaningful-branch-name
    git status

4. Change the code locally and commit changes::

    git add .
    git commit -m 'A meaningful comment on the changes.'

5. Push branch, so everyone can see it::

    git push --set-upstream origin meaningful-branch-name

6. Create a pull request. This is not a Git, but a Github feature, so you must use the Github user-interface, as described in the `Github documentaton on creating a pull request from a branch <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request#creating-the-pull-request>`_.

7. After discussing the changes and possibly additional commits, the feature-branch can be merged into the main branch::

    git checkout master
    git merge meaningful-branch-name

8. Eventually, solve merge conflicts. Use ``git status`` and ``git diff`` for displaying conflicts. Git marks conflicts in your files, `as described in the Github documentation on solving merge conflicts <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/resolving-a-merge-conflict-using-the-command-line>`_.

9. Finally, the feature-branch can safely be removed::

    git branch -d meaningful-branch-name

10. Go to the Github user-interface and also delete the now obsolete online copy of the feature-branch.

Good luck!

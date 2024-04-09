Inputs
~~~~~~~~~~

This flow requires as an input a 'FamilyBaseDataCombinedReport.csv' text file.

location:
- \_02_ModifyFamilyLibraryReloadAdvanced\_Users\YOURUSERNAME\_Input

This flow also requires as an input a 'ChangedFilesTaskList.csv' text file:

Calling python script (PreTaskFileReloadListBuilder) with an argument:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Argument needs to be the fully qualified file path to ChangedFilesTaskList.csv file.
- current default path for this file passt in is:

    - \_02_ModifyFamilyLibraryReloadAdvanced\_Users\YOURUSERNAME\_Input\ChangedFilesTaskList.csv

Change file properties
^^^^^^^^^^^^^^^^^^^^^^^^^^

- file extension: '.csv'
    - file type: comma separated
    - header row: yes
    - first column: family name without file extension
    - second column: contains fully qualified file path to family files
    - third column: family category

Calling python script without any argument:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Script will terminate without processing any family.
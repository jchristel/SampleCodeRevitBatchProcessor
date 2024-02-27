Inputs
~~~~~~~~~~

This flow has a number of optional input which can be of two types.

Calling python script with an argument:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- argument needs to be a directory path
- directory past in needs to contain at least one task file

Calling python script without any argument:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- script will check for task files in 

    - \_01_ModifyFamilyChange\_Users\YOURUSERNAME\Input

No arguments past in and no task files present in pre-defined directory or past in directory:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- script will default to processing the entire library

Task file properties
^^^^^^^^^^^^^^^^^^^^^^^^^^

- file extension: '.task'
    - file type: comma separated
    - header row: no
    - first column: contains fully qualified file path to family files

Delete unwanted shared parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- script will check for file in 

    - \_01_ModifyFamilyChange\_Users\YOURUSERNAME\_Input

    - file name: UnwantedSharedParameterGUIDS.csv
    - file extension: '.csv'
    - file type: comma separated
    - header row: no
    - first column: contains shared parameter name
    - second column: shared parameter GUID

Change shared parameters to project parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- script will check for file in 

    - \_01_ModifyFamilyChange\_Users\YOURUSERNAME\_Input

    - file name: ChangeSharedParameterToFamilyParameter.csv
    - file extension: '.csv'
    - file type: comma separated
    - header row: no
    - first column: shared parameter name
    - second column: family parameter name

Note: parameter storage type, Instance vs type based, parameter grouping are unchanged after the conversion.

Swap shared parameters 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- script will check for file in 

    - \_01_ModifyFamilyChange\_Users\YOURUSERNAME\_Input

    - file name: SharedParameterSwapping.csv
    - file extension: '.csv'
    - file type: comma separated
    - header row: yes
    - column 1: current shared parameter name
    - column 2: new shared parameter name
    - column 3: fully qualified file path of shared parameter file
    - column 4: Is parameter instance (True / False)
    - column 5: parameter grouping name ( refer to module: parameter_grouping)

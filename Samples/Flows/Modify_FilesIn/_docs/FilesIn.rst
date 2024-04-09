#############################################
Files In
#############################################

*******
Summary
*******

The 'File In' flow is aimed at model receiving processes requiring:

- Received Revit and other models to be checked and cleaned up before being used in the project.:
    - Revit files:
        - A purge unused elements is under taken.
        - Worksets of levels / grids / scope boxes / reference planes are checked and if required changed to the default value
        - files are saved under a new file name in the prescribed location (by file )
        - files are saved in a prescribed filing location for record keeping
    - Other model files:
        - Files are saved under a new file name in the prescribed location (by file )
        - Files are saved in a prescribed filing location for record keeping
    

Actions Overview 
----------------

This flow is run through a powershell script which executes:

#. A pre-processing script collecting all Revit file info from source directory.
#. Main Process: No 3 off parallel running sessions of Revit Batch Processor which:
    #. Create a detached copy of the Revit file(s) in a given location. (Revit files are opened with all worksets closed)
        #. Saves file under a new file name
    #. Delete any links from the model ( Optional )
    #. Workset checking and, if required adjusting, of of worksets of levels / grids / scope boxes / reference planes
    #. Create a text file for each new revit file containing meta data for received models tracker in post process

#. A post process which:
    #. Updates file recievd list with latest files received information.
    #. Checks revit batch processor log files for any exceptions


Setup
-----

This chapter describes the flow directory setup.

Directory structure
^^^^^^^^^^^^^^^^^^^

This flow expects the following directory structure to be in place:

├───_docs

├───_LogMarker

├───_Output

├───_sampleFiles

├───_Script

│   └───logs

│   └───utils

├───_SessionData

├───_settings

└───_TaskList


_docs
^^^^^^^^^^^^^^^^^^^

Directory containing flow related documentation.

_LogMarker
^^^^^^^^^^^^^^^^^^^

Directory containing log marker files. Those will be deleted at the end of each flow run.

_Output
^^^^^^^^^^^^^^^^^^^

- empty for this flow

_sampleFiles
^^^^^^^^^^^^^^^^^^^

Any sample files provided. 

_Script
^^^^^^^^^^^^^^^^^^^

The python and powershell scripts of the flow:

- ModifyRevitFileSaveAs.py

    - task script executed by each Revit Batch Processor session

- Post_FilesOut.py

    - the post script executed by each Revit Batch Processor session

- Pre_MarkerFilesTaskList.py

    - the pre process script executed by each Revit Batch Processor session

- settings.py

    - a module containing global variables / settings for this flow

- startAddRevision.ps1

    - The powershell script executing:
        - concurrent Revit Batch Processor sessions

- file_data.csv

    - Revit project meta data file:
        - This is a comma separated text files which contains meta data of the revit files to be processed in the following format:
        - header row: yes
        - column 1: The beginning of the file name as received 
        - column 2: The new file name to be used for the file
        - column 3: The name of the workset where any levels, grids, scope boxes and reference planes are to be moved to
        - column 4: Default revision ie: -  which will be used in revision tracker doc if no revision was identified on the original file name
        - column 5: file extension in format ie: .rvt
        - column 6: Fully qualified directory path to where incoming files are stored for filing only
        - column 7: Fully qualified directory path to where incoming files are stored to be used in live project
        - column 8: This is a comment column


_Script/logs
^^^^^^^^^^^^^^^^^^^

Log files which cover script outputs outside of Revit Batch Processor log files

_settings
^^^^^^^^^^^^^^^^^^^

Location of Revit Batch Processor settings files.

For this flow there is 1 settings files in this folder:

- 1 one single session of Revit Batch Processor (OneA)


_SessionData
^^^^^^^^^^^^^^^^^^^

Directory containing Revit Batch Processor session data files. (This sample flow has session data files disabled.)

_TaskList
^^^^^^^^^^^^^^^^^^^

Location of task list files processed by Revit Batch Processor.

For this flow there is 1 task list file in this folder.
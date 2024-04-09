#############################################
Model Milestone
#############################################

*******
Summary
*******

The 'Model Milestone' flow is aimed at creating a dated set of detached Revit files for archiving purposes:
    

Actions Overview 
----------------

This flow is run through a powershell script which executes:

#. A pre-processing script collecting all Revit files to be archived.
#. Main Process: No 3 off parallel running sessions of Revit Batch Processor which:
    #. Create a detached copy of the Revit file(s) in a given location. (Revit files are opened with all worksets closed)
        #. Saves file under a new file name which includes a date stamp

#. A post process which:
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

- ModifyModelMilestone.py

    - task script executed by each Revit Batch Processor session

- Post_FilesOut.py

    - the post script executed by each Revit Batch Processor session

- Pre_MarkerFilesTaskList.py

    - the pre process script executed by single Revit Batch Processor session ( when just one batch processor session is run )

- settings.py

    - a module containing global variables / settings for this flow

- startMilestone.ps1

    - The powershell script executing:
        - concurrent Revit Batch Processor sessions


_Script/logs
^^^^^^^^^^^^^^^^^^^

Log files which cover script outputs outside of Revit Batch Processor log files

_settings
^^^^^^^^^^^^^^^^^^^

Location of Revit Batch Processor settings files.

For this flow there are 3 settings files in this folder, one for each session of Revit Batch Processor.


_SessionData
^^^^^^^^^^^^^^^^^^^

Directory containing Revit Batch Processor session data files. (This sample flow has session data files disabled.)

_TaskList
^^^^^^^^^^^^^^^^^^^

Location of task list files processed by Revit Batch Processor.

For this flow there are 3 task list file in this folder.
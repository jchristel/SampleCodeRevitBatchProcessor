#############################################
Files Out
#############################################

*******
Summary
*******

The 'File Out' flow is aimed at model issue processes requiring:

- Revit models to be issued and:
    - Certain views / sheets are removed from the model prior issue.
    - A purge unused elements is under taken.
    - Worksets of levels / grids / scope boxes / reference planes are checked and if required changed to the default value
    - Revision information is appended to the revit file name.

- NavisWorks:
    - Cache files are generated either from a number of 3D views or the entire model
    - Cache files are named following a given naming convention.

- IFC:
    - IFC files are generated either from a number of 3D views or the entire model
    - IFC files are named following a given naming convention.

- A meta data file for document exchange platforms 


Actions Overview 
----------------

This flow is run through a powershell script which executes:

#. A pre-processing script allowing the user to select which files to issue out.
#. STEP 1: No 3 off parallel running sessions of Revit Batch Processor which:
    #. Create a detached copy of the Revit file(s) in a given location. (Revit files are opened with all worksets closed)
        #. Saves file under a new file name includes Revision information
    #. Delete views as specified per model.
    #. Delete any links from the model ( That is so that the second step can open this model with all worksets open for exports to NWC and IFC)
    #. Workset checking and, if required adjusting, of of worksets of levels / grids / scope boxes / reference planes
    #. Create a text file for each new revit file containing meta data for document exchange platform
#. A STEP 2 pre-processing script creating task files based on revit files created in STEP 1.
#. STEP 2: No 3 off parallel running sessions of Revit Batch Processor which:
    #. Create detached copies of Revit files created in STEP 1
    #. Delete all views but the ones required to export.
    #. Exports view or entire model to navisworks cache file ( including revision information in file name )
    #. Create a text file for navisworks cache file containing meta data for document exchange platform
    #. Copies navisworks cache file into separate /BIM360 folder and strip revision information from file name. (This file can be used on BIM360 to directly overwrite previous versions)
    #. Exports view or entire model to ifc file ( including revision information in file name )
    #. Create a text file for ifc file containing meta data for document exchange platform
    #. Optimizes ifc file using Solibri IFC optimizer ( separate installation required )
#. A post process which:
    #. Combines meta data text files of all exports into single meta data file.
    #. Updates file list with latest revision information.
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

This folder contains a number of temp files:

- Step 2 creates temp revit files which are saved in this directory and deleted at the end of the flow.
- Pre processing script for STEP 2 writes task files for STEP 2 into this directory as well.

_sampleFiles
^^^^^^^^^^^^^^^^^^^

Any sample files provided. 

_Script
^^^^^^^^^^^^^^^^^^^

The python and powershell scripts of the flow:

- ModifyFilesOut_StepOne.py

    - the first task script executed by each Revit Batch Processor session

ModifyFilesOut_StepTwo

    - the second task script executed by each Revit Batch Processor session

- Post_FilesOut.py

    - the post script executed by the flow after all Revit Batch Processor sessions of STEP 1 and STEP 2 have finished

- Post_KillWSM.py

    - the post process script executed by each Revit Batch Processor session

- Pre_MarkerFiles.py

    - the pre process script executed by the second and third Revit Batch Processor session

- Pre_StepOne_MarkerFilesAndModelOutDir.py

    - the pre process script executed by the first Revit Batch Processor session of STEP 1 only

- Pre_StepTwo_FilesOut.py

    - the pre process script executed by the first Revit Batch Processor session of STEP 2 only

- settings.py

    - a module containing global variables / settings for this flow

- startAddRevision.ps1

    - The powershell script executing:
        - pre Revit Batch Processor scripts
        - concurrent Revit Batch Processor sessions STEP 1
        - concurrent Revit Batch Processor sessions STEP 2
        - post Revit Batch Processor scripts

- FileNames.csv

    - Revit project meta data file:
        - This is a comma separated text files which contains meta data of the revit files to be processed in the following format:
        - header row: none
        - column 1: current file name (Revit) or view name for IFC / NWC exports
        - column 2: Export file name (including revision separator prefix)
        - column 3: revision
        - column 4: revision suffix and end of file name
        - column 5: file extension in format .extension
        - column 6: meta data document number
        - column 7: meta data document name


_Script/logs
^^^^^^^^^^^^^^^^^^^

Log files which cover script outputs outside of Revit Batch Processor log files

_settings
^^^^^^^^^^^^^^^^^^^

Location of Revit Batch Processor settings files.

For this flow there are 6 settings files in this folder:

- 3 for STEP 1 - one for each session of Revit Batch Processor (OneA, OneB, OneC)
- 3 for STEP 2 - one for each session of Revit Batch Processor. (TwoA, TwoB, TwoC)

_SessionData
^^^^^^^^^^^^^^^^^^^

Directory containing Revit Batch Processor session data files. (This sample flow has session data files disabled.)

_TaskList
^^^^^^^^^^^^^^^^^^^

Location of task list files processed by Revit Batch Processor.

For this flow there are 3 task list files in this folder, one for each session of Revit Batch Processor.
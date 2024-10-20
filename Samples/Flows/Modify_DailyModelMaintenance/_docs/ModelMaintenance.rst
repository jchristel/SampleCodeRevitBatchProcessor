#############################################
Model Maintenance
#############################################

*******
Summary
*******

The 'Model Maintenance' flow ia aimed at a QA process where one has the requirement to regularly:

#. report on given categories:

    #. links (revit and cad)
    #. wall properties
    #. grids and levels
    #. worksets
    #. model health parameters
    #. sheets and sheets abbreviated
    #. shared parameters
    #. families in model and placement count
    #. views (abbreviated)
    #. rooms and ceilings geometry (which can be processed further -> i.e. which ceiling is in which room)
    #. warnings
    #. view template overrides

#. reload families
#. fix worksets of given categories
#. fix some warnings
#. remove duplicated line styles
#. remove unwanted shared parameters
#. rename loaded families
#. Enforce view naming policy


Actions Overview 
----------------

This flow is run through a powershell script which executes:

#. A pre-processing script collecting all Revit files in a given directory.
#. No 3 off parallel running sessions of Revit Batch Processor processing the selected files.
#. A first post process running in python 3.x which 

    #. processes the log files of the above sessions and searches for any exceptions messages therein.
    #. collates report files into combined csv files
    #. collates room and ceiling data reports and creates a rooms with associated ceiling types report
    #. collates view template reports and converts them into a flattened 3D array in parquet file format

#. A second post process script running in iron python 2.7 which:

    #. cleans up any marker files (log and work sharing monitor).


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

Directory containing any flow output.

#. A report file per revit file processed and category reported on.
#. A combined report file which contains all the reports per a single categories for all files.
#. Rooms and associated ceilings .json file
#. View template parquet files

_sampleFiles
^^^^^^^^^^^^^^^^^^^

Any sample files provided. 

_Script
^^^^^^^^^^^^^^^^^^^

The python and powershell scripts of the flow.

- ModifyDailyModelMaintenance.py

    - the task script executed by each Revit Batch Processor session

- Post_DailyModelMaintenance.py (requires python >3.8)

    - the first post script executed by the flow after all Revit Batch Processor sessions have finished

- Post_DailyModelMaintenance_cleanUp.py

    - the second post script executed by the flow after all Revit Batch Processor sessions and the fist post script have finished

- Post_AddRevisionKillWSM.py

    - the post process script executed by each Revit Batch Processor session

- Pre_ModifyDailyModelMaintenanceStandAlone.py

    - the pre script executed by the flow before any Revit Batch Processor sessions are started
    
- Pre_ModifyDailyModelMaintenance.py

    - the pre process script executed by each Revit Batch Processor session

- settings.py

    - a module containing global variables / settings for this flow

- startDailyMaintenance.ps1

    - The powershell script executing:

        - pre Revit Batch Processor scripts
        - concurrent Revit Batch Processor sessions
        - post Revit Batch Processor scripts

Report files used for some scripts:

- UnwantedSharedParameters.csv

    - First column: shared parameter name
    - second column: shared parameter GUID

- ProjectsWorksets.csv

    - First column: host file path
    - Second column: Workset Id
    - Third column: Workset name
    - Fourth column: is workset visible by default (TRUE/FALSE)

- RenameDirective.csv 
    
    Note: There can be multiple of the files. They all need to start with "RenameDirective" and need to be of file type ".csv"

    - First column: old family name
    - Second column: host file path (can be empty )
    - Third column: the family category
    - Fourth column: the new family name


_Script/logs
^^^^^^^^^^^^^^^^^^^

Log files which cover script outputs outside of Revit Batch Processor log files

_Script/utils
^^^^^^^^^^^^^^^^^^^

A number of utility scripts executed in the main script.

- check_tag_locations.py

    - Moves tags to their location as per report. (use case: In case a family reload moves a tag, this will move the tag back to its original location, since the tag location was recorded prior the family reload.)

- cleanup_actions.py

    - Set's up filters required to moves items to specified worksets.

- delete_elements.py

    - Deletes:

        - Unwanted shared parameters
        - Line styles starting with "IMPORT"
        - Line pattern duplicates ( keeps the one with the lowest Id -> oldest)
        - Un-used elevation markers 

- families.py

    - Reloads family from a given location
    - Renames families as per re-name directives

- geometry_data.py

    - Exports room data (properties and geometry) and ceiling data (properties and geometry) for post processing

- mark_views_for_deletion.py

    - Marks any views ending on copy x for deletion. (Prefixed view name with DELETE and a time stamp)

- model_health.py

    - Updates model health tracker family in model with model health values.
    - Writes model health data to file.

- reports.py

    Created the following reports:

    - links (revit and cad)
    - wall properties
    - grids and levels
    - worksets
    - sheets and sheets abbreviated
    - shared parameters
    - families in model and placement count
    - views (abbreviated)
    - warning types

- view_templates.py

    - exports view template graphical and filter override files as .json files
    
- warnings_solver.py

    Solves the following warnings:

    - Duplicate mark warnings.
    - Room tags outside of room warnings.
    - Overlapping room and area separation line warnings.

- worksets.py

    - Modify element worksets
    - Restores worksets default visibility as per report file.

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

For this flow there are 3 task list files in this folder, one for each session of Revit Batch Processor.


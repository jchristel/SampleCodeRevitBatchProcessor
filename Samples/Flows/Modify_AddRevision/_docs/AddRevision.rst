#############################################
Add Revision
#############################################

*******
Summary
*******

The 'Add Revision' flow ia aimed at a QA process where one has the requirement to apply a revision to a model issued to other parties. The revision information needs to be stored within the model, not just as part of the file name.
This flow adds a revision to the model and then applies that revision to a nominated sheet which, in turn, is set as the start up view for the model.

The revision information of that sheet can be used in other flows to append a revision to other exported  models (i.e. IFC or NavisWorks files)


Actions Overview 
----------------

This flow is run through a powershell script which executes:

#. A pre-processing script allowing the user to select which files apply a new revision to.
#. No 3 off parallel running sessions of Revit Batch Processor applying revisions to the selected files.
#. A post process which processes the log files of the above sessions and searches for any exceptions messages therein. And finally cleans up any marker files (log and work sharing monitor).


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

Directory containing any flow output. (None in this case.)

_sampleFiles
^^^^^^^^^^^^^^^^^^^

Any sample files provided. 

_Script
^^^^^^^^^^^^^^^^^^^

The python and powershell scripts of the flow.

- ModifyRevision.py

    - the task script executed by each Revit Batch Processor session

- Post_AddRevision.py

    - the post script executed by the flow after all Revit Batch Processor sessions have finished

- Post_AddRevisionKillWSM.py

    - the post process script executed by each Revit Batch Processor session

- Pre_AddRevision.py

    - the pre process script executed by each Revit Batch Processor session

- settings.py

    - a module containing global variables / settings for this flow

- startAddRevision.ps1

    - The powershell script executing:
        - pre Revit Batch Processor scripts
        - concurrent Revit Batch Processor sessions
        - post Revit Batch Processor scripts

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

For this flow there are 3 task list files in this folder, one for each session of Revit Batch Processor.
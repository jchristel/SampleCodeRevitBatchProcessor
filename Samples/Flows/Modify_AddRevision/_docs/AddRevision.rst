#############################################
Add Revision
#############################################

Summary
=======

The 'Add Revision' flow ia aimed at a QA process where one has the requirement to apply a revision to a model issued to other parties. The revision information needs to be stored within the model not just as part of the file name.
This flow adds a revision to the model and then applies that revision to a nominated sheet which, in turn, is set as the start up view for the model.

The revision information of that sheet can be used in other flows to append a revision to other exported  models (i.e. IFC or NavisWorks files)


Actions Overview 
==================

This flow is run through a powershell script which executes:

#. A pre-processing script allowing the user to select which files apply a new revision to.
#. No 3 off parallel running sessions of Revit Batch Processor applying revisions to the selected files.
#. A post process which processes the log files of the above sessions for any exceptions and cleans up any marker files (log and work sharing monitor).

Setup
======

Directory structure
-------------------

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
^^^^^

Directory containing flow related documentation.

_LogMarker
^^^^^^^^^^

Directory containing log marker files. Those will be deleted at the end of each flow run.

_sampleFiles
^^^^^^^^^^^^^

Any sample files provided.

_Script
^^^^^^^

The python and powershell scripts of the flow.

_Script/logs
^^^^^^^^^^^^^^

Log files which cover script outputs outside of Revit Batch Processor log files


Flow
====

#. Changing

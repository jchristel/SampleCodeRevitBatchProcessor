#############################################
Add Revision
#############################################

Summary
=======




Actions Overview 
==================


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

Contains test files for the various Revit versions supported.

_Script
^^^^^^^

The python and powershell scripts of the flow.

_Script/logs
^^^^^^^^^^^^^^

Log files which cover script outputs outside of Revit Batch Processor log files


Flow
====
